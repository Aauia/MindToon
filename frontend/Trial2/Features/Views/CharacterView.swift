import SwiftUI

struct CharacterView: View {
    var body: some View {
        Image("character") // Add your character image to Assets.xcassets
            .resizable()
            .aspectRatio(contentMode: .fit)
    }
}
