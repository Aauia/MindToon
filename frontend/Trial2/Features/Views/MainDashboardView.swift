import SwiftUI


struct MainDashboardView: View {
    @State private var twinkleToggle = false
    @ObservedObject var navigation: NavigationViewModel

    var body: some View {
        ZStack {
            // Gradient Sky
            LinearGradient(
                gradient: Gradient(colors: [
                    Color(red: 0.85, green: 0.73, blue: 0.94), // lavender
                    Color(red: 0.99, green: 0.85, blue: 0.85)  // peach
                ]),
                startPoint: .top,
                endPoint: .bottom
            )
            .ignoresSafeArea()

            // Stars
            ForEach(0..<30, id: \.self) { _ in
                Circle()
                    .fill(Color.white.opacity(0.8))
                    .frame(width: 2, height: 2)
                    .position(
                        x: CGFloat.random(in: 0...UIScreen.main.bounds.width),
                        y: CGFloat.random(in: 0...UIScreen.main.bounds.height * 0.4)
                    )
            }

            // Moon + Crescent
            VStack {
                ZStack {
                    // Main Moon with outline
                    Circle()
                        .fill(Color(red: 0.95, green: 0.98, blue: 1.0))
                        .frame(width: 200, height: 200)
                        .overlay(
                            Circle()
                                .stroke(Color.black.opacity(0.2), lineWidth: 2)
                        )
                        .shadow(color: Color.white.opacity(0.6), radius: 20)

                    // Crescent Moon
                    ZStack {
                        Circle()
                            .fill(Color.yellow.opacity(0.5))
                            .frame(width: 70, height: 70)
                        Circle()
                            .fill(Color(red: 0.85, green: 0.73, blue: 0.94))
                            .frame(width: 60, height: 60)
                            .offset(x: 10)
                    }
                    .offset(x: 90, y: -60)
                }
                .padding(.top, 60)

                Spacer()
            }

            // Pixel City + Reflection
            let buildings = generatePixelBuildings()
            VStack(spacing: 0) {
                PixelCityView(buildings: buildings, isReflection: false)
                ZStack {
                    // Water color overlay
                    Rectangle()
                        .fill(Color(red: 0.55, green: 0.85, blue: 0.95).opacity(0.85))
                        .frame(height: 110)
                        .offset(y: 55)
                        .blendMode(.color)
                        .mask(
                            PixelCityView(buildings: buildings, isReflection: true)
                                .opacity(0.7)
                        )
                    // Pixelated reflection
                    PixelCityView(buildings: buildings, isReflection: true)
                        .opacity(0.5)
                }
                
            }
            
            
            
            .padding(.bottom, 72) // leave space for bottom bar
            .frame(maxHeight: .infinity, alignment: .bottom)
            // Animated typewriter text below the moon
            TypewriterText(text: "Welcome to MindToon! Unleash your imagination, one comic at a time.")
                .font(.custom("Noteworthy", size: 22))
                .foregroundColor(Color.black)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 56)
                .padding(.bottom, 16)

           
            
            // 🟪 Bottom bar
       VStack(spacing: 0) {
                Spacer()
                BottombarView(navigation: navigation)
                    .frame(maxWidth: 420)
                    .padding(.horizontal, 16)
                    .background(Color.white.opacity(0.05))
                    .cornerRadius(20)
                    .shadow(color: Color.black.opacity(0.1), radius: 8, y: -2)
                    .frame(maxWidth: .infinity)
                        .background(Color(hex: "#5A3FA0"))
                
                
            }
            
            .ignoresSafeArea(.keyboard)
        }
        .onAppear {
            Timer.scheduledTimer(withTimeInterval: 1.2, repeats: true) { _ in
                twinkleToggle.toggle()
            }
        }
    }
}
// MARK: - Preview
struct MainDashboardView_Previews: PreviewProvider {
    static var previews: some View {
        MainDashboardView(navigation: NavigationViewModel())
    }
}

struct TypewriterText: View {
    let text: String
    @State private var displayedText = ""
    @State private var charIndex = 0
    let typingInterval = 0.045

    var body: some View {
        Text(displayedText)
            .onAppear {
                displayedText = ""
                charIndex = 0
                typeNextChar()
            }
    }

    private func typeNextChar() {
        guard charIndex < text.count else { return }
        DispatchQueue.main.asyncAfter(deadline: .now() + typingInterval) {
            let nextIndex = text.index(text.startIndex, offsetBy: charIndex + 1)
            displayedText = String(text[..<nextIndex])
            charIndex += 1
            typeNextChar()
        }
    }
}

