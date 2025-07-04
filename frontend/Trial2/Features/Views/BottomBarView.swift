import SwiftUI

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
        .padding(.vertical, 10)
        .background(Color.purple.opacity(0.1).edgesIgnoringSafeArea(.bottom))
        .cornerRadius(20)
        .shadow(radius: 5)
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
            VStack {
                Image(systemName: iconName)
                    .font(.title2)
                Text(label)
                    .font(.caption2)
            }
            .foregroundColor(isSelected ? .black : .purple) // Change color if selected
        }
    }
}

// MARK: - Preview
#Preview {
    BottombarView(navigation: NavigationViewModel())
}
