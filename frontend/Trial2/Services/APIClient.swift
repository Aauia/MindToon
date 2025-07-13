import Foundation
import UniformTypeIdentifiers

class APIClient {
    static let shared = APIClient()
    private let baseURLString = "https://mindtoon.space" // Change for production
    private var baseURL: URL { URL(string: baseURLString)! }
    
    // Custom URLSession with increased timeout
    private let session: URLSession = {
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 420 // seconds (5 minutes)
        config.timeoutIntervalForResource = 420 // seconds (5 minutes)
        return URLSession(configuration: config)
    }()
    
    private init() {}
    
    // MARK: - Token Management
    private func getToken() async -> String? {
        let token = await AuthManager.shared.getStoredToken()
        print("🔑 Retrieved token: \(token != nil ? "✅ Found" : "❌ Nil")")
        if let token = token {
            print("🔑 Token length: \(token.count)")
        }
        return token
    }
    
    // MARK: - Authentication
    func login(username: String, password: String) async throws -> TokenResponse {
        let url = URL(string: "\(baseURLString)/api/auth/token")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/x-www-form-urlencoded", forHTTPHeaderField: "Content-Type")
        
        let body = "username=\(username)&password=\(password)"
        request.httpBody = body.data(using: .utf8)
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        if httpResponse.statusCode != 200 {
            let errorData = ErrorHandler.parseServerError(data: data, statusCode: httpResponse.statusCode)
            throw errorData
        }
        
        return try JSONDecoder().decode(TokenResponse.self, from: data)
    }
    
    func register(user: RegisterRequest) async throws -> UserResponse {
        let url = URL(string: "\(baseURLString)/api/auth/register")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let jsonData = try JSONEncoder().encode(user)
        request.httpBody = jsonData
        
        print("📡 APIClient: Sending registration request to \(url)")
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            print("❌ APIClient: Register - Invalid HTTP response.")
            throw APIError.invalidResponse
        }
        
        print("📡 APIClient: Register response status code: \(httpResponse.statusCode)")
        if httpResponse.statusCode != 201 && httpResponse.statusCode != 200 { // Accept both 201 and 200 as success
            let errorData = ErrorHandler.parseServerError(data: data, statusCode: httpResponse.statusCode)
            print("❌ APIClient: Register failed with status \(httpResponse.statusCode). Error: \(errorData)")
            throw errorData
        }
        
