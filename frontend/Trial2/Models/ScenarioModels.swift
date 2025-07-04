import Foundation
import SwiftUI

// MARK: - Scenario Request Models
struct ScenarioSaveRequest: Codable {
    let comicId: Int
    let detailedScenario: String
    let characterDescriptions: [String: String]
    let plotSummary: String
    let themes: [String]
    let complexity: ScenarioComplexity
    let targetAudience: TargetAudience
    
    enum CodingKeys: String, CodingKey {
        case comicId = "comic_id"
        case detailedScenario = "detailed_scenario"
        case characterDescriptions = "character_descriptions"
        case plotSummary = "plot_summary"
        case themes, complexity
        case targetAudience = "target_audience"
    }
}

struct ScenarioGenerationRequest: Codable {
    let concept: String
    let genre: String
    let worldType: WorldType
    let complexity: ScenarioComplexity
    let targetAudience: TargetAudience
    let includeCharacters: Bool
    let templateId: Int?
    
    enum CodingKeys: String, CodingKey {
        case concept, genre, complexity
        case worldType = "world_type"
        case targetAudience = "target_audience"
        case includeCharacters = "include_characters"
        case templateId = "template_id"
    }
}

struct ScenarioUpdateRequest: Codable {
    let detailedScenario: String?
    let characterDescriptions: [String: String]?
    let plotSummary: String?
    let themes: [String]?
    let complexity: ScenarioComplexity?
    let targetAudience: TargetAudience?
    
    enum CodingKeys: String, CodingKey {
        case detailedScenario = "detailed_scenario"
        case characterDescriptions = "character_descriptions"
        case plotSummary = "plot_summary"
        case themes, complexity
        case targetAudience = "target_audience"
    }
}

// MARK: - Scenario Response Models
struct DetailedScenario: Codable, Identifiable {
    let id: Int
    let comicId: Int
    let detailedScenario: String
    let characterDescriptions: [String: String]
    let plotSummary: String
    let themes: [String]
    let complexity: ScenarioComplexity
    let targetAudience: TargetAudience
    let createdAt: String
    let updatedAt: String
    let worldType: WorldType
    let plotPoints: [PlotPoint]
    let characterRoles: [CharacterRole]
    
    enum CodingKeys: String, CodingKey {
        case id
        case comicId = "comic_id"
        case detailedScenario = "detailed_scenario"
        case characterDescriptions = "character_descriptions"
        case plotSummary = "plot_summary"
        case themes, complexity
        case targetAudience = "target_audience"
        case createdAt = "created_at"
        case updatedAt = "updated_at"
        case worldType = "world_type"
        case plotPoints = "plot_points"
        case characterRoles = "character_roles"
    }
}

struct ScenarioSaveResponse: Codable {
    let id: Int
    let comicId: Int
    let message: String
    let analysisScore: Double
    let suggestions: [String]
    
    enum CodingKeys: String, CodingKey {
        case id
        case comicId = "comic_id"
        case message
        case analysisScore = "analysis_score"
        case suggestions
    }
}

struct ScenarioListResponse: Codable, Identifiable {
    let id: Int
    let comicId: Int
    let comicTitle: String
    let plotSummary: String
    let themes: [String]
    let complexity: ScenarioComplexity
    let worldType: WorldType
    let createdAt: String
    let characterCount: Int
    let plotPointCount: Int
    
    enum CodingKeys: String, CodingKey {
        case id
        case comicId = "comic_id"
        case comicTitle = "comic_title"
        case plotSummary = "plot_summary"
        case themes, complexity
        case worldType = "world_type"
        case createdAt = "created_at"
        case characterCount = "character_count"
        case plotPointCount = "plot_point_count"
    }
}

// MARK: - Scenario Supporting Models
enum ScenarioComplexity: String, CaseIterable, Codable {
    case simple = "simple"
    case moderate = "moderate"
    case complex = "complex"
    case advanced = "advanced"
    case masterful = "masterful"
    
    var displayName: String {
        switch self {
        case .simple: return "Simple"
        case .moderate: return "Moderate"
        case .complex: return "Complex"
        case .advanced: return "Advanced"
        case .masterful: return "Masterful"
        }
    }
    
    var description: String {
        switch self {
        case .simple: return "Basic story with few characters and simple plot"
        case .moderate: return "Standard story with multiple characters and plot twists"
        case .complex: return "Intricate story with complex relationships and subplots"
        case .advanced: return "Highly sophisticated narrative with deep themes"
        case .masterful: return "Masterpiece-level storytelling with exceptional depth"
        }
    }
    
    var color: Color {
        switch self {
        case .simple: return .green
        case .moderate: return .blue
        case .complex: return .orange
        case .advanced: return .red
        case .masterful: return .purple
        }
    }
}

