import Foundation
import SwiftUI

// MARK: - Collection Request Models
struct ComicCollectionRequest: Codable {
    let name: String
    let description: String?
    let worldType: WorldType
    let isPublic: Bool
    let tags: [String]
    
    enum CodingKeys: String, CodingKey {
        case name, description, tags
        case worldType = "world_type"
        case isPublic = "is_public"
    }
}

struct CollectionUpdateRequest: Codable {
    let name: String?
    let description: String?
    let isPublic: Bool?
    let tags: [String]?
    
    enum CodingKeys: String, CodingKey {
        case name, description, tags
        case isPublic = "is_public"
    }
}

// MARK: - Collection Response Models
struct ComicCollectionResponse: Codable, Identifiable {
    let id: Int
    let name: String
    let description: String?
    let worldType: WorldType
    let isPublic: Bool
    let comicsCount: Int
    let tags: [String]
    let createdAt: String
    let updatedAt: String
    let comics: [ComicListResponse]?
    let previewImages: [String]
    
    enum CodingKeys: String, CodingKey {
        case id, name, description, tags, comics
        case worldType = "world_type"
        case isPublic = "is_public"
        case comicsCount = "comics_count"
        case createdAt = "created_at"
        case updatedAt = "updated_at"
        case previewImages = "preview_images"
    }
}

struct CollectionDetailResponse: Codable {
    let collection: ComicCollectionResponse
    let comics: [ComicGenerationResponse]
    let canEdit: Bool
    let totalPages: Int
    let currentPage: Int
    
    enum CodingKeys: String, CodingKey {
        case collection, comics
        case canEdit = "can_edit"
        case totalPages = "total_pages"
        case currentPage = "current_page"
    }
}

// MARK: - Collection Management Models
struct AddComicToCollectionRequest: Codable {
    let comicId: Int
    let collectionId: Int
    
    enum CodingKeys: String, CodingKey {
        case comicId = "comic_id"
        case collectionId = "collection_id"
    }
}

struct RemoveComicFromCollectionRequest: Codable {
    let comicId: Int
    let collectionId: Int
    
    enum CodingKeys: String, CodingKey {
        case comicId = "comic_id"
        case collectionId = "collection_id"
    }
}

struct CollectionSearchRequest: Codable {
    let worldType: WorldType?
    let searchTerm: String?
    let tags: [String]?
    let isPublic: Bool?
    let sortBy: CollectionSortBy
    let page: Int
    let limit: Int
    
    enum CodingKeys: String, CodingKey {
        case searchTerm = "search_term"
        case worldType = "world_type"
        case tags
        case isPublic = "is_public"
        case sortBy = "sort_by"
        case page
        case limit
    }
}

enum CollectionSortBy: String, CaseIterable, Codable {
    case newest = "newest"
    case oldest = "oldest"
    case name = "name"
    case comicsCount = "comics_count"
    case updated = "updated"
    
    var displayName: String {
        switch self {
        case .newest: return "Newest First"
        case .oldest: return "Oldest First"
        case .name: return "Name A-Z"
        case .comicsCount: return "Most Comics"
        case .updated: return "Recently Updated"
        }
    }
}

// MARK: - Collection UI State Models
struct CollectionUIState {
    var isCreating: Bool = false
    var isEditing: Bool = false
    var isDeleting: Bool = false
    var isAddingComic: Bool = false
    var isRemovingComic: Bool = false
    var selectedCollection: ComicCollectionResponse?
    var searchText: String = ""
    var selectedTags: Set<String> = []
    var sortBy: CollectionSortBy = .newest
    var filterByWorld: WorldType?
    var showPublicOnly: Bool = false
    var currentPage: Int = 1
    var isLoading: Bool = false
    var errorMessage: String?
}

struct CollectionFormData {
    var name: String = ""
    var description: String = ""
    var worldType: WorldType = .imaginationWorld
    var isPublic: Bool = false
    var tags: [String] = []
    var selectedComics: Set<Int> = []
    
    var isValid: Bool {
        !name.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
    }
    
    mutating func reset() {
        name = ""
        description = ""
        worldType = .imaginationWorld
        isPublic = false
        tags = []
        selectedComics = []
    }
}

