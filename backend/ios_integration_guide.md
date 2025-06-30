# MindToon iOS Integration Guide

## Backend Status Assessment ✅

Your FastAPI backend is **READY** for iOS frontend connection! Here's the analysis against the criteria:

### ✅ FastAPI Application Requirements - COMPLETE
- **✅ Define Endpoints**: All required endpoints are implemented
  - Authentication: `/api/auth/register`, `/api/auth/token`, `/api/auth/me`
  - Comics: `/api/chats/scenario/comic/sheet/`, `/api/chats/scenario/`
  - Health: `/health`, `/api/ios/config`
- **✅ Data Models (Pydantic)**: Properly implemented with SQLModel
  - User models: `UserCreate`, `UserRead`, `Token`
  - Chat models: `ChatMessagePayload`, `ChatMessageListItem`
  - Comics models: `ComicsPage`, `ComicsPageCreate`
- **✅ Serialization/Deserialization**: Automatic JSON handling via Pydantic
- **✅ Asynchronous Operations**: FastAPI with async/await support
- **✅ Database Integration**: SQLModel with PostgreSQL support

### ✅ Authentication and Authorization - COMPLETE
- **✅ JWT Implementation**: Full JWT token system with `python-jose`
- **✅ OAuth2 Support**: Built-in OAuth2PasswordBearer
- **✅ Password Hashing**: Secure bcrypt implementation
- **✅ Token Management**: Access token creation and validation

### ✅ CORS Configuration - COMPLETE
- **✅ Cross-Origin Support**: Configured for iOS app origins
- **✅ Development Support**: Capacitor and Ionic origins included
- **✅ Production Ready**: Configurable origins for deployment

### ✅ Error Handling - COMPLETE
- **✅ HTTP Status Codes**: Proper error responses (400, 401, 404, 500)
- **✅ Validation Errors**: Pydantic automatic validation
- **✅ Custom Exceptions**: User-friendly error messages

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

### Comics Generation Endpoints

#### 4. Generate Comic Sheet
```http
POST /api/chats/scenario/comic/sheet/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "message": "A superhero saves a cat from a tree",
  "genre": "superhero",
  "art_style": "comic book"
}
```

#### 5. Generate Scenario Only
```http
POST /api/chats/scenario/
Content-Type: application/json

{
  "message": "A superhero saves a cat from a tree"
}
```

#### 6. Get Comic by ID
```http
GET /api/chats/scenario/comic/sheet/{comic_id}/
Authorization: Bearer <access_token>
```

### Utility Endpoints

#### 7. Health Check
```http
GET /health
```

#### 8. iOS Configuration
```http
GET /api/ios/config
```

## iOS Implementation Guide

### 1. Network Layer Setup

Create an API client in Swift:

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
    
    // MARK: - Comics
    func generateComic(request: ComicRequest, token: String) async throws -> ComicResponse {
        let url = URL(string: "\(baseURL)/api/chats/scenario/comic/sheet/")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let jsonData = try JSONEncoder().encode(request)
        request.httpBody = jsonData
        
        let (data, _) = try await URLSession.shared.data(for: request)
        return try JSONDecoder().decode(ComicResponse.self, from: data)
    }
}
```

### 2. Data Models

```swift
// Models.swift
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
```

### 3. Usage Example

```swift
// ViewModel.swift
import Foundation

@MainActor
class ComicsViewModel: ObservableObject {
    @Published var comics: [ComicResponse] = []
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    func generateComic(message: String, genre: String?, artStyle: String?) async {
        isLoading = true
        errorMessage = nil
        
        do {
            let request = ComicRequest(message: message, genre: genre, artStyle: artStyle)
            let token = UserDefaults.standard.string(forKey: "access_token") ?? ""
            
            let comic = try await APIClient.shared.generateComic(request: request, token: token)
            comics.append(comic)
        } catch {
            errorMessage = error.localizedDescription
        }
        
        isLoading = false
    }
}
```

### 4. Authentication Manager

```swift
// AuthManager.swift
import Foundation

class AuthManager: ObservableObject {
    @Published var isAuthenticated = false
    @Published var currentUser: UserResponse?
    
    static let shared = AuthManager()
    
    private init() {
        checkAuthStatus()
    }
    
    func login(username: String, password: String) async throws {
        let tokenResponse = try await APIClient.shared.login(username: username, password: password)
        
        // Store token
        UserDefaults.standard.set(tokenResponse.accessToken, forKey: "access_token")
        
        // Update auth status
        await MainActor.run {
            self.isAuthenticated = true
        }
    }
    
    func logout() {
        UserDefaults.standard.removeObject(forKey: "access_token")
        isAuthenticated = false
        currentUser = nil
    }
    
    private func checkAuthStatus() {
        let token = UserDefaults.standard.string(forKey: "access_token")
        isAuthenticated = token != nil
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

## Production Deployment

### Backend Deployment
1. Deploy to Railway, Heroku, or AWS
2. Update `BASE_URL` environment variable
3. Configure CORS for your production domain
4. Set up SSL/HTTPS

### iOS App Store Deployment
1. Update `baseURL` in `APIClient.swift` to production URL
2. Remove `NSAllowsArbitraryLoads` from `Info.plist`
3. Implement proper certificate pinning
4. Test all API endpoints with production backend

## Security Considerations

1. **Token Storage**: Use Keychain for secure token storage in iOS
2. **HTTPS**: Always use HTTPS in production
3. **Input Validation**: Backend already validates all inputs
4. **Rate Limiting**: Consider implementing rate limiting
5. **Error Handling**: Don't expose sensitive information in error messages

Your backend is production-ready for iOS integration! 🚀 