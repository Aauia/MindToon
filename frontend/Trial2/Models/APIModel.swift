import Foundation

// MARK: - Helper Types for Flexible JSON Decoding

// AnyCodable wrapper for decoding arbitrary JSON values
struct AnyCodable: Codable {
    let value: Any
    
    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        
        if container.decodeNil() {
            value = NSNull()
        } else if let bool = try? container.decode(Bool.self) {
            value = bool
        } else if let int = try? container.decode(Int.self) {
            value = int
        } else if let double = try? container.decode(Double.self) {
            value = double
        } else if let string = try? container.decode(String.self) {
            value = string
        } else if let array = try? container.decode([AnyCodable].self) {
            value = array.map { $0.value }
        } else if let dictionary = try? container.decode([String: AnyCodable].self) {
            value = dictionary.mapValues { $0.value }
        } else {
            throw DecodingError.dataCorruptedError(in: container, debugDescription: "AnyCodable cannot decode value")
        }
    }
    
    func encode(to encoder: Encoder) throws {
        var container = encoder.singleValueContainer()
        
        if value is NSNull {
            try container.encodeNil()
        } else if let bool = value as? Bool {
            try container.encode(bool)
        } else if let int = value as? Int {
            try container.encode(int)
        } else if let double = value as? Double {
            try container.encode(double)
        } else if let string = value as? String {
            try container.encode(string)
        } else if let array = value as? [Any] {
            let codableArray = array.map { AnyCodable(value: $0) }
            try container.encode(codableArray)
        } else if let dictionary = value as? [String: Any] {
            let codableDictionary = dictionary.mapValues { AnyCodable(value: $0) }
            try container.encode(codableDictionary)
        } else {
            throw EncodingError.invalidValue(value, EncodingError.Context(codingPath: encoder.codingPath, debugDescription: "AnyCodable cannot encode value"))
        }
    }
    
    private init(value: Any) {
        self.value = value
    }
}
enum JSONValue: Codable {
    case string(String)
    case object([String: JSONValue])
    case array([JSONValue])
    case number(Double)
    case bool(Bool)
    case null
    
    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        
        // Try different types in order of likelihood
        if container.decodeNil() {
            self = .null
        } else if let string = try? container.decode(String.self) {
            self = .string(string)
        } else if let bool = try? container.decode(Bool.self) {
            self = .bool(bool)
        } else if let number = try? container.decode(Double.self) {
            self = .number(number)
        } else if let array = try? container.decode([JSONValue].self) {
            self = .array(array)
        } else if let object = try? container.decode([String: JSONValue].self) {
            self = .object(object)
        } else {
            // Last resort: try to get the raw value and convert to string
            print("⚠️ JSONValue fallback: attempting raw string conversion")
            if let rawString = try? container.decode(String.self) {
                self = .string(rawString)
            } else {
                throw DecodingError.typeMismatch(JSONValue.self, DecodingError.Context(codingPath: decoder.codingPath, debugDescription: "Invalid JSON value"))
            }
        }
    }
    
    func encode(to encoder: Encoder) throws {
        var container = encoder.singleValueContainer()
        switch self {
        case .string(let string):
            try container.encode(string)
        case .object(let object):
            try container.encode(object)
        case .array(let array):
            try container.encode(array)
        case .number(let number):
            try container.encode(number)
        case .bool(let bool):
            try container.encode(bool)
        case .null:
            try container.encodeNil()
        }
    }
}

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

// MARK: - World Types
enum WorldType: String, CaseIterable, Codable {
    case dreamWorld = "dream_world"
    case mindWorld = "mind_world"
    case imaginationWorld = "imagination_world"
    
    var displayName: String {
        switch self {
        case .dreamWorld:
            return "Planet of Dreams"
        case .mindWorld:
            return "Planet of Mind"
        case .imaginationWorld:
            return "Planet of Fantasy"
        }
    }
    
    var description: String {
        switch self {
        case .dreamWorld:
            return "Your dream novels & dreamboards"
        case .mindWorld:
            return "Your graphic essays & reflections"
        case .imaginationWorld:
            return "Your comic projects, manga pages, and visual drafts"
        }
    }
}

// MARK: - Comics Models

// Request models for comic generation
struct ComicGenerationRequest: Codable {
    let title: String
    let concept: String
    let genre: String
    let artStyle: String
    let worldType: WorldType
    
    enum CodingKeys: String, CodingKey {
        case title
        case concept
        case genre
        case artStyle = "art_style"
        case worldType = "world_type"
    }
}

struct ComicSaveRequest: Codable {
    let title: String
    let concept: String
    let genre: String
    let artStyle: String
    let worldType: WorldType
    let imageBase64: String
    let panelsData: String
    let isFavorite: Bool
    let isPublic: Bool
    
