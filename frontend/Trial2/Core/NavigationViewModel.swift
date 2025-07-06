import Foundation
import SwiftUI
import Combine

class NavigationViewModel: ObservableObject {
    enum Screen {
        case welcome
        case login
        case register
        case mainDashboard
        case create
        case worlds
        case profile
        case dreamWorld
        case mindWorld
        case imaginationWorld
        case comicGenerator
        case comicViewer
        case imageGenerator
        case scenarios
        case detailedScenario
        case accountDeletion
    }
    @Published var currentScreen: Screen = .welcome
    @Published var generatedComic: ComicGenerationResponse?
    @Published var selectedScenario: DetailedScenario?
    
    func navigateTo(_ screen: Screen) {
        currentScreen = screen
    }
    
    func showComicViewer(with comic: ComicGenerationResponse) {
        print("📱 NavigationViewModel.showComicViewer called")
        print("📱 Comic title: '\(comic.title)'")
     
        print("📱 Current thread: \(Thread.isMainThread ? "Main" : "Background")")
        generatedComic = comic
        print("📱 generatedComic set successfully")
        print("📱 Setting currentScreen to .comicViewer")
        currentScreen = .comicViewer
        print("📱 currentScreen is now: \(currentScreen)")
        print("📱 generatedComic after assignment: \(generatedComic?.title ?? "nil")")
    }
    
    func showDetailedScenario(with scenario: DetailedScenario) {
        print("📱 NavigationViewModel.showDetailedScenario called")
        print("📱 Scenario plot summary: '\(scenario.plotSummary)'")
        selectedScenario = scenario
        currentScreen = .detailedScenario
        print("📱 selectedScenario set and navigated to detailedScenario")
    }
}


struct BottombarView_Previews: PreviewProvider {
    static var previews: some View {
        BottombarView(navigation: NavigationViewModel())
    }
}

#Preview {
    WelcomeView(viewModel: WelcomeViewModel(), navigation: NavigationViewModel())
}
