import Foundation

// MARK: - Authentication Models
struct RegisterRequest: Codable {
    let username: String
    let email: String
    let fullName: String
    let password: String
    
    enum CodingKeys: String, CodingKey {
        case username, email, password
        case fullName = "full_name"
    }
}

struct TokenResponse: Codable {
    let accessToken: String
    let tokenType: String
    
    enum CodingKeys: String, CodingKey {
        case accessToken = "access_token"
        case tokenType = "token_type"
    }
}

struct UserResponse: Codable {
    let id: Int
    let username: String
    let email: String
    let fullName: String?
    let createdAt: String
    
    enum CodingKeys: String, CodingKey {
        case id, username, email
        case fullName = "full_name"
        case createdAt = "created_at"
    }
}

// MARK: - Account Deletion Models
struct AccountDeletionRequest: Codable {
    let confirmDeletion: Bool
    let usernameConfirmation: String
    let understandingAcknowledgment: String
    
    enum CodingKeys: String, CodingKey {
        case confirmDeletion = "confirm_deletion"
        case usernameConfirmation = "username_confirmation"
        case understandingAcknowledgment = "understanding_acknowledgment"
    }
}

struct DeletionSummary: Codable {
    let username: String
    let comicsDeleted: Int
    let collectionsDeleted: Int
    let scenariosDeleted: Int
    let storageCleared: String
    let deletedAt: String
    
    enum CodingKeys: String, CodingKey {
        case username
        case comicsDeleted = "comics_deleted"
        case collectionsDeleted = "collections_deleted"
        case scenariosDeleted = "scenarios_deleted"
        case storageCleared = "storage_cleared"
        case deletedAt = "deleted_at"
    }
}

// MARK: - Comics Models (Updated)
struct ComicRequest: Codable {
    let concept: String  // Changed from 'message' to 'concept'
    let genre: String?
    let artStyle: String?
    let includeDetailedScenario: Bool
    
    enum CodingKeys: String, CodingKey {
        case concept, genre
        case artStyle = "art_style"
        case includeDetailedScenario = "include_detailed_scenario"
    }
}

struct ComicGenerationRequest: Codable {
    let concept: String
    let genre: String?
    let artStyle: String?
    let includeDetailedScenario: Bool
    
    enum CodingKeys: String, CodingKey {
        case concept, genre
        case artStyle = "art_style"
        case includeDetailedScenario = "include_detailed_scenario"
    }
}

struct ComicSaveRequest: Codable {
    let title: String
    let concept: String
    let genre: String
    let artStyle: String
    let worldType: WorldType
    let includeDetailedScenario: Bool
    let imageBase64: String?
    let panelsData: String?
    let isFavorite: Bool?
    let isPublic: Bool?
    
    enum CodingKeys: String, CodingKey {
        case title, concept, genre
        case artStyle = "art_style"
        case worldType = "world_type"
        case includeDetailedScenario = "include_detailed_scenario"
        case imageBase64 = "image_base64"
        case panelsData = "panels_data"
        case isFavorite = "is_favorite"
        case isPublic = "is_public"
    }
}

struct ComicGenerationResponse: Codable, Identifiable, Equatable {
    let id: Int
    let title: String
    let concept: String
    let genre: String
    let artStyle: String
    let worldType: WorldType
    let imageBase64: String? // Now optional
    let panelsData: String?
    let createdAt: String
    let isFavorite: Bool
    let isPublic: Bool
    let hasDetailedScenario: Bool
    let imageUrl: String?
    
    enum CodingKeys: String, CodingKey {
        case id, title, concept, genre
        case artStyle = "art_style"
        case worldType = "world_type"
        case imageBase64 = "image_base64"
        case panelsData = "panels_data"
        case createdAt = "created_at"
        case isFavorite = "is_favorite"
        case isPublic = "is_public"
        case hasDetailedScenario = "has_detailed_scenario"
        case imageUrl = "image_url"
    }
    