enum TargetAudience: String, CaseIterable, Codable {
    case children = "children"
    case teens = "teens"
    case adults = "adults"
    case allAges = "all_ages"
    
    var displayName: String {
        switch self {
        case .children: return "Children (6-12)"
        case .teens: return "Teens (13-17)"
        case .adults: return "Adults (18+)"
        case .allAges: return "All Ages"
        }
    }
    
    var themes: [String] {
        switch self {
        case .children: return ["friendship", "learning", "adventure", "family"]
        case .teens: return ["coming of age", "identity", "relationships", "challenges"]
        case .adults: return ["complex emotions", "life lessons", "mature themes", "philosophical"]
        case .allAges: return ["universal values", "humor", "hope", "togetherness"]
        }
    }
}

struct PlotPoint: Codable, Identifiable {
    let id: Int
    let sequence: Int
    let title: String
    let description: String
    let type: PlotPointType
    let characters: [String]
    let significance: PlotPointSignificance
    
    enum CodingKeys: String, CodingKey {
        case id, sequence, title, description, type, characters, significance
    }
}

enum PlotPointType: String, CaseIterable, Codable {
    case exposition = "exposition"
    case incitingIncident = "inciting_incident"
    case risingAction = "rising_action"
    case climax = "climax"
    case fallingAction = "falling_action"
    case resolution = "resolution"
    
    var displayName: String {
        switch self {
        case .exposition: return "Exposition"
        case .incitingIncident: return "Inciting Incident"
        case .risingAction: return "Rising Action"
        case .climax: return "Climax"
        case .fallingAction: return "Falling Action"
        case .resolution: return "Resolution"
        }
    }
}

enum PlotPointSignificance: String, CaseIterable, Codable {
    case minor = "minor"
    case moderate = "moderate"
    case major = "major"
    case critical = "critical"
    
    var displayName: String {
        rawValue.capitalized
    }
    
    var color: Color {
        switch self {
        case .minor: return .gray
        case .moderate: return .blue
        case .major: return .orange
        case .critical: return .red
        }
    }
}

struct CharacterRole: Codable, Identifiable {
    let id: Int
    let name: String
    let description: String
    let role: CharacterRoleType
    let personality: [String]
    let relationships: [String: String]
    let significance: CharacterSignificance
    
    enum CodingKeys: String, CodingKey {
        case id, name, description, role, personality, relationships, significance
    }
}

enum CharacterRoleType: String, CaseIterable, Codable {
    case protagonist = "protagonist"
    case antagonist = "antagonist"
    case supporting = "supporting"
    case background = "background"
    case narrator = "narrator"
    
    var displayName: String {
        rawValue.capitalized
    }
    
    var color: Color {
        switch self {
        case .protagonist: return .blue
        case .antagonist: return .red
        case .supporting: return .green
        case .background: return .gray
        case .narrator: return .purple
        }
    }
}

enum CharacterSignificance: String, CaseIterable, Codable {
    case minor = "minor"
    case moderate = "moderate"
    case important = "important"
    case essential = "essential"
    
    var displayName: String {
        rawValue.capitalized
    }
}

// MARK: - Scenario Templates
struct ScenarioTemplate: Codable, Identifiable {
    let id: Int
    let name: String
    let description: String
    let worldType: WorldType
    let complexity: ScenarioComplexity
    let structure: TemplateStructure
    let characterTemplates: [CharacterTemplate]
    let plotOutline: [PlotOutlineItem]
    let suggestedThemes: [String]
    let isPublic: Bool
    let usageCount: Int
    let rating: Double
    
    enum CodingKeys: String, CodingKey {
        case id, name, description, complexity, structure, rating
        case worldType = "world_type"
        case characterTemplates = "character_templates"
        case plotOutline = "plot_outline"
        case suggestedThemes = "suggested_themes"
        case isPublic = "is_public"
        case usageCount = "usage_count"
    }
}

struct TemplateStructure: Codable {
    let acts: [TemplateAct]
    let estimatedLength: Int
    let pacing: TemplatePacing
    
    enum CodingKeys: String, CodingKey {
        case acts
        case estimatedLength = "estimated_length"
        case pacing
    }
}

struct TemplateAct: Codable, Identifiable {
    let id: Int
    let name: String
    let description: String
    let estimatedPanels: Int
    let keyEvents: [String]
    
    enum CodingKeys: String, CodingKey {
        case id, name, description, keyEvents
        case estimatedPanels = "estimated_panels"
    }
}

enum TemplatePacing: String, CaseIterable, Codable {
    case slow = "slow"
    case moderate = "moderate"
    case fast = "fast"
    case variable = "variable"
    
    var displayName: String {
        rawValue.capitalized
    }
}

