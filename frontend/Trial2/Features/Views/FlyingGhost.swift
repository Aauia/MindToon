import SwiftUI

struct FlyingGhost: View {
    var body: some View {
        ZStack {
            // Ghost body
            Circle()
                .fill(Color.white.opacity(0.9))
                .frame(width: 40, height: 40)
                .shadow(radius: 5)

            // Eyes
            HStack(spacing: 10) {
                Circle()
                    .frame(width: 5)
                Circle()
                    .frame(width: 5)
            }
            .offset(y: -5)

            // Pencil Rocket
            Path { path in
                path.move(to: CGPoint(x: 20, y: 30))
                path.addLine(to: CGPoint(x: 60, y: 20))
                path.addLine(to: CGPoint(x: 65, y: 25))
                path.addLine(to: CGPoint(x: 25, y: 35))
                path.closeSubpath()
            }
            .fill(Color.purple)
        }
        .frame(width: 80, height: 60)
    }
}

