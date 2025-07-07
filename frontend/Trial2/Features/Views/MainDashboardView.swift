import SwiftUI

// MARK: - MainDashboardView
struct MainDashboardView: View {
    @ObservedObject var navigation: NavigationViewModel

    var body: some View {
        ZStack { // Use ZStack to layer the pixel art background and dashboard content
            // MARK: - Pixel Art Background (Adapted from FlyingWitchView)
            ZStack {
                // Background Gradient
                LinearGradient(gradient: Gradient(colors: [
                    Color(red: 207/255, green: 167/255, blue: 217/255), // Top light purple
                    Color(red: 237/255, green: 204/255, blue: 234/255)  // Mid light pink
                ]),
                               startPoint: .top, endPoint: .center)

                LinearGradient(gradient: Gradient(colors: [
                    Color(red: 250/255, green: 232/255, blue: 238/255), // Upper yellowish/pink
                    Color(red: 231/255, green: 208/255, blue: 229/255)  // Lower light purple
                ]),
                               startPoint: .center, endPoint: .bottom)

                // Stars
                ForEach(0..<50) { _ in
                    StarShape()
                        .fill(Color.white.opacity(0.3))
                        .frame(width: CGFloat.random(in: 2...6), height: CGFloat.random(in: 2...6))
                        .position(x: CGFloat.random(in: 0...UIScreen.main.bounds.width),
                                  y: CGFloat.random(in: 0...UIScreen.main.bounds.height * 0.6))
                }

                // Moon
                Circle()
                    .fill(Color.white)
                    .frame(width: 150, height: 150)
                    .position(x: UIScreen.main.bounds.width * 0.5, y: UIScreen.main.bounds.height * 0.25)

                // Crescent Moon Outline
                MoonOutlineShape()
                    .stroke(Color(red: 240/255, green: 247/255, blue: 187/255), lineWidth: 8)
                    .frame(width: 60, height: 100)
                    .position(x: UIScreen.main.bounds.width * 0.7, y: UIScreen.main.bounds.height * 0.18)

                // Witch Silhouette
                Image("witch_silhouette") // Ensure this image is in your Assets.xcassets
                    .resizable()
                    .scaledToFit()
                    .frame(width: 180)
                    .position(x: UIScreen.main.bounds.width * 0.45, y: UIScreen.main.bounds.height * 0.23)

                // Cityscape (positioned lower for dashboard content)
                GeometryReader { geometry in
                    VStack { // Use a VStack to group the cityscape and reflection
                        Spacer() // Push cityscape to the bottom of its ZStack layer
                        HStack(spacing: -10) {
                            BuildingShape(heightScale: 0.3, windowColor: Color(red: 255/255, green: 255/255, blue: 153/255).opacity(0.8))
                            BuildingShape(heightScale: 0.45, windowColor: Color(red: 255/255, green: 255/255, blue: 153/255).opacity(0.6))
                            BuildingShape(heightScale: 0.35, windowColor: Color(red: 255/255, green: 255/255, blue: 153/255).opacity(0.7))
                            BuildingShape(heightScale: 0.55, windowColor: Color(red: 255/255, green: 255/255, blue: 153/255).opacity(0.9))
                            BuildingShape(heightScale: 0.4, windowColor: Color(red: 255/255, green: 255/255, blue: 153/255).opacity(0.5))
                            BuildingShape(heightScale: 0.3, windowColor: Color(red: 255/255, green: 255/255, blue: 153/255).opacity(0.8))
                            BuildingShape(heightScale: 0.45, windowColor: Color(red: 255/255, green: 255/255, blue: 153/255).opacity(0.6))
                            BuildingShape(heightScale: 0.35, windowColor: Color(red: 255/255, green: 255/255, blue: 153/255).opacity(0.7))
                        }
                        .frame(height: geometry.size.height * 0.3)
                        .scaleEffect(x: 1.2, y: 1, anchor: .bottom)
                        .offset(y: 20) // Nudge down

                        // Water Reflection
                        HStack(spacing: -10) {
                            BuildingShape(heightScale: 0.3, windowColor: Color(red: 173/255, green: 216/255, blue: 230/255).opacity(0.5))
                                .scaleEffect(y: -1)
                            BuildingShape(heightScale: 0.45, windowColor: Color(red: 173/255, green: 216/255, blue: 230/255).opacity(0.4))
                                .scaleEffect(y: -1)
                            BuildingShape(heightScale: 0.35, windowColor: Color(red: 173/255, green: 216/255, blue: 230/255).opacity(0.45))
                                .scaleEffect(y: -1)
                            BuildingShape(heightScale: 0.55, windowColor: Color(red: 173/255, green: 216/255, blue: 230/255).opacity(0.6))
                                .scaleEffect(y: -1)
                            BuildingShape(heightScale: 0.4, windowColor: Color(red: 173/255, green: 216/255, blue: 230/255).opacity(0.35))
                                .scaleEffect(y: -1)
                            BuildingShape(heightScale: 0.3, windowColor: Color(red: 173/255, green: 216/255, blue: 230/255).opacity(0.5))
                                .scaleEffect(y: -1)
                            BuildingShape(heightScale: 0.45, windowColor: Color(red: 173/255, green: 216/255, blue: 230/255).opacity(0.4))
                                .scaleEffect(y: -1)
                            BuildingShape(heightScale: 0.35, windowColor: Color(red: 173/255, green: 216/255, blue: 230/255).opacity(0.45))
                                .scaleEffect(y: -1)
                        }
                        .frame(height: geometry.size.height * 0.3)
                        .scaleEffect(x: 1.2, y: 1, anchor: .top)
                        .offset(y: -20) // Nudge up

                        Rectangle()
                            .fill(Color(red: 153/255, green: 204/255, blue: 204/255).opacity(0.7))
                            .frame(height: UIScreen.main.bounds.height * 0.3)
                    }
                }
            }
            .ignoresSafeArea() // Ensure the background fills the entire screen

            // MARK: - Dashboard Content Overlay
            VStack(spacing: 0) {
                // This ScrollView will contain your original dashboard elements
                ScrollView {
                    VStack(spacing: 20) {
                        Spacer() // Pushes content towards center/top

                        Image(systemName: "brain.head.profile")
                            .resizable()
                            .scaledToFit()
                            .frame(width: 150, height: 150)
                            .foregroundColor(.white) // Changed to white for better contrast
                            .padding(.bottom, 20)
                            .shadow(radius: 10) // Add a subtle shadow to make it pop

                        Text("Welcome to MindToon!")
                            .font(.largeTitle)
                            .fontWeight(.bold)
                            .foregroundColor(.white) // Changed to white for better contrast
                            .shadow(radius: 5)

                        Text("How can I help you today?")
                            .font(.title2)
                            .foregroundColor(.white.opacity(0.8)) // Changed to white for better contrast
                            .shadow(radius: 5)

                        // Test Image Generator Button
                        VStack(spacing: 12) {
                            Text("🧪 Testing Features")
                                .font(.headline)
                                .foregroundColor(.white) // Changed to white
                                .shadow(radius: 3)
                            
                            Button(action: {
                                navigation.navigateTo(.imageGenerator)
                            }) {
                                HStack {
                                    Image(systemName: "photo.badge.plus")
                                        .font(.title2)
                                    Text("Test Image Generator")
                                        .font(.headline)
                                }
                                .foregroundColor(.purple) // Button text color
                                .padding()
                                .frame(maxWidth: .infinity)
                                .background(Color.white.opacity(0.9)) // Semi-transparent white background
                                .cornerRadius(15)
                                .shadow(radius: 5) // Add shadow to button
                            }
                        }
                        .padding(.horizontal)
                        .padding(.top, 20)

                        Spacer() // Pushes content up, allowing bottom bar to stick
                    }
                    .frame(maxWidth: .infinity, minHeight: UIScreen.main.bounds.height - 80) // Adjust minHeight to account for bottom bar
                    // The .background() here would apply to the scrollable content, not the whole view
                }
                .padding(.bottom, -8) // Adjust to prevent extra padding above custom tab bar

                // Integrate the separate BottombarView here
                BottombarView(navigation: navigation)
                    .frame(maxHeight: 80) // Fixed height for the bottom bar
                    .background(Color.clear) // Make sure bottom bar is clear or frosted to blend
            }
        }
        // No .navigationBarTitleDisplayMode or .background here, as it's handled by ZStack content
        // and a NavigationView should wrap this view from outside if needed.
    }
}

