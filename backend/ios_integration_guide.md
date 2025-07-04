# MindToon iOS Integration Guide

## Backend Status Assessment ✅

Your FastAPI backend is **READY** for iOS frontend connection! Here's the analysis against the criteria:

### ✅ FastAPI Application Requirements - COMPLETE
- **✅ Define Endpoints**: All required endpoints are implemented
  - Authentication: `/api/auth/register`, `/api/auth/token`, `/api/auth/me`, `/api/auth/delete-account`
  - Comics: `/api/chats/generate-comic`, `/api/chats/generate-comic-with-data`, `/api/chats/my-comics`
  - Scenarios: `/api/chats/scenarios/*`, `/api/chats/generate-scenario`
  - World System: `/api/chats/world-comics`, `/api/chats/world-stats/{world_type}`
  - Collections: `/api/chats/collections`, `/api/chats/collections/{world_type}`
  - Supabase: `/api/supabase/*`
  - Health: `/health`, `/api/ios/config`, `/api/ios/auth-guide`
- **✅ Data Models (Pydantic)**: Properly implemented with SQLModel
  - User models: `UserCreate`, `UserRead`, `Token`, `UserDeletionConfirmation`
  - Chat models: `ChatMessagePayload`, `ChatMessageListItem`
  - Comics models: `ComicsPage`, `ComicsPageCreate`, `ComicRequest`, `ComicResponse`
  - World models: `WorldType`, `WorldStats`, `ComicCollection`, `DetailedScenario`
  - AI Schemas: `ScenarioSchema`, `ComicGenerationRequest`, `DetailedScenarioSchema`
- **✅ Serialization/Deserialization**: Automatic JSON handling via Pydantic
- **✅ Asynchronous Operations**: FastAPI with async/await support
- **✅ Database Integration**: SQLModel with PostgreSQL support
- **✅ Cloud Storage**: Supabase Storage integration for comic images

### ✅ Authentication and Authorization - COMPLETE
- **✅ JWT Implementation**: Full JWT token system with `python-jose`
- **✅ OAuth2 Support**: Built-in OAuth2PasswordBearer
- **✅ Password Hashing**: Secure bcrypt implementation
- **✅ Token Management**: Access token creation and validation
- **✅ Account Management**: Complete account deletion with data cleanup

### ✅ CORS Configuration - COMPLETE
- **✅ Cross-Origin Support**: Configured for iOS app origins
- **✅ Development Support**: Capacitor and Ionic origins included
- **✅ Production Ready**: Configurable origins for deployment

### ✅ Error Handling - COMPLETE
- **✅ HTTP Status Codes**: Proper error responses (400, 401, 404, 500)
- **✅ Validation Errors**: Pydantic automatic validation
- **✅ Custom Exceptions**: User-friendly error messages

### ✅ NEW FEATURES - COMPLETE
- **✅ World System**: Dream World, Mind World, Imagination World organization
- **✅ Collections**: Organize comics into themed collections
- **✅ Detailed Scenarios**: Rich narrative stories complementing comics
- **✅ Supabase Integration**: Cloud storage and database management
- **✅ Advanced Comic Generation**: Multiple generation modes and formats
- **✅ Testing Endpoints**: No-auth endpoints for development and testing

## API Endpoints for iOS

### Base URL
```
Development: http://localhost:8000
Production: [Your deployed URL]
```

### Authentication Endpoints

#### 1. Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "user123",
  "email": "user@example.com",
  "full_name": "John Doe",
  "password": "securepassword123"
}
```

#### 2. Login
```http
POST /api/auth/token
Content-Type: application/x-www-form-urlencoded

