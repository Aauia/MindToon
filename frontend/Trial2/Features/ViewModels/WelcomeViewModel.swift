import Foundation
import Combine

// MARK: - WelcomeViewModel
class WelcomeViewModel: ObservableObject {
    // @Published properties will automatically notify SwiftUI views when they change
    @Published var appTitle: String = "Welcome to the App!"
    @Published var appSubtitle: String = "Your journey begins here."
    @Published var welcomeMessage: String = "Get started to explore the app."
    @Published var mainCallToAction: String = "Get Started"

    // MARK: - Methods
    func handleGetStarted() {
        // When the "Get Started" button is tapped, send a signal through the publisher
        // Navigation is now handled by NavigationViewModel
    }
}
