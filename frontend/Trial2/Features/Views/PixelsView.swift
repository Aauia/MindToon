import SwiftUI

// MARK: - Pixel Sky (Stars + Optional Moon)
struct PixelSkyView: View {
    var showMoon: Bool = true
    var body: some View {
        ZStack {
            ForEach(0..<32, id: \.self) { i in
                let x = CGFloat.random(in: 0...UIScreen.main.bounds.width)
                let y = CGFloat.random(in: 0...UIScreen.main.bounds.height * 0.6)
                Circle()
                    .fill(Color.white.opacity(.random(in: 0.7...1)))
                    .frame(width: [2, 3, 4].randomElement()!, height: [2, 3, 4].randomElement()!)
                    .position(x: x, y: y)
            }
            if showMoon {
                CrescentMoon()
                    .frame(width: 48, height: 48)
                    .position(x: UIScreen.main.bounds.width - 60, y: 90)
            }
        }
    }
}

struct CrescentMoon: View {
    var body: some View {
        ZStack {
            Circle()
                .fill(Color.yellow.opacity(0.85))
            Circle()
                .fill(Color(red: 0.75, green: 0.67, blue: 0.95))
                .offset(x: 12)
        }
        .compositingGroup()
    }
}

struct PixelBuilding: Identifiable {
    let id = UUID()
    let width: CGFloat
    let height: CGFloat
    let color: Color
    let windowPattern: [[Bool]]
    let windowColor: Color
    let hasAntenna: Bool
}

struct PixelBuildingView: View {
    let building: PixelBuilding
    let isReflection: Bool
    let twinklePhase: Double
    var body: some View {
        VStack(spacing: 0) {
            if building.hasAntenna && !isReflection {
                Rectangle()
                    .fill(Color.white.opacity(0.7))
                    .frame(width: 2, height: 10)
            }
            Rectangle()
                .fill(building.color)
                .frame(width: building.width, height: building.height)
                .overlay(
                    PixelWindowsView(windowPattern: building.windowPattern, windowColor: building.windowColor, isReflection: isReflection, twinklePhase: twinklePhase, buildingID: building.id),
                    alignment: .topLeading
                )
        }
    }
}

struct PixelWindowsView: View {
    let windowPattern: [[Bool]]
    let windowColor: Color
    let isReflection: Bool
    let twinklePhase: Double
    let buildingID: UUID
    var body: some View {
        GeometryReader { geo in
            let windowSize: CGFloat = 5
            let windowSpacing: CGFloat = 3
            let padding: CGFloat = 5
            let totalWidth = CGFloat(windowPattern.first?.count ?? 0) * windowSize + CGFloat(max(0, (windowPattern.first?.count ?? 0) - 1)) * windowSpacing
            let totalHeight = CGFloat(windowPattern.count) * windowSize + CGFloat(max(0, windowPattern.count - 1)) * windowSpacing
            VStack(spacing: windowSpacing) {
                ForEach(0..<windowPattern.count) { row in
                    HStack(spacing: windowSpacing) {
                        ForEach(0..<windowPattern[row].count) { col in
                            if windowPattern[row][col] {
                                // Shine and twinkle effect
                                let twinkleSeed = Double(abs(buildingID.hashValue ^ (row * 31 + col * 17)))
                                let base = sin(twinklePhase * 2 + twinkleSeed * 0.3)
                                // Occasionally flash to full brightness
                                let flash = (sin(twinklePhase * 6 + twinkleSeed * 0.7) > 0.98) ? 1.0 : 0.0
                                let twinkle = max(0.5, 0.7 + 0.3 * base) + flash * 0.7
                                Rectangle()
                                    .fill(windowColor.opacity((isReflection ? 0.4 : 1.0) * twinkle))
                                    .frame(width: windowSize, height: windowSize)
                                    .shadow(color: windowColor.opacity(twinkle * 0.7), radius: twinkle > 1.1 ? 4 : 0)
                            } else {
                                Rectangle()
                                    .fill(Color.clear)
                                    .frame(width: windowSize, height: windowSize)
                            }
                        }
                    }
                }
            }
            .frame(width: totalWidth, height: totalHeight, alignment: .topLeading)
            .position(x: padding + totalWidth / 2, y: padding + totalHeight / 2)
        }
    }
}

