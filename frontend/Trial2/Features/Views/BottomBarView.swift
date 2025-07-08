import SwiftUI
#if canImport(UIKit)
import UIKit
#endif

// MARK: - BottomBarTab (Enum for Tab Identification)
enum BottomBarTab: String, CaseIterable {
    case home = "Home"
    case create = "Create"
    case worlds = "Worlds"
    case profile = "Profile"

    var iconName: String {
        switch self {
        case .home: return "house.fill"
        case .create: return "plus.circle.fill"
        case .worlds: return "globe.americas.fill"
        case .profile: return "person.fill"
        }
    }
}

// MARK: - BottombarView
struct BottombarView: View {
    @ObservedObject var navigation: NavigationViewModel
    
    // Helper to map NavigationViewModel.Screen to BottomBarTab
    private func tab(for screen: NavigationViewModel.Screen) -> BottomBarTab {
        switch screen {
        case .mainDashboard: return .home
        case .create, .comicGenerator: return .create
        case .worlds, .dreamWorld, .mindWorld, .imaginationWorld: return .worlds
        case .profile: return .profile
        default: return .home
        }
    }
    
    // Helper to map BottomBarTab to NavigationViewModel.Screen
    private func screen(for tab: BottomBarTab) -> NavigationViewModel.Screen {
        switch tab {
        case .home: return .mainDashboard
        case .create: return .create
        case .worlds: return .worlds
        case .profile: return .profile
        }
    }

    var body: some View {
        let selectedTab = tab(for: navigation.currentScreen)
        HStack {
            Spacer()
            // Iterate over all cases of our enum to create tabs
            ForEach(BottomBarTab.allCases, id: \.self) { tab in
                TabBarItem(
                    iconName: tab.iconName,
                    label: tab.rawValue,
                    isSelected: selectedTab == tab
                ) {
                    // Only update if not already selected
                    if selectedTab != tab {
                        navigation.currentScreen = screen(for: tab)
                    }
                }
                Spacer()
            }
        }
        // Restore original vertical padding
        .padding(.vertical, 12) // modest height
        .padding(.horizontal, 0) // edge-to-edge
        .background(
            Color(hex: "#5A3FA0").opacity(0.85)
        )
        .ignoresSafeArea(.container, edges: .bottom)
        .padding(.horizontal, 0) // no extra margin
        .padding(.bottom, 0) // flush with bottom
    }
}

// MARK: - TabBarItem
struct TabBarItem: View {
    let iconName: String
    let label: String
    let isSelected: Bool
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            VStack(spacing: 2) {
                Image(systemName: iconName)
                    .font(.system(size: 26, weight: .semibold))
                    .foregroundColor(isSelected ? .black : Color(hex: "#E6D6FF"))
                Text(label)
                    .font(.system(size: 13, weight: .medium))
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

// MARK: - Preview
#Preview {
    BottombarView(navigation: NavigationViewModel())
}


