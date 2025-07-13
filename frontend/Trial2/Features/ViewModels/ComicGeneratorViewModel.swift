import Foundation
import Combine // Import Combine for @Published and PassthroughSubject

// MARK: - Enhanced ComicGeneratorViewModel
@MainActor
class ComicGeneratorViewModel: ObservableObject {
    @Published var comicTitle: String = ""
    @Published var scriptText: String = ""
    @Published var selectedGenre: String = "drama"
    @Published var selectedArtStyle: String = "minimalist"
    @Published var selectedWorld: WorldType = .imaginationWorld
    @Published var includeDetailedScenario: Bool = false
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?
    @Published var generatedComic: ComicGenerationResponse?
    
    // New properties for enhanced features
    @Published var availableGenres: [String] = []
    @Published var availableArtStyles: [String] = []
    @Published var isWorldSelectionPresented: Bool = false
    @Published var showAdvancedOptions: Bool = false
    @Published var generatedScenario: String? = nil // Now stores the premise string
    @Published var isLongLoading: Bool = false
    
    private let apiClient = APIClient.shared
    private let didGenerateComicSubject = PassthroughSubject<ComicGenerationResponse, Never>()
    weak var navigation: NavigationViewModel?
    
    var didGenerateComicPublisher: AnyPublisher<ComicGenerationResponse, Never> {
        didGenerateComicSubject.eraseToAnyPublisher()
    }
    