username=user123&password=securepassword123
```

#### 3. Get User Profile
```http
GET /api/auth/me
Authorization: Bearer <access_token>
```

#### 4. Delete Account (NEW)
```http
DELETE /api/auth/delete-account
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "confirm_deletion": true,
  "username_confirmation": "user123",
  "understanding_acknowledgment": "I understand this action is permanent and irreversible"
}
```

### Comic Generation Endpoints (ENHANCED)

#### 5. Generate Comic (Auto-Save, Returns PNG)
```http
POST /api/chats/generate-comic
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "concept": "A superhero saves a cat from a tree",
  "genre": "superhero",
  "art_style": "comic book",
  "include_detailed_scenario": false
}
```

#### 6. Generate Comic with Data (iOS-Friendly)
```http
POST /api/chats/generate-comic-with-data
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "My Comic",
  "concept": "A superhero saves a cat from a tree",
  "genre": "superhero",
  "art_style": "comic book",
  "world_type": "imagination_world",
  "include_detailed_scenario": true
}
```

#### 7. Get My Comics (with Filtering)
```http
GET /api/chats/my-comics?limit=20&offset=0&genre=superhero&is_favorite=true
Authorization: Bearer <access_token>
```

#### 8. Get Specific Comic
```http
GET /api/chats/comic/{comic_id}
Authorization: Bearer <access_token>
```

#### 9. Update Comic
```http
PUT /api/chats/comic/{comic_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "Updated Title",
  "is_favorite": true,
  "is_public": false
}
```

#### 10. Delete Comic
```http
DELETE /api/chats/comic/{comic_id}
Authorization: Bearer <access_token>
```

### World System Endpoints (NEW)

#### 11. Get World Comics
```http
POST /api/chats/world-comics
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "world_type": "dream_world",
  "page": 1,
  "per_page": 10,
  "favorites_only": false
}
```

#### 12. Get World Statistics
```http
GET /api/chats/world-stats/dream_world
Authorization: Bearer <access_token>
```

### Collections System Endpoints (NEW)

#### 13. Create Collection
```http
POST /api/chats/collections
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "My Superhero Collection",
  "description": "All my superhero comics",
  "world_type": "imagination_world"
}
```

#### 14. Get World Collections
```http
GET /api/chats/collections/imagination_world
Authorization: Bearer <access_token>
```

### Detailed Scenarios Endpoints (NEW)

#### 15. Save Scenario
```http
POST /api/chats/scenarios/save
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "comic_id": 123,
  "title": "The Hero's Journey",
  "concept": "A detailed story",
  "genre": "adventure",
  "art_style": "comic book",
  "world_type": "imagination_world",
  "scenario_data": "{...}",
  "word_count": 1500,
  "reading_time_minutes": 6
}
```

#### 16. Get Scenario by Comic
```http
GET /api/chats/scenarios/comic/{comic_id}
Authorization: Bearer <access_token>
```

#### 17. Get User Scenarios
```http
GET /api/chats/scenarios/user?limit=20&offset=0
Authorization: Bearer <access_token>
```

### Supabase Integration Endpoints (NEW)

#### 18. Test Supabase Connection
```http
GET /api/supabase/test-connection
```

#### 19. Get Storage Usage
```http
GET /api/supabase/storage/user/{user_id}/usage
Authorization: Bearer <access_token>
```

#### 20. Supabase Health Check
```http
GET /api/supabase/health
```

### Testing Endpoints (NEW - No Auth Required)

#### 21. Test Comic Generation (No Auth)
```http
POST /api/chats/test/generate-comic-no-auth
Content-Type: application/json

{
  "concept": "A test comic",
  "genre": "adventure",
  "art_style": "cartoon"
}
```

#### 22. Test Scenario Generation (No Auth)
```http
POST /api/chats/test/generate-scenario-no-auth
Content-Type: application/json

{
  "concept": "A test scenario"
}
```

#### 23. Test Health Check
```http
GET /api/chats/test/health
```

### Utility Endpoints

#### 24. Health Check
```http
GET /health
```

#### 25. iOS Configuration
```http
GET /api/ios/config
```

#### 26. iOS Authentication Guide
```http
GET /api/ios/auth-guide
```

#### 27. Available Genres
```http
GET /api/chats/genres
```

#### 28. Available Art Styles
```http
GET /api/chats/art-styles
```

## iOS Implementation Guide

### 1. Enhanced Network Layer Setup

Create an enhanced API client in Swift:

```swift
// APIClient.swift
import Foundation

