import SwiftUI

struct DreamWorldView: View {
    @ObservedObject var navigation: NavigationViewModel

    var body: some View {
        ZStack {
            Color.purple.opacity(0.6).edgesIgnoringSafeArea(.all) // Distinct background
            VStack {
                Text("Dream World Library")
                    .font(.largeTitle)
                    .fontWeight(.bold)
                    .foregroundColor(.white)
                Text("Your collected dream novels and dreamboards will appear here.")
                    .foregroundColor(.white.opacity(0.9))
                    .multilineTextAlignment(.center)
                    .padding()
            }
        }
        .toolbar {
            CustomTopBarContent(title: "Dream Library", showBackButton: true, leadingAction: {
                navigation.currentScreen = .worlds // Or previous screen
            })
        }
        .navigationBarTitleDisplayMode(.inline)
    }
}

#Preview {
    DreamWorldView(navigation: NavigationViewModel())
}
