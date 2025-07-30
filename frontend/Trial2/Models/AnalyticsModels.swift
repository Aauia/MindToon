import Foundation

struct PsychologicalProfile: Codable, Identifiable {
    var id: String { worldType }
    let worldType: String
    let dominantEmotionalTone: String
    let mostCommonGenres: [String]
    let recurringSymbols: [String]
    let typicalCharacterRole: String
    let psychologicalTheme: String
    let comicCount: Int
    
    enum CodingKeys: String, CodingKey {
        case worldType = "world_type"
        case dominantEmotionalTone = "dominant_emotional_tone"
        case mostCommonGenres = "most_common_genres"
        case recurringSymbols = "recurring_symbols"
        case typicalCharacterRole = "typical_character_role"
        case psychologicalTheme = "psychological_theme"
        case comicCount = "comic_count"
    }
}

struct CrossWorldAssumption: Codable {
    let userId: Int
    let analysisDate: String
    let worldProfiles: [String: PsychologicalProfile]
    let crossWorldPatterns: [String: String]
    let psychologicalAssumption: String
    let confidenceLevel: Double
    let recommendationAreas: [String]
    
    enum CodingKeys: String, CodingKey {
        case userId = "user_id"
        case analysisDate = "analysis_date"
        case worldProfiles = "world_profiles"
        case crossWorldPatterns = "cross_world_patterns"
        case psychologicalAssumption = "psychological_assumption"
        case confidenceLevel = "confidence_level"
        case recommendationAreas = "recommendation_areas"
    }
}

struct WeeklyInsight: Codable {
    let topGenres: [GenreStats]
    let topArtStyles: [ArtStyleStats]
    let worldDistribution: [WorldStats]
    let totalComics: Int
    let weekStart: String
    let weekEnd: String
    
    enum CodingKeys: String, CodingKey {
        case topGenres = "top_genres"
        case topArtStyles = "top_art_styles"
        case worldDistribution = "world_distribution"
        case totalComics = "total_comics"
        case weekStart = "week_start"
        case weekEnd = "week_end"
    }
}

struct GenreStats: Codable {
    let genre: String
    let count: Int
    let percentage: Double
}

struct ArtStyleStats: Codable {
    let artStyle: String
    let count: Int
    let percentage: Double
    
    enum CodingKeys: String, CodingKey {
        case artStyle = "art_style"
        case count, percentage
    }
}

struct WorldStats: Codable {
    let worldType: String
    let count: Int
    let percentage: Double
    
    enum CodingKeys: String, CodingKey {
        case worldType = "world_type"
        case count, percentage
    }
}

struct AnalyticsSummary: Codable {
    let totalEntries: Int
    let genreDistribution: [GenreStats]
    let artStyleDistribution: [ArtStyleStats]
    let worldDistribution: [WorldStats]
    let timeSeries: [TimeSeriesData]
    let recentPrompts: [String]
    let insightsAvailable: Bool
}

struct TimeSeriesData: Codable {
    let date: String
    let count: Int
    let genres: [String]
    let artStyles: [String]
}

struct InsightResponse: Codable {
    let success: Bool
    let insightType: String
    let title: String
    let description: String
    let data: [String: SafeCodableValue]
    let createdAt: String
}

/// Type-erased JSON wrapper for heterogeneous values
enum SafeCodableValue: Codable {
    case int(Int)
    case double(Double)
    case bool(Bool)
    case string(String)
    case array([SafeCodableValue])
    case dictionary([String: SafeCodableValue])
    case null

    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()

        if container.decodeNil() {
            self = .null
        } else if let value = try? container.decode(Int.self) {
            self = .int(value)
        } else if let value = try? container.decode(Double.self) {
            self = .double(value)
        } else if let value = try? container.decode(Bool.self) {
            self = .bool(value)
        } else if let value = try? container.decode(String.self) {
            self = .string(value)
        } else if let value = try? container.decode([SafeCodableValue].self) {
            self = .array(value)
        } else if let value = try? container.decode([String: SafeCodableValue].self) {
            self = .dictionary(value)
        } else {
            throw DecodingError.dataCorruptedError(
                in: container,
                debugDescription: "Unable to decode SafeCodableValue"
            )
        }
    }

    func encode(to encoder: Encoder) throws {
        var container = encoder.singleValueContainer()

        switch self {
        case .int(let value):
            try container.encode(value)
        case .double(let value):
            try container.encode(value)
        case .bool(let value):
            try container.encode(value)
        case .string(let value):
            try container.encode(value)
        case .array(let value):
            try container.encode(value)
        case .dictionary(let value):
            try container.encode(value)
        case .null:
            try container.encodeNil()
        }
    }
}
