import Foundation
import SwiftUI
import Combine

// MARK: - Collection ViewModel
@MainActor
class CollectionViewModel: ObservableObject {
    // Published properties
    @Published var collections: [ComicCollectionResponse] = []
    @Published var selectedCollection: ComicCollectionResponse?
    @Published var collectionStats: CollectionStats?
    @Published var isLoading: Bool = false
    @Published var isCreating: Bool = false
    @Published var isEditing: Bool = false
    @Published var errorMessage: String?
    @Published var searchText: String = ""
    @Published var selectedWorldFilter: WorldType?
    @Published var showPublicOnly: Bool = false
    @Published var sortBy: CollectionSortBy = .newest
    @Published var selectedTags: Set<String> = []
    @Published var currentPage: Int = 1
    @Published var hasMorePages: Bool = true
    @Published var showingFilters: Bool = false
    @Published var sortOption: CollectionSortOption = .name
    @Published var minComicsFilter: Int = 0
    
    // Form data
    @Published var formData = CollectionFormData()
    
    // Private properties
    private let apiClient = APIClient.shared
    private var cancellables: Set<AnyCancellable> = []
    private let pageSize = 20
    
    // Computed properties
    var filteredCollections: [ComicCollectionResponse] {
        var filtered = collections
        
        // Apply search filter
        if !searchText.isEmpty {
            filtered = filtered.filter { collection in
                collection.name.localizedCaseInsensitiveContains(searchText) ||
                (collection.description?.localizedCaseInsensitiveContains(searchText) ?? false) ||
                collection.tags.contains { $0.localizedCaseInsensitiveContains(searchText) }
            }
        }
        
        // Apply world filter
        if let worldFilter = selectedWorldFilter {
            filtered = filtered.filter { $0.worldType == worldFilter }
        }
        
        // Apply public filter
        if showPublicOnly {
            filtered = filtered.filter { $0.isPublic }
        }
        
        // Apply tag filter
        if !selectedTags.isEmpty {
            filtered = filtered.filter { collection in
                !Set(collection.tags).isDisjoint(with: selectedTags)
            }
        }
        
        return filtered
    }
    
    var availableTags: [String] {
        let allTags = collections.flatMap { $0.tags }
        return Array(Set(allTags)).sorted()
    }
    
    var worldDistribution: [WorldType: Int] {
        Dictionary(grouping: collections, by: { $0.worldType })
            .mapValues { $0.count }
    }
    