    enum CodingKeys: String, CodingKey {
        case title
        case concept
        case genre
        case artStyle = "art_style"
        case worldType = "world_type"
        case imageBase64 = "image_base64"
        case panelsData = "panels_data"
        case isFavorite = "is_favorite"
        case isPublic = "is_public"
    }
}

// Response models for comic data
struct ComicGenerationResponse: Codable, Identifiable, Hashable {
    var title: String
    var concept: String
    var genre: String
    var artStyle: String
    var worldType: WorldType
    var imageBase64: String
    var panelsData: String
    var createdAt: String
    
    // Computed properties for SwiftUI
    var id: String { 
        return "\(title)_\(createdAt)"
    }
    
    // Computed property to get panelsData as dictionary
    var panelsDataDict: [String: Any]? {
        // Try to parse as JSON string first
        if let data = panelsData.data(using: .utf8),
           let jsonObject = try? JSONSerialization.jsonObject(with: data) {
            
            // Handle array format: [{panel: 1, ...}, {panel: 2, ...}]
            if let panelsArray = jsonObject as? [[String: Any]] {
                var panelsDict: [String: Any] = [:]
                for panelData in panelsArray {
                    if let panelNumber = panelData["panel"] as? Int {
                        panelsDict["panel\(panelNumber)"] = panelData
                    }
                }
                return panelsDict
            }
            
            // Handle dictionary format: {panel1: {...}, panel2: {...}}
            if let panelsDict = jsonObject as? [String: Any] {
                return panelsDict
            }
        }
        
        return nil
    }
    
    enum CodingKeys: String, CodingKey {
        case title
        case concept
        case genre
        case artStyle = "art_style"
        case worldType = "world_type"
        case imageBase64 = "image_base64"
        case panelsData = "panels_data"
        case createdAt = "created_at"
    }
    
    // Custom decoder to handle both string and object formats for panels_data
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        
        title = try container.decode(String.self, forKey: .title)
        concept = try container.decode(String.self, forKey: .concept)
        genre = try container.decode(String.self, forKey: .genre)
        artStyle = try container.decode(String.self, forKey: .artStyle)
        worldType = try container.decode(WorldType.self, forKey: .worldType)
        imageBase64 = try container.decode(String.self, forKey: .imageBase64)
        createdAt = try container.decode(String.self, forKey: .createdAt)
        