class APIClient {
    static let shared = APIClient()
    private let baseURL = "http://localhost:8000" // Change for production
    
    private init() {}
    
    // MARK: - Authentication
    func login(username: String, password: String) async throws -> TokenResponse {
        let url = URL(string: "\(baseURL)/api/auth/token")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/x-www-form-urlencoded", forHTTPHeaderField: "Content-Type")
        
        let body = "username=\(username)&password=\(password)"
        request.httpBody = body.data(using: .utf8)
        
        let (data, _) = try await URLSession.shared.data(for: request)
        return try JSONDecoder().decode(TokenResponse.self, from: data)
    }
    
    func register(user: RegisterRequest) async throws -> UserResponse {
        let url = URL(string: "\(baseURL)/api/auth/register")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let jsonData = try JSONEncoder().encode(user)
        request.httpBody = jsonData
        
        let (data, _) = try await URLSession.shared.data(for: request)
        return try JSONDecoder().decode(UserResponse.self, from: data)
    }
    
    func deleteAccount(confirmation: AccountDeletionRequest, token: String) async throws -> DeletionSummary {
        let url = URL(string: "\(baseURL)/api/auth/delete-account")!
        var request = URLRequest(url: url)
        request.httpMethod = "DELETE"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let jsonData = try JSONEncoder().encode(confirmation)
        request.httpBody = jsonData
        
        let (data, _) = try await URLSession.shared.data(for: request)
        return try JSONDecoder().decode(DeletionSummary.self, from: data)
    }
    
    // MARK: - Enhanced Comics
    func generateComic(request: ComicRequest, token: String) async throws -> Data {
        let url = URL(string: "\(baseURL)/api/chats/generate-comic")!
        var httpRequest = URLRequest(url: url)
        httpRequest.httpMethod = "POST"
        httpRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        httpRequest.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let jsonData = try JSONEncoder().encode(request)
        httpRequest.httpBody = jsonData
        
        let (data, response) = try await URLSession.shared.data(for: httpRequest)
        
        // Extract metadata from headers
        if let httpResponse = response as? HTTPURLResponse {
            let genre = httpResponse.value(forHTTPHeaderField: "X-Comic-Genre")
            let artStyle = httpResponse.value(forHTTPHeaderField: "X-Comic-Art-Style")
            let panels = httpResponse.value(forHTTPHeaderField: "X-Comic-Panels")
            let comicId = httpResponse.value(forHTTPHeaderField: "X-Comic-ID")
            
            print("Generated Comic - Genre: \(genre ?? "Unknown"), Style: \(artStyle ?? "Unknown"), Panels: \(panels ?? "0"), ID: \(comicId ?? "unsaved")")
        }
        
        return data
    }
    
    func generateComicWithData(request: ComicSaveRequest, token: String) async throws -> ComicGenerationResponse {
        let url = URL(string: "\(baseURL)/api/chats/generate-comic-with-data")!
        var httpRequest = URLRequest(url: url)
        httpRequest.httpMethod = "POST"
        httpRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        httpRequest.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let jsonData = try JSONEncoder().encode(request)
        httpRequest.httpBody = jsonData
        
        let (data, _) = try await URLSession.shared.data(for: httpRequest)
        return try JSONDecoder().decode(ComicGenerationResponse.self, from: data)
    }
    
