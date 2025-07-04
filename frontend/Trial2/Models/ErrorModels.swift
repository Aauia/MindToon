import Foundation

// MARK: - API Error Enum
enum APIError: Error, LocalizedError {
    case invalidURL
    case invalidResponse
    case unauthorized
    case forbidden
    case notFound
    case serverError(Int)
    case serverErrorMessage(String)
    case decodingError(Error)
    case networkError(Error)
    case supabaseError(String)
    case worldNotFound
    case collectionError(String)
    case scenarioError(String)
    case validationError([String])
    case rateLimitExceeded
    case storageQuotaExceeded
    case comicGenerationFailed(String)
    case tokenExpired
    case accountDeleted
    case featureNotAvailable
    
    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "Invalid URL provided"
        case .invalidResponse:
            return "Invalid response from server"
        case .unauthorized:
            return "Please log in to continue"
        case .forbidden:
            return "You don't have permission to perform this action"
        case .notFound:
            return "The requested resource was not found"
        case .serverError(let code):
            return "Server error: \(code)"
        case .serverErrorMessage(let message):
            return message
        case .decodingError(let error):
            return "Data parsing error: \(error.localizedDescription)"
        case .networkError(let error):
            return "Network error: \(error.localizedDescription)"
        case .supabaseError(let message):
            return "Storage error: \(message)"
        case .worldNotFound:
            return "World not found"
        case .collectionError(let message):
            return "Collection error: \(message)"
        case .scenarioError(let message):
            return "Scenario error: \(message)"
        case .validationError(let errors):
            return "Validation errors: \(errors.joined(separator: ", "))"
        case .rateLimitExceeded:
            return "Too many requests. Please try again later."
        case .storageQuotaExceeded:
            return "Storage quota exceeded. Please delete some comics to free up space."
        case .comicGenerationFailed(let message):
            return "Comic generation failed: \(message)"
        case .tokenExpired:
            return "Your session has expired. Please log in again."
        case .accountDeleted:
            return "This account has been deleted"
        case .featureNotAvailable:
            return "This feature is not available"
        }
    }
    
    var userFriendlyMessage: String {
        switch self {
        case .invalidURL, .invalidResponse, .decodingError:
            return "Something went wrong. Please try again."
        case .unauthorized:
            return "Please log in to continue"
        case .forbidden:
            return "You don't have permission to perform this action"
        case .notFound:
            return "The requested item was not found"
        case .serverError(let code):
            return code >= 500 ? "Server is temporarily unavailable. Please try again later." : "Something went wrong. Please try again."
        case .serverErrorMessage(let message):
            return message
        case .networkError:
            return "Please check your internet connection and try again"
        case .supabaseError:
            return "Storage error occurred. Please try again."
        case .worldNotFound:
            return "World not found"
        case .collectionError(let message):
            return "Collection error: \(message)"
        case .scenarioError(let message):
            return "Scenario error: \(message)"
        case .validationError(let errors):
            return "Please fix the following: \(errors.joined(separator: ", "))"
        case .rateLimitExceeded:
            return "Too many requests. Please wait a moment and try again."
        case .storageQuotaExceeded:
            return "Storage quota exceeded. Please delete some comics to free up space."
        case .comicGenerationFailed(let message):
            return "Comic generation failed: \(message)"
        case .tokenExpired:
            return "Your session has expired. Please log in again."
        case .accountDeleted:
            return "This account has been deleted"
        case .featureNotAvailable:
            return "This feature is not available"
        }
    }
    
    var errorCode: String {
        switch self {
        case .invalidURL: return "INVALID_URL"
        case .invalidResponse: return "INVALID_RESPONSE"
        case .unauthorized: return "UNAUTHORIZED"
        case .forbidden: return "FORBIDDEN"
        case .notFound: return "NOT_FOUND"
        case .serverError(let code): return "SERVER_ERROR_\(code)"
        case .serverErrorMessage: return "SERVER_ERROR_MESSAGE"
        case .decodingError: return "DECODING_ERROR"
        case .networkError: return "NETWORK_ERROR"
        case .supabaseError: return "SUPABASE_ERROR"
        case .worldNotFound: return "WORLD_NOT_FOUND"
        case .collectionError: return "COLLECTION_ERROR"
        case .scenarioError: return "SCENARIO_ERROR"
        case .validationError: return "VALIDATION_ERROR"
        case .rateLimitExceeded: return "RATE_LIMIT_EXCEEDED"
        case .storageQuotaExceeded: return "STORAGE_QUOTA_EXCEEDED"
        case .comicGenerationFailed: return "COMIC_GENERATION_FAILED"
        case .tokenExpired: return "TOKEN_EXPIRED"
        case .accountDeleted: return "ACCOUNT_DELETED"
        case .featureNotAvailable: return "FEATURE_NOT_AVAILABLE"
        }
    }
    
    var isRetryable: Bool {
        switch self {
        case .networkError:
            return true
        case .serverError(let code):
            return code >= 500
        case .rateLimitExceeded:
            return true
        default:
            return false
        }
    }
}

