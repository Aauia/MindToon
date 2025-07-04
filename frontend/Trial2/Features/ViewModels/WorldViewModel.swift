import Foundation
import SwiftUI
import Combine

// MARK: - World ViewModel
@MainActor
class WorldViewModel: ObservableObject {
    // Published properties
    @Published var selectedWorld: WorldType = .imaginationWorld
    @Published var worldComics: [WorldType: [ComicGenerationResponse]] = [:]
    @Published var worldStats: [WorldType: WorldStatsResponse] = [:]
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?
    @Published var searchText: String = ""
    @Published var selectedGenreFilter: String?
    @Published var selectedArtStyleFilter: String?
    @Published var showFavoritesOnly: Bool = false
    @Published var sortBy: WorldComicSortBy = .newest
    @Published var currentPage: [WorldType: Int] = [:]
    @Published var hasMorePages: [WorldType: Bool] = [:]
    
    // Private properties
    private let worldManager = WorldManager.shared
    private var cancellables: Set<AnyCancellable> = []
    
    // Computed properties
    var filteredComics: [ComicGenerationResponse] {
        guard let comics = worldComics[selectedWorld] else { return [] }
        
        var filtered = comics
        
        // Apply search filter
        if !searchText.isEmpty {
            filtered = filtered.filter { comic in
                comic.title.localizedCaseInsensitiveContains(searchText) ||
                comic.concept.localizedCaseInsensitiveContains(searchText) ||
                comic.genre.localizedCaseInsensitiveContains(searchText)
            }
        }
        
        // Apply genre filter
        if let genreFilter = selectedGenreFilter {
            filtered = filtered.filter { $0.genre == genreFilter }
        }
        
        // Apply art style filter
        if let artStyleFilter = selectedArtStyleFilter {
            filtered = filtered.filter { $0.artStyle == artStyleFilter }
        }
        
        // Apply favorites filter
        if showFavoritesOnly {
            filtered = filtered.filter { $0.isFavorite }
        }
        
        return filtered
    }
    
    var availableGenres: [String] {
        guard let comics = worldComics[selectedWorld] else { return [] }
        return Array(Set(comics.map { $0.genre })).sorted()
    }
    
    var availableArtStyles: [String] {
        guard let comics = worldComics[selectedWorld] else { return [] }
        return Array(Set(comics.map { $0.artStyle })).sorted()
    }
    
    init() {
        setupBindings()
        initializeWorldData()
    }
    
    // MARK: - Setup
    private func setupBindings() {
        // Bind to WorldManager
        worldManager.$worlds
            .receive(on: DispatchQueue.main)
            .assign(to: \.worldComics, on: self)
            .store(in: &cancellables)
        
        worldManager.$worldStats
            .receive(on: DispatchQueue.main)
            .assign(to: \.worldStats, on: self)
            .store(in: &cancellables)
        
        worldManager.$isLoading
            .receive(on: DispatchQueue.main)
            .assign(to: \.isLoading, on: self)
            .store(in: &cancellables)
        
        worldManager.$errorMessage
            .receive(on: DispatchQueue.main)
            .assign(to: \.errorMessage, on: self)
            .store(in: &cancellables)
        
        worldManager.$currentPage
            .receive(on: DispatchQueue.main)
            .assign(to: \.currentPage, on: self)
            .store(in: &cancellables)
        
        worldManager.$hasMorePages
            .receive(on: DispatchQueue.main)
            .assign(to: \.hasMorePages, on: self)
            .store(in: &cancellables)
    }
    
    private func initializeWorldData() {
        Task {
            await loadInitialData()
        }
    }
    
    // MARK: - Data Loading
    func loadInitialData() async {
        await withTaskGroup(of: Void.self) { group in
            for worldType in WorldType.allCases {
                group.addTask {
                    await self.worldManager.loadWorldComics(for: worldType, page: 1)
                    await self.worldManager.loadWorldStats(for: worldType)
                }
            }
        }
    }
    