        let decodedResponse = try JSONDecoder().decode(UserResponse.self, from: data)
        print("✅ APIClient: Registration successful. UserResponse received: \(decodedResponse)")
        return decodedResponse
    }
    func getUserProfile(token: String) async throws -> UserResponse {
        let url = URL(string: "\(baseURLString)/api/auth/me")!
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        if httpResponse.statusCode != 200 {
            let errorData = ErrorHandler.parseServerError(data: data, statusCode: httpResponse.statusCode)
            throw errorData
        }
        
        return try JSONDecoder().decode(UserResponse.self, from: data)
    }
    
    func deleteAccount(confirmation: AccountDeletionRequest, token: String) async throws -> DeletionSummary? {
        let url = URL(string: "\(baseURLString)/api/auth/delete-account")!
        var request = URLRequest(url: url)
        request.httpMethod = "DELETE"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let jsonData = try JSONEncoder().encode(confirmation)
        request.httpBody = jsonData
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        if httpResponse.statusCode != 200 {
            let errorData = ErrorHandler.parseServerError(data: data, statusCode: httpResponse.statusCode)
            throw errorData
        }
        
        // If data is empty, just return nil
        if data.isEmpty {
            return nil
        }
        return try? JSONDecoder().decode(DeletionSummary.self, from: data)
    }
    
    // MARK: - Comic Generation & Management
    func generateComicWithData(request: ComicSaveRequest, token: String) async throws -> ComicGenerationResponse {
        let url = URL(string: "\(baseURLString)/api/chats/generate-comic-with-data")!
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let jsonData = try JSONEncoder().encode(request)
        urlRequest.httpBody = jsonData
        
        let (data, response) = try await session.data(for: urlRequest)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        if httpResponse.statusCode != 200 {
            let errorData = ErrorHandler.parseServerError(data: data, statusCode: httpResponse.statusCode)
            throw errorData
        }
        
        return try JSONDecoder().decode(ComicGenerationResponse.self, from: data)
    }
    
    func generateComicImage(request: ComicGenerationRequest, token: String) async throws -> Data {
        let url = URL(string: "\(baseURLString)/api/chats/generate-comic")!
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let jsonData = try JSONEncoder().encode(request)
        urlRequest.httpBody = jsonData
        
        let (data, response) = try await session.data(for: urlRequest)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        if httpResponse.statusCode != 200 {
            throw APIError.serverError(httpResponse.statusCode)
        }
        
        return data
    }
    
    func getMyComics(
        token: String,
        limit: Int = 20,
        offset: Int = 0,
        genre: String? = nil,
        artStyle: String? = nil,
        isFavorite: Bool? = nil
    ) async throws -> [ComicListResponse] {
        var urlComponents = URLComponents(string: "\(baseURLString)/api/chats/my-comics")!
        
        var queryItems: [URLQueryItem] = [
            URLQueryItem(name: "limit", value: String(limit)),
            URLQueryItem(name: "offset", value: String(offset))
        ]
        
        if let genre = genre {
            queryItems.append(URLQueryItem(name: "genre", value: genre))
        }
        if let artStyle = artStyle {
            queryItems.append(URLQueryItem(name: "art_style", value: artStyle))
        }
        if let isFavorite = isFavorite {
            queryItems.append(URLQueryItem(name: "is_favorite", value: String(isFavorite)))
        }
        
        urlComponents.queryItems = queryItems
        
        var request = URLRequest(url: urlComponents.url!)
        request.httpMethod = "GET"
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        if httpResponse.statusCode != 200 {
            let errorData = ErrorHandler.parseServerError(data: data, statusCode: httpResponse.statusCode)
            throw errorData
        }
        
        return try JSONDecoder().decode([ComicListResponse].self, from: data)
    }
    
    func getComic(id: Int, token: String) async throws -> ComicResponse {
        let url = URL(string: "\(baseURLString)/api/chats/comic/\(id)")!
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        if httpResponse.statusCode != 200 {
            let errorData = ErrorHandler.parseServerError(data: data, statusCode: httpResponse.statusCode)
            throw errorData
        }
        
        return try JSONDecoder().decode(ComicResponse.self, from: data)
    }
    
    func updateComic(id: Int, updates: ComicUpdateRequest, token: String) async throws -> ComicResponse {
        let url = URL(string: "\(baseURLString)/api/chats/comic/\(id)")!
        var request = URLRequest(url: url)
        request.httpMethod = "PUT"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let jsonData = try JSONEncoder().encode(updates)
        request.httpBody = jsonData
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        if httpResponse.statusCode != 200 {
            let errorData = ErrorHandler.parseServerError(data: data, statusCode: httpResponse.statusCode)
            throw errorData
        }
        
        return try JSONDecoder().decode(ComicResponse.self, from: data)
    }
    
    func deleteComic(id: Int, token: String) async throws -> SuccessResponse {
        let url = URL(string: "\(baseURLString)/api/chats/comic/\(id)")!
        var request = URLRequest(url: url)
        request.httpMethod = "DELETE"
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        if httpResponse.statusCode != 200 {
            let errorData = ErrorHandler.parseServerError(data: data, statusCode: httpResponse.statusCode)
            throw errorData
        }
        
        return try JSONDecoder().decode(SuccessResponse.self, from: data)
    }
    
    func getPublicComics(
        limit: Int = 20,
        offset: Int = 0,
        genre: String? = nil,
        artStyle: String? = nil
    ) async throws -> [ComicListResponse] {
        var urlComponents = URLComponents(string: "\(baseURLString)/api/chats/public-comics")!
        
        var queryItems: [URLQueryItem] = [
            URLQueryItem(name: "limit", value: String(limit)),
            URLQueryItem(name: "offset", value: String(offset))
        ]
        
        if let genre = genre {
            queryItems.append(URLQueryItem(name: "genre", value: genre))
        }
        if let artStyle = artStyle {
            queryItems.append(URLQueryItem(name: "art_style", value: artStyle))
        }
        
        urlComponents.queryItems = queryItems
        
        let request = URLRequest(url: urlComponents.url!)
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        if httpResponse.statusCode != 200 {
            throw APIError.serverError(httpResponse.statusCode)
        }
        
        return try JSONDecoder().decode([ComicListResponse].self, from: data)
    }
    
    // MARK: - Image Generation
    func generateImage(prompt: String) async throws -> Data {
        guard let token = await getToken() else {
            throw APIError.unauthorized
        }
        
        let request = ImageRequest(prompt: prompt)
        let requestData = try JSONEncoder().encode(request)
        
        var urlRequest = URLRequest(url: baseURL.appendingPathComponent("api/chats/generate-image", conformingTo: .url))
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        urlRequest.httpBody = requestData
        
        print("🖼️ Image Generation Request URL: \(urlRequest.url?.absoluteString ?? "nil")")
        print("🖼️ Request prompt: '\(prompt)'")
        
        let (data, response) = try await session.data(for: urlRequest)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        print("🖼️ Image Generation Response Status: \(httpResponse.statusCode)")
        
        if httpResponse.statusCode == 401 {
            throw APIError.unauthorized
        }
        
        guard httpResponse.statusCode == 200 else {
            let errorString = String(data: data, encoding: .utf8) ?? "Unknown error"
            print("❌ Image Generation Error: \(errorString)")
            throw APIError.serverErrorMessage(errorString)
        }
        
        print("✅ Successfully generated image, data size: \(data.count) bytes")
        return data
    }
    
    func generateImageAsBase64(prompt: String) async throws -> String {
        let imageData = try await generateImage(prompt: prompt)
        let base64String = imageData.base64EncodedString()
        print("✅ Converted image to base64, length: \(base64String.count)")
        return base64String
    }
    
    // MARK: - World System
    func getWorldComics(request: WorldComicsRequest, token: String) async throws -> [ComicGenerationResponse] {
        let url = URL(string: "\(baseURLString)/api/chats/world-comics")!
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let jsonData = try JSONEncoder().encode(request)
        urlRequest.httpBody = jsonData
        
        let (data, response) = try await session.data(for: urlRequest)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        if httpResponse.statusCode != 200 {
            let errorData = ErrorHandler.parseServerError(data: data, statusCode: httpResponse.statusCode)
            throw errorData
        }
        
        return try JSONDecoder().decode([ComicGenerationResponse].self, from: data)
    }
    
    func getWorldStats(worldType: WorldType, token: String) async throws -> WorldStatsResponse {
        let url = URL(string: "\(baseURLString)/api/chats/world-stats/\(worldType.rawValue)")!
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        if httpResponse.statusCode != 200 {
            let errorData = ErrorHandler.parseServerError(data: data, statusCode: httpResponse.statusCode)
            throw errorData
        }
        
        return try JSONDecoder().decode(WorldStatsResponse.self, from: data)
    }
    
    // MARK: - Collections
    func createCollection(request: ComicCollectionRequest, token: String) async throws -> ComicCollectionResponse {
        let url = URL(string: "\(baseURLString)/api/collections")!
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let jsonData = try JSONEncoder().encode(request)
        urlRequest.httpBody = jsonData
        
        let (data, response) = try await session.data(for: urlRequest)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        if httpResponse.statusCode != 200 {
            let errorData = ErrorHandler.parseServerError(data: data, statusCode: httpResponse.statusCode)
            throw errorData
        }
        
        return try JSONDecoder().decode(ComicCollectionResponse.self, from: data)
    }
    
    func getWorldCollections(worldType: WorldType, token: String) async throws -> [ComicCollectionResponse] {
        let url = URL(string: "\(baseURLString)/api/chats/collections/\(worldType.rawValue)")!
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        if httpResponse.statusCode != 200 {
            let errorData = ErrorHandler.parseServerError(data: data, statusCode: httpResponse.statusCode)
            throw errorData
        }
        
        return try JSONDecoder().decode([ComicCollectionResponse].self, from: data)
    }
    
    func addComicToCollection(collectionId: Int, comicId: Int, token: String) async throws -> SuccessResponse {
        let url = URL(string: "\(baseURLString)/api/collections/\(collectionId)/comics/\(comicId)")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        if httpResponse.statusCode != 200 {
            let errorData = ErrorHandler.parseServerError(data: data, statusCode: httpResponse.statusCode)
            throw errorData
        }
        
        return try JSONDecoder().decode(SuccessResponse.self, from: data)
    }
    
    // MARK: - Scenarios
    func saveScenario(request: ScenarioSaveRequest, token: String) async throws -> ScenarioSaveResponse {
        let url = URL(string: "\(baseURLString)/api/chats/scenarios")!
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let jsonData = try JSONEncoder().encode(request)
        urlRequest.httpBody = jsonData
        
        let (data, response) = try await session.data(for: urlRequest)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        if httpResponse.statusCode != 200 {
            let errorData = ErrorHandler.parseServerError(data: data, statusCode: httpResponse.statusCode)
            throw errorData
        }
        
        return try JSONDecoder().decode(ScenarioSaveResponse.self, from: data)
    }
    
    func getScenarioByComic(comicId: Int, token: String) async throws -> String {
        print("[getScenarioByComic] Step 1: Input comicId = \(comicId)")
        let (data, response) = try await rawScenarioByComic(comicId: comicId, token: token)
        print("[getScenarioByComic] Step 2: rawScenarioByComic call complete")
        guard let httpResponse = response as? HTTPURLResponse else {
            print("[getScenarioByComic] Error: Invalid response")
            throw APIError.invalidResponse
        }
        if httpResponse.statusCode != 200 {
            print("[getScenarioByComic] Error: Server error \(httpResponse.statusCode)")
            let errorData = ErrorHandler.parseServerError(data: data, statusCode: httpResponse.statusCode)
            throw errorData
        }
        guard let json = try? JSONSerialization.jsonObject(with: data, options: []) as? [String: Any],
              let scenarioDataString = json["scenario_data"] as? String else {
            print("[getScenarioByComic] Error: scenario_data field not found in response")
            throw APIError.serverErrorMessage("scenario_data field not found in response")
        }
        print("[getScenarioByComic] Step 3: scenario_data extracted successfully.")
        // Parse scenario_data as JSON and extract 'premise'
        if let scenarioDataJson = scenarioDataString.data(using: .utf8),
           let scenarioDict = try? JSONSerialization.jsonObject(with: scenarioDataJson, options: []) as? [String: Any],
           let premise = scenarioDict["premise"] as? String {
            print("[getScenarioByComic] Step 4: premise extracted: \(premise)")
            return premise
        } else {
            print("[getScenarioByComic] Error: premise field not found in scenario_data")
            throw APIError.serverErrorMessage("premise field not found in scenario_data")
        }
    }
    func getUserScenarios(limit: Int, offset: Int, token: String) async throws -> [DetailedScenario] {
        var urlComponents = URLComponents(string: "\(baseURLString)/api/chats/scenarios")!
        urlComponents.queryItems = [
            URLQueryItem(name: "limit", value: String(limit)),
            URLQueryItem(name: "offset", value: String(offset))
        ]
        
        var request = URLRequest(url: urlComponents.url!)
        request.httpMethod = "GET"
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        if httpResponse.statusCode != 200 {
            let errorData = ErrorHandler.parseServerError(data: data, statusCode: httpResponse.statusCode)
            throw errorData
        }
        
        return try JSONDecoder().decode([DetailedScenario].self, from: data)
    }
    
    // MARK: - Testing (No Auth Required)
    func testGenerateComic(request: ComicRequest) async throws -> Data {
        let url = URL(string: "\(baseURLString)/api/test/generate-comic")!
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let jsonData = try JSONEncoder().encode(request)
        urlRequest.httpBody = jsonData
        
        let (data, response) = try await session.data(for: urlRequest)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        if httpResponse.statusCode != 200 {
            let errorData = ErrorHandler.parseServerError(data: data, statusCode: httpResponse.statusCode)
            throw errorData
        }
        
        return data
    }
    
    func testHealth() async throws -> HealthResponse {
        let url = URL(string: "\(baseURLString)/api/test/health")!
        let (data, response) = try await session.data(from: url)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        if httpResponse.statusCode != 200 {
            let errorData = ErrorHandler.parseServerError(data: data, statusCode: httpResponse.statusCode)
            throw errorData
        }
        
        return try JSONDecoder().decode(HealthResponse.self, from: data)
    }
    
    // MARK: - Utility
    func getAvailableGenres() async throws -> [String] {
        let url = URL(string: "\(baseURLString)/api/utils/genres")!
        let (data, response) = try await session.data(from: url)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        if httpResponse.statusCode != 200 {
            let errorData = ErrorHandler.parseServerError(data: data, statusCode: httpResponse.statusCode)
            throw errorData
        }
        
        return try JSONDecoder().decode([String].self, from: data)
    }
    
    func getAvailableArtStyles() async throws -> [String] {
        let url = URL(string: "\(baseURLString)/api/utils/art-styles")!
        let (data, response) = try await session.data(from: url)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        if httpResponse.statusCode != 200 {
            let errorData = ErrorHandler.parseServerError(data: data, statusCode: httpResponse.statusCode)
            throw errorData
        }
        
        return try JSONDecoder().decode([String].self, from: data)
    }
    
    // MARK: - Storage Integration
    func uploadToStorage(request: StorageUploadRequest, token: String) async throws -> StorageUploadResponse {
        let url = URL(string: "\(baseURLString)/api/storage/upload")!
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let jsonData = try JSONEncoder().encode(request)
        urlRequest.httpBody = jsonData
        
        let (data, response) = try await session.data(for: urlRequest)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        if httpResponse.statusCode != 200 {
            let errorData = ErrorHandler.parseServerError(data: data, statusCode: httpResponse.statusCode)
            throw errorData
        }
        
        return try JSONDecoder().decode(StorageUploadResponse.self, from: data)
    }
    
    func downloadFromStorage(url: String, token: String) async throws -> Data {
        guard let downloadURL = URL(string: url) else {
            throw APIError.invalidURL
        }
        
        var request = URLRequest(url: downloadURL)
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        if httpResponse.statusCode != 200 {
            let errorData = ErrorHandler.parseServerError(data: data, statusCode: httpResponse.statusCode)
            throw errorData
        }
        
        return data
    }
    
    func deleteFromStorage(url: String, token: String) async throws {
        let deleteURL = URL(string: "\(baseURLString)/api/storage/delete")!
        var request = URLRequest(url: deleteURL)
        request.httpMethod = "DELETE"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let body = ["url": url]
        let jsonData = try JSONSerialization.data(withJSONObject: body)
        request.httpBody = jsonData
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        if httpResponse.statusCode != 200 {
            let errorData = ErrorHandler.parseServerError(data: data, statusCode: httpResponse.statusCode)
            throw errorData
        }
    }
    
    func getStorageUsage(token: String) async throws -> StorageUsage {
        let url = URL(string: "\(baseURLString)/api/storage/usage")!
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        if httpResponse.statusCode != 200 {
            let errorData = ErrorHandler.parseServerError(data: data, statusCode: httpResponse.statusCode)
            throw errorData
        }
        
        return try JSONDecoder().decode(StorageUsage.self, from: data)
    }
    
    func cleanupStorage(token: String) async throws -> StorageCleanupResult {
        let url = URL(string: "\(baseURLString)/api/storage/cleanup")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        if httpResponse.statusCode != 200 {
            let errorData = ErrorHandler.parseServerError(data: data, statusCode: httpResponse.statusCode)
            throw errorData
        }
        
        return try JSONDecoder().decode(StorageCleanupResult.self, from: data)
    }
    
    func optimizeStorage(token: String) async throws -> StorageOptimizationResult {
        let url = URL(string: "\(baseURLString)/api/storage/optimize")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        if httpResponse.statusCode != 200 {
            let errorData = ErrorHandler.parseServerError(data: data, statusCode: httpResponse.statusCode)
            throw errorData
        }
        
        return try JSONDecoder().decode(StorageOptimizationResult.self, from: data)
    }
    
    // MARK: - File Upload and Download
    func uploadFile(request: StorageUploadRequest, token: String) async throws -> StorageUploadResponse {
        let url = URL(string: "\(baseURLString)/api/storage/upload")!
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let jsonData = try JSONEncoder().encode(request)
        urlRequest.httpBody = jsonData
        
        let (data, response) = try await session.data(for: urlRequest)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        if httpResponse.statusCode != 200 {
            let errorData = ErrorHandler.parseServerError(data: data, statusCode: httpResponse.statusCode)
            throw errorData
        }
        
        return try JSONDecoder().decode(StorageUploadResponse.self, from: data)
    }
    
    func downloadFile(url: String, token: String) async throws -> Data {
        guard let downloadURL = URL(string: url) else {
            throw APIError.invalidURL
        }
        
        var request = URLRequest(url: downloadURL)
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        if httpResponse.statusCode != 200 {
            let errorData = ErrorHandler.parseServerError(data: data, statusCode: httpResponse.statusCode)
            throw errorData
        }
        
        return data
    }
    
    func deleteFile(url: String, token: String) async throws {
        let url = URL(string: "\(baseURLString)/api/storage/delete")!
        var request = URLRequest(url: url)
        request.httpMethod = "DELETE"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let body = ["url": url]
        let jsonData = try JSONEncoder().encode(body)
        request.httpBody = jsonData
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        if httpResponse.statusCode != 200 {
            let errorData = ErrorHandler.parseServerError(data: data, statusCode: httpResponse.statusCode)
            throw errorData
        }
    }
    
    func deleteFiles(comicId: Int, token: String) async throws {
        let url = URL(string: "\(baseURLString)/api/storage/delete-comic-files")!
        var request = URLRequest(url: url)
        request.httpMethod = "DELETE"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let body = ["comic_id": comicId]
        let jsonData = try JSONEncoder().encode(body)
        request.httpBody = jsonData
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        if httpResponse.statusCode != 200 {
            let errorData = ErrorHandler.parseServerError(data: data, statusCode: httpResponse.statusCode)
            throw errorData
        }
    }
    
    // MARK: - Legacy Methods (for backwards compatibility)
    func generateScenario(message: String) async throws -> ScenarioResponse {
        guard let token = await getToken() else {
            throw APIError.unauthorized
        }
        
        let url = URL(string: "\(baseURLString)/api/chats/scenario/")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let body = ["message": message]
        let jsonData = try JSONEncoder().encode(body)
        request.httpBody = jsonData
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        if httpResponse.statusCode != 200 {
            let errorString = String(data: data, encoding: .utf8) ?? "Unknown error"
            throw APIError.serverError(httpResponse.statusCode)
        }
        
        return try JSONDecoder().decode(ScenarioResponse.self, from: data)
    }
    
    func healthCheck() async throws -> HealthResponse {
        let url = URL(string: "\(baseURLString)/health")!
        let (data, response) = try await session.data(from: url)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        if httpResponse.statusCode != 200 {
            throw APIError.serverError(httpResponse.statusCode)
        }
        
        return try JSONDecoder().decode(HealthResponse.self, from: data)
    }
    
    func getIOSConfig() async throws -> IOSConfigResponse {
        let url = URL(string: "\(baseURLString)/api/ios/config")!
        let (data, response) = try await session.data(from: url)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        if httpResponse.statusCode != 200 {
            throw APIError.serverError(httpResponse.statusCode)
        }
        
        return try JSONDecoder().decode(IOSConfigResponse.self, from: data)
    }
    
    func getWorldPreferences(worldType: WorldType, token: String) async throws -> WorldPreferences {
        let url = URL(string: "\(baseURLString)/api/chats/world-preferences/\(worldType.rawValue)")!
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        if httpResponse.statusCode != 200 {
            let errorData = ErrorHandler.parseServerError(data: data, statusCode: httpResponse.statusCode)
            throw errorData
        }
        
        return try JSONDecoder().decode(WorldPreferences.self, from: data)
    }
    
    // MARK: - Collection Management Methods
    func searchCollections(request: CollectionSearchRequest, token: String) async throws -> [ComicCollectionResponse] {
        let url = URL(string: "\(baseURLString)/api/collections/search")!
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let jsonData = try JSONEncoder().encode(request)
        urlRequest.httpBody = jsonData
        
        let (data, response) = try await session.data(for: urlRequest)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        if httpResponse.statusCode != 200 {
            let errorData = ErrorHandler.parseServerError(data: data, statusCode: httpResponse.statusCode)
            throw errorData
        }
        
        return try JSONDecoder().decode([ComicCollectionResponse].self, from: data)
    }
    
    func getCollectionStats(token: String) async throws -> CollectionStats {
        let url = URL(string: "\(baseURLString)/api/collections/stats")!
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        if httpResponse.statusCode != 200 {
            let errorData = ErrorHandler.parseServerError(data: data, statusCode: httpResponse.statusCode)
            throw errorData
        }
        
        return try JSONDecoder().decode(CollectionStats.self, from: data)
    }
    
    func updateCollection(id: Int, updates: CollectionUpdateRequest, token: String) async throws -> ComicCollectionResponse {
        let url = URL(string: "\(baseURLString)/api/collections/\(id)")!
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "PUT"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let jsonData = try JSONEncoder().encode(updates)
        urlRequest.httpBody = jsonData
        
        let (data, response) = try await session.data(for: urlRequest)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        if httpResponse.statusCode != 200 {
            let errorData = ErrorHandler.parseServerError(data: data, statusCode: httpResponse.statusCode)
            throw errorData
        }
        
        return try JSONDecoder().decode(ComicCollectionResponse.self, from: data)
    }
    
    func deleteCollection(id: Int, token: String) async throws {
        let url = URL(string: "\(baseURLString)/api/collections/\(id)")!
        var request = URLRequest(url: url)
        request.httpMethod = "DELETE"
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        if httpResponse.statusCode != 200 {
            let errorData = ErrorHandler.parseServerError(data: data, statusCode: httpResponse.statusCode)
            throw errorData
        }
    }
    
    func removeComicFromCollection(collectionId: Int, comicId: Int, token: String) async throws {
        let url = URL(string: "\(baseURLString)/api/collections/\(collectionId)/comics/\(comicId)")!
        var request = URLRequest(url: url)
        request.httpMethod = "DELETE"
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        if httpResponse.statusCode != 200 {
            let errorData = ErrorHandler.parseServerError(data: data, statusCode: httpResponse.statusCode)
            throw errorData
        }
    }
    
    func shareCollection(request: CollectionShareRequest, token: String) async throws -> CollectionShareResponse {
        let url = URL(string: "\(baseURLString)/api/collections/share")!
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let jsonData = try JSONEncoder().encode(request)
        urlRequest.httpBody = jsonData
        
        let (data, response) = try await session.data(for: urlRequest)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        if httpResponse.statusCode != 200 {
            let errorData = ErrorHandler.parseServerError(data: data, statusCode: httpResponse.statusCode)
            throw errorData
        }
        
        return try JSONDecoder().decode(CollectionShareResponse.self, from: data)
    }
}