struct CharacterTemplate: Codable, Identifiable {
    let id: Int
    let name: String
    let role: CharacterRoleType
    let description: String
    let personalityTraits: [String]
    let motivations: [String]
    let conflicts: [String]
    
    enum CodingKeys: String, CodingKey {
        case id, name, role, description, motivations, conflicts
        case personalityTraits = "personality_traits"
    }
}

struct PlotOutlineItem: Codable, Identifiable {
    let id: Int
    let sequence: Int
    let title: String
    let description: String
    let type: PlotPointType
    let estimatedPanels: Int
    
    enum CodingKeys: String, CodingKey {
        case id, sequence, title, description, type
        case estimatedPanels = "estimated_panels"
    }
}

// MARK: - Scenario Analysis
struct ScenarioAnalysis: Codable {
    let scenarioId: Int
    let overallScore: Double
    let strengths: [AnalysisPoint]
    let improvements: [AnalysisPoint]
    let themeConsistency: Double
    let characterDevelopment: Double
    let plotCoherence: Double
    let pacing: Double
    let suggestions: [String]
    
    enum CodingKeys: String, CodingKey {
        case scenarioId = "scenario_id"
        case overallScore = "overall_score"
        case strengths, improvements
        case themeConsistency = "theme_consistency"
        case characterDevelopment = "character_development"
        case plotCoherence = "plot_coherence"
        case pacing, suggestions
    }
}

struct AnalysisPoint: Codable, Identifiable {
    let id = UUID()
    let category: String
    let description: String
    let score: Double
    let impact: AnalysisImpact
    
    enum CodingKeys: String, CodingKey {
        case category, description, score, impact
    }
}

enum AnalysisImpact: String, CaseIterable, Codable {
    case low = "low"
    case medium = "medium"
    case high = "high"
    
    var displayName: String {
        rawValue.capitalized
    }
    
    var color: Color {
        switch self {
        case .low: return .green
        case .medium: return .orange
        case .high: return .red
        }
    }
}

// MARK: - Preview Data
#if DEBUG
extension DetailedScenario {
    static let preview = DetailedScenario(
        id: 1,
        comicId: 1,
        detailedScenario: "A young hero discovers a magical artifact that grants incredible powers, but also attracts dangerous enemies. They must learn to control their new abilities while protecting their loved ones.",
        characterDescriptions: [
            "Hero": "A brave but inexperienced young person with a strong moral compass",
            "Mentor": "A wise old wizard who guides the hero",
            "Villain": "A dark sorcerer seeking the artifact's power"
        ],
        plotSummary: "Classic hero's journey with magical elements",
        themes: ["courage", "growth", "responsibility", "friendship"],
        complexity: .moderate,
        targetAudience: .teens,
        createdAt: "2024-01-15T10:30:00Z",
        updatedAt: "2024-01-15T10:30:00Z",
        worldType: .imaginationWorld,
        plotPoints: [
            PlotPoint(
                id: 1,
                sequence: 1,
                title: "Discovery",
                description: "Hero finds the magical artifact",
                type: .incitingIncident,
                characters: ["Hero"],
                significance: .critical
            )
        ],
        characterRoles: [
            CharacterRole(
                id: 1,
                name: "Hero",
                description: "The main protagonist",
                role: .protagonist,
                personality: ["brave", "curious", "determined"],
                relationships: ["Mentor": "student"],
                significance: .essential
            )
        ]
    )
}

extension ScenarioTemplate {
    static let preview = ScenarioTemplate(
        id: 1,
        name: "Hero's Journey",
        description: "Classic three-act hero's journey template",
        worldType: .imaginationWorld,
        complexity: .moderate,
        structure: TemplateStructure(
            acts: [
                TemplateAct(
                    id: 1,
                    name: "Act 1: Setup",
                    description: "Introduction and inciting incident",
                    estimatedPanels: 3,
                    keyEvents: ["Introduction", "Call to adventure", "Crossing the threshold"]
                )
            ],
            estimatedLength: 8,
            pacing: .moderate
        ),
        characterTemplates: [
            CharacterTemplate(
                id: 1,
                name: "Hero",
                role: .protagonist,
                description: "The main character who goes on the journey",
                personalityTraits: ["brave", "curious"],
                motivations: ["save others", "find purpose"],
                conflicts: ["self-doubt", "external threats"]
            )
        ],
        plotOutline: [
            PlotOutlineItem(
                id: 1,
                sequence: 1,
                title: "The Call",
                description: "Hero receives their call to adventure",
                type: .incitingIncident,
                estimatedPanels: 2
            )
        ],
        suggestedThemes: ["growth", "courage", "destiny"],
        isPublic: true,
        usageCount: 47,
        rating: 4.2
    )
}
#endif 