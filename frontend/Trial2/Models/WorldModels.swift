import Foundation
import SwiftUI

// MARK: - World Type Enum
enum WorldType: String, CaseIterable, Codable {
    case dreamWorld = "dream_world"
    case mindWorld = "mind_world"
    case imaginationWorld = "imagination_world"
    
    var displayName: String {
        switch self {
        case .dreamWorld: return "Dream World"
        case .mindWorld: return "Mind World"
        case .imaginationWorld: return "Imagination World"
        }
    }
    
    var description: String {
        switch self {
        case .dreamWorld: return "Explore the depths of your subconscious mind through surreal and symbolic narratives"
        case .mindWorld: return "Journey through psychological landscapes and mental adventures"
        case .imaginationWorld: return "Create unlimited stories where anything is possible"
        }
    }
    
    var detailedDescription: String {
        switch self {
        case .dreamWorld: return "A realm where the subconscious mind takes form through surreal imagery, symbolic narratives, and ethereal landscapes. Here, dreams become reality and reality becomes dreams, creating stories that explore the deepest corners of human consciousness."
        case .mindWorld: return "A psychological landscape where thoughts, emotions, and memories intertwine to form complex narratives. This world delves into the human psyche, exploring mental health, consciousness, and the intricate workings of the mind."
        case .imaginationWorld: return "A boundless realm of unlimited creativity where fantasy meets reality. Here, anything is possible - from magical creatures to futuristic technology, from epic adventures to heartwarming tales of friendship and love."
        }
    }
    
    var icon: String {
        switch self {
        case .dreamWorld: return "moon.stars.fill"
        case .mindWorld: return "brain.head.profile"
        case .imaginationWorld: return "wand.and.stars"
        }
    }
    
    var color: Color {
        switch self {
        case .dreamWorld: return .purple
        case .mindWorld: return .indigo
        case .imaginationWorld: return .pink
        }
    }
    
    /*var linearGradient: LinearGradient {
        switch self {
        case .dreamWorld: return LinearGradient(
            colors: [.purple.opacity(0.3), .blue.opacity(0.3)],
            startPoint: .topLeading,
            endPoint: .bottomTrailing
        )
        case .mindWorld: return LinearGradient(
            colors: [.indigo.opacity(0.3), .cyan.opacity(0.3)],
            startPoint: .topLeading,
            endPoint: .bottomTrailing
        )
        case .imaginationWorld: return LinearGradient(
            colors: [.pink.opacity(0.3), .orange.opacity(0.3)],
            startPoint: .topLeading,
            endPoint: .bottomTrailing
        )
        }
    }*/
    
    var themes: [String] {
        switch self {
        case .dreamWorld: return ["surreal", "symbolic", "subconscious", "mysterious", "ethereal"]
        case .mindWorld: return ["psychological", "introspective", "mental health", "consciousness", "thought"]
        case .imaginationWorld: return ["fantasy", "creative", "limitless", "magical", "inventive"]
        }
    }
    
    var suggestedGenres: [String] {
        switch self {
        case .dreamWorld: return ["mystery", "psychological thriller", "surreal", "horror"]
        case .mindWorld: return ["drama", "psychological", "slice of life", "educational"]
        case .imaginationWorld: return ["fantasy", "adventure", "sci-fi", "comedy", "romance"]
        }
    }
    
    var primaryColor: Color {
        switch self {
        case .dreamWorld: return .pink
        case .mindWorld: return .green
        case .imaginationWorld: return .orange
        }
    }
}

// MARK: - World Stats Response (Enhanced)
struct WorldStatsResponse: Codable {
    let worldType: WorldType
    let totalComics: Int
    let favoriteComics: Int
    let publicComics: Int
    let totalCollections: Int
    let totalScenarios: Int // Now non-optional, always has a value
    let lastActivity: String?
    
    enum CodingKeys: String, CodingKey {
        case worldType = "world_type"
        case totalComics = "total_comics"
        case favoriteComics = "favorite_comics"
        case publicComics = "public_comics"
        case totalCollections = "total_collections"
        case totalScenarios = "total_scenarios"
        case lastActivity = "last_activity"
    }
    
    // Custom decoder to provide default value for totalScenarios
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        worldType = try container.decode(WorldType.self, forKey: .worldType)
        totalComics = try container.decode(Int.self, forKey: .totalComics)
        favoriteComics = try container.decode(Int.self, forKey: .favoriteComics)
        publicComics = try container.decode(Int.self, forKey: .publicComics)
        totalCollections = try container.decode(Int.self, forKey: .totalCollections)
        totalScenarios = (try? container.decodeIfPresent(Int.self, forKey: .totalScenarios)) ?? 0
        lastActivity = try container.decodeIfPresent(String.self, forKey: .lastActivity)
    }
    
    // Initialize with default values for backward compatibility
    init(worldType: WorldType, totalComics: Int, favoriteComics: Int, publicComics: Int, totalCollections: Int = 0, totalScenarios: Int? = nil, lastActivity: String? = nil) {
        self.worldType = worldType
        self.totalComics = totalComics
        self.favoriteComics = favoriteComics
        self.publicComics = publicComics
        self.totalCollections = totalCollections
        self.totalScenarios = totalScenarios ?? 0 // Use the new decoder's logic
        self.lastActivity = lastActivity
    }
}