    func loadWorldComics(for worldType: WorldType, refresh: Bool = false) async {
        await worldManager.loadWorldComics(
            for: worldType,
            page: 1,
            refresh: refresh,
            favoritesOnly: showFavoritesOnly,
            sortBy: sortBy,
            searchTerm: searchText.isEmpty ? nil : searchText
        )
    }
    
    func loadMoreComics() async {
        await worldManager.loadNextPage(for: selectedWorld)
    }
    
    func refreshCurrentWorld() async {
        await worldManager.refreshWorld(selectedWorld)
    }
    
    func loadWorldStats(for worldType: WorldType, refresh: Bool = false) async {
        await worldManager.loadWorldStats(for: worldType, refresh: refresh)
    }
    
    // MARK: - World Management
    func switchWorld(to worldType: WorldType) {
        selectedWorld = worldType
        clearFilters()
        
        Task {
            // Load data for the new world if not already loaded
            if worldComics[worldType]?.isEmpty ?? true {
                await loadWorldComics(for: worldType)
            }
            
            if worldStats[worldType] == nil {
                await loadWorldStats(for: worldType)
            }
        }
    }
    
    func getComicsCount(for worldType: WorldType) -> Int {
        return worldManager.getComicsCount(for: worldType)
    }
    
    func getFavoriteComics(for worldType: WorldType) -> [ComicGenerationResponse] {
        return worldManager.getFavoriteComics(for: worldType)
    }
    
    func getPublicComics(for worldType: WorldType) -> [ComicGenerationResponse] {
        return worldManager.getPublicComics(for: worldType)
    }
    
    // MARK: - Comic Management
    func addComicToCurrentWorld(_ comic: ComicGenerationResponse) {
        worldManager.addComicToWorld(comic, worldType: selectedWorld)
    }
    
    func updateComic(_ comic: ComicGenerationResponse) {
        worldManager.updateComicInWorld(comic, worldType: selectedWorld)
    }
    
    func removeComic(comicId: Int) {
        worldManager.removeComicFromWorld(comicId: comicId, worldType: selectedWorld)
    }
    
    func toggleFavorite(for comic: ComicGenerationResponse) async {
        do {
            let token = await AuthManager.shared.getStoredToken()
            guard let token = token else {
                throw APIError.unauthorized
            }
            
            let updateRequest = ComicUpdateRequest(
                title: nil,
                isFavorite: !comic.isFavorite,
                isPublic: nil
            )
            
            _ = try await APIClient.shared.updateComic(id: comic.id, updates: updateRequest, token: token)
            
            // Update local data
            let updatedComic = ComicGenerationResponse(
                id: comic.id,
                title: comic.title,
                concept: comic.concept,
                genre: comic.genre,
                artStyle: comic.artStyle,
                worldType: comic.worldType,
                imageBase64: comic.imageBase64,
                panelsData: comic.panelsData,
                createdAt: comic.createdAt,
                isFavorite: !comic.isFavorite,
                isPublic: comic.isPublic,
                hasDetailedScenario: comic.hasDetailedScenario
            )
            
            updateComic(updatedComic)
            
        } catch {
            errorMessage = (error as? APIError)?.userFriendlyMessage ?? error.localizedDescription
        }
    }
    
    func togglePublic(for comic: ComicGenerationResponse) async {
        do {
            let token = await AuthManager.shared.getStoredToken()
            guard let token = token else {
                throw APIError.unauthorized
            }
            
            let updateRequest = ComicUpdateRequest(
                title: nil,
                isFavorite: nil,
                isPublic: !comic.isPublic
            )
            
            _ = try await APIClient.shared.updateComic(id: comic.id, updates: updateRequest, token: token)
            
            // Update local data
            let updatedComic = ComicGenerationResponse(
                id: comic.id,
                title: comic.title,
                concept: comic.concept,
                genre: comic.genre,
                artStyle: comic.artStyle,
                worldType: comic.worldType,
                imageBase64: comic.imageBase64,
                panelsData: comic.panelsData,
                createdAt: comic.createdAt,
                isFavorite: comic.isFavorite,
                isPublic: !comic.isPublic,
                hasDetailedScenario: comic.hasDetailedScenario
            )
            
            updateComic(updatedComic)
            
        } catch {
            errorMessage = (error as? APIError)?.userFriendlyMessage ?? error.localizedDescription
        }
    }
    