    // Custom decoding to handle both String and Array types for panels_data, and optional imageBase64
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        
        id = try container.decode(Int.self, forKey: .id)
        title = try container.decode(String.self, forKey: .title)
        concept = try container.decode(String.self, forKey: .concept)
        genre = try container.decode(String.self, forKey: .genre)
        artStyle = try container.decode(String.self, forKey: .artStyle)
        worldType = try container.decode(WorldType.self, forKey: .worldType)
        imageBase64 = try container.decodeIfPresent(String.self, forKey: .imageBase64)
        createdAt = try container.decode(String.self, forKey: .createdAt)
        isFavorite = try container.decode(Bool.self, forKey: .isFavorite)
        isPublic = try container.decode(Bool.self, forKey: .isPublic)
        hasDetailedScenario = try container.decode(Bool.self, forKey: .hasDetailedScenario)
        imageUrl = try container.decodeIfPresent(String.self, forKey: .imageUrl)
        // Handle panels_data as String, Array, Dictionary, or other types
        if let panelsDataString = try? container.decode(String.self, forKey: .panelsData) {
            panelsData = panelsDataString
        } else if let panelsDataArray = try? container.decode([String].self, forKey: .panelsData) {
            let jsonData = try? JSONSerialization.data(withJSONObject: panelsDataArray)
            panelsData = jsonData.flatMap { String(data: $0, encoding: .utf8) }
        } else if let panelsDataDict = try? container.decode([String: AnyCodable].self, forKey: .panelsData) {
            // Convert dictionary to JSON string
            let dict = panelsDataDict.mapValues { $0.value }
            let jsonData = try? JSONSerialization.data(withJSONObject: dict)
            panelsData = jsonData.flatMap { String(data: $0, encoding: .utf8) }
        } else if (try? container.decodeNil(forKey: .panelsData)) == true {
            panelsData = nil
        } else {
            if let _ = try? container.decode(Int.self, forKey: .panelsData) {
                panelsData = nil
            } else if let _ = try? container.decode(Double.self, forKey: .panelsData) {
                panelsData = nil
            } else if let _ = try? container.decode(Bool.self, forKey: .panelsData) {
                panelsData = nil
            } else {
                print("[ComicGenerationResponse] Unknown panels_data type encountered, setting to nil.")
                panelsData = nil
            }
        }
    }
    
    // Initialize with default values if needed
    init(id: Int? = nil, title: String, concept: String, genre: String, artStyle: String, worldType: WorldType, imageBase64: String? = nil, panelsData: String?, createdAt: String, isFavorite: Bool? = nil, isPublic: Bool? = nil, hasDetailedScenario: Bool? = nil, imageUrl: String? = nil) {
        self.id = id ?? UUID().hashValue
        self.title = title
        self.concept = concept
        self.genre = genre
        self.artStyle = artStyle
        self.worldType = worldType
        self.imageBase64 = imageBase64
        self.panelsData = panelsData
        self.createdAt = createdAt
        self.isFavorite = isFavorite ?? false
        self.isPublic = isPublic ?? false
        self.hasDetailedScenario = hasDetailedScenario ?? false
        self.imageUrl = imageUrl
    }
}

struct ComicListResponse: Codable, Identifiable {
    let id: Int
    let title: String
    let genre: String
    let artStyle: String
    let worldType: WorldType
    let createdAt: String
    let isFavorite: Bool
    let isPublic: Bool
    
    enum CodingKeys: String, CodingKey {
        case id, title, genre
        case artStyle = "art_style"
        case worldType = "world_type"
        case createdAt = "created_at"
        case isFavorite = "is_favorite"
        case isPublic = "is_public"
    }
}

struct ComicUpdateRequest: Codable {
    let title: String?
    let isFavorite: Bool?
    let isPublic: Bool?
    
    enum CodingKeys: String, CodingKey {
        case title
        case isFavorite = "is_favorite"
        case isPublic = "is_public"
    }
}

struct ComicResponse: Codable {
    let id: Int?
    let genre: String
    let artStyle: String
    let panels: [ComicPanel]
    let sheetUrl: String
    
    enum CodingKeys: String, CodingKey {
        case id, genre, panels
        case artStyle = "art_style"
        case sheetUrl = "sheet_url"
    }
}

struct ComicPanel: Codable {
    let imageUrl: String
    let imagePrompt: String
    
    enum CodingKeys: String, CodingKey {
        case imageUrl = "image_url"
        case imagePrompt = "image_prompt"
    }
}