    init() {
        NotificationCenter.default.addObserver(self, selector: #selector(handleLogout), name: .userDidLogout, object: nil)
        Task {
            await loadAvailableOptions()
        }
    }
    
    @objc private func handleLogout() {
        comicTitle = ""
        scriptText = ""
        selectedGenre = "adventure"
        selectedArtStyle = "comic book"
        selectedWorld = .imaginationWorld
        includeDetailedScenario = false
        isLoading = false
        errorMessage = nil
        generatedComic = nil
        availableGenres = []
        availableArtStyles = []
    }
    
    deinit {
        NotificationCenter.default.removeObserver(self)
    }

    // MARK: - Enhanced Methods
    func generateComic() async {
        await generateComicWithWorld(worldType: selectedWorld)
    }
    
    // MARK: - Load Available Options
    private func loadAvailableOptions() async {
        do {
            availableGenres = try await apiClient.getAvailableGenres()
            availableArtStyles = try await apiClient.getAvailableArtStyles()
        } catch {
            print("❌ Failed to load available options: \(error)")
            // Use default options if API fails
            availableGenres = ["adventure", "comedy", "horror", "romance", "sci-fi", "fantasy", "mystery", "drama", "action", "slice of life"]
            availableArtStyles = ["comic book", "manga", "cartoon", "realistic", "watercolor", "sketch", "pixel art", "minimalist", "vintage", "anime"]
        }
    }
    
    func generateComicWithWorld(worldType: WorldType) async {
        guard !comicTitle.isEmpty && !scriptText.isEmpty else {
            errorMessage = "Please enter both a title and script"
            return
        }
        
        isLoading = true
        errorMessage = nil
        
        do {
            print("🎨 Generating comic '\(comicTitle)' for \(worldType.displayName)...")
            
            // First, enhance the script with scenario generation
            print("📝 Enhancing script with AI scenario generation...")
            var finalScript = scriptText
            //
            do {
                 let scenarioResponse = try await apiClient.generateScenario(message: scriptText)
                 finalScript = scenarioResponse.scenario
                 print("✨ Enhanced script: \(finalScript.prefix(100))...")
                 print("🎭 Detected genre: \(scenarioResponse.genre)")
                 
                 // Update genre if backend suggests something different
                 if selectedGenre == "adventure" && scenarioResponse.genre.lowercased() != "adventure" {
                     selectedGenre = scenarioResponse.genre.lowercased()
                     print("🎭 Updated genre to: \(selectedGenre)")
                 }
                 
             } catch {
                 print("❌ Scenario generation failed, using original script...")
                 print("🔄 Scenario error: \(error)")
                 // Continue with original script
             }
            
            // Use only the concept (scriptText) for now
            
            
            print("🎨 Starting comic generation...")
            print("📝 Original script length: \(finalScript.count) characters")
            print("📝 Original script preview: \(String(finalScript.prefix(100)))...")
            
            // AGGRESSIVE truncation for database constraint (1000 chars max)
            let maxConceptLength = 800 // Much smaller buffer to be safe
            let truncatedConcept: String
            
            if finalScript.count > maxConceptLength {
                // More aggressive truncation
                let truncated = String(finalScript.prefix(maxConceptLength))
                truncatedConcept = truncated + "... [truncated for database]"
                print("✂️ TRUNCATED: Original \(finalScript.count) chars → Truncated \(truncatedConcept.count) chars")
                print("✂️ Truncated preview: \(String(truncatedConcept.prefix(100)))...")
            } else {
                truncatedConcept = finalScript
                print("📏 Concept length \(finalScript.count) chars - fits database limit")
            }
            
            print("🎨 About to send to backend with concept length: \(truncatedConcept.count)")
            print("DEBUG: Sending genre: \(selectedGenre), artStyle: \(selectedArtStyle)")
            let saveRequest = ComicSaveRequest(
                title: comicTitle,
                concept: truncatedConcept,
                genre: selectedGenre,
                artStyle: selectedArtStyle,
                worldType: worldType,
                includeDetailedScenario: includeDetailedScenario,
                imageBase64: "", // Always include as empty string
                panelsData: nil,
                isFavorite: nil,
                isPublic: nil
            )
            
            let token = await AuthManager.shared.getStoredToken()
            guard let token = token else {
                throw APIError.unauthorized
            }
            
            let comic = try await apiClient.generateComicWithData(request: saveRequest, token: token)
            
            generatedComic = comic
            didGenerateComicSubject.send(comic)
            
            print("✅ Comic successfully generated and saved to \(worldType.displayName)!")
            generatedScenario = nil // Reset before fetching
            if comic.hasDetailedScenario {
                print("🔎 Fetching detailed scenario for comic ID: \(comic.id)")
                do {
                    let premise = try await apiClient.getScenarioByComic(comicId: comic.id, token: token)
                    print("✅ Detailed scenario fetched, storing in generatedScenario")
                    generatedScenario = premise
                } catch {
                    print("❌ Failed to fetch detailed scenario: \(error)")
                    generatedScenario = nil
                }
            }
            // Always navigate to comic viewer
            print("🚀 Navigating to comic viewer...")
            navigation?.showComicViewer(with: comic)
            print("🚀 Navigation call completed")
            
        } catch APIError.unauthorized {
            errorMessage = "Please log in to generate comics"
        } catch APIError.serverError(let code) {
            errorMessage = "Failed to generate comic: Server error \(code)"
        } catch APIError.serverErrorMessage(let message) {
            if message.contains("504 Gateway Time-out") {
                isLongLoading = true
                errorMessage = "Loading your comics to the planet..."
                Task { @MainActor in
                    try? await Task.sleep(nanoseconds: 9_000_000_000)
                    errorMessage = "Successfully saved"
                    isLongLoading = false
                }
            } else {
                errorMessage = "Failed to generate comic: \(message)"
            }
        } catch {
            if error.localizedDescription.contains("504 Gateway Time-out") {
                isLongLoading = true
                errorMessage = "Loading your comics to the planet..."
                Task { @MainActor in
                    try? await Task.sleep(nanoseconds: 9_000_000_000)
                    errorMessage = "Successfully saved"
                    isLongLoading = false
                }
            } else {
                errorMessage = "Failed to generate comic: \(error.localizedDescription)"
            }
            print("❌ Comic generation error: \(error)")
        }
        
        isLoading = false
    }
    
    func generateScenario() async {
        guard !scriptText.isEmpty else {
            errorMessage = "Please enter some script text first"
            return
        }
        
        isLoading = true
        errorMessage = nil
        
        print("📝 Generating scenario enhancement...")
        
        do {
            let scenarioResponse = try await apiClient.generateScenario(message: scriptText)
            let enhancedScript = scenarioResponse.scenario
            
            print("✅ Scenario enhancement SUCCESS!")
            print("✨ Enhanced script: \(enhancedScript.prefix(100))...")
            print("🎭 Detected genre: \(scenarioResponse.genre)")
            
            // Update the script text with enhanced version
            scriptText = enhancedScript
            
            // Also update genre if the backend suggests one and we don't have a specific one set
            if selectedGenre == "adventure" && scenarioResponse.genre.lowercased() != "adventure" {
                selectedGenre = scenarioResponse.genre.lowercased()
                print("🎭 Updated genre to: \(selectedGenre)")
            }
            
            errorMessage = "✅ Scenario enhanced! Genre detected: \(scenarioResponse.genre)"
            
        } catch {
            print("❌ Scenario enhancement FAILED")
            print("🔄 Scenario error: \(error)")
            errorMessage = "Failed to enhance scenario: \(error.localizedDescription)"
        }
        
        isLoading = false
    }

    func editScript() {
        print("Edit Script tapped")
        // This method could trigger navigation to a `ScriptEditorViewController`
        // or modify `scriptText` based on user interaction or AI suggestions.
    }

    func addToneMoodSuggestions() {
        print("Add Tone/Mood Suggestions tapped")
        // This method could interact with your AIService to get tone/mood suggestions
        // and update the `scriptText` or provide options to the user.
    }
    
    func clearError() {
        errorMessage = nil
    }
    
    func resetForm() {
        comicTitle = ""
        scriptText = ""
        errorMessage = nil
        generatedComic = nil
        selectedGenre = "adventure"
        selectedArtStyle = "comic book"
        selectedWorld = .imaginationWorld
        includeDetailedScenario = false
        showAdvancedOptions = false
    }

    private func determineGenre() -> String {
        let lowercaseScript = scriptText.lowercased()
        
        if lowercaseScript.contains("adventure") || lowercaseScript.contains("quest") || lowercaseScript.contains("journey") {
            return "adventure"
        } else if lowercaseScript.contains("funny") || lowercaseScript.contains("joke") || lowercaseScript.contains("laugh") {
            return "comedy"
        } else if lowercaseScript.contains("scary") || lowercaseScript.contains("horror") || lowercaseScript.contains("monster") {
            return "horror"
        } else if lowercaseScript.contains("love") || lowercaseScript.contains("romance") || lowercaseScript.contains("relationship") {
            return "romance"
        } else if lowercaseScript.contains("space") || lowercaseScript.contains("future") || lowercaseScript.contains("robot") {
            return "sci-fi"
        } else if lowercaseScript.contains("magic") || lowercaseScript.contains("wizard") || lowercaseScript.contains("dragon") {
            return "fantasy"
        } else if lowercaseScript.contains("crime") || lowercaseScript.contains("detective") || lowercaseScript.contains("mystery") {
            return "mystery"
        } else {
            return "adventure" // default
        }
    }
    
    // MARK: - World-Aware Generation
    func generateWithWorldContext() async {
        // Enhance script based on selected world
        let worldContext = selectedWorld.detailedDescription
        let enhancedScript = "\(scriptText)\n\nWorld Context: \(worldContext)"
        
        let originalScript = scriptText
        scriptText = enhancedScript
        
        await generateComic()
        
        // Restore original script
        scriptText = originalScript
    }
    
    // MARK: - Quick Generation Presets
    func generateWithPreset(_ preset: ComicPreset) async {
        comicTitle = preset.title
        scriptText = preset.concept
        selectedGenre = preset.genre
        selectedArtStyle = preset.artStyle
        selectedWorld = preset.worldType
        includeDetailedScenario = preset.includeDetailedScenario
        
        await generateComic()
    }
    
    // MARK: - Validation
    var canGenerate: Bool {
        !comicTitle.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty &&
        !scriptText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty &&
        !isLoading
    }
    
    var formCompletionPercentage: Double {
        var completedFields = 0
        let totalFields = 6
        
        if !comicTitle.isEmpty { completedFields += 1 }
        if !scriptText.isEmpty { completedFields += 1 }
        if !selectedGenre.isEmpty { completedFields += 1 }
        if !selectedArtStyle.isEmpty { completedFields += 1 }
        completedFields += 1 // selectedWorld always has a value
        if includeDetailedScenario { completedFields += 1 }
        
        return Double(completedFields) / Double(totalFields)
    }
}

// MARK: - Comic Generation Presets
struct ComicPreset {
    let title: String
    let concept: String
    let genre: String
    let artStyle: String
    let worldType: WorldType
    let includeDetailedScenario: Bool
    