    func deleteComic(_ comic: ComicGenerationResponse) async {
        do {
            let token = await AuthManager.shared.getStoredToken()
            guard let token = token else {
                throw APIError.unauthorized
            }
            
            _ = try await APIClient.shared.deleteComic(id: comic.id, token: token)
            
            // Remove from local data
            removeComic(comicId: comic.id)
            
        } catch {
            errorMessage = (error as? APIError)?.userFriendlyMessage ?? error.localizedDescription
        }
    }
    
    // MARK: - Filtering and Sorting
    func applyGenreFilter(_ genre: String?) {
        selectedGenreFilter = genre
    }
    
    func applyArtStyleFilter(_ artStyle: String?) {
        selectedArtStyleFilter = artStyle
    }
    
    func toggleFavoritesFilter() {
        showFavoritesOnly.toggle()
        Task {
            await loadWorldComics(for: selectedWorld, refresh: true)
        }
    }
    
    func applySorting(_ sortOption: WorldComicSortBy) {
        sortBy = sortOption
        Task {
            await loadWorldComics(for: selectedWorld, refresh: true)
        }
    }
    
    func clearFilters() {
        searchText = ""
        selectedGenreFilter = nil
        selectedArtStyleFilter = nil
        showFavoritesOnly = false
        sortBy = .newest
    }
    
    func applyFilters() {
        Task {
            await loadWorldComics(for: selectedWorld, refresh: true)
        }
    }
    
    // MARK: - Search
    func searchComics(query: String) {
        searchText = query
        if query.isEmpty {
            // Reset to full list
            return
        }
        
        Task {
            await loadWorldComics(for: selectedWorld, refresh: true)
        }
    }
    
    // MARK: - Statistics
    func getTotalComicsAcrossWorlds() -> Int {
        return worldStats.values.reduce(0) { $0 + $1.totalComics }
    }
    
    func getFavoriteComicsAcrossWorlds() -> Int {
        return worldStats.values.reduce(0) { $0 + $1.favoriteComics }
    }
    
    func getPublicComicsAcrossWorlds() -> Int {
        return worldStats.values.reduce(0) { $0 + $1.publicComics }
    }
    
    func getMostPopularWorld() -> WorldType? {
        return worldStats.max(by: { $0.value.totalComics < $1.value.totalComics })?.key
    }
    
    func getWorldDistribution() -> [WorldType: Double] {
        let total = Double(getTotalComicsAcrossWorlds())
        guard total > 0 else { return [:] }
        
        var distribution: [WorldType: Double] = [:]
        for (worldType, stats) in worldStats {
            distribution[worldType] = Double(stats.totalComics) / total
        }
        return distribution
    }
    
    func getWorldProgress(for worldType: WorldType) -> Double {
        // This could represent progress towards some goal or achievement
        guard let stats = worldStats[worldType] else { return 0.0 }
        
        // Example: Progress based on number of comics created
        let maxComicsForFullProgress = 50
        return min(Double(stats.totalComics) / Double(maxComicsForFullProgress), 1.0)
    }
    
    // MARK: - UI State Management
    func clearError() {
        errorMessage = nil
        worldManager.clearError()
    }
    
    func isCurrentWorldEmpty() -> Bool {
        return filteredComics.isEmpty
    }
    
    func canLoadMore() -> Bool {
        return hasMorePages[selectedWorld] ?? false
    }
    
    func shouldShowEmptyState() -> Bool {
        return !isLoading && isCurrentWorldEmpty() && searchText.isEmpty && selectedGenreFilter == nil && selectedArtStyleFilter == nil && !showFavoritesOnly
    }
    