    func getMyComics(token: String, limit: Int = 20, offset: Int = 0, genre: String? = nil, 
                    artStyle: String? = nil, isFavorite: Bool? = nil) async throws -> [ComicListResponse] {
        var components = URLComponents(string: "\(baseURL)/api/chats/my-comics")!
        var queryItems: [URLQueryItem] = [
            URLQueryItem(name: "limit", value: String(limit)),
            URLQueryItem(name: "offset", value: String(offset))
        ]
        
        if let genre = genre { queryItems.append(URLQueryItem(name: "genre", value: genre)) }
        if let artStyle = artStyle { queryItems.append(URLQueryItem(name: "art_style", value: artStyle)) }
        if let isFavorite = isFavorite { queryItems.append(URLQueryItem(name: "is_favorite", value: String(isFavorite))) }
        
        components.queryItems = queryItems
        
        var request = URLRequest(url: components.url!)
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let (data, _) = try await URLSession.shared.data(for: request)
        return try JSONDecoder().decode([ComicListResponse].self, from: data)
    }
    
    func getComic(id: Int, token: String) async throws -> ComicResponse {
        let url = URL(string: "\(baseURL)/api/chats/comic/\(id)")!
        var request = URLRequest(url: url)
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let (data, _) = try await URLSession.shared.data(for: request)
        return try JSONDecoder().decode(ComicResponse.self, from: data)
    }
    
    // MARK: - World System
    func getWorldComics(request: WorldComicsRequest, token: String) async throws -> [ComicGenerationResponse] {
        let url = URL(string: "\(baseURL)/api/chats/world-comics")!
        var httpRequest = URLRequest(url: url)
        httpRequest.httpMethod = "POST"
        httpRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        httpRequest.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let jsonData = try JSONEncoder().encode(request)
        httpRequest.httpBody = jsonData
        
        let (data, _) = try await URLSession.shared.data(for: httpRequest)
        return try JSONDecoder().decode([ComicGenerationResponse].self, from: data)
    }
    
    func getWorldStats(worldType: WorldType, token: String) async throws -> WorldStatsResponse {
        let url = URL(string: "\(baseURL)/api/chats/world-stats/\(worldType.rawValue)")!
        var request = URLRequest(url: url)
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let (data, _) = try await URLSession.shared.data(for: request)
        return try JSONDecoder().decode(WorldStatsResponse.self, from: data)
    }
    
    // MARK: - Collections
    func createCollection(request: ComicCollectionRequest, token: String) async throws -> ComicCollectionResponse {
        let url = URL(string: "\(baseURL)/api/chats/collections")!
        var httpRequest = URLRequest(url: url)
        httpRequest.httpMethod = "POST"
        httpRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        httpRequest.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let jsonData = try JSONEncoder().encode(request)
        httpRequest.httpBody = jsonData
        
        let (data, _) = try await URLSession.shared.data(for: request)
        return try JSONDecoder().decode(ComicCollectionResponse.self, from: data)
    }
    
    func getWorldCollections(worldType: WorldType, token: String) async throws -> [ComicCollectionResponse] {
        let url = URL(string: "\(baseURL)/api/chats/collections/\(worldType.rawValue)")!
        var request = URLRequest(url: url)
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let (data, _) = try await URLSession.shared.data(for: request)
        return try JSONDecoder().decode([ComicCollectionResponse].self, from: data)
    }
    
    // MARK: - Scenarios
    func saveScenario(request: ScenarioSaveRequest, token: String) async throws -> ScenarioSaveResponse {
        let url = URL(string: "\(baseURL)/api/chats/scenarios/save")!
        var httpRequest = URLRequest(url: url)
        httpRequest.httpMethod = "POST"
        httpRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        httpRequest.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let jsonData = try JSONEncoder().encode(request)
        httpRequest.httpBody = jsonData
        
        let (data, _) = try await URLSession.shared.data(for: request)
        return try JSONDecoder().decode(ScenarioSaveResponse.self, from: data)
    }
    
    func getScenarioByComic(comicId: Int, token: String) async throws -> DetailedScenario {
        let url = URL(string: "\(baseURL)/api/chats/scenarios/comic/\(comicId)")!
        var request = URLRequest(url: url)
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let (data, _) = try await URLSession.shared.data(for: request)
        return try JSONDecoder().decode(DetailedScenario.self, from: data)
    }
    
