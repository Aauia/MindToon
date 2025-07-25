import SwiftUI

struct LoginView: View {
    @ObservedObject var navigation: NavigationViewModel
    @ObservedObject var authManager: AuthManager
    @State private var username = ""
    @State private var password = ""

    // Custom static colors
    let textColor = Color(red: 0.95, green: 0.95, blue: 0.98) // light lavender/gray
    let fieldTextColor = Color.black // Force black color for input text
    let buttonColor = Color(red: 0.7, green: 0.4, blue: 0.9)

    var body: some View {
        ZStack {
            Color(red: 0.75, green: 0.67, blue: 0.95).ignoresSafeArea()
            PixelSkyView(showMoon: false)

            VStack(spacing: 24) {
                Text("Login")
                    .font(.largeTitle)
                    .fontWeight(.bold)
                    .foregroundColor(textColor)
                    .shadow(color: Color.purple.opacity(0.2), radius: 2, x: 0, y: 2)
                    .padding(.top, 40)

                VStack(spacing: 16) {
                    TextField("Username", text: $username)
                        .padding()
                        .background(Color.white.opacity(0.22))
                        .cornerRadius(14)
                        .overlay(
                            RoundedRectangle(cornerRadius: 14)
                                .stroke(Color.white.opacity(0.4), lineWidth: 1)
                        )
                        .foregroundColor(fieldTextColor)
                        .autocapitalization(.none)
                        .disableAutocorrection(true)

                    SecureField("Password", text: $password)
                        .padding()
                        .background(Color.white.opacity(0.22))
                        .cornerRadius(14)
                        .overlay(
                            RoundedRectangle(cornerRadius: 14)
                                .stroke(Color.white.opacity(0.4), lineWidth: 1)
                        )
                        .foregroundColor(fieldTextColor)
                }
                .colorScheme(.light) // Ensures consistent text color in dark mode

                if let errorMessage = authManager.errorMessage {
                    Text(errorMessage)
                        .foregroundColor(.pink)
                        .multilineTextAlignment(.center)
                        .padding(.horizontal)
                }

                Button("Sign In") {
                    Task {
                        await authManager.login(username: username, password: password)
                    }
                }
                .font(.headline)
                .foregroundColor(.white)
                .padding()
                .frame(maxWidth: .infinity)
                .background(authManager.isLoading ? Color.gray : buttonColor)
                .cornerRadius(15)
                .shadow(color: Color.purple.opacity(0.18), radius: 8, x: 0, y: 4)
                .padding(.horizontal)
                .disabled(authManager.isLoading || username.isEmpty || password.isEmpty)

                if authManager.isLoading {
                    ProgressView()
                        .padding()
                }

                Button("Forgot Password?") {
                    navigation.currentScreen = .forgotPassword
                }
                .font(.subheadline)
                .foregroundColor(textColor.opacity(0.85))
                .underline()
                .padding(.top, 5)

                Button("Don't have an account? Register") {
                    navigation.currentScreen = .register
                }
                .foregroundColor(Color(red: 1.0, green: 0.9, blue: 1.0))
                .padding(.top, 10)
            }
            .padding(.horizontal, 28)
            .padding(.bottom, 40)
        }
        .onAppear {
            username = ""
            password = ""
            authManager.clearError()
            authManager.isLoading = false
        }
    }
}
