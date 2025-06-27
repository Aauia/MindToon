import SwiftUI

// MARK: - WorldsView
struct WorldsView: View {
    @ObservedObject var navigation: NavigationViewModel

    var body: some View {
        VStack(spacing: 0) { // Main VStack to hold content and bottom bar
            // ZStack for background and world selections
            ZStack {
                // Background: Space/Galaxy theme as per Figma
                // Replace with your actual image asset like Image("space_background")
                LinearGradient(gradient: Gradient(colors: [Color.purple.opacity(0.8), Color.blue.opacity(0.8)]), startPoint: .topLeading, endPoint: .bottomTrailing)
                    .edgesIgnoringSafeArea(.all)

                // Content: World selections
                VStack(spacing: 40) {
                    Text("Explore Your Worlds")
                        .font(.largeTitle)
                        .fontWeight(.bold)
                        .foregroundColor(.white)
                        .shadow(radius: 5)
                        .padding(.top, 20)

                    Spacer()

                    // Dream World
                    WorldSelectionButton(
                        title: "Planet of Dreams",
                        description: "Your dream novels & dreamboards",
                        color: Color.pink.opacity(0.7)
                    ) {
                        navigation.currentScreen = .dreamWorld
                    }

                    // Mind World
                    WorldSelectionButton(
                        title: "Planet of Mind",
                        description: "Your graphic essays & reflections",
                        color: Color.green.opacity(0.7)
                    ) {
                        navigation.currentScreen = .mindWorld
                    }

                    // Script World (Planet of Fantasy/Creativity)
                    WorldSelectionButton(
                        title: "Planet of Fantasy",
                        description: "Your comic projects, manga pages, and visual drafts",
                        color: Color.orange.opacity(0.7)
                    ) {
                        navigation.currentScreen = .imaginationWorld
                    }

                    Spacer()
                }
                .padding(.horizontal)
            }

            // Persistent Bottom Bar View, as seen in Figma and other views
            BottombarView(navigation: navigation)
                .frame(maxHeight: 80)
        }
        .toolbar {
            CustomTopBarContent(title: "Worlds", showBackButton: true, leadingAction: {
                navigation.currentScreen = .mainDashboard // Or previous screen
            })
        }
        .navigationBarTitleDisplayMode(.inline)
    }
}

// MARK: - WorldSelectionButton (Reusable Helper View)
struct WorldSelectionButton: View {
    let title: String
    let description: String
    let color: Color
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            HStack {
                Circle() // Placeholder for planet image
                    .fill(color)
                    .frame(width: 60, height: 60)
                    .overlay(
                        Image(systemName: "sparkles.square.fill") // Example icon
                            .font(.title2)
                            .foregroundColor(.white)
                    )
                    .shadow(color: color.opacity(0.5), radius: 10, x: 0, y: 5)

                VStack(alignment: .leading) {
                    Text(title)
                        .font(.title2)
                        .fontWeight(.semibold)
                        .foregroundColor(.white)
                    Text(description)
                        .font(.subheadline)
                        .foregroundColor(.white.opacity(0.8))
                }
                Spacer()
                Image(systemName: "chevron.right")
                    .foregroundColor(.white)
            }
            .padding()
            .background(Color.white.opacity(0.1))
            .cornerRadius(15)
            .overlay(
                RoundedRectangle(cornerRadius: 15)
                    .stroke(color, lineWidth: 2)
            )
        }
    }
}

// MARK: - Preview
#Preview {
    WorldsView(navigation: NavigationViewModel())
}
