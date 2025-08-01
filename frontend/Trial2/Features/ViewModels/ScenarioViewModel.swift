import Foundation
import Combine

// MARK: - Scenario Editor State
struct ScenarioEditorState {
    var detailedScenario: String = ""
    var characterDescriptions: [String: String] = [:]
    var plotSummary: String = ""
    var themes: [String] = []
    var selectedThemes: Set<String> = []
    var availableThemes: [String] = []
    
    // Character management
    var isAddingCharacter: Bool = false
    var newCharacterName: String = ""
    var newCharacterDescription: String = ""
    
    // Template management
    var selectedTemplate: ScenarioTemplate?
    
    mutating func reset() {
        detailedScenario = ""
        characterDescriptions = [:]
        plotSummary = ""
        themes = []
        selectedThemes = []
        availableThemes = []
        isAddingCharacter = false
        newCharacterName = ""
        newCharacterDescription = ""
        selectedTemplate = nil
    }
}

// MARK: - Scenario Management ViewModel
@MainActor
class ScenarioViewModel: ObservableObject {
    @Published var scenarios: [DetailedScenario] = []
    @Published var selectedScenario: DetailedScenario?
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?
    @Published var isCreatingScenario: Bool = false
    @Published var isEditingScenario: Bool = false
    
    // Scenario editor state
    @Published var editorState = ScenarioEditorState()
    @Published var selectedTemplate: ScenarioTemplate?
    @Published var currentComicId: Int?
    
    // Filtering and search
    @Published var searchText: String = ""
    @Published var selectedWorldFilter: WorldType? = nil
    @Published var selectedThemeFilter: String = "All"
    @Published var selectedComplexityFilter: ScenarioComplexity? = nil
    
    private let apiClient = APIClient.shared
    private var cancellables = Set<AnyCancellable>()
    
    init() {
        NotificationCenter.default.addObserver(self, selector: #selector(handleLogout), name: .userDidLogout, object: nil)
        Task {
            await loadUserScenarios()
        }
    }
    
    @objc private func handleLogout() {
        scenarios = []
        selectedScenario = nil
        isLoading = false
        errorMessage = nil
    }
    
    deinit {
        NotificationCenter.default.removeObserver(self)
    }
    
    // MARK: - Scenario Loading
    func loadUserScenarios(limit: Int = 50, offset: Int = 0) async {
        isLoading = true
        errorMessage = nil
        
        do {
            let token = await AuthManager.shared.getStoredToken()
            guard let token = token else {
                throw APIError.unauthorized
            }
            
            let userScenarios = try await apiClient.getUserScenarios(limit: limit, offset: offset)
            scenarios = userScenarios
            
            print("✅ Loaded \(userScenarios.count) user scenarios")
        } catch {
            let apiError = error as? APIError ?? APIError.networkError(error)
            errorMessage = apiError.userFriendlyMessage
            ErrorLogger.shared.log(apiError, context: "Loading user scenarios")
        }
        
        isLoading = false
    }
  
    func refreshScenarios() async {
        await loadUserScenarios()
    }
    
    // MARK: - Scenario Creation and Editing
    func presentCreateScenario(for comicId: Int) {
        currentComicId = comicId
        resetEditorState()
        isCreatingScenario = true
    }
    
    func presentEditScenario(_ scenario: DetailedScenario) {
        selectedScenario = scenario
        currentComicId = scenario.comicId
        
        // Load scenario data into editor
    
        
        isEditingScenario = true
    }
    
    func saveScenario() async {
        guard let comicId = currentComicId else {
            errorMessage = "No comic selected for scenario"
            return
        }
        
        guard !editorState.detailedScenario.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
            errorMessage = "Scenario content cannot be empty"
            return
        }
        
        isLoading = true
        errorMessage = nil
        
        do {
            let token = await AuthManager.shared.getStoredToken()
            guard let token = token else {
                throw APIError.unauthorized
            }
            
            let request = ScenarioSaveRequest(
                comicId: comicId,
                detailedScenario: editorState.detailedScenario,
                characterDescriptions: editorState.characterDescriptions,
                plotSummary: editorState.plotSummary,
                themes: Array(editorState.selectedThemes),
                complexity: .moderate,
                targetAudience: .allAges
            )
            
            let response = try await apiClient.saveScenario(request: request)
            
            // Refresh scenarios list
            await loadUserScenarios()
            
            // Close editor
            isCreatingScenario = false
            isEditingScenario = false
            resetEditorState()
            
            print("✅ Successfully saved scenario for comic \(comicId)")
            
        } catch {
            let apiError = error as? APIError ?? APIError.networkError(error)
            errorMessage = apiError.userFriendlyMessage
            ErrorLogger.shared.log(apiError, context: "Saving scenario for comic \(comicId)")
        }
        
        isLoading = false
    }
    
    func cancelScenarioEdit() {
        isCreatingScenario = false
        isEditingScenario = false
        resetEditorState()
        selectedScenario = nil
        currentComicId = nil
        errorMessage = nil
    }
    
    // MARK: - Template Management
    func loadTemplate(_ template: ScenarioTemplate) {
        selectedTemplate = template
        editorState.detailedScenario = template.description
        editorState.selectedThemes = Set(template.suggestedThemes)
        
        // Add template themes to available themes if not already present
        for theme in template.suggestedThemes {
            if !editorState.availableThemes.contains(theme) {
                editorState.availableThemes.append(theme)
            }
        }
    }
    
