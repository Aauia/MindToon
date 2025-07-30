import Foundation

// Comic Recommendation Models
struct ComicRecommendation: Codable {
    let title: String
    let concept: String
    let suggestedAuthor: String
    let recommendedPlatform: String
    let genre: String
    let artStyle: String
    let mainCharacter: String
    let setting: String
    let plotSummary: String
    let uniqueElements: [String]
    let confidenceScore: Double
    let reasoning: String
    let similarToUserPatterns: [String]
    
    enum CodingKeys: String, CodingKey {
        case title
        case concept
        case suggestedAuthor = "suggested_author"
        case recommendedPlatform = "recommended_platform"
        case genre
        case artStyle = "art_style"
        case mainCharacter = "main_character"
        case setting
        case plotSummary = "plot_summary"
        case uniqueElements = "unique_elements"
        case confidenceScore = "confidence_score"
        case reasoning
        case similarToUserPatterns = "similar_to_user_patterns"
    }
}

struct ComicRecommendationsResponse: Codable {
    let userId: Int
    let recommendations: [ComicRecommendation]
    let totalRecommendations: Int
    
    enum CodingKeys: String, CodingKey {
        case userId = "user_id"
        case recommendations
        case totalRecommendations = "total_recommendations"
    }
}

class AnalyticsService {
    static let shared = AnalyticsService()
    private let baseURL = "https://mindtoon.space" // Update as needed

    /// Fetch comic recommendations (per world or cross-world)
    func fetchComicRecommendations(userId: Int, world: String? = nil, limit: Int = 5, completion: @escaping (Result<ComicRecommendationsResponse, Error>) -> Void) {
        var urlString: String
        if let world = world {
            // Use hyphen for world names
            let worldPath = world.replacingOccurrences(of: "_", with: "-")
            urlString = "\(baseURL)/api/analytics/comic-recommendations/\(worldPath)/\(userId)?limit=\(limit)"
        } else {
            urlString = "\(baseURL)/api/analytics/comic-recommendations/\(userId)?limit=\(limit)"
        }
        fetch(urlString: urlString, method: "POST", completion: completion)
    }

    /// Fetch weekly insight
    func fetchWeeklyInsight(userId: Int, completion: @escaping (Result<WeeklyInsight, Error>) -> Void) {
        // Use correct backend route
        let urlString = "\(baseURL)/api/analytics/insights/weekly/\(userId)"
        fetch(urlString: urlString, method: "GET", completion: completion)
    }
    
    /// Fetch insight by period (weekly, monthly, all_time)
    func fetchInsightByPeriod(userId: Int, period: String, completion: @escaping (Result<WeeklyInsight, Error>) -> Void) {
        let urlString = "\(baseURL)/api/analytics/insights/\(userId)?period=\(period)"
        fetch(urlString: urlString, method: "GET", completion: completion)
    }

    /// Fetch analytics summary (optionally for a specific world)
    func fetchSummary(userId: Int, world: String? = nil, completion: @escaping (Result<AnalyticsSummary, Error>) -> Void) {
        var urlString = "\(baseURL)/api/analytics/summary/\(userId)"
        if let world = world {
            urlString += "?world_type=\(world)"
        }
        fetch(urlString: urlString, method: "GET", completion: completion)
    }

    /// Fetch all insights (optionally by type)
    func fetchInsights(userId: Int, insightType: String? = nil, completion: @escaping (Result<[InsightResponse], Error>) -> Void) {
        var urlString = "\(baseURL)/api/analytics/insights/\(userId)"
        if let insightType = insightType {
            urlString += "?insight_type=\(insightType)"
        }
        fetch(urlString: urlString, method: "GET", completion: completion)
    }

    /// Generic fetch helper for all analytics endpoints
    private func fetch<T: Decodable>(urlString: String, method: String = "GET", completion: @escaping (Result<T, Error>) -> Void) {
        guard let url = URL(string: urlString) else {
            print("❌ [AnalyticsService] Invalid URL: \(urlString)")
            completion(.failure(NSError(domain: "Invalid URL", code: 0)))
            return
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = method
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let task = URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                print("❌ [AnalyticsService] Network error for \(urlString): \(error.localizedDescription)")
                completion(.failure(error))
                return
            }
            guard let data = data else {
                print("❌ [AnalyticsService] No data received for \(urlString)")
                completion(.failure(NSError(domain: "No data", code: 0)))
                return
            }
            // Print the raw response for debugging
            if let rawString = String(data: data, encoding: .utf8) {
                print("📦 [AnalyticsService] Raw response for \(urlString):\n\(rawString)")
            }
            // Check for backend error response with 'detail' key
            if let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
               let detail = json["detail"] as? String {
                print("❌ [AnalyticsService] Backend error for \(urlString): \(detail)")
                completion(.failure(NSError(domain: "Backend error", code: 0, userInfo: [NSLocalizedDescriptionKey: detail])))
                return
            }
            do {
                let decoded = try JSONDecoder().decode(T.self, from: data)
                completion(.success(decoded))
            } catch {
                print("❌ [AnalyticsService] Decoding error for \(urlString): \(error)")
                if let rawString = String(data: data, encoding: .utf8) {
                    print("❌ [AnalyticsService] Raw data that failed to decode:\n\(rawString)")
                }
                completion(.failure(error))
            }
        }
        task.resume()
    }
}