// MARK: - World Comics Request
struct WorldComicsRequest: Codable {
    let worldType: WorldType
    let page: Int
    let perPage: Int
    let favoritesOnly: Bool
    let sortBy: WorldComicSortBy
    let searchTerm: String?
    
    enum CodingKeys: String, CodingKey {
        case worldType = "world_type"
        case page
        case perPage = "per_page"
        case favoritesOnly = "favorites_only"
        case sortBy = "sort_by"
        case searchTerm = "search_term"
    }
}

enum WorldComicSortBy: String, CaseIterable, Codable {
    case newest = "newest"
    case oldest = "oldest"
    case title = "title"
    case favorite = "favorite"
    case popular = "popular"
    
    var displayName: String {
        switch self {
        case .newest: return "Newest First"
        case .oldest: return "Oldest First"
        case .title: return "Title A-Z"
        case .favorite: return "Favorites"
        case .popular: return "Most Popular"
        }
    }
}

// MARK: - World Analytics
struct WorldAnalytics: Codable {
    let worldType: WorldType
    let creationTrends: [CreationTrend]
    let popularThemes: [ThemeCount]
    let genreDistribution: [GenreCount]
    let activityScore: Double
    
    enum CodingKeys: String, CodingKey {
        case worldType = "world_type"
        case creationTrends = "creation_trends"
        case popularThemes = "popular_themes"
        case genreDistribution = "genre_distribution"
        case activityScore = "activity_score"
    }
}

struct CreationTrend: Codable {
    let date: String
    let count: Int
}

struct ThemeCount: Codable {
    let theme: String
    let count: Int
}

struct GenreCount: Codable {
    let genre: String
    let count: Int
}

// MARK: - World Preferences
struct WorldPreferences: Codable {
    let worldType: WorldType
    let preferredGenres: [String]
    let preferredArtStyles: [String]
    let defaultPrivacy: WorldPrivacy
    let notifications: WorldNotificationSettings
    
    enum CodingKeys: String, CodingKey {
        case worldType = "world_type"
        case preferredGenres = "preferred_genres"
        case preferredArtStyles = "preferred_art_styles"
        case defaultPrivacy = "default_privacy"
        case notifications
    }
}

enum WorldPrivacy: String, CaseIterable, Codable {
    case `private` = "private"
    case `public` = "public"
    case friendsOnly = "friends_only"
    
    var displayName: String {
        switch self {
        case .private: return "Private"
        case .public: return "Public"
        case .friendsOnly: return "Friends Only"
        }
    }
}

struct WorldNotificationSettings: Codable {
    let newComics: Bool
    let collections: Bool
    let scenarios: Bool
    let analytics: Bool
    
    enum CodingKeys: String, CodingKey {
        case newComics = "new_comics"
        case collections
        case scenarios
        case analytics
    }
}

// MARK: - World Navigation
struct WorldNavigationState {
    var selectedWorld: WorldType = .imaginationWorld
    var isWorldSelectionPresented: Bool = false
    var worldComics: [WorldType: [ComicGenerationResponse]] = [:]
    var worldStats: [WorldType: WorldStatsResponse] = [:]
}

// MARK: - World UI Models
struct WorldCardData {
    let world: WorldType
    let stats: WorldStatsResponse?
    let isSelected: Bool
    let onTap: () -> Void
}

// MARK: - World Preview Data
#if DEBUG
extension WorldStatsResponse {
    static let preview = WorldStatsResponse(
        worldType: .imaginationWorld,
        totalComics: 15,
        favoriteComics: 5,
        publicComics: 3,
        totalCollections: 2,
        totalScenarios: 8,
        lastActivity: "2024-01-15T10:30:00Z"
    )
    
    static let dreamWorldPreview = WorldStatsResponse(
        worldType: .dreamWorld,
        totalComics: 8,
        favoriteComics: 3,
        publicComics: 1,
        totalCollections: 1,
        totalScenarios: 4,
        lastActivity: "2024-01-14T15:20:00Z"
    )
    
    static let mindWorldPreview = WorldStatsResponse(
        worldType: .mindWorld,
        totalComics: 12,
        favoriteComics: 4,
        publicComics: 2,
        totalCollections: 3,
        totalScenarios: 6,
        lastActivity: "2024-01-16T09:45:00Z"
    )
}

extension WorldAnalytics {
    static let preview = WorldAnalytics(
        worldType: .imaginationWorld,
        creationTrends: [
            CreationTrend(date: "2024-01-10", count: 2),
            CreationTrend(date: "2024-01-11", count: 1),
            CreationTrend(date: "2024-01-12", count: 3),
            CreationTrend(date: "2024-01-13", count: 1),
            CreationTrend(date: "2024-01-14", count: 2)
        ],
        popularThemes: [
            ThemeCount(theme: "adventure", count: 8),
            ThemeCount(theme: "fantasy", count: 5),
            ThemeCount(theme: "magic", count: 4)
        ],
        genreDistribution: [
            GenreCount(genre: "fantasy", count: 6),
            GenreCount(genre: "adventure", count: 5),
            GenreCount(genre: "comedy", count: 4)
        ],
        activityScore: 8.5
    )
}
#endif 