// MARK: - Helper Views for Dashboard (WorldButton unchanged)

// You need to ensure these custom shapes are defined in the same file or accessible:
// MARK: - Custom Shape: Star
struct StarShape: Shape {
    func path(in rect: CGRect) -> Path {
        var path = Path()
        let center = CGPoint(x: rect.midX, y: rect.midY)
        let points = 5
        let innerRadius = min(rect.width, rect.height) / 4
        let outerRadius = min(rect.width, rect.height) / 2
        
        for i in 0..<points * 2 {
            let radius = i.isMultiple(of: 2) ? outerRadius : innerRadius
            let angle = CGFloat(i) * .pi / CGFloat(points) - .pi / 2
            let x = center.x + radius * cos(angle)
            let y = center.y + radius * sin(angle)
            if i == 0 {
                path.move(to: CGPoint(x: x, y: y))
            } else {
                path.addLine(to: CGPoint(x: x, y: y))
            }
        }
        path.closeSubpath()
        return path
    }
}

// MARK: - Custom Shape: Moon Outline (Crescent)
struct MoonOutlineShape: Shape {
    func path(in rect: CGRect) -> Path {
        var path = Path()
        
        path.addArc(center: CGPoint(x: rect.midX, y: rect.midY),
                    radius: rect.height / 2,
                    startAngle: Angle(degrees: 20),
                    endAngle: Angle(degrees: 200),
                    clockwise: false)
        
        path.addArc(center: CGPoint(x: rect.midX * 0.8, y: rect.midY),
                    radius: rect.height / 2 * 0.8,
                    startAngle: Angle(degrees: 200),
                    endAngle: Angle(degrees: 20),
                    clockwise: true)
        
        return path
    }
}

// MARK: - Custom Shape: Building
struct BuildingShape: Shape {
    var heightScale: CGFloat
    var windowColor: Color
    
    func path(in rect: CGRect) -> Path {
        var path = Path()
        let width = rect.width
        let height = rect.height * heightScale
        
        path.addRect(CGRect(x: 0, y: rect.maxY - height, width: width, height: height))
        
        let windowWidth = width / 4
        let windowHeight = height / 8
        let padding: CGFloat = 5
        
        for row in 0..<4 {
            for col in 0..<3 {
                let x = padding + CGFloat(col) * (windowWidth + padding)
                let y = rect.maxY - height + padding + CGFloat(row) * (windowHeight + padding)
                path.addRect(CGRect(x: x, y: y, width: windowWidth, height: windowHeight))
            }
        }
        
        return path.applying(CGAffineTransform(translationX: 0, y: 0))
    }
}

// MARK: - Preview
// Ensure NavigationViewModel and BottombarView are available for preview
struct MainDashboardView_Previews: PreviewProvider {
    static var previews: some View {
        // You might need to provide mock implementations or actual instances for preview
        MainDashboardView(navigation: NavigationViewModel())
    }
}


// Dummy BottombarView for preview/compilation if not defined elsewhere