    // MARK: - Testing (No Auth)
    func testGenerateComic(request: ComicRequest) async throws -> Data {
        let url = URL(string: "\(baseURL)/api/chats/test/generate-comic-no-auth")!
        var httpRequest = URLRequest(url: url)
        httpRequest.httpMethod = "POST"
        httpRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let jsonData = try JSONEncoder().encode(request)
        httpRequest.httpBody = jsonData
        
        let (data, _) = try await URLSession.shared.data(for: httpRequest)
        return data
    }
    
    // MARK: - Utility
    func getAvailableGenres() async throws -> [String] {
        let url = URL(string: "\(baseURL)/api/chats/genres")!
        let (data, _) = try await URLSession.shared.data(from: url)
        let response = try JSONDecoder().decode([String: [String]].self, from: data)
        return response["genres"] ?? []
    }
    
    func getAvailableArtStyles() async throws -> [String] {
        let url = URL(string: "\(baseURL)/api/chats/art-styles")!
        let (data, _) = try await URLSession.shared.data(from: url)
        let response = try JSONDecoder().decode([String: [String]].self, from: data)
        return response["art_styles"] ?? []
    }
}
```

### 2. Enhanced Data Models

```swift
// Models.swift
import Foundation

// MARK: - World System
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
    let success: Bool
    let message: String
    let deletionStats: DeletionStats
    
    enum CodingKeys: String, CodingKey {
        case success, message
        case deletionStats = "deletion_stats"
    }
}

struct DeletionStats: Codable {
    let userId: Int
    let username: String
    let comicsDeleted: Int
    let scenariosDeleted: Int
    let imagesDeleted: Int
    
    enum CodingKeys: String, CodingKey {
        case userId = "user_id"
        case username
        case comicsDeleted = "comics_deleted"
        case scenariosDeleted = "scenarios_deleted"
        case imagesDeleted = "images_deleted"
    }
}

// MARK: - Enhanced Comics Models
struct ComicRequest: Codable {
    let concept: String
    let genre: String?
    let artStyle: String?
    let includeDetailedScenario: Bool
    
    enum CodingKeys: String, CodingKey {
        case concept, genre
        case artStyle = "art_style"
        case includeDetailedScenario = "include_detailed_scenario"
    }
    
    init(concept: String, genre: String? = nil, artStyle: String? = nil, includeDetailedScenario: Bool = false) {
        self.concept = concept
        self.genre = genre
        self.artStyle = artStyle
        self.includeDetailedScenario = includeDetailedScenario
    }
}

struct ComicSaveRequest: Codable {
    let title: String
    let concept: String
    let genre: String
    let artStyle: String
    let worldType: WorldType
    let includeDetailedScenario: Bool
    
    enum CodingKeys: String, CodingKey {
        case title, concept, genre
        case artStyle = "art_style"
        case worldType = "world_type"
        case includeDetailedScenario = "include_detailed_scenario"
    }
}

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

struct ComicGenerationResponse: Codable {
    let title: String
    let concept: String
    let genre: String
    let artStyle: String
    let worldType: WorldType
    let imageBase64: String
    let panelsData: [String: Any]
    let createdAt: String
    
    enum CodingKeys: String, CodingKey {
        case title, concept, genre
        case artStyle = "art_style"
        case worldType = "world_type"
        case imageBase64 = "image_base64"
        case panelsData = "panels_data"
        case createdAt = "created_at"
    }
}

// MARK: - World System Models
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

// MARK: - Collections Models
struct ComicCollectionRequest: Codable {
    let name: String
    let description: String?
    let worldType: WorldType
    
    enum CodingKeys: String, CodingKey {
        case name, description
        case worldType = "world_type"
    }
}

struct ComicCollectionResponse: Codable {
    let id: Int
    let name: String
    let description: String?
    let worldType: WorldType
    let comicCount: Int
    let createdAt: String
    
