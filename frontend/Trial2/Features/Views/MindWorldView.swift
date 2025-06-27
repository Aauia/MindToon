import SwiftUI

struct MindWorldView: View {
    @ObservedObject var navigation: NavigationViewModel

    var body: some View {
        ZStack {
            Color.blue.opacity(0.6).edgesIgnoringSafeArea(.all) // Distinct background
            VStack {
                Text("Mind World Library")
                    .font(.largeTitle)
                    .fontWeight(.bold)
                    .foregroundColor(.white)
                Text("Your graphic essays and philosophical reflections will appear here.")
                    .foregroundColor(.white.opacity(0.9))
                    .multilineTextAlignment(.center)
                    .padding()
            }
        }
        .toolbar {
            CustomTopBarContent(title: "Mind Library", showBackButton: true, leadingAction: {
                navigation.currentScreen = .worlds // Or previous screen
            })
        }
        .navigationBarTitleDisplayMode(.inline)
    }
}

#Preview {
    MindWorldView(navigation: NavigationViewModel())
}