    init() {
        NotificationCenter.default.addObserver(self, selector: #selector(handleLogout), name: .userDidLogout, object: nil)
        setupBindings()
        Task {
            await loadInitialData()
        }
    }
    
    @objc private func handleLogout() {
        collections = []
        selectedCollection = nil
        isLoading = false
        errorMessage = nil
    }
    
    deinit {
        NotificationCenter.default.removeObserver(self)
    }
    
    // MARK: - Setup
    private func setupBindings() {
        // Auto-search when search text changes (with debounce)
        $searchText
            .debounce(for: .milliseconds(500), scheduler: RunLoop.main)
            .sink { [weak self] _ in
                Task {
                    await self?.searchCollections()
                }
            }
            .store(in: &cancellables)
    }
    
    // MARK: - Data Loading
    func loadInitialData() async {
        await withTaskGroup(of: Void.self) { group in
            group.addTask { await self.loadCollections() }
            group.addTask { await self.loadCollectionStats() }
        }
    }
    
    func loadCollections(refresh: Bool = false) async {
        if refresh {
            currentPage = 1
            collections.removeAll()
        }
        
        isLoading = true
        errorMessage = nil
        
        do {
            let token = await AuthManager.shared.getStoredToken()
            guard let token = token else {
                throw APIError.unauthorized
            }
            
            let request = CollectionSearchRequest(
                worldType: selectedWorldFilter,
                searchTerm: searchText.isEmpty ? nil : searchText,
                tags: selectedTags.isEmpty ? nil : Array(selectedTags),
                isPublic: showPublicOnly ? true : nil,
                sortBy: sortBy,
                page: currentPage,
                limit: pageSize
            )
            
            let newCollections = try await apiClient.searchCollections(request: request, token: token)
            
            if currentPage == 1 {
                collections = newCollections
            } else {
                collections.append(contentsOf: newCollections)
            }
            
            hasMorePages = newCollections.count == pageSize
            
            print("✅ Loaded \(newCollections.count) collections (page \(currentPage))")
            
        } catch {
            ErrorLogger.shared.log(
                error as? APIError ?? APIError.networkError(error),
                context: "loadCollections"
            )
            errorMessage = (error as? APIError)?.userFriendlyMessage ?? error.localizedDescription
        }
        
        isLoading = false
    }
    
    func loadMoreCollections() async {
        guard hasMorePages && !isLoading else { return }
        
        currentPage += 1
        await loadCollections()
    }
    
    func refreshCollections() async {
        await loadCollections(refresh: true)
        await loadCollectionStats()
    }
    
    func loadCollectionStats() async {
        do {
            let token = await AuthManager.shared.getStoredToken()
            guard let token = token else {
                throw APIError.unauthorized
            }
            
            let stats = try await apiClient.getCollectionStats(token: token)
            collectionStats = stats
            
        } catch {
            ErrorLogger.shared.log(
                error as? APIError ?? APIError.networkError(error),
                context: "loadCollectionStats"
            )
            print("❌ Failed to load collection stats: \(error)")
        }
    }
    
    // MARK: - Collection Management
    func createCollection() async {
        guard formData.isValid else {
            errorMessage = "Please enter a collection name"
            return
        }
        
        isCreating = true
        errorMessage = nil
        
        do {
            let token = await AuthManager.shared.getStoredToken()
            guard let token = token else {
                throw APIError.unauthorized
            }
            
            let request = ComicCollectionRequest(
                name: formData.name,
                description: formData.description.isEmpty ? nil : formData.description,
                worldType: formData.worldType,
                isPublic: formData.isPublic,
                tags: formData.tags
            )
            
            let newCollection = try await apiClient.createCollection(request: request)
            
            // Add to local collections
            collections.insert(newCollection, at: 0)
            
            // Reset form
            formData.reset()
            
            print("✅ Created collection: \(newCollection.name)")
            
        } catch {
            ErrorLogger.shared.log(
                error as? APIError ?? APIError.networkError(error),
                context: "createCollection"
            )
            errorMessage = (error as? APIError)?.userFriendlyMessage ?? error.localizedDescription
        }
        
        isCreating = false
    }
    
    func updateCollection(_ collection: ComicCollectionResponse) async {
        guard formData.isValid else {
            errorMessage = "Please enter a collection name"
            return
        }
        
        isEditing = true
        errorMessage = nil
        
        do {
            let token = await AuthManager.shared.getStoredToken()
            guard let token = token else {
                throw APIError.unauthorized
            }
            
            let request = CollectionUpdateRequest(
                name: formData.name,
                description: formData.description.isEmpty ? nil : formData.description,
                isPublic: formData.isPublic,
                tags: formData.tags
            )
            
            let updatedCollection = try await apiClient.updateCollection(
                id: collection.id,
                updates: request,
                token: token
            )
            
            // Update local collection
            if let index = collections.firstIndex(where: { $0.id == collection.id }) {
                collections[index] = updatedCollection
            }
            
            selectedCollection = updatedCollection
            
            print("✅ Updated collection: \(updatedCollection.name)")
            
        } catch {
            ErrorLogger.shared.log(
                error as? APIError ?? APIError.networkError(error),
                context: "updateCollection - \(collection.id)"
            )
            errorMessage = (error as? APIError)?.userFriendlyMessage ?? error.localizedDescription
        }
        
        isEditing = false
    }
    
    func deleteCollection(_ collection: ComicCollectionResponse) async {
        do {
            let token = await AuthManager.shared.getStoredToken()
            guard let token = token else {
                throw APIError.unauthorized
            }
            
            _ = try await apiClient.deleteCollection(id: collection.id, token: token)
            
            // Remove from local collections
            collections.removeAll { $0.id == collection.id }
            
            if selectedCollection?.id == collection.id {
                selectedCollection = nil
            }
            
            print("✅ Deleted collection: \(collection.name)")
            
        } catch {
            ErrorLogger.shared.log(
                error as? APIError ?? APIError.networkError(error),
                context: "deleteCollection - \(collection.id)"
            )
            errorMessage = (error as? APIError)?.userFriendlyMessage ?? error.localizedDescription
        }
    }
    
    // MARK: - Comic Management in Collections
    func addComicToCollection(comicId: Int, collectionId: Int) async {
        do {
            let token = await AuthManager.shared.getStoredToken()
            guard let token = token else {
                throw APIError.unauthorized
            }
            
            let _ = try await apiClient.addComicToCollection(
                collectionId: collectionId,
                comicId: comicId,
               
            )
            
            if let index = collections.firstIndex(where: { $0.id == collectionId }) {
                var updatedCollection = collections[index]
                updatedCollection = ComicCollectionResponse(
                    id: updatedCollection.id,
                    name: updatedCollection.name,
                    description: updatedCollection.description,
                    worldType: updatedCollection.worldType,
                    isPublic: updatedCollection.isPublic,
                    comicsCount: updatedCollection.comicsCount + 1, // or - 1 for remove
                    tags: updatedCollection.tags,
                    createdAt: updatedCollection.createdAt,
                    updatedAt: Date().ISO8601Format(),
                    comics: updatedCollection.comics,
                    previewImages: updatedCollection.previewImages // <-- FIXED
                )
                collections[index] = updatedCollection
            }
            
            print("✅ Added comic \(comicId) to collection \(collectionId)")
            
        } catch {
            ErrorLogger.shared.log(
                error as? APIError ?? APIError.networkError(error),
                context: "addComicToCollection - comic: \(comicId), collection: \(collectionId)"
            )
            errorMessage = (error as? APIError)?.userFriendlyMessage ?? error.localizedDescription
        }
    }
    
    func removeComicFromCollection(comicId: Int, collectionId: Int) async {
        do {
            let token = await AuthManager.shared.getStoredToken()
            guard let token = token else {
                throw APIError.unauthorized
            }
            
            _ = try await apiClient.removeComicFromCollection(
                collectionId: collectionId,
                comicId: comicId,
                token: token
            )
            
            // Update local collection comic count
            if let index = collections.firstIndex(where: { $0.id == collectionId }) {
                var updatedCollection = collections[index]
                updatedCollection = ComicCollectionResponse(
                    id: updatedCollection.id,
                    name: updatedCollection.name,
                    description: updatedCollection.description,
                    worldType: updatedCollection.worldType,
                    isPublic: updatedCollection.isPublic,
                    comicsCount: max(0, updatedCollection.comicsCount - 1),
                    tags: updatedCollection.tags,
                    createdAt: updatedCollection.createdAt,
                    updatedAt: Date().ISO8601Format(),
                    comics: updatedCollection.comics,
                    previewImages: updatedCollection.previewImages // <-- FIXED
                )
                collections[index] = updatedCollection
            }
            
            print("✅ Removed comic \(comicId) from collection \(collectionId)")
            
        } catch {
            ErrorLogger.shared.log(
                error as? APIError ?? APIError.networkError(error),
                context: "removeComicFromCollection - comic: \(comicId), collection: \(collectionId)"
            )
            errorMessage = (error as? APIError)?.userFriendlyMessage ?? error.localizedDescription
        }
    }
    
    // MARK: - Filtering and Sorting
    func applyWorldFilter(_ worldType: WorldType?) {
        selectedWorldFilter = worldType
        Task {
            await loadCollections(refresh: true)
        }
    }
    
    func togglePublicFilter() {
        showPublicOnly.toggle()
        Task {
            await loadCollections(refresh: true)
        }
    }
    
    func applySorting(_ sortOption: CollectionSortBy) {
        sortBy = sortOption
        Task {
            await loadCollections(refresh: true)
        }
    }
    
    func toggleTag(_ tag: String) {
        if selectedTags.contains(tag) {
            selectedTags.remove(tag)
        } else {
            selectedTags.insert(tag)
        }
        
        Task {
            await loadCollections(refresh: true)
        }
    }
    
    func clearFilters() {
        searchText = ""
        selectedWorldFilter = nil
        showPublicOnly = false
        selectedTags.removeAll()
        sortBy = .newest
        
        Task {
            await loadCollections(refresh: true)
        }
    }
    
    // MARK: - Search
    private func searchCollections() async {
        await loadCollections(refresh: true)
    }
    
    // MARK: - Form Management
    func prepareFormForCreation() {
        formData.reset()
        selectedCollection = nil
    }
    
    func prepareFormForEditing(_ collection: ComicCollectionResponse) {
        formData.name = collection.name
        formData.description = collection.description ?? ""
        formData.worldType = collection.worldType
        formData.isPublic = collection.isPublic
        formData.tags = collection.tags
        selectedCollection = collection
    }
    
    func addTagToForm(_ tag: String) {
        if !formData.tags.contains(tag) {
            formData.tags.append(tag)
        }
    }
    
    func removeTagFromForm(_ tag: String) {
        formData.tags.removeAll { $0 == tag }
    }
    
    // MARK: - Collection Sharing
    func shareCollection(_ collection: ComicCollectionResponse, shareType: CollectionShareType) async -> CollectionShareResponse? {
        do {
            let token = await AuthManager.shared.getStoredToken()
            guard let token = token else {
                throw APIError.unauthorized
            }
            
            let request = CollectionShareRequest(
                collectionId: collection.id,
                shareType: shareType,
                message: nil
            )
            
            let shareResponse = try await apiClient.shareCollection(request: request, token: token)
            
            print("✅ Shared collection \(collection.name) via \(shareType.displayName)")
            return shareResponse
            
        } catch {
            ErrorLogger.shared.log(
                error as? APIError ?? APIError.networkError(error),
                context: "shareCollection - \(collection.id)"
            )
            errorMessage = (error as? APIError)?.userFriendlyMessage ?? error.localizedDescription
            return nil
        }
    }
    
    // MARK: - Statistics and Insights
    func getCollectionInsights() -> CollectionInsights? {
        guard let stats = collectionStats else { return nil }
        
        let tagFrequency = Dictionary(
            collections.flatMap { $0.tags }.map { ($0, 1) },
            uniquingKeysWith: +
        )
        
        let averageComicsPerCollection = collections.isEmpty ? 0.0 : 
            Double(collections.reduce(0) { $0 + $1.comicsCount }) / Double(collections.count)
        
        return CollectionInsights(
            totalCollections: stats.totalCollections,
            averageComicsPerCollection: averageComicsPerCollection,
            mostPopularTags: Array(tagFrequency.sorted { $0.value > $1.value }.prefix(5)),
            worldDistribution: worldDistribution,
            publicCollectionPercentage: stats.totalCollections > 0 ? 
                Double(stats.publicCollections) / Double(stats.totalCollections) * 100 : 0
        )
    }
    
    // MARK: - Utility Methods
    func clearError() {
        errorMessage = nil
    }
    
    func isCollectionEmpty() -> Bool {
        return filteredCollections.isEmpty
    }
    
    func canLoadMore() -> Bool {
        return hasMorePages && !isLoading
    }
    
    func shouldShowEmptyState() -> Bool {
        return !isLoading && collections.isEmpty && searchText.isEmpty && selectedWorldFilter == nil && !showPublicOnly
    }
    
    func shouldShowNoResultsState() -> Bool {
        return !isLoading && filteredCollections.isEmpty && (!searchText.isEmpty || selectedWorldFilter != nil || showPublicOnly)
    }
}

// MARK: - Collection Insights Model
struct CollectionInsights {
    let totalCollections: Int
    let averageComicsPerCollection: Double
    let mostPopularTags: [(String, Int)]
    let worldDistribution: [WorldType: Int]
    let publicCollectionPercentage: Double
}

// MARK: - Preview Data
#if DEBUG
extension CollectionViewModel {
    static let preview: CollectionViewModel = {
        let viewModel = CollectionViewModel()
        
        viewModel.collections = [
            ComicCollectionResponse.preview,
            ComicCollectionResponse.dreamWorldPreview,
            ComicCollectionResponse.mindWorldPreview
        ]
        
        viewModel.collectionStats = CollectionStats.preview
        
        return viewModel
    }()
}

extension CollectionInsights {
    static let preview = CollectionInsights(
        totalCollections: 15,
        averageComicsPerCollection: 3.2,
        mostPopularTags: [
            ("adventure", 8),
            ("fantasy", 6),
            ("comedy", 4),
            ("drama", 3),
            ("sci-fi", 2)
        ],
        worldDistribution: [
            .imaginationWorld: 8,
            .dreamWorld: 4,
            .mindWorld: 3
        ],
        publicCollectionPercentage: 53.3
    )
}
#endif 
