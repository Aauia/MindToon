import SwiftUI
#if canImport(UIKit)
import UIKit
#endif


enum BottomBarTab: String, CaseIterable {
    case home = "Home"
    case create = "Create"
    case worlds = "Worlds"
    case analytics = "Analytics"
    case profile = "Profile"

    var iconName: String {
        switch self {
        case .home: return "house.fill"
        case .create: return "plus.circle.fill"
        case .worlds: return "globe.americas.fill"
        case .analytics: return "chart.bar.xaxis"
        case .profile: return "person.fill"
        }
    }
}


struct BottombarView: View {
    @ObservedObject var navigation: NavigationViewModel
    

    private func tab(for screen: NavigationViewModel.Screen) -> BottomBarTab {
        switch screen {
        case .mainDashboard: return .home
        case .create, .comicGenerator: return .create
        case .worlds, .dreamWorld, .mindWorld, .imaginationWorld: return .worlds
        case .analyticsDashboard: return .analytics
        case .profile: return .profile
        default: return .home
        }
    }
    
   
    private func screen(for tab: BottomBarTab) -> NavigationViewModel.Screen {
        switch tab {
        case .home: return .mainDashboard
        case .create: return .create
        case .worlds: return .worlds
        case .analytics: return .analyticsDashboard
        case .profile: return .profile
        }
    }

    var body: some View {
        let selectedTab = tab(for: navigation.currentScreen)
        HStack {
            Spacer()
           
            ForEach(BottomBarTab.allCases, id: \.self) { tab in
                TabBarItem(
                    iconName: tab.iconName,
                    label: tab.rawValue,
                    isSelected: selectedTab == tab
                ) {
                   
                    if selectedTab != tab {
                        navigation.currentScreen = screen(for: tab)
                    }
                }
                Spacer()
            }
        }

        .padding(.vertical, 12) 
        .padding(.horizontal, 0) 
        .background(
            Color(hex: "#5A3FA0").opacity(0.85)
        )
        .ignoresSafeArea(.container, edges: .bottom)
        .padding(.horizontal, 0)
        .padding(.bottom, 0) 
    }
}


struct TabBarItem: View {
    let iconName: String
    let label: String
    let isSelected: Bool
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            VStack(spacing: 4) {
                Image(systemName: iconName)
                    .font(.system(size: 20, weight: .medium))
                    .foregroundColor(isSelected ? .black : Color(hex: "#E6D6FF"))
                Text(label)
                    .font(.system(size: 11, weight: .medium))
                    .foregroundColor(isSelected ? .black : Color(hex: "#E6D6FF"))
            }
        }
    }
}

#if canImport(UIKit)
struct BlurView: UIViewRepresentable {
    var style: UIBlurEffect.Style = .systemMaterial
    func makeUIView(context: Context) -> UIVisualEffectView {
        return UIVisualEffectView(effect: UIBlurEffect(style: style))
    }
    func updateUIView(_ uiView: UIVisualEffectView, context: Context) {}
}
#endif


#Preview {
    BottombarView(navigation: NavigationViewModel())
}