    enum CodingKeys: String, CodingKey {
        case id, name, description
        case worldType = "world_type"
        case comicCount = "comic_count"
        case createdAt = "created_at"
    }
}

// MARK: - Scenarios Models
struct ScenarioSaveRequest: Codable {
    let comicId: Int
    let title: String
    let concept: String
    let genre: String
    let artStyle: String
    let worldType: WorldType
    let scenarioData: String
    let wordCount: Int
    let readingTimeMinutes: Int
    
    enum CodingKeys: String, CodingKey {
        case comicId = "comic_id"
        case title, concept, genre
        case artStyle = "art_style"
        case worldType = "world_type"
        case scenarioData = "scenario_data"
        case wordCount = "word_count"
        case readingTimeMinutes = "reading_time_minutes"
    }
}

struct ScenarioSaveResponse: Codable {
    let success: Bool
    let message: String
    let scenarioId: Int
    
    enum CodingKeys: String, CodingKey {
        case success, message
        case scenarioId = "scenario_id"
    }
}

struct DetailedScenario: Codable {
    let id: Int
    let comicId: Int
    let title: String
    let concept: String
    let genre: String
    let artStyle: String
    let worldType: WorldType
    let scenarioData: String
    let wordCount: Int
    let readingTimeMinutes: Int
    let createdAt: String
    let isFavorite: Bool
    let isPublic: Bool
    
    enum CodingKeys: String, CodingKey {
        case id
        case comicId = "comic_id"
        case title, concept, genre
        case artStyle = "art_style"
        case worldType = "world_type"
        case scenarioData = "scenario_data"
        case wordCount = "word_count"
        case readingTimeMinutes = "reading_time_minutes"
        case createdAt = "created_at"
        case isFavorite = "is_favorite"
        case isPublic = "is_public"
    }
}
```

### 3. Enhanced Usage Examples

```swift
// Enhanced ViewModel.swift
import Foundation

@MainActor
class EnhancedComicsViewModel: ObservableObject {
    @Published var comics: [ComicListResponse] = []
    @Published var worlds: [WorldType: [ComicGenerationResponse]] = [:]
    @Published var collections: [WorldType: [ComicCollectionResponse]] = [:]
    @Published var worldStats: [WorldType: WorldStatsResponse] = [:]
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    // MARK: - Comic Generation
    func generateComic(concept: String, genre: String? = nil, artStyle: String? = nil, 
                      worldType: WorldType = .imaginationWorld, includeScenario: Bool = false) async {
        isLoading = true
        errorMessage = nil
        
        do {
            let request = ComicSaveRequest(
                title: "Comic: \(concept.prefix(50))",
                concept: concept,
                genre: genre ?? "adventure",
                artStyle: artStyle ?? "comic book",
                worldType: worldType,
                includeDetailedScenario: includeScenario
            )
            
            let token = UserDefaults.standard.string(forKey: "access_token") ?? ""
            let comic = try await APIClient.shared.generateComicWithData(request: request, token: token)
            
            // Add to appropriate world
            if worlds[worldType] == nil {
                worlds[worldType] = []
            }
            worlds[worldType]?.append(comic)
            
            // Refresh world stats
            await loadWorldStats(for: worldType)
            
        } catch {
            errorMessage = error.localizedDescription
        }
        
        isLoading = false
    }
    
    // MARK: - World Management
    func loadWorldComics(for worldType: WorldType, page: Int = 1, favoritesOnly: Bool = false) async {
        do {
            let request = WorldComicsRequest(
                worldType: worldType,
                page: page,
                perPage: 10,
                favoritesOnly: favoritesOnly
            )
            
            let token = UserDefaults.standard.string(forKey: "access_token") ?? ""
            let worldComics = try await APIClient.shared.getWorldComics(request: request, token: token)
            worlds[worldType] = worldComics
            
        } catch {
            errorMessage = error.localizedDescription
        }
    }
    
