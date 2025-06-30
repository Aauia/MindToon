import Foundation
import Combine // Import Combine for @Published and PassthroughSubject

// MARK: - ComicGeneratorViewModel
@MainActor
class ComicGeneratorViewModel: ObservableObject {
    @Published var comicTitle: String = ""
    @Published var scriptText: String = ""
    @Published var isLoading: Bool = false
    @Published var errorMessage: String? = nil
    @Published var generatedComic: ComicGenerationResponse?
    @Published var genre: String = "adventure"
    @Published var artStyle: String = "comic book"

    private let apiClient = APIClient.shared
    private let didGenerateComicSubject = PassthroughSubject<ComicGenerationResponse, Never>()
    weak var navigation: NavigationViewModel?
    
    var didGenerateComicPublisher: AnyPublisher<ComicGenerationResponse, Never> {
        didGenerateComicSubject.eraseToAnyPublisher()
    }

    // MARK: - Methods
    func generateComic() async {
        await generateComicWithWorld(worldType: .imaginationWorld)
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
            
            do {
                let scenarioResponse = try await apiClient.generateScenario(message: scriptText)
                finalScript = scenarioResponse.scenario
                print("✨ Enhanced script: \(finalScript.prefix(100))...")
                print("🎭 Detected genre: \(scenarioResponse.genre)")
                
                // Update genre if backend suggests something different
                if genre == "adventure" && scenarioResponse.genre.lowercased() != "adventure" {
                    genre = scenarioResponse.genre.lowercased()
                    print("🎭 Updated genre to: \(genre)")
                }
                
            } catch {
                print("❌ Scenario generation failed, using original script...")
                print("🔄 Scenario error: \(error)")
                // Continue with original script
            }
            
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
            
            let comic = try await apiClient.generateComicWithWorld(
                title: comicTitle,
                concept: truncatedConcept, // Use truncated version for backend
                genre: genre,
                artStyle: artStyle,
                worldType: worldType
            )
            
            generatedComic = comic
            didGenerateComicSubject.send(comic)
            
            print("✅ Comic successfully generated and saved to \(worldType.displayName)!")
            
            // Navigate to comic viewer
            print("🚀 Navigating to comic viewer...")
            navigation?.showComicViewer(with: comic)
            print("🚀 Navigation call completed")
            
        } catch APIError.unauthorized {
            errorMessage = "Please log in to generate comics"
        } catch APIError.serverError(let code) {
            errorMessage = "Failed to generate comic: Server error \(code)"
        } catch APIError.serverErrorMessage(let message) {
            errorMessage = "Failed to generate comic: \(message)"
        } catch {
            errorMessage = "Failed to generate comic: \(error.localizedDescription)"
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
            if genre == "adventure" && scenarioResponse.genre.lowercased() != "adventure" {
                genre = scenarioResponse.genre.lowercased()
                print("🎭 Updated genre to: \(genre)")
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
        genre = "adventure"
        artStyle = "comic book"
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
}
