import Foundation
import Combine

// MARK: - World Manager
@MainActor
class WorldManager: ObservableObject {
    static let shared = WorldManager()
    
    // Published properties
    @Published var worlds: [WorldType: [ComicGenerationResponse]] = [:]
    @Published var worldStats: [WorldType: WorldStatsResponse] = [:]
    @Published var worldAnalytics: [WorldType: WorldAnalytics] = [:]
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?
    @Published var currentPage: [WorldType: Int] = [:]
    @Published var hasMorePages: [WorldType: Bool] = [:]
    
    // Private properties
    private let apiClient = APIClient.shared
    private var cancellables: Set<AnyCancellable> = []
    private let cache = WorldCache()
    
    // Constants
    private let pageSize = 20
    private let maxCacheAge: TimeInterval = 5 * 60 // 5 minutes
    
    private init() {
        initializeWorlds()
        NotificationCenter.default.addObserver(self, selector: #selector(handleLogout), name: .userDidLogout, object: nil)
    }

    @objc private func handleLogout() {
        clearCache()
        worlds = [:]
        worldStats = [:]
        worldAnalytics = [:]
        isLoading = false;
        errorMessage = nil;
        currentPage = [:]
        hasMorePages = [:]
        initializeWorlds() // Optionally re-initialize empty structure
    }

    deinit {
        NotificationCenter.default.removeObserver(self)
    }
    
    // MARK: - Initialization
    private func initializeWorlds() {
        for worldType in WorldType.allCases {
            worlds[worldType] = []
            currentPage[worldType] = 1
            hasMorePages[worldType] = true
        }
    }
    
    // MARK: - World Comics Management
    func loadWorldComics(
        for worldType: WorldType,
        page: Int = 1,
        refresh: Bool = false,
        favoritesOnly: Bool = false,
        sortBy: WorldComicSortBy = .newest,
        searchTerm: String? = nil
    ) async {
        
        // Check cache first if not refreshing
        if !refresh, let cachedComics = cache.getComics(for: worldType, page: page) {
            if page == 1 {
                worlds[worldType] = cachedComics
            } else {
                worlds[worldType]?.append(contentsOf: cachedComics)
            }
            return
        }
        
        isLoading = true
        errorMessage = nil
        
        do {
            let token = await AuthManager.shared.getStoredToken()
            guard let token = token else {
                throw APIError.unauthorized
            }
            
            let request = WorldComicsRequest(
                worldType: worldType,
                page: page,
                perPage: pageSize,
                favoritesOnly: favoritesOnly,
                sortBy: sortBy,
                searchTerm: searchTerm
            )
            
            let comics = try await apiClient.getWorldComics(request: request)
            
            // Update UI
            if page == 1 {
                worlds[worldType] = comics
            } else {
                worlds[worldType]?.append(contentsOf: comics)
            }
            
            // Update pagination
            currentPage[worldType] = page
            hasMorePages[worldType] = comics.count == pageSize
            
            // Cache results
            cache.setComics(comics, for: worldType, page: page)
            
            print("✅ Loaded \(comics.count) comics for \(worldType.displayName) (page \(page))")
            
        } catch let decodingError as DecodingError {
            // Handle specific decoding errors gracefully
            ErrorLogger.shared.log(
                APIError.decodingError(decodingError),
                context: "loadWorldComics - \(worldType.displayName)",
                userID: await AuthManager.shared.currentUser?.username
            )
            print("❌ Failed to decode comics for \(worldType.displayName): \(decodingError)")
            
            // Provide fallback empty array for decoding errors
            if page == 1 {
                worlds[worldType] = []
            }
            errorMessage = "Failed to load comics: Data format error"
            
        } catch {
            ErrorLogger.shared.log(
                error as? APIError ?? APIError.networkError(error),
                context: "loadWorldComics - \(worldType.displayName)",
                userID: await AuthManager.shared.currentUser?.username
            )
            errorMessage = (error as? APIError)?.userFriendlyMessage ?? error.localizedDescription
            print("❌ Failed to load comics for \(worldType.displayName): \(error)")
        }
        
        isLoading = false
    }
    
    func loadNextPage(for worldType: WorldType) async {
        guard let currentPage = currentPage[worldType],
              hasMorePages[worldType] == true else { return }
        
        await loadWorldComics(for: worldType, page: currentPage + 1)
    }
    
    func refreshWorld(_ worldType: WorldType) async {
        cache.clearComics(for: worldType)
        await loadWorldComics(for: worldType, page: 1, refresh: true)
        await loadWorldStats(for: worldType, refresh: true)
    }
    
    // MARK: - World Statistics
    func loadWorldStats(for worldType: WorldType, refresh: Bool = false) async {
        // Check cache first
        if !refresh, let cachedStats = cache.getStats(for: worldType) {
            worldStats[worldType] = cachedStats
            return
        }
        
        do {
            let token = await AuthManager.shared.getStoredToken()
            guard let token = token else {
                throw APIError.unauthorized
            }
            
            let stats = try await apiClient.getWorldStats(worldType: worldType)
            worldStats[worldType] = stats
            
            // Cache results
            cache.setStats(stats, for: worldType)
            
            print("✅ Loaded stats for \(worldType.displayName)")
            
        } catch let decodingError as DecodingError {
            // Handle specific decoding errors gracefully
            ErrorLogger.shared.log(
                APIError.decodingError(decodingError),
                context: "loadWorldStats - \(worldType.displayName)"
            )
            print("❌ Failed to decode stats for \(worldType.displayName): \(decodingError)")
            
            // Provide fallback stats with default values
            let fallbackStats = WorldStatsResponse(
                worldType: worldType,
                totalComics: 0,
                favoriteComics: 0,
                publicComics: 0,
                totalCollections: 0,
                totalScenarios: nil, // Use nil for missing field
                lastActivity: nil
            )
            worldStats[worldType] = fallbackStats
            
        } catch {
            ErrorLogger.shared.log(
                error as? APIError ?? APIError.networkError(error),
                context: "loadWorldStats - \(worldType.displayName)"
            )
            print("❌ Failed to load stats for \(worldType.displayName): \(error)")
            
            // Provide fallback stats for network errors
            let fallbackStats = WorldStatsResponse(
                worldType: worldType,
                totalComics: 0,
                favoriteComics: 0,
                publicComics: 0,
                totalCollections: 0,
                totalScenarios: nil,
                lastActivity: nil
            )
            worldStats[worldType] = fallbackStats
        }
    }
    
    func loadAllWorldStats() async {
        await withTaskGroup(of: Void.self) { group in
            for worldType in WorldType.allCases {
                group.addTask {
                    await self.loadWorldStats(for: worldType)
                }
            }
        }
    }
    
    // MARK: - World Analytics
    func loadWorldAnalytics(for worldType: WorldType) async {
        do {
            let token = await AuthManager.shared.getStoredToken()
            guard let token = token else {
                throw APIError.unauthorized
            }
            
            let analytics = try await apiClient.getWorldAnalytics(worldType: worldType, token: token)
            worldAnalytics[worldType] = analytics
            
            print("✅ Loaded analytics for \(worldType.displayName)")
            
        } catch {
            ErrorLogger.shared.log(
                error as? APIError ?? APIError.networkError(error),
                context: "loadWorldAnalytics - \(worldType.displayName)"
            )
            print("❌ Failed to load analytics for \(worldType.displayName): \(error)")
        }
    }
    
    // MARK: - Comic Management
    func addComicToWorld(_ comic: ComicGenerationResponse, worldType: WorldType) {
        if worlds[worldType] == nil {
            worlds[worldType] = []
        }
        worlds[worldType]?.insert(comic, at: 0)
        
        // Update stats
        if var stats = worldStats[worldType] {
            stats = WorldStatsResponse(
                worldType: stats.worldType,
                totalComics: stats.totalComics + 1,
                favoriteComics: stats.favoriteComics + (comic.isFavorite ? 1 : 0),
                publicComics: stats.publicComics + (comic.isPublic ? 1 : 0),
                totalCollections: stats.totalCollections,
                totalScenarios: stats.totalScenarios,
                lastActivity: Date().ISO8601Format()
            )
            worldStats[worldType] = stats
        }
        
        // Clear cache to force refresh
        cache.clearComics(for: worldType)
    }
    
    func updateComicInWorld(_ updatedComic: ComicGenerationResponse, worldType: WorldType) {
        guard let comics = worlds[worldType],
              let index = comics.firstIndex(where: { $0.id == updatedComic.id }) else { return }
        
        worlds[worldType]?[index] = updatedComic
        
        // Clear cache to force refresh
        cache.clearComics(for: worldType)
    }
    
    func removeComicFromWorld(comicId: Int, worldType: WorldType) {
        worlds[worldType]?.removeAll { $0.id == comicId }
        
        // Update stats
        if var stats = worldStats[worldType] {
            stats = WorldStatsResponse(
                worldType: stats.worldType,
                totalComics: max(0, stats.totalComics - 1),
                favoriteComics: stats.favoriteComics,
                publicComics: stats.publicComics,
                totalCollections: stats.totalCollections,
                totalScenarios: stats.totalScenarios,
                lastActivity: Date().ISO8601Format()
            )
            worldStats[worldType] = stats
        }
        
        // Clear cache to force refresh
        cache.clearComics(for: worldType)
    }
    
    // MARK: - Utility Methods
    func getComicsCount(for worldType: WorldType) -> Int {
        return worlds[worldType]?.count ?? 0
    }
    
    func getFavoriteComics(for worldType: WorldType) -> [ComicGenerationResponse] {
        return worlds[worldType]?.filter { $0.isFavorite } ?? []
    }
    
    func getPublicComics(for worldType: WorldType) -> [ComicGenerationResponse] {
        return worlds[worldType]?.filter { $0.isPublic } ?? []
    }
    
    func searchComics(in worldType: WorldType, query: String) -> [ComicGenerationResponse] {
        guard let comics = worlds[worldType] else { return [] }
        
        let lowercaseQuery = query.lowercased()
        return comics.filter { comic in
            comic.title.lowercased().contains(lowercaseQuery) ||
            comic.concept.lowercased().contains(lowercaseQuery) ||
            comic.genre.lowercased().contains(lowercaseQuery)
        }
    }
    
    func clearError() {
        errorMessage = nil
    }
    
    func clearCache() {
        cache.clearAll()
    }
    
    // MARK: - World Preferences
    func saveWorldPreferences(_ preferences: WorldPreferences) async {
        do {
            let token = await AuthManager.shared.getStoredToken()
            guard let token = token else {
                throw APIError.unauthorized
            }
            
            try await apiClient.saveWorldPreferences(preferences, token: token)
            print("✅ Saved preferences for \(preferences.worldType.displayName)")
            
        } catch {
            ErrorLogger.shared.log(
                error as? APIError ?? APIError.networkError(error),
                context: "saveWorldPreferences - \(preferences.worldType.displayName)"
            )
            errorMessage = (error as? APIError)?.userFriendlyMessage ?? error.localizedDescription
        }
    }
    
    func loadWorldPreferences(for worldType: WorldType) async -> WorldPreferences? {
        do {
            let token = await AuthManager.shared.getStoredToken()
            guard let token = token else {
                throw APIError.unauthorized
            }
            
            return try await apiClient.getWorldPreferences(worldType: worldType, token: token)
            
        } catch {
            ErrorLogger.shared.log(
                error as? APIError ?? APIError.networkError(error),
                context: "loadWorldPreferences - \(worldType.displayName)"
            )
            return nil
        }
    }
}

// MARK: - World Cache
private class WorldCache {
    private var comicsCache: [WorldType: [Int: CachedComics]] = [:]
    private var statsCache: [WorldType: CachedStats] = [:]
    