// MARK: - Collection Statistics
struct CollectionStats: Codable {
    let totalCollections: Int
    let publicCollections: Int
    let privateCollections: Int
    let totalComicsInCollections: Int
    let averageComicsPerCollection: Double
    let mostPopularTags: [TagCount]
    let collectionsByWorld: [WorldType: Int]
    
    enum CodingKeys: String, CodingKey {
        case totalCollections = "total_collections"
        case publicCollections = "public_collections"
        case privateCollections = "private_collections"
        case totalComicsInCollections = "total_comics_in_collections"
        case averageComicsPerCollection = "average_comics_per_collection"
        case mostPopularTags = "most_popular_tags"
        case collectionsByWorld = "collections_by_world"
    }
}

struct TagCount: Codable, Identifiable {
    let id = UUID()
    let tag: String
    let count: Int
    
    enum CodingKeys: String, CodingKey {
        case tag, count
    }
}

// MARK: - Collection Sharing
struct CollectionShareRequest: Codable {
    let collectionId: Int
    let shareType: CollectionShareType
    let message: String?
    
    enum CodingKeys: String, CodingKey {
        case collectionId = "collection_id"
        case shareType = "share_type"
        case message
    }
}

enum CollectionShareType: String, CaseIterable, Codable {
    case link = "link"
    case email = "email"
    case social = "social"
    
    var displayName: String {
        switch self {
        case .link: return "Share Link"
        case .email: return "Email"
        case .social: return "Social Media"
        }
    }
}

struct CollectionShareResponse: Codable {
    let shareUrl: String
    let expires: String?
    let accessCode: String?
    
    enum CodingKeys: String, CodingKey {
        case shareUrl = "share_url"
        case expires
        case accessCode = "access_code"
    }
}

// MARK: - Preview Data
#if DEBUG
extension ComicCollectionResponse {
    static let preview = ComicCollectionResponse(
        id: 1,
        name: "Epic Adventures",
        description: "A collection of thrilling adventure comics",
        worldType: .imaginationWorld,
        isPublic: true,
        comicsCount: 5,
        tags: ["adventure", "fantasy", "heroes"],
        createdAt: "2024-01-15T10:30:00Z",
        updatedAt: "2024-01-16T14:20:00Z",
        comics: nil,
        previewImages: []
    )
    
    static let dreamWorldPreview = ComicCollectionResponse(
        id: 2,
        name: "Mystical Dreams",
        description: "Surreal and symbolic dream narratives",
        worldType: .dreamWorld,
        isPublic: false,
        comicsCount: 3,
        tags: ["dreams", "surreal", "mystery"],
        createdAt: "2024-01-10T09:15:00Z",
        updatedAt: "2024-01-12T16:45:00Z",
        comics: nil,
        previewImages: []
    )
    
    static let mindWorldPreview = ComicCollectionResponse(
        id: 3,
        name: "Mental Journeys",
        description: "Psychological explorations and introspective stories",
        worldType: .mindWorld,
        isPublic: true,
        comicsCount: 7,
        tags: ["psychology", "introspection", "growth"],
        createdAt: "2024-01-08T11:20:00Z",
        updatedAt: "2024-01-14T13:30:00Z",
        comics: nil,
        previewImages: []
    )
}

extension CollectionStats {
    static let preview = CollectionStats(
        totalCollections: 15,
        publicCollections: 8,
        privateCollections: 7,
        totalComicsInCollections: 45,
        averageComicsPerCollection: 3.0,
        mostPopularTags: [
            TagCount(tag: "adventure", count: 12),
            TagCount(tag: "fantasy", count: 8),
            TagCount(tag: "comedy", count: 6),
            TagCount(tag: "drama", count: 5)
        ],
        collectionsByWorld: [
            .imaginationWorld: 8,
            .dreamWorld: 4,
            .mindWorld: 3
        ]
    )
}

extension CollectionFormData {
    static let preview = CollectionFormData(
        name: "Sample Collection",
        description: "A sample collection for previews",
        worldType: .imaginationWorld,
        isPublic: false,
        tags: ["sample", "preview"],
        selectedComics: []
    )
}
#endif 

enum CollectionSortOption: String, CaseIterable, Codable {
    case name
    case dateCreated = "date_created"
    case comicCount = "comic_count"
    
    var rawValueDisplay: String {
        switch self {
        case .name: return "Name"
        case .dateCreated: return "Date Created"
        case .comicCount: return "Comic Count"
        }
    }
} 
