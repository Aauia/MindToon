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
            
            // 🟪 Bottom bar
            VStack(spacing: 0) {
                Spacer()
                BottombarView(navigation: navigation)
                
                // --- TEST: Fetch Detailed Scenario by Comic ID ---
              
                // --- END TEST ---
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