struct PixelCityView: View {
    let buildings: [PixelBuilding]
    let isReflection: Bool
    @State private var twinklePhase: Double = 0

    var body: some View {
        HStack(alignment: .bottom, spacing: 2) {
            ForEach(buildings) { building in
                PixelBuildingView(building: building, isReflection: isReflection, twinklePhase: twinklePhase)
            }
        }
        .scaleEffect(y: isReflection ? -1 : 1)
        .opacity(isReflection ? 0.6 : 1.0)
        .onAppear {
            Timer.scheduledTimer(withTimeInterval: 0.7, repeats: true) { _ in
                withAnimation(.easeInOut(duration: 0.7)) {
                    twinklePhase = Double.random(in: 0...10000)
                }
            }
        }
    }
}

// Helper to generate a city row
func generatePixelBuildings() -> [PixelBuilding] {
    let palette: [Color] = [
        Color(hex: "#B79EFF"), Color(hex: "#A18AFF"), Color(hex: "#7B6AFF"),
        Color(hex: "#6A5AFF"), Color(hex: "#8A7BFF"), Color(hex: "#C1B6FF")
    ]
    let windowColors: [Color] = [Color.yellow, Color.white, Color.cyan.opacity(0.8)]
    var buildings: [PixelBuilding] = []
    let count = 18
    for i in 0..<count {
        let width = CGFloat(Int.random(in: 18...32))
        let height = CGFloat(Int.random(in: 60...140))
        let color = palette.randomElement()!
        let windowColor = windowColors.randomElement()!
        // Calculate max number of columns and rows so windows fit inside the building
        let windowSize: CGFloat = 5
        let windowSpacing: CGFloat = 3
        let padding: CGFloat = 5
        let maxCols = max(1, Int((width - 2 * padding + windowSpacing) / (windowSize + windowSpacing)))
        let maxRows = max(1, Int((height - 2 * padding + windowSpacing) / (windowSize + windowSpacing)))
        var windowPattern: [[Bool]] = []
        for _ in 0..<maxRows {
            var row: [Bool] = []
            for _ in 0..<maxCols {
                row.append(Bool.random())
            }
            windowPattern.append(row)
        }
        let hasAntenna = Bool.random() && i % 4 == 0
        buildings.append(PixelBuilding(width: width, height: height, color: color, windowPattern: windowPattern, windowColor: windowColor, hasAntenna: hasAntenna))
    }
    return buildings
}

extension Color {
    init(hex: String) {
        let hex = hex.trimmingCharacters(in: .whitespacesAndNewlines).dropFirst()
        var int = UInt64()
        Scanner(string: String(hex)).scanHexInt64(&int)
        let r = Double((int >> 16) & 0xFF) / 255
        let g = Double((int >> 8) & 0xFF) / 255
        let b = Double(int & 0xFF) / 255
        self.init(red: r, green: g, blue: b)
    }
}


struct CosmicBackground: View {
    var body: some View {
        ZStack {
            // Gradient
            LinearGradient(
                gradient: Gradient(colors: [Color(hex: "#5A3FA0"), Color(hex: "#E6D6FF")]),
                startPoint: .top,
                endPoint: .bottom
            )
            .ignoresSafeArea()

            // Stars
            ForEach(0..<40) { _ in
                Circle()
                    .fill(Color.white.opacity(.random(in: 0.5...1)))
                    .frame(width: CGFloat.random(in: 2...4), height: CGFloat.random(in: 2...4))
                    .position(
                        x: CGFloat.random(in: 0...UIScreen.main.bounds.width),
                        y: CGFloat.random(in: 0...UIScreen.main.bounds.height)
                    )
            }

            // Optional: Clouds at the bottom
            VStack {
                Spacer()
                ForEach(0..<6) { _ in
                    Ellipse()
                        .fill(Color.pink.opacity(0.3))
                        .frame(width: CGFloat.random(in: 80...180), height: CGFloat.random(in: 30...60))
                        .offset(x: CGFloat.random(in: -120...120), y: CGFloat.random(in: 0...40))
                        .blur(radius: 2)
                }
            }
        }
    }
} 