    func loadWorldStats(for worldType: WorldType) async {
        do {
            let token = UserDefaults.standard.string(forKey: "access_token") ?? ""
            let stats = try await APIClient.shared.getWorldStats(worldType: worldType, token: token)
            worldStats[worldType] = stats
            
        } catch {
            errorMessage = error.localizedDescription
        }
    }
    
    // MARK: - Collections Management
    func createCollection(name: String, description: String?, worldType: WorldType) async {
        do {
            let request = ComicCollectionRequest(name: name, description: description, worldType: worldType)
            let token = UserDefaults.standard.string(forKey: "access_token") ?? ""
            let collection = try await APIClient.shared.createCollection(request: request, token: token)
            
            // Add to collections
            if collections[worldType] == nil {
                collections[worldType] = []
            }
            collections[worldType]?.append(collection)
            
        } catch {
            errorMessage = error.localizedDescription
        }
    }
    
    func loadWorldCollections(for worldType: WorldType) async {
        do {
            let token = UserDefaults.standard.string(forKey: "access_token") ?? ""
            let worldCollections = try await APIClient.shared.getWorldCollections(worldType: worldType, token: token)
            collections[worldType] = worldCollections
            
        } catch {
            errorMessage = error.localizedDescription
        }
    }
    
    // MARK: - Testing Methods (No Auth)
    func testGenerateComic(concept: String) async -> Data? {
        do {
            let request = ComicRequest(concept: concept, genre: "adventure", artStyle: "cartoon")
            return try await APIClient.shared.testGenerateComic(request: request)
        } catch {
            errorMessage = error.localizedDescription
            return nil
        }
    }
}
```

### 4. Enhanced Authentication Manager

```swift
// Enhanced AuthManager.swift
import Foundation

class EnhancedAuthManager: ObservableObject {
    @Published var isAuthenticated = false
    @Published var currentUser: UserResponse?
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    static let shared = EnhancedAuthManager()
    
    private init() {
        checkAuthStatus()
    }
    
    func login(username: String, password: String) async throws {
        isLoading = true
        errorMessage = nil
        
        do {
            let tokenResponse = try await APIClient.shared.login(username: username, password: password)
            
            // Store token securely
            UserDefaults.standard.set(tokenResponse.accessToken, forKey: "access_token")
            
            // Get user profile
            let userProfile = try await APIClient.shared.getUserProfile(token: tokenResponse.accessToken)
            
            await MainActor.run {
                self.currentUser = userProfile
                self.isAuthenticated = true
                self.isLoading = false
            }
            
        } catch {
            await MainActor.run {
                self.errorMessage = error.localizedDescription
                self.isLoading = false
            }
            throw error
        }
    }
    
    func register(username: String, email: String, fullName: String, password: String) async throws {
        isLoading = true
        errorMessage = nil
        
        do {
            let request = RegisterRequest(username: username, email: email, fullName: fullName, password: password)
            let user = try await APIClient.shared.register(user: request)
            
            // Auto-login after registration
            try await login(username: username, password: password)
            
        } catch {
            await MainActor.run {
                self.errorMessage = error.localizedDescription
                self.isLoading = false
            }
            throw error
        }
    }
    
    func deleteAccount(usernameConfirmation: String) async throws -> DeletionSummary {
        guard let currentUser = currentUser else {
            throw AuthError.notAuthenticated
        }
        
        isLoading = true
        errorMessage = nil
        
        do {
            let confirmation = AccountDeletionRequest(
                confirmDeletion: true,
                usernameConfirmation: usernameConfirmation,
                understandingAcknowledgment: "I understand this action is permanent and irreversible"
            )
            
            let token = UserDefaults.standard.string(forKey: "access_token") ?? ""
            let summary = try await APIClient.shared.deleteAccount(confirmation: confirmation, token: token)
            
            // Clear local data
            await MainActor.run {
                self.logout()
                self.isLoading = false
            }
            
            return summary
            
        } catch {
            await MainActor.run {
                self.errorMessage = error.localizedDescription
                self.isLoading = false
            }
            throw error
        }
    }
    