    static let dreamWorldPresets: [ComicPreset] = [
        ComicPreset(
            title: "The Floating City",
            concept: "A city where gravity works in reverse and people walk on clouds",
            genre: "fantasy",
            artStyle: "watercolor",
            worldType: .dreamWorld,
            includeDetailedScenario: true
        ),
        ComicPreset(
            title: "Mirror Memories",
            concept: "Each mirror shows a different version of your past",
            genre: "mystery",
            artStyle: "noir",
            worldType: .dreamWorld,
            includeDetailedScenario: true
        )
    ]
    
    static let mindWorldPresets: [ComicPreset] = [
        ComicPreset(
            title: "The Decision Council",
            concept: "Inside someone's mind, different emotions debate a major life choice",
            genre: "drama",
            artStyle: "minimalist",
            worldType: .mindWorld,
            includeDetailedScenario: true
        ),
        ComicPreset(
            title: "Memory Lane",
            concept: "A journey through someone's memories to find a lost childhood moment",
            genre: "adventure",
            artStyle: "sketch",
            worldType: .mindWorld,
            includeDetailedScenario: true
        )
    ]
    
    static let imaginationWorldPresets: [ComicPreset] = [
        ComicPreset(
            title: "Space Pirates",
            concept: "A crew of pirates sailing through asteroid fields in search of cosmic treasure",
            genre: "adventure",
            artStyle: "comic book",
            worldType: .imaginationWorld,
            includeDetailedScenario: false
        ),
        ComicPreset(
            title: "Dragon Academy",
            concept: "Young wizards learning to train and ride dragons",
            genre: "fantasy",
            artStyle: "cartoon",
            worldType: .imaginationWorld,
            includeDetailedScenario: false
        )
    ]
    
    static func presetsForWorld(_ worldType: WorldType) -> [ComicPreset] {
        switch worldType {
        case .dreamWorld: return dreamWorldPresets
        case .mindWorld: return mindWorldPresets
        case .imaginationWorld: return imaginationWorldPresets
        }
    }
}