// MARK: - API Client Extensions for Convenience
extension APIClient {
    /// Quick method to generate and save a comic in one call
    func createComic(
        title: String,
        concept: String,
        genre: String,
        artStyle: String,
        worldType: WorldType = .imaginationWorld,
        isFavorite: Bool = false,
        isPublic: Bool = false,
        token: String
    ) async throws -> ComicGenerationResponse {
        let request = ComicSaveRequest(
            title: title,
            concept: concept,
            genre: genre,
            artStyle: artStyle,
            worldType: worldType,
            includeDetailedScenario: false,
            imageBase64: nil,
            panelsData: nil,
            isFavorite: isFavorite,
            isPublic: isPublic
        )
        
        return try await generateComicWithData(request: request, token: token)
    }
    
    /// Toggle favorite status of a comic
    func toggleFavorite(comicId: Int, currentStatus: Bool, token: String) async throws -> ComicResponse {
        let updates = ComicUpdateRequest(title: nil, isFavorite: !currentStatus, isPublic: nil)
        return try await updateComic(id: comicId, updates: updates, token: token)
    }
    
    /// Toggle public status of a comic
    func togglePublic(comicId: Int, currentStatus: Bool, token: String) async throws -> ComicResponse {
        let updates = ComicUpdateRequest(title: nil, isFavorite: nil, isPublic: !currentStatus)
        return try await updateComic(id: comicId, updates: updates, token: token)
    }
    
    // MARK: - Missing World Methods
    func getWorldAnalytics(worldType: WorldType, token: String) async throws -> WorldAnalytics {
        let url = URL(string: "\(baseURLString)/api/chats/world-analytics/\(worldType.rawValue)")!
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        if httpResponse.statusCode != 200 {
            let errorData = ErrorHandler.parseServerError(data: data, statusCode: httpResponse.statusCode)
            throw errorData
        }
        
        return try JSONDecoder().decode(WorldAnalytics.self, from: data)
    }
    
    func saveWorldPreferences(_ preferences: WorldPreferences, token: String) async throws {
        let url = URL(string: "\(baseURLString)/api/chats/world-preferences")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let jsonData = try JSONEncoder().encode(preferences)
        request.httpBody = jsonData
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        if httpResponse.statusCode != 200 {
            let errorData = ErrorHandler.parseServerError(data: data, statusCode: httpResponse.statusCode)
            throw errorData
        }
    }
} 
extension APIClient {
    func rawScenarioByComic(comicId: Int, token: String) async throws -> (Data, URLResponse) {
        let url = URL(string: "\(baseURLString)/api/chats/scenarios/comic/\(comicId)")!
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        let (data, response) = try await URLSession.shared.data(for: request)
        return (data, response)
    }
}
