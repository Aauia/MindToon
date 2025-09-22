import Foundation
import Combine


class WelcomeViewModel: ObservableObject {

    @Published var appTitle: String = "Welcome to the App!"
    @Published var appSubtitle: String = "Your journey begins here."
    @Published var welcomeMessage: String = "Get started to explore the app."
    @Published var mainCallToAction: String = "Get Started"


    func handleGetStarted() {
        
    }
}
