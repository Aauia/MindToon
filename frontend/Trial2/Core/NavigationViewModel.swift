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
    }
    @Published var currentScreen: Screen = .welcome
} 


struct BottombarView_Previews: PreviewProvider {
    static var previews: some View {
        BottombarView(navigation: NavigationViewModel())
    }
}

#Preview {
    WelcomeView(viewModel: WelcomeViewModel(), navigation: NavigationViewModel())
}
