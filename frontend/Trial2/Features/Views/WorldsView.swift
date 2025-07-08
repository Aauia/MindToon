import SwiftUI

struct WorldsView: View {
    @ObservedObject var navigation: NavigationViewModel
    @State private var twinkle = false

    var body: some View {
        ZStack {
            // 🌌 Background gradient — soft but flat feel
            LinearGradient(
                gradient: Gradient(colors: [
                    Color(hex: "#FCDADA"),
                    Color(hex: "#D7A8F0")
                ]),
                startPoint: .top,
                endPoint: .bottom
            )
            .ignoresSafeArea()

            // ✨ Light twinkling stars
            ForEach(0..<20, id: \.self) { _ in
                Circle()
                    .fill(Color.white.opacity(twinkle ? 0.25 : 0.5))
                    .frame(width: 2, height: 2)
                    .position(
                        x: CGFloat.random(in: 0...UIScreen.main.bounds.width),
                        y: CGFloat.random(in: 0...UIScreen.main.bounds.height * 0.75)
                    )
            }

            VStack(spacing: 40) {
                Spacer().frame(height: 60)

                // Title
                Text("Explore Your Worlds")
                    .font(.title2)
                    .fontWeight(.bold)
                    .foregroundColor(.black)
                    .padding(.bottom, 10)

                // ✨ World Planet Buttons
                VStack(spacing: 28) {
                    WorldOrb2D(
                        title: "Planet of Dreams",
                        subtitle: "Dreamboards & novels",
                        icon: "moon.stars",
                        color: Color(hex: "#FFD6F5"),
                        action: {
                            navigation.currentScreen = .dreamWorld
                        }
                    )

                    WorldOrb2D(
                        title: "Planet of Mind",
                        subtitle: "Essays & reflections",
                        icon: "brain.head.profile",
                        color: Color(hex: "#C5F3FF"),
                        action: {
                            navigation.currentScreen = .mindWorld
                        }
                    )

                    WorldOrb2D(
                        title: "Planet of Fantasy",
                        subtitle: "Comics & manga",
                        icon: "sparkles",
                        color: Color(hex: "#FBC1FF"),
                        action: {
                            navigation.currentScreen = .imaginationWorld
                        }
                    )
                }

                Spacer()
            }

            // 🟪 Bottom bar
            VStack(spacing: 0) {
                Spacer()
                BottombarView(navigation: navigation)

            }
            .ignoresSafeArea(.keyboard)
        }
        .onAppear {
            withAnimation(Animation.easeInOut(duration: 2).repeatForever()) {
                twinkle.toggle()
            }
        }

        .navigationBarTitleDisplayMode(.inline)
    }
}


struct WorldOrb2D: View {
    var title: String
    var subtitle: String
    var icon: String
    var color: Color
    var action: () -> Void

    var body: some View {
        Button(action: action) {
            HStack(spacing: 16) {
                ZStack {
                    Rectangle() // Pixelated orb background
                        .fill(color.opacity(0.8))
                        .frame(width: 60, height: 60)
                        .overlay(
                            Rectangle()
                                .stroke(Color.white.opacity(0.4), lineWidth: 1) // White pixelated border
                        )

                    Image(systemName: icon)
                        .font(.system(size: 28, weight: .bold)) // Larger, bolder icon
                        .foregroundColor(.white) // White icon
                        .shadow(color: .black.opacity(0.3), radius: 1, x: 1, y: 1) // Subtle shadow
                }

                VStack(alignment: .leading, spacing: 2) {
                    Text(title)
                        .font(.custom("PixeloidSans", size: 18)) // Placeholder for pixel font
                        .fontWeight(.bold)
                        .foregroundColor(.white)
                        .shadow(color: .black.opacity(0.3), radius: 1, x: 1, y: 1)
                    Text(subtitle)
                        .font(.custom("PixeloidSans", size: 12)) // Placeholder for pixel font
                        .foregroundColor(.white.opacity(0.8))
                        .shadow(color: .black.opacity(0.2), radius: 1, x: 0.5, y: 0.5)
                }

                Spacer()

                Image(systemName: "chevron.right")
                    .foregroundColor(.white.opacity(0.7))
                    .font(.system(size: 16, weight: .bold)) // Bolder chevron
            }
            .padding(12) // Reduced padding slightly
            .background(Color(hex: "#483D8B").opacity(0.6)) // Dark slate blue, semi-transparent background
            .clipShape(RoundedRectangle(cornerRadius: 15, style: .continuous)) // Less rounded corners
            .overlay(
                RoundedRectangle(cornerRadius: 15)
                    .stroke(Color(hex: "#BA55D3").opacity(0.7), lineWidth: 2) // Medium Orchid border
            )
        }
        .padding(.horizontal, 16) // Slightly less horizontal padding
    }
}

// Extension to handle Hex Colors


#Preview {
    WorldsView(navigation: NavigationViewModel())
}
