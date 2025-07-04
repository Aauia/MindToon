import SwiftUI

struct RegistrationView: View {
    @ObservedObject var navigation: NavigationViewModel
    @ObservedObject var authManager: AuthManager
    @State private var username = ""
    @State private var email = ""
    @State private var fullName = ""
    @State private var password = ""
    @State private var confirmPassword = ""

    var body: some View {
        VStack(spacing: 20) {
            Text("Register")
                .font(.largeTitle)
                .fontWeight(.bold)

            TextField("Username", text: $username)
               
                .padding(.horizontal)
                .autocapitalization(.none)
                .disableAutocorrection(true)

            TextField("Email", text: $email)
                
                .padding(.horizontal)
                .autocapitalization(.none)
                .keyboardType(.emailAddress)

            TextField("Full Name", text: $fullName)
                
                .padding(.horizontal)

            SecureField("Password", text: $password)
               
                .padding(.horizontal)

            SecureField("Confirm Password", text: $confirmPassword)
              
                .padding(.horizontal)

            if let errorMessage = authManager.errorMessage, !authManager.isAuthenticated {
                Text(errorMessage)
                    .foregroundColor(.red)
                    .multilineTextAlignment(.center)
                    .padding(.horizontal)
            }

            Button("Register") {
                Task {
                    await authManager.register(
                        username: username,
                        email: email,
                        fullName: fullName,
                        password: password
                    )
                }
            }
            .font(.headline)
            .foregroundColor(.white)
            .padding()
            .frame(maxWidth: .infinity)
            .background(authManager.isLoading ? Color.gray : Color.green)
            .cornerRadius(15)
            .padding(.horizontal)
            .disabled(authManager.isLoading || !isFormValid)

            if authManager.isLoading {
                ProgressView()
                    .padding()
            }

            Button("Already have an account? Login") {
                navigation.currentScreen = .login
            }
            .padding(.top, 10)
        }
        .padding()
        .onAppear {
            authManager.clearError()
        }
        // Removed the .onReceive block here
    }

    private var isFormValid: Bool {
        !username.isEmpty &&
        !email.isEmpty &&
        !fullName.isEmpty &&
        !password.isEmpty &&
        !confirmPassword.isEmpty &&
        password == confirmPassword
    }
}
