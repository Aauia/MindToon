import SwiftUI

struct CharacterView: View {
    var body: some View {
        Image("character") 
            .resizable()
            .aspectRatio(contentMode: .fit)
    }
}