// MARK: - World System Models
// WorldComicsRequest and WorldStatsResponse are defined in WorldModels.swift

// MARK: - Collection Models
// ComicCollectionRequest and ComicCollectionResponse are defined in CollectionModels.swift

// MARK: - Scenario Models
// ScenarioSaveRequest and ScenarioSaveResponse are defined in ScenarioModels.swift

// DetailedScenario is now defined in ScenarioModels.swift to avoid duplication

struct ScenarioResponse: Codable {
    let scenario: String
    let genre: String
    let artStyle: String?
    let invalidRequest: String?
    
    enum CodingKeys: String, CodingKey {
        case scenario
        case genre
        case artStyle = "art_style"
        case invalidRequest = "invalid_request"
    }
}

// MARK: - Utility Models
struct HealthResponse: Codable {
    let status: String
    let timestamp: String
}

struct SuccessResponse: Codable {
    let success: Bool
    let message: String
}

struct IOSConfigResponse: Codable {
    let version: String
    let features: [String]
    let config: [String: String]
}

// MARK: - Comic Model for App
struct Comic: Identifiable, Codable {
    let id: UUID
    let title: String
    let script: String
    let genre: String
    let artStyle: String
    let panels: [ComicPanel]
    let sheetUrl: String
    let createdAt: Date
    
    init(title: String, script: String, genre: String = "general", artStyle: String = "comic book") {
        self.id = UUID()
        self.title = title
        self.script = script
        self.genre = genre
        self.artStyle = artStyle
        self.panels = []
        self.sheetUrl = ""
        self.createdAt = Date()
    }
    
    init(from response: ComicResponse) {
        self.id = UUID()
        self.title = response.genre.capitalized
        self.script = response.panels.map { $0.imagePrompt }.joined(separator: "\n")
        self.genre = response.genre
        self.artStyle = response.artStyle
        self.panels = response.panels
        self.sheetUrl = response.sheetUrl
        self.createdAt = Date()
    }
    
    init(from response: ComicGenerationResponse) {
        self.id = UUID()
        self.title = response.title
        self.script = response.concept
        self.genre = response.genre
        self.artStyle = response.artStyle
        self.panels = [] // ComicGenerationResponse doesn't have panels structure
        self.sheetUrl = response.imageBase64 ?? "" // Use base64 as URL placeholder, handle optional
        self.createdAt = Date()
    }
}

// MARK: - Image Generation Models
struct ImageRequest: Codable {
    let prompt: String
}

// MARK: - Storage Models
// Storage models are defined in StorageManager.swift 

// Add this type-erased AnyCodable for decoding arbitrary JSON values
struct AnyCodable: Codable {
    let value: Any
    
    init(_ value: Any) {
        self.value = value
    }
    
    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        if let intVal = try? container.decode(Int.self) {
            value = intVal
        } else if let doubleVal = try? container.decode(Double.self) {
            value = doubleVal
        } else if let boolVal = try? container.decode(Bool.self) {
            value = boolVal
        } else if let stringVal = try? container.decode(String.self) {
            value = stringVal
        } else if let arrayVal = try? container.decode([AnyCodable].self) {
            value = arrayVal.map { $0.value }
        } else if let dictVal = try? container.decode([String: AnyCodable].self) {
            value = dictVal.mapValues { $0.value }
        } else {
            value = ""
        }
    }
    
    func encode(to encoder: Encoder) throws {
        var container = encoder.singleValueContainer()
        if let intVal = value as? Int {
            try container.encode(intVal)
        } else if let doubleVal = value as? Double {
            try container.encode(doubleVal)
        } else if let boolVal = value as? Bool {
            try container.encode(boolVal)
        } else if let stringVal = value as? String {
            try container.encode(stringVal)
        } else if let arrayVal = value as? [Any] {
            let encodableArray = arrayVal.map { AnyCodable($0) }
            try container.encode(encodableArray)
        } else if let dictVal = value as? [String: Any] {
            let encodableDict = dictVal.mapValues { AnyCodable($0) }
            try container.encode(encodableDict)
        } else {
            try container.encodeNil()
        }
    }
} 
