import SwiftUI


struct WelcomeView: View {
    @StateObject var viewModel: WelcomeViewModel
    @ObservedObject var navigation: NavigationViewModel

    var body: some View {
        ZStack {
            Color(red: 0.75, green: 0.67, blue: 0.95).ignoresSafeArea()
            PixelSkyView()
           

            // Foreground content
            VStack(spacing: 24) {
                Spacer()
                
                VStack(spacing: 8) {
                    Text("MindToon")
                        .font(.system(size: 38, weight: .heavy, design: .rounded))
                        .foregroundColor(.white)
                        .shadow(color: Color.purple.opacity(0.2), radius: 2, x: 0, y: 2)
                    Text("Enter your comic galaxy...")
                        .font(.title3)
                        .foregroundColor(Color(red: 1.0, green: 0.9, blue: 1.0))
                        .shadow(color: Color.purple.opacity(0.1), radius: 1, x: 0, y: 1)
                }
                .padding(.bottom, 8)

                Spacer()

                Button(action: {
                    navigation.currentScreen = .login
                }) {
                    Text("Get Started")
                        .font(.headline)
                        .foregroundColor(.white)
                        .padding(.vertical, 16)
                        .frame(maxWidth: .infinity)
                        .background(Color(red: 0.7, green: 0.4, blue: 0.9))
                        .cornerRadius(18)
                        .overlay(
                            RoundedRectangle(cornerRadius: 18)
                                .stroke(Color.white.opacity(0.7), lineWidth: 2)
                        )
                }
                .padding(.horizontal, 40)
                .padding(.bottom, 60)
            }
        }
    }
}

// MARK: - Preview
struct WelcomeView_Previews: PreviewProvider {
    static var previews: some View {
        NavigationView {
            WelcomeView(viewModel: WelcomeViewModel(), navigation: NavigationViewModel())
        }
    }
}
struct CustomInputField: View {
    var placeholder: String
    @Binding var text: String
    var keyboard: UIKeyboardType = .default

    var body: some View {
        TextField(placeholder, text: $text)
            .keyboardType(keyboard)
            .autocapitalization(.none)
            .padding()
            .background(Color.white.opacity(0.9))
            .cornerRadius(12)
            .shadow(color: .black.opacity(0.05), radius: 4, x: 0, y: 2)
    }
}

struct CustomSecureField: View {
    var placeholder: String
    @Binding var text: String

    var body: some View {
        SecureField(placeholder, text: $text)
            .autocapitalization(.none)
            .padding()
            .background(Color.white.opacity(0.9))
            .cornerRadius(12)
            .shadow(color: .black.opacity(0.05), radius: 4, x: 0, y: 2)
    }
}
