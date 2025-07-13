import SwiftUI


struct LoginView: View {
    @ObservedObject var navigation: NavigationViewModel
    @ObservedObject var authManager: AuthManager
    @State private var username = ""
    @State private var password = ""

    var body: some View {
        ZStack {
            Color(red: 0.75, green: 0.67, blue: 0.95).ignoresSafeArea()
            PixelSkyView(showMoon: false)
 
            
            VStack(spacing: 24) {
                Text("Login")
                    .font(.largeTitle)
                    .fontWeight(.bold)
                    .foregroundColor(.white)
                    .shadow(color: Color.purple.opacity(0.2), radius: 2, x: 0, y: 2)
                    .padding(.top, 40)

                TextField("Username", text: $username)
                    .padding()
                    .background(Color.white.opacity(0.22))
                    .cornerRadius(14)
                    .overlay(
                        RoundedRectangle(cornerRadius: 14)
                            .stroke(Color.white.opacity(0.4), lineWidth: 1)
                    )
                    .foregroundColor(.primary)
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
                    .foregroundColor(.primary)

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
                .background(authManager.isLoading ? Color.gray : Color(red: 0.7, green: 0.4, blue: 0.9))
                .cornerRadius(15)
                .shadow(color: Color.purple.opacity(0.18), radius: 8, x: 0, y: 4)
                .padding(.horizontal)
                .disabled(authManager.isLoading || username.isEmpty || password.isEmpty)

                if authManager.isLoading {
                    ProgressView()
                        .padding()
                }

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
            authManager.clearError()
        }
    }
}