    func getTemplatesForWorld(_ worldType: WorldType) -> [ScenarioTemplate] {
        // Return empty array for now - templates would be loaded from backend
        return []
    }
    
    // MARK: - Character Management
    func addCharacter() {
        guard !editorState.newCharacterName.isEmpty && !editorState.newCharacterDescription.isEmpty else {
            errorMessage = "Character name and description cannot be empty"
            return
        }
        
        editorState.characterDescriptions[editorState.newCharacterName] = editorState.newCharacterDescription
        editorState.newCharacterName = ""
        editorState.newCharacterDescription = ""
        editorState.isAddingCharacter = false
        clearError()
    }
    
    func removeCharacter(_ characterName: String) {
        editorState.characterDescriptions.removeValue(forKey: characterName)
    }
    
    func presentAddCharacter() {
        editorState.isAddingCharacter = true
        editorState.newCharacterName = ""
        editorState.newCharacterDescription = ""
    }
    
    func cancelAddCharacter() {
        editorState.isAddingCharacter = false
        editorState.newCharacterName = ""
        editorState.newCharacterDescription = ""
    }
    
    // MARK: - Theme Management
    func toggleTheme(_ theme: String) {
        if editorState.selectedThemes.contains(theme) {
            editorState.selectedThemes.remove(theme)
        } else {
            editorState.selectedThemes.insert(theme)
        }
        editorState.themes = Array(editorState.selectedThemes)
    }
    
    func addCustomTheme(_ theme: String) {
        let trimmedTheme = theme.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmedTheme.isEmpty else { return }
        
        if !editorState.availableThemes.contains(trimmedTheme) {
            editorState.availableThemes.append(trimmedTheme)
        }
        editorState.selectedThemes.insert(trimmedTheme)
        editorState.themes = Array(editorState.selectedThemes)
    }
    
    // MARK: - Filtering and Search

    
 
    
    func clearSearch() {
        searchText = ""
    }
    
    func clearFilters() {
        selectedWorldFilter = nil
        selectedThemeFilter = "All"
        selectedComplexityFilter = nil
        searchText = ""
    }
    

    
    // MARK: - Helper Methods
    private func resetEditorState() {
        editorState = ScenarioEditorState()
        selectedTemplate = nil
    }
    
    private func extractTraits(from description: String) -> [String] {
        // Basic trait extraction - would be enhanced with AI
        let traitKeywords = ["brave", "kind", "mysterious", "wise", "clever", "strong", "gentle", "fierce"]
        return traitKeywords.filter { description.lowercased().contains($0) }
    }
    
    private func generateBasicPlotPoints(from scenario: String) -> [PlotPoint] {
        // Basic plot point extraction - would be enhanced with AI
        let sentences = scenario.components(separatedBy: ". ")
        return sentences.enumerated().compactMap { index, sentence in
            guard !sentence.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else { return nil }
            return PlotPoint(
                id: index + 1,
                sequence: index + 1,
                title: "Plot Point \(index + 1)",
                description: String(sentence.prefix(100)),
                type: determinePlotPointType(for: index, total: sentences.count),
                characters: [],
                significance: .moderate
            )
        }
    }
    

    
    private func determineMood(from scenario: String) -> String {
        let scenarioLower = scenario.lowercased()
        
        if scenarioLower.contains("dark") || scenarioLower.contains("scary") {
            return "Dark and mysterious"
        } else if scenarioLower.contains("funny") || scenarioLower.contains("laugh") {
            return "Light and humorous"
        } else if scenarioLower.contains("adventure") || scenarioLower.contains("quest") {
            return "Adventurous and exciting"
        } else if scenarioLower.contains("love") || scenarioLower.contains("romantic") {
            return "Romantic and emotional"
        } else {
            return "Balanced and engaging"
        }
    }
    
    private func determineGenre(from themes: [String]) -> String {
        let themeSet = Set(themes.map { $0.lowercased() })
        
        if themeSet.contains("adventure") || themeSet.contains("heroism") {
            return "Adventure"
        } else if themeSet.contains("romance") || themeSet.contains("love") {
            return "Romance"
        } else if themeSet.contains("mystery") || themeSet.contains("detective") {
            return "Mystery"
        } else if themeSet.contains("horror") || themeSet.contains("fear") {
            return "Horror"
        } else if themeSet.contains("comedy") || themeSet.contains("humor") {
            return "Comedy"
        } else {
            return "Drama"
        }
    }
    
    private func determinePlotPointType(for index: Int, total: Int) -> PlotPointType {
        let position = Double(index) / Double(max(1, total - 1))
        
        switch position {
        case 0...0.2: return .exposition
        case 0.2...0.3: return .incitingIncident
        case 0.3...0.7: return .risingAction
        case 0.7...0.8: return .climax
        case 0.8...0.9: return .fallingAction
        default: return .resolution
        }
    }
    
    // MARK: - Error Handling
    func clearError() {
        errorMessage = nil
    }
    
    func retryLastOperation() async {
        await refreshScenarios()
    }
}

// MARK: - Preview Data
#if DEBUG
extension ScenarioViewModel {
    static func preview() -> ScenarioViewModel {
        let viewModel = ScenarioViewModel()
        
       
        
        return viewModel
    }
}
#endif 
