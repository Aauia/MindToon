import Foundation
import Combine // Import Combine for @Published and PassthroughSubject

// MARK: - ComicGeneratorViewModel
@MainActor
class ComicGeneratorViewModel: ObservableObject {
    @Published var comicTitle: String = ""
    @Published var scriptText: String = ""
    @Published var isLoading: Bool = false
    @Published var errorMessage: String? = nil
    @Published var generatedComic: Comic?
    @Published var genre: String = "general"
    @Published var artStyle: String = "comic book"

    // Publisher to signal when comic generation is complete
    let didGenerateComicPublisher = PassthroughSubject<Void, Never>()

    // MARK: - Methods
    func generateComic() async {
        isLoading = true
        errorMessage = nil
        
        guard let token = AuthManager.shared.getStoredToken() else {
            errorMessage = "Authentication required. Please login again."
            isLoading = false
            return
        }
        
        // Use script text as the message for comic generation
        let message = scriptText.isEmpty ? comicTitle : scriptText
        
        do {
            let request = ComicRequest(
                message: message,
                genre: genre,
                artStyle: artStyle
            )
            
            let response = try await APIClient.shared.generateComic(comicRequest: request, token: token)
            generatedComic = Comic(from: response)
            
            print("Comic generated successfully!")
            self.didGenerateComicPublisher.send()
        } catch {
            print("Error generating comic: \(error.localizedDescription)")
            errorMessage = "Failed to generate comic: \(error.localizedDescription)"
        }
        
        isLoading = false
    }
    
    func generateScenario() async {
        isLoading = true
        errorMessage = nil
        
        let message = scriptText.isEmpty ? comicTitle : scriptText
        
        do {
            let response = try await APIClient.shared.generateScenario(message: message)
            scriptText = response.scenario
            print("Scenario generated successfully!")
        } catch {
            print("Error generating scenario: \(error.localizedDescription)")
            errorMessage = "Failed to generate scenario: \(error.localizedDescription)"
        }
        
        isLoading = false
    }

    func editScript() {
        print("Edit Script action triggered.")
        // This method could trigger navigation to a `ScriptEditorViewController`
        // or modify `scriptText` based on user interaction or AI suggestions.
    }

    func addToneMoodSuggestions() {
        print("Add Tone/Mood Suggestions action triggered.")
        // This method could interact with your AIService to get tone/mood suggestions
        // and update the `scriptText` or provide options to the user.
    }
    
    func clearError() {
        errorMessage = nil
    }
    
    func resetForm() {
        comicTitle = ""
        scriptText = ""
        generatedComic = nil
        errorMessage = nil
        genre = "general"
        artStyle = "comic book"
    }
}