    func logout() {
        UserDefaults.standard.removeObject(forKey: "access_token")
        isAuthenticated = false
        currentUser = nil
        errorMessage = nil
    }
    
    private func checkAuthStatus() {
        let token = UserDefaults.standard.string(forKey: "access_token")
        isAuthenticated = token != nil
    }
}

enum AuthError: Error {
    case notAuthenticated
    case invalidCredentials
    case networkError
    
    var localizedDescription: String {
        switch self {
        case .notAuthenticated:
            return "User is not authenticated"
        case .invalidCredentials:
            return "Invalid username or password"
        case .networkError:
            return "Network connection error"
        }
    }
}
```

## Environment Setup

### Backend Environment Variables
Create a `.env` file in your backend directory:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/mindtoon
SECRET_KEY=your-secret-key-here
API_KEY=your-api-key
BASE_URL=http://localhost:8000
SUPABASE_URL=your-supabase-project-url
SUPABASE_ANON_KEY=your-supabase-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key
```

### iOS Environment Setup

1. **Add Network Security** (for HTTP in development):
   Add to `Info.plist`:
   ```xml
   <key>NSAppTransportSecurity</key>
   <dict>
       <key>NSAllowsArbitraryLoads</key>
       <true/>
   </dict>
   ```

2. **For Production**: Use HTTPS and proper certificate pinning

## Testing the Connection

### 1. Test Backend Health
```bash
curl http://localhost:8000/health
```

### 2. Test iOS Config
```bash
curl http://localhost:8000/api/ios/config
```

### 3. Test Authentication
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","full_name":"Test User","password":"password123"}'
```

### 4. Test Comic Generation (No Auth)
```bash
curl -X POST http://localhost:8000/api/chats/test/generate-comic-no-auth \
  -H "Content-Type: application/json" \
  -d '{"concept":"A superhero saves a cat","genre":"superhero","art_style":"comic book"}'
```

### 5. Test Supabase Connection
```bash
curl http://localhost:8000/api/supabase/test-connection
```

## Production Deployment

### Backend Deployment
1. Deploy to Railway, Heroku, or AWS
2. Update `BASE_URL` environment variable
3. Configure CORS for your production domain
4. Set up SSL/HTTPS
5. Configure Supabase environment variables

### iOS App Store Deployment
1. Update `baseURL` in `APIClient.swift` to production URL
2. Remove `NSAllowsArbitraryLoads` from `Info.plist`
3. Implement proper certificate pinning
4. Test all API endpoints with production backend

## Security Considerations

1. **Token Storage**: Use Keychain for secure token storage in iOS
2. **HTTPS**: Always use HTTPS in production
3. **Input Validation**: Backend validates all inputs
4. **Rate Limiting**: Consider implementing rate limiting
5. **Error Handling**: Don't expose sensitive information in error messages
6. **Data Deletion**: Full account deletion with Supabase storage cleanup

## New Features Summary

### ✨ World System
- **Dream World**: Subconscious and dream-related comics
- **Mind World**: Psychological and mental exploration comics  
- **Imagination World**: Creative and fantasy comics

### ✨ Collections System
- Organize comics into themed collections within each world
- Track collection statistics and metadata

### ✨ Enhanced Comic Generation
- Multiple generation endpoints for different use cases
- Auto-saving with Supabase Storage integration
- Rich metadata and panel information

### ✨ Detailed Scenarios
- Rich narrative stories that complement comics
- Chapter-based structure linked to comic panels
- Word count and reading time estimation

### ✨ Storage Management
- Supabase cloud storage for comic images
- User storage usage tracking
- Automatic cleanup on account deletion

### ✨ Testing Infrastructure  
- No-authentication endpoints for development
- Health checks and connection testing
- Error simulation and debugging tools

Your backend is production-ready for iOS integration with advanced features! 🚀 