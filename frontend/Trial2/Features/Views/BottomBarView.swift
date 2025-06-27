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
    @State private var selectedTab: BottomBarTab = .home

    var body: some View {
        HStack {
            Spacer()
            // Iterate over all cases of our enum to create tabs
            ForEach(BottomBarTab.allCases, id: \.self) { tab in
                TabBarItem(
                    iconName: tab.iconName,
                    label: tab.rawValue,
                    isSelected: self.selectedTab == tab
                ) {
                    self.selectedTab = tab // Update selected tab
                    // Trigger navigation based on the tapped tab
                    switch tab {
                    case .home:
                        navigation.currentScreen = .mainDashboard
                    case .create:
                        navigation.currentScreen = .create
                    case .worlds:
                        navigation.currentScreen = .worlds
                    case .profile:
                        navigation.currentScreen = .profile
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
