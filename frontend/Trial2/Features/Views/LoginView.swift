import SwiftUI

struct LoginView: View {
    @ObservedObject var navigation: NavigationViewModel
    @ObservedObject var authManager: AuthManager
    @State private var username = ""
    @State private var password = ""

    var body: some View {
        VStack(spacing: 20) {
            Text("Login")
                .font(.largeTitle)
                .fontWeight(.bold)
            
            TextField("Username", text: $username)
                .textFieldStyle(RoundedBorderTextFieldStyle())
                .padding(.horizontal)
                .autocapitalization(.none)
                .disableAutocorrection(true)
            
            SecureField("Password", text: $password)
                .textFieldStyle(RoundedBorderTextFieldStyle())
                .padding(.horizontal)
            
            if let errorMessage = authManager.errorMessage {
                Text(errorMessage)
                    .foregroundColor(.red)
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
            .background(authManager.isLoading ? Color.gray : Color.blue)
            .cornerRadius(15)
            .padding(.horizontal)
            .disabled(authManager.isLoading || username.isEmpty || password.isEmpty)
            
            if authManager.isLoading {
                ProgressView()
                    .padding()
            }
            
            Button("Don't have an account? Register") {
                navigation.currentScreen = .register
            }
            .padding(.top, 10)
        }
        .padding()
        .onAppear {
            authManager.clearError()
        }
    }
} 