        // Handle panels_data with multiple fallback strategies
        do {
            let jsonValue = try container.decode(JSONValue.self, forKey: .panelsData)
            switch jsonValue {
            case .string(let stringValue):
                // Backend sent as string
                panelsData = stringValue
                print("✅ panels_data decoded as string")
            case .array(let arrayValue):
                // Backend sent as array - convert to dictionary format to match backend expectations
                print("🔄 Converting panels_data from array to dictionary format")
                var panelsDict: [String: Any] = [:]
                
                // Extract array as raw data first
                if let jsonData = try? JSONEncoder().encode(jsonValue),
                   let arrayData = try? JSONSerialization.jsonObject(with: jsonData) as? [[String: Any]] {
                    
                    // Convert array to dictionary format: {panel1: {...}, panel2: {...}}
                    for (index, panelData) in arrayData.enumerated() {
                        let panelKey = "panel\(index + 1)"
                        panelsDict[panelKey] = panelData
                    }
                    
                    // Convert back to JSON string
                    if let dictData = try? JSONSerialization.data(withJSONObject: panelsDict),
                       let dictString = String(data: dictData, encoding: .utf8) {
                        panelsData = dictString
                        print("✅ Successfully converted array to dictionary format")
                    } else {
                        panelsData = "{}"
                        print("⚠️ Failed to convert dictionary to string, using empty object")
                    }
                } else {
                    // Fallback: keep as array string
                    if let jsonData = try? JSONEncoder().encode(jsonValue),
                       let jsonString = String(data: jsonData, encoding: .utf8) {
                        panelsData = jsonString
                        print("⚠️ Keeping original array format as fallback")
                    } else {
                        panelsData = "[]"
                    }
                }
            case .object(_):
                // Backend sent as object - convert to string
                if let jsonData = try? JSONEncoder().encode(jsonValue),
                   let jsonString = String(data: jsonData, encoding: .utf8) {
                    panelsData = jsonString
                    print("✅ panels_data decoded as object")
                } else {
                    panelsData = "{}"
                }
            case .number(let numberValue):
                // Unexpected: number value for panels_data
                panelsData = "{\"error\": \"panels_data was a number: \(numberValue)\"}"
                print("⚠️ panels_data was unexpectedly a number: \(numberValue)")
            case .bool(let boolValue):
                // Unexpected: boolean value for panels_data
                panelsData = "{\"error\": \"panels_data was a boolean: \(boolValue)\"}"
                print("⚠️ panels_data was unexpectedly a boolean: \(boolValue)")
            case .null:
                // Null value for panels_data
                panelsData = "{}"
                print("⚠️ panels_data was null, using empty object")
            }
        } catch {
            // Comprehensive fallback for any decoding issues
            print("⚠️ panels_data decoding failed: \(error)")
            
            // Try to decode as raw string directly
            do {
                panelsData = try container.decode(String.self, forKey: .panelsData)
                print("✅ Fallback: successfully decoded panels_data as raw string")
            } catch {
                print("⚠️ Even string fallback failed: \(error)")
                
                // Try to get any value and convert to string
                do {
                    if let anyValue = try? container.decode(AnyCodable.self, forKey: .panelsData) {
                        if let data = try? JSONSerialization.data(withJSONObject: anyValue.value),
                           let string = String(data: data, encoding: .utf8) {
                            panelsData = string
                            print("✅ Fallback: converted arbitrary JSON to string")
                        } else {
                            panelsData = "{}"
                            print("⚠️ Final fallback: using empty object")
                        }
                    } else {
                        panelsData = "{}"
                        print("⚠️ Ultimate fallback: using empty object")
                    }
                } catch {
                    panelsData = "{}"
                    print("⚠️ All fallbacks failed, using empty object")
                }
            }
        }
    }
    
    // Custom encoder
    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        
        try container.encode(title, forKey: .title)
        try container.encode(concept, forKey: .concept)
        try container.encode(genre, forKey: .genre)
        try container.encode(artStyle, forKey: .artStyle)
        try container.encode(worldType, forKey: .worldType)
        try container.encode(imageBase64, forKey: .imageBase64)
        try container.encode(panelsData, forKey: .panelsData)
        try container.encode(createdAt, forKey: .createdAt)
    }
    
    // Manual initializer for fallback creation
    init(title: String, concept: String, genre: String, artStyle: String, worldType: WorldType, imageBase64: String, panelsData: String, createdAt: String) {
        self.title = title
        self.concept = concept
        self.genre = genre
        self.artStyle = artStyle
        self.worldType = worldType
        self.imageBase64 = imageBase64
        self.panelsData = panelsData
        self.createdAt = createdAt
    }
    
    // Hashable conformance
    func hash(into hasher: inout Hasher) {
        hasher.combine(id)
    }
    
    static func == (lhs: ComicGenerationResponse, rhs: ComicGenerationResponse) -> Bool {
        return lhs.id == rhs.id
    }
}

struct ComicData: Codable {
    let id: Int
    let title: String
    let genre: String
    let artStyle: String
    let concept: String
    let panels: [PanelData]
    let createdAt: String
    let isFavorite: Bool
    let isPublic: Bool
    
    enum CodingKeys: String, CodingKey {
        case id, title, genre, concept, panels
        case artStyle = "art_style"
        case createdAt = "created_at"
        case isFavorite = "is_favorite"
        case isPublic = "is_public"
    }
}

struct PanelData: Codable {
    let panel: Int
    let dialogue: String?
    let imagePrompt: String
    
    enum CodingKeys: String, CodingKey {
        case panel, dialogue
        case imagePrompt = "image_prompt"
    }
}

// Full comic response model (with image data)
struct ComicResponse: Codable {
    let id: Int
    let title: String
    let concept: String
    let genre: String
    let artStyle: String
    let imageBase64: String
    let panelsData: String
    let createdAt: String
    let isFavorite: Bool
    let isPublic: Bool
    let viewCount: Int
    
    enum CodingKeys: String, CodingKey {
        case id, title, concept, genre
        case artStyle = "art_style"
        case imageBase64 = "image_base64"
        case panelsData = "panels_data"
        case createdAt = "created_at"
        case isFavorite = "is_favorite"
        case isPublic = "is_public"
        case viewCount = "view_count"
    }
}

// List comic response model (without image data for performance)
struct ComicListResponse: Codable {
    let id: Int
    let title: String
    let concept: String
    let genre: String
    let artStyle: String
    let createdAt: String
    let isFavorite: Bool
    let isPublic: Bool
    let viewCount: Int
    
    enum CodingKeys: String, CodingKey {
        case id, title, concept, genre
        case artStyle = "art_style"
        case createdAt = "created_at"
        case isFavorite = "is_favorite"
        case isPublic = "is_public"
        case viewCount = "view_count"
    }
}

