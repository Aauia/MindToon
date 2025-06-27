import Foundation
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
    }
    @Published var currentScreen: Screen = .welcome
} 