
import SwiftUI

// MARK: - Pixel Sky (Stars + Optional Moon)
struct PixelSkyView: View {
    var showMoon: Bool = true
    var body: some View {
        ZStack {
            ForEach(0..<32, id: \ .self) { i in
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

// MARK: - Animated Pixel Star Field
struct PixelStarFieldView: View {
    let starCount: Int = 48
    let starPositions: [(CGFloat, CGFloat, Double)] = (0..<48).map { _ in
        (
            CGFloat.random(in: 0...UIScreen.main.bounds.width),
            CGFloat.random(in: 0...UIScreen.main.bounds.height),
            Double.random(in: 0...2 * .pi)
        )
    }
    var body: some View {
        TimelineView(.animation) { timeline in
            let t = timeline.date.timeIntervalSinceReferenceDate
            ZStack {
                ForEach(0..<starCount, id: \ .self) { i in
                    let (x, y, phase) = starPositions[i]
                    let twinkle = 0.6 + 0.4 * abs(sin(t * 0.8 + phase))
                    let floatY = y + CGFloat(sin(t * 0.7 + phase)) * 3
                    Circle()
                        .fill(Color.white.opacity(twinkle))
                        .frame(width: [2, 3, 4].randomElement()!, height: [2, 3, 4].randomElement()!)
                        .position(x: x, y: floatY)
                }
            }
        }
    }
}

// MARK: - Pixel Moon (Large, for Dashboard)
struct PixelMoonView: View {
    var body: some View {
        ZStack {
            Circle()
                .fill(Color.yellow.opacity(0.85))
                .frame(width: 80, height: 80)
            Circle()
                .fill(Color(red: 0.75, green: 0.67, blue: 0.95))
                .frame(width: 80, height: 80)
                .offset(x: 24)
        }
        .compositingGroup()
    }
}

// MARK: - Pixel Cityscape (with optional reflection)
struct PixelCityscapeView: View {
    var withReflection: Bool = true
    var body: some View {
        GeometryReader { geo in
            let w = geo.size.width
            let h = geo.size.height
            ZStack(alignment: .bottom) {
                // City buildings
                Path { path in
                    path.move(to: CGPoint(x: 0, y: h * 0.5))
                    path.addLine(to: CGPoint(x: 0, y: h * 0.2))
                    path.addLine(to: CGPoint(x: w * 0.08, y: h * 0.1))
                    path.addLine(to: CGPoint(x: w * 0.15, y: h * 0.3))
                    path.addLine(to: CGPoint(x: w * 0.22, y: h * 0.18))
                    path.addLine(to: CGPoint(x: w * 0.3, y: h * 0.35))
                    path.addLine(to: CGPoint(x: w * 0.38, y: h * 0.12))
                    path.addLine(to: CGPoint(x: w * 0.45, y: h * 0.28))
                    path.addLine(to: CGPoint(x: w * 0.52, y: h * 0.15))
                    path.addLine(to: CGPoint(x: w * 0.6, y: h * 0.32))
                    path.addLine(to: CGPoint(x: w * 0.68, y: h * 0.2))
                    path.addLine(to: CGPoint(x: w * 0.75, y: h * 0.38))
                    path.addLine(to: CGPoint(x: w * 0.82, y: h * 0.1))
                    path.addLine(to: CGPoint(x: w * 0.9, y: h * 0.3))
                    path.addLine(to: CGPoint(x: w, y: h * 0.18))
                    path.addLine(to: CGPoint(x: w, y: h * 0.5))
                    path.closeSubpath()
                }
                .fill(LinearGradient(
                    gradient: Gradient(colors: [
                        Color(red: 0.7, green: 0.6, blue: 0.95),
                        Color(red: 0.6, green: 0.4, blue: 0.8),
                        Color(red: 0.5, green: 0.3, blue: 0.7)
                    ]),
                    startPoint: .top,
                    endPoint: .bottom
                ))
                .shadow(color: Color.purple.opacity(0.18), radius: 8, x: 0, y: 4)

                // Windows
                ForEach(0..<18, id: \ .self) { i in
                    let x = CGFloat.random(in: 0...(w - 10))
                    let y = CGFloat.random(in: h * 0.2...h * 0.45)
                    Rectangle()
                        .fill(Color.yellow.opacity(0.7))
                        .frame(width: 8, height: [10, 14, 18].randomElement()!)
                        .position(x: x, y: y)
                }

                // Reflection
                if withReflection {
                    Path { path in
                        path.move(to: CGPoint(x: 0, y: h * 0.5))
                        path.addLine(to: CGPoint(x: 0, y: h * 0.7))
                        path.addLine(to: CGPoint(x: w, y: h * 0.7))
                        path.addLine(to: CGPoint(x: w, y: h * 0.5))
                        path.closeSubpath()
                    }
                    .fill(LinearGradient(
                        gradient: Gradient(colors: [
                            Color(red: 0.7, green: 0.6, blue: 0.95).opacity(0.3),
                            Color(red: 0.5, green: 0.3, blue: 0.7).opacity(0.1)
                        ]),
                        startPoint: .top,
                        endPoint: .bottom
                    ))
                }
            }
        }
        .frame(height: 180)
    }
}