// MARK: - Error Response Models
struct ErrorResponse: Codable {
    let error: String
    let message: String
    let statusCode: Int?
    let details: [String]?
    let timestamp: String?
    
    enum CodingKeys: String, CodingKey {
        case error, message, details, timestamp
        case statusCode = "status_code"
    }
}

struct ValidationErrorResponse: Codable {
    let error: String
    let message: String
    let validationErrors: [ValidationError]
    
    enum CodingKeys: String, CodingKey {
        case error, message
        case validationErrors = "validation_errors"
    }
}

struct ValidationError: Codable {
    let field: String
    let message: String
    let code: String?
    
    enum CodingKeys: String, CodingKey {
        case field, message, code
    }
}

struct APISuccessResponse: Codable {
    let success: Bool
    let message: String
    let data: [String: String]?
    
    enum CodingKeys: String, CodingKey {
        case success, message, data
    }
}

// MARK: - Error Handler Utility
struct ErrorHandler {
    static func parseServerError(data: Data, statusCode: Int) -> APIError {
        // Try to decode as ValidationErrorResponse first
        if let validationResponse = try? JSONDecoder().decode(ValidationErrorResponse.self, from: data) {
            let errorMessages = validationResponse.validationErrors.map { "\($0.field): \($0.message)" }
            return .validationError(errorMessages)
        }
        
        // Try to decode as ErrorResponse
        if let errorResponse = try? JSONDecoder().decode(ErrorResponse.self, from: data) {
            return .serverErrorMessage(errorResponse.message)
        }
        
        // Try to extract error message from raw data
        if let jsonData = try? JSONSerialization.jsonObject(with: data, options: []) as? [String: Any] {
            if let detail = jsonData["detail"] as? String {
                return .serverErrorMessage(detail)
            }
            if let message = jsonData["message"] as? String {
                return .serverErrorMessage(message)
            }
        }
        
        // Fallback to string parsing
        if let errorString = String(data: data, encoding: .utf8) {
            return .serverErrorMessage(errorString)
        }
        
        return .serverError(statusCode)
    }
    
    static func handleNetworkError(_ error: Error) -> APIError {
        if let urlError = error as? URLError {
            switch urlError.code {
            case .notConnectedToInternet, .networkConnectionLost:
                return .networkError(urlError)
            case .timedOut:
                return .networkError(urlError)
            case .cannotFindHost, .cannotConnectToHost:
                return .networkError(urlError)
            default:
                return .networkError(urlError)
            }
        }
        
        return .networkError(error)
    }
    
    static func logError(_ error: APIError, context: String) {
        ErrorLogger.shared.log(error, context: context)
    }
}

// MARK: - Error Logger (Legacy - keeping for compatibility)
class ErrorLogger {
    static let shared = ErrorLogger()
    
    private init() {}
    
    func log(_ error: APIError, context: String, userID: String? = nil) {
        let timestamp = Date().ISO8601Format()
        let errorCode = error.errorCode
        let description = error.errorDescription ?? "Unknown error"
        
        let logEntry = """
        [ERROR] \(timestamp)
        Context: \(context)
        Code: \(errorCode)
        Description: \(description)
        User: \(userID ?? "unknown")
        Retryable: \(error.isRetryable)
        ---
        """
        
        print("🔴 \(logEntry)")
        
        // In production, you might want to send this to a logging service
        // or store it locally for debugging
    }
    
    func log(_ error: Error, context: String, userID: String? = nil) {
        let apiError = error as? APIError ?? APIError.networkError(error)
        log(apiError, context: context, userID: userID)
    }
}

// MARK: - Error Recovery
struct ErrorRecovery {
    static func shouldRetry(_ error: APIError, attemptCount: Int) -> Bool {
        guard attemptCount < 3 else { return false }
        return error.isRetryable
    }
    
    static func retryDelay(for attemptCount: Int) -> Double {
        // Exponential backoff: 1s, 2s, 4s
        return pow(2.0, Double(attemptCount))
    }
}

// MARK: - Error Retry Logic
struct RetryConfiguration {
    let maxRetries: Int
    let baseDelay: TimeInterval
    let maxDelay: TimeInterval
    let backoffMultiplier: Double
    
    static let `default` = RetryConfiguration(
        maxRetries: 3,
        baseDelay: 1.0,
        maxDelay: 30.0,
        backoffMultiplier: 2.0
    )
    