    struct CachedComics {
        let comics: [ComicGenerationResponse]
        let timestamp: Date
    }
    
    struct CachedStats {
        let stats: WorldStatsResponse
        let timestamp: Date
    }
    
    private let maxCacheAge: TimeInterval = 5 * 60 // 5 minutes
    
    init() {
        // Initialize cache for all worlds
        for worldType in WorldType.allCases {
            comicsCache[worldType] = [:]
        }
    }
    
    func getComics(for worldType: WorldType, page: Int) -> [ComicGenerationResponse]? {
        guard let cachedComics = comicsCache[worldType]?[page],
              Date().timeIntervalSince(cachedComics.timestamp) < maxCacheAge else {
            return nil
        }
        
        return cachedComics.comics
    }
    
    func setComics(_ comics: [ComicGenerationResponse], for worldType: WorldType, page: Int) {
        if comicsCache[worldType] == nil {
            comicsCache[worldType] = [:]
        }
        
        comicsCache[worldType]?[page] = CachedComics(comics: comics, timestamp: Date())
    }
    
    func getStats(for worldType: WorldType) -> WorldStatsResponse? {
        guard let cachedStats = statsCache[worldType],
              Date().timeIntervalSince(cachedStats.timestamp) < maxCacheAge else {
            return nil
        }
        
        return cachedStats.stats
    }
    
    func setStats(_ stats: WorldStatsResponse, for worldType: WorldType) {
        statsCache[worldType] = CachedStats(stats: stats, timestamp: Date())
    }
    
    func clearComics(for worldType: WorldType) {
        comicsCache[worldType] = [:]
    }
    
    func clearStats(for worldType: WorldType) {
        statsCache[worldType] = nil
    }
    
    func clearAll() {
        comicsCache.removeAll()
        statsCache.removeAll()
        
        // Reinitialize
        for worldType in WorldType.allCases {
            comicsCache[worldType] = [:]
        }
    }
} 
