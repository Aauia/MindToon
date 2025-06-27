import Foundation

class APIClient {
    static let shared = APIClient()
    private let baseURL = "http://localhost:8080" // Change for production
    
    private init() {}
    
    // MARK: - Authentication
    func login(username: String, password: String) async throws -> TokenResponse {
        let url = URL(string: "\(baseURL)/api/auth/token")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/x-www-form-urlencoded", forHTTPHeaderField: "Content-Type")
        
        let body = "username=\(username)&password=\(password)"
        request.httpBody = body.data(using: .utf8)
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        if httpResponse.statusCode != 200 {
            throw APIError.serverError(httpResponse.statusCode)
        }
        
        return try JSONDecoder().decode(TokenResponse.self, from: data)
    }
    
    func register(user: RegisterRequest) async throws -> UserResponse {
        let url = URL(string: "\(baseURL)/api/auth/register")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let jsonData = try JSONEncoder().encode(user)
        request.httpBody = jsonData
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        if httpResponse.statusCode != 201 {
            throw APIError.serverError(httpResponse.statusCode)
        }
        
        return try JSONDecoder().decode(UserResponse.self, from: data)
    }
    
    func getUserProfile(token: String) async throws -> UserResponse {
        let url = URL(string: "\(baseURL)/api/auth/me")!
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        if httpResponse.statusCode != 200 {
            throw APIError.serverError(httpResponse.statusCode)
        }
        
        return try JSONDecoder().decode(UserResponse.self, from: data)
    }
    
    // MARK: - Comics
    // MARK: - Comics
      func generateComic(comicRequest: ComicRequest, token: String) async throws -> ComicResponse {
          let url = URL(string: "\(baseURL)/api/chats/scenario/comic/sheet/")!
          var request = URLRequest(url: url)
          request.httpMethod = "POST"
          request.setValue("application/json", forHTTPHeaderField: "Content-Type")
          request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
          
          let jsonData = try JSONEncoder().encode(comicRequest)
          request.httpBody = jsonData
          
          let (data, response) = try await URLSession.shared.data(for: request)
          
          guard let httpResponse = response as? HTTPURLResponse else {
              throw APIError.invalidResponse
          }
          
          if httpResponse.statusCode != 200 {
              throw APIError.serverError(httpResponse.statusCode)
          }
          
          return try JSONDecoder().decode(ComicResponse.self, from: data)
      }
      
    func generateScenario(message: String) async throws -> ScenarioResponse {
        let url = URL(string: "\(baseURL)/api/chats/scenario/")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body = ["message": message]
        let jsonData = try JSONEncoder().encode(body)
        request.httpBody = jsonData
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        if httpResponse.statusCode != 200 {
            throw APIError.serverError(httpResponse.statusCode)
        }
        
        return try JSONDecoder().decode(ScenarioResponse.self, from: data)
    }
    
    func getComicById(comicId: Int, token: String) async throws -> ComicResponse {
        let url = URL(string: "\(baseURL)/api/chats/scenario/comic/sheet/\(comicId)/")!
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        if httpResponse.statusCode != 200 {
            throw APIError.serverError(httpResponse.statusCode)
        }
        
        return try JSONDecoder().decode(ComicResponse.self, from: data)
    }
    
    // MARK: - Utility
    func healthCheck() async throws -> HealthResponse {
        let url = URL(string: "\(baseURL)/health")!
        let (data, response) = try await URLSession.shared.data(from: url)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        if httpResponse.statusCode != 200 {
            throw APIError.serverError(httpResponse.statusCode)
        }
        
        return try JSONDecoder().decode(HealthResponse.self, from: data)
    }
    
    func getIOSConfig() async throws -> IOSConfigResponse {
        let url = URL(string: "\(baseURL)/api/ios/config")!
        let (data, response) = try await URLSession.shared.data(from: url)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        if httpResponse.statusCode != 200 {
            throw APIError.serverError(httpResponse.statusCode)
        }
        
        return try JSONDecoder().decode(IOSConfigResponse.self, from: data)
    }
}

// MARK: - API Errors
enum APIError: Error, LocalizedError {
    case invalidResponse
    case serverError(Int)
    case decodingError
    case networkError
    
    var errorDescription: String? {
        switch self {
        case .invalidResponse:
            return "Invalid response from server"
        case .serverError(let code):
            return "Server error with status code: \(code)"
        case .decodingError:
            return "Failed to decode response"
        case .networkError:
            return "Network connection error"
        }
    }
} 
