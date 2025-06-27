import SwiftUI

struct SpeechBubbleView: View {
    let text: String
    var body: some View {
        ZStack {
            RoundedRectangle(cornerRadius: 30)
                .stroke(lineWidth: 5)
                .foregroundColor(.black)
            Text(text)
                .font(.title3)
                .foregroundColor(.black)
                .padding()
        }
    }
}