    func shouldShowNoResultsState() -> Bool {
        return !isLoading && isCurrentWorldEmpty() && (!searchText.isEmpty || selectedGenreFilter != nil || selectedArtStyleFilter != nil || showFavoritesOnly)
    }
    
    // MARK: - World Insights
    func getWorldInsights(for worldType: WorldType) -> WorldInsights? {
        guard let stats = worldStats[worldType],
              let comics = worldComics[worldType] else { return nil }
        
        let genreDistribution = Dictionary(grouping: comics, by: { $0.genre })
            .mapValues { $0.count }
        
        let artStyleDistribution = Dictionary(grouping: comics, by: { $0.artStyle })
            .mapValues { $0.count }
        
        let recentComics = comics.filter { comic in
            // Comics created in the last 7 days
            if let date = ISO8601DateFormatter().date(from: comic.createdAt) {
                return date.timeIntervalSinceNow > -7 * 24 * 60 * 60
            }
            return false
        }
        
        return WorldInsights(
            worldType: worldType,
            totalComics: stats.totalComics,
            favoritePercentage: stats.totalComics > 0 ? Double(stats.favoriteComics) / Double(stats.totalComics) * 100 : 0,
            publicPercentage: stats.totalComics > 0 ? Double(stats.publicComics) / Double(stats.totalComics) * 100 : 0,
            recentActivity: recentComics.count,
            popularGenre: genreDistribution.max(by: { $0.value < $1.value })?.key,
            popularArtStyle: artStyleDistribution.max(by: { $0.value < $1.value })?.key,
            genreDistribution: genreDistribution,
            artStyleDistribution: artStyleDistribution
        )
    }
}

// MARK: - World Insights Model
struct WorldInsights {
    let worldType: WorldType
    let totalComics: Int
    let favoritePercentage: Double
    let publicPercentage: Double
    let recentActivity: Int
    let popularGenre: String?
    let popularArtStyle: String?
    let genreDistribution: [String: Int]
    let artStyleDistribution: [String: Int]
}

// MARK: - Preview Data
#if DEBUG
extension WorldViewModel {
    static let preview: WorldViewModel = {
        let viewModel = WorldViewModel()
        
        // Mock data
        viewModel.worldComics = [
            .imaginationWorld: [
                ComicGenerationResponse(
                    id: 1,
                    title: "Space Adventure",
                    concept: "Heroes exploring the galaxy",
                    genre: "sci-fi",
                    artStyle: "comic book",
                    worldType: .imaginationWorld,
                    imageBase64: "sample_data",
                    panelsData: "{}",
                    createdAt: "2024-01-15T10:30:00Z",
                    isFavorite: true,
                    isPublic: false,
                    hasDetailedScenario: true
                ),
                ComicGenerationResponse(
                    id: 2,
                    title: "Magic Quest",
                    concept: "A wizard's journey",
                    genre: "fantasy",
                    artStyle: "watercolor",
                    worldType: .imaginationWorld,
                    imageBase64: "sample_data",
                    panelsData: "{}",
                    createdAt: "2024-01-14T15:20:00Z",
                    isFavorite: false,
                    isPublic: true,
                    hasDetailedScenario: false
                )
            ]
        ]
        
        viewModel.worldStats = [
            .imaginationWorld: WorldStatsResponse.preview,
            .dreamWorld: WorldStatsResponse.dreamWorldPreview,
            .mindWorld: WorldStatsResponse.mindWorldPreview
        ]
        
        return viewModel
    }()
}

extension WorldInsights {
    static let preview = WorldInsights(
        worldType: .imaginationWorld,
        totalComics: 15,
        favoritePercentage: 33.3,
        publicPercentage: 20.0,
        recentActivity: 3,
        popularGenre: "fantasy",
        popularArtStyle: "comic book",
        genreDistribution: [
            "fantasy": 6,
            "sci-fi": 4,
            "adventure": 3,
            "comedy": 2
        ],
        artStyleDistribution: [
            "comic book": 8,
            "watercolor": 4,
            "cartoon": 3
        ]
    )
}
#endif 