    static let aggressive = RetryConfiguration(
        maxRetries: 5,
        baseDelay: 0.5,
        maxDelay: 60.0,
        backoffMultiplier: 1.5
    )
    
    static let conservative = RetryConfiguration(
        maxRetries: 2,
        baseDelay: 2.0,
        maxDelay: 15.0,
        backoffMultiplier: 3.0
    )
}

struct RetryHelper {
    static func execute<T>(
        operation: @escaping () async throws -> T,
        configuration: RetryConfiguration = .default,
        shouldRetry: @escaping (Error) -> Bool = { error in
            if let apiError = error as? APIError {
                return apiError.isRetryable
            }
            return false
        }
    ) async throws -> T {
        
        var lastError: Error?
        
        for attempt in 0..<configuration.maxRetries {
            do {
                return try await operation()
            } catch {
                lastError = error
                
                if !shouldRetry(error) || attempt == configuration.maxRetries - 1 {
                    throw error
                }
                
                let delay = min(
                    configuration.baseDelay * pow(configuration.backoffMultiplier, Double(attempt)),
                    configuration.maxDelay
                )
                
                print("🔄 Retrying operation in \(delay)s (attempt \(attempt + 1)/\(configuration.maxRetries))")
                try await Task.sleep(nanoseconds: UInt64(delay * 1_000_000_000))
            }
        }
        
        throw lastError ?? APIError.networkError(NSError(domain: "RetryHelper", code: -1, userInfo: [NSLocalizedDescriptionKey: "Max retries exceeded"]))
    }
}

// MARK: - Error Logging and Analytics
struct ErrorAnalytics {
    static let shared = ErrorAnalytics()
    
    private var errorLog: [ErrorLogEntry] = []
    private let maxLogEntries = 100
    
    struct ErrorLogEntry {
        let timestamp: Date
        let error: APIError
        let context: String?
        let userID: String?
        let sessionID: String
        
        init(error: APIError, context: String? = nil, userID: String? = nil) {
            self.timestamp = Date()
            self.error = error
            self.context = context
            self.userID = userID
            self.sessionID = UUID().uuidString
        }
    }
    
    mutating func log(_ error: APIError, context: String? = nil, userID: String? = nil) {
        let entry = ErrorLogEntry(error: error, context: context, userID: userID)
        
        // Add to in-memory log
        errorLog.append(entry)
        
        // Keep log size manageable
        if errorLog.count > maxLogEntries {
            errorLog.removeFirst(errorLog.count - maxLogEntries)
        }
        
        // Log to console
        ErrorHandler.logError(error, context: context ?? "Unknown")
        
        #if DEBUG
        print("📊 Error logged: \(entry.timestamp) - \(error.errorCode)")
        #endif
    }
    
    func getErrorLog() -> [ErrorLogEntry] {
        return errorLog
    }
    
    mutating func clearLog() {
        errorLog.removeAll()
    }
    
    func getErrorStats() -> ErrorStats {
        let totalErrors = errorLog.count
        let errorsByType = Dictionary(grouping: errorLog, by: { $0.error.errorCode })
            .mapValues { $0.count }
        
        let recentErrors = errorLog.filter { entry in
            entry.timestamp.timeIntervalSinceNow > -3600 // Last hour
        }.count
        
        return ErrorStats(
            totalErrors: totalErrors,
            recentErrors: recentErrors,
            errorsByType: errorsByType,
            lastError: errorLog.last?.error
        )
    }
}

struct ErrorStats {
    let totalErrors: Int
    let recentErrors: Int
    let errorsByType: [String: Int]
    let lastError: APIError?
}

// MARK: - User-Friendly Error Messages
extension APIError {
    var shouldShowRetryButton: Bool {
        return isRetryable
    }
    
    var shouldShowContactSupport: Bool {
        switch self {
        case .serverError, .supabaseError, .comicGenerationFailed:
            return true
        default:
            return false
        }
    }
}

// MARK: - Preview Data
#if DEBUG
extension ErrorResponse {
    static let preview = ErrorResponse(
        error: "validation_error",
        message: "The request contains invalid data",
        statusCode: 400,
        details: ["Title is required", "Genre must be selected"],
        timestamp: "2024-01-15T10:30:00Z"
    )
}

extension ErrorStats {
    static let preview = ErrorStats(
        totalErrors: 15,
        recentErrors: 3,
        errorsByType: [
            "NETWORK_ERROR": 8,
            "SERVER_ERROR_500": 4,
            "VALIDATION_ERROR": 2,
            "UNAUTHORIZED": 1
        ],
        lastError: .networkError(URLError(.notConnectedToInternet))
    )
}
#endif 
