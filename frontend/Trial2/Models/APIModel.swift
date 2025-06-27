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

// MARK: - Comics Models
struct ComicRequest: Codable {
    let message: String
    let genre: String?
    let artStyle: String?
    
    enum CodingKeys: String, CodingKey {
        case message, genre
        case artStyle = "art_style"
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

struct ScenarioResponse: Codable {
    let scenario: String
    let message: String
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
} 