// Legacy models for backwards compatibility
struct ComicRequest: Codable {
    let message: String
    let genre: String?
    let artStyle: String?
    
    enum CodingKeys: String, CodingKey {
        case message, genre
        case artStyle = "art_style"
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

struct IOSConfigResponse: Codable {
    let version: String
    let features: [String]
    let config: [String: String]
}

struct APISuccessResponse: Codable {
    let success: Bool
    let message: String
}

// MARK: - Swift App Models
struct Comic: Identifiable, Codable, Hashable {
    let id: Int
    let title: String
    let concept: String
    let genre: String
    let artStyle: String
    let imageData: Data?
    let panelsData: String?
    let createdAt: Date
    var isFavorite: Bool
    var isPublic: Bool
    let viewCount: Int
    
    // For creating new comics
    init(title: String, concept: String, genre: String, artStyle: String) {
        self.id = 0 // Will be set by server
        self.title = title
        self.concept = concept
        self.genre = genre
        self.artStyle = artStyle
        self.imageData = nil
        self.panelsData = nil
        self.createdAt = Date()
        self.isFavorite = false
        self.isPublic = false
        self.viewCount = 0
    }
    
    // For creating from API response (list view)
    init(from listResponse: ComicListResponse) {
        self.id = listResponse.id
        self.title = listResponse.title
        self.concept = listResponse.concept
        self.genre = listResponse.genre
        self.artStyle = listResponse.artStyle
        self.imageData = nil
        self.panelsData = nil
        self.createdAt = ISO8601DateFormatter().date(from: listResponse.createdAt) ?? Date()
        self.isFavorite = listResponse.isFavorite
        self.isPublic = listResponse.isPublic
        self.viewCount = listResponse.viewCount
    }
    
    // For creating from API response (full comic)
    init(from response: ComicResponse) {
        self.id = response.id
        self.title = response.title
        self.concept = response.concept
        self.genre = response.genre
        self.artStyle = response.artStyle
        self.imageData = Data(base64Encoded: response.imageBase64)
        self.panelsData = response.panelsData
        self.createdAt = ISO8601DateFormatter().date(from: response.createdAt) ?? Date()
        self.isFavorite = response.isFavorite
        self.isPublic = response.isPublic
        self.viewCount = response.viewCount
    }
    
    // For creating from generation response
    init(from response: ComicGenerationResponse) {
        self.id = 0 // Will be set by server
        self.title = response.title
        self.concept = response.concept
        self.genre = response.genre
        self.artStyle = response.artStyle
        self.imageData = Data(base64Encoded: response.imageBase64)
        self.panelsData = response.panelsData
        self.createdAt = ISO8601DateFormatter().date(from: response.createdAt) ?? Date()
        self.isFavorite = false
        self.isPublic = false
        self.viewCount = 0
    }
    
    // Hashable conformance
    func hash(into hasher: inout Hasher) {
        hasher.combine(id)
    }
    
    static func == (lhs: Comic, rhs: Comic) -> Bool {
        return lhs.id == rhs.id
    }
}

// MARK: - World-specific Models
struct WorldComicsRequest: Codable {
    let worldType: WorldType
    let page: Int
    let perPage: Int
    let favoritesOnly: Bool
    
    enum CodingKeys: String, CodingKey {
        case worldType = "world_type"
        case page
        case perPage = "per_page"
        case favoritesOnly = "favorites_only"
    }
}

struct WorldStatsResponse: Codable {
    let worldType: WorldType
    let totalComics: Int
    let favoriteComics: Int
    let publicComics: Int
    
    enum CodingKeys: String, CodingKey {
        case worldType = "world_type"
        case totalComics = "total_comics"
        case favoriteComics = "favorite_comics"
        case publicComics = "public_comics"
    }
}

struct ComicCollectionRequest: Codable {
    let name: String
    let description: String?
    let worldType: WorldType
    
    enum CodingKeys: String, CodingKey {
        case name
        case description
        case worldType = "world_type"
    }
}

struct ComicCollectionResponse: Codable, Identifiable {
    let id: Int
    let name: String
    let description: String?
    let worldType: WorldType
    let comicCount: Int
    let createdAt: String
    
    enum CodingKeys: String, CodingKey {
        case id
        case name
        case description
        case worldType = "world_type"
        case comicCount = "comic_count"
        case createdAt = "created_at"
    }
}

// MARK: - Image Generation Models
struct ImageRequest: Codable {
    let prompt: String
}

struct ImageGenerationResponse: Codable {
    let imageBase64: String
    let prompt: String
    let createdAt: String
    
    enum CodingKeys: String, CodingKey {
        case imageBase64 = "image_base64"
        case prompt
        case createdAt = "created_at"
    }
} 
