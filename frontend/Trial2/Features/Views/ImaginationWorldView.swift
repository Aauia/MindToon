import SwiftUI

struct ImaginationWorldView: View {
    @ObservedObject var navigation: NavigationViewModel

    var body: some View {
        ZStack {
            Color.green.opacity(0.6).edgesIgnoringSafeArea(.all) // Distinct background
            VStack {
                Text("Script World Library")
                    .font(.largeTitle)
                    .fontWeight(.bold)
                    .foregroundColor(.white)
                Text("Your comic projects, manga pages, and visual drafts will appear here.")
                    .foregroundColor(.white.opacity(0.9))
                    .multilineTextAlignment(.center)
                    .padding()
            }
        }
        .toolbar {
            CustomTopBarContent(title: "Script Library", showBackButton: true, leadingAction: {
                navigation.currentScreen = .worlds // Or previous screen
            })
        }
        .navigationBarTitleDisplayMode(.inline)
    }
}

#Preview {
    ImaginationWorldView(navigation: NavigationViewModel())
}
