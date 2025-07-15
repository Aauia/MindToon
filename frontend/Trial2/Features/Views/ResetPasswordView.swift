import SwiftUI

struct ResetPasswordView: View {
    @ObservedObject var authManager: AuthManager
    @ObservedObject var navigation: NavigationViewModel

    @State private var email = ""
    @State private var code = ""
    @State private var newPassword = ""
    @State private var confirmPassword = ""

    @State private var step = 1

    var body: some View {
        ZStack {
            Color.purple.opacity(0.15).ignoresSafeArea()
            VStack(spacing: 24) {
                Text(step == 1 ? "Forgot Password" : "Reset Password")
                    .font(.largeTitle)
                    .fontWeight(.bold)

                if step == 1 {
                    TextField("Enter your email", text: $email)
                        .padding()
                        .background(Color.white)
                        .cornerRadius(10)
                        .autocapitalization(.none)
                } else {
                    TextField("Enter code", text: $code)
                        .keyboardType(.numberPad)
                        .padding()
                        .background(Color.white)
                        .cornerRadius(10)

                    SecureField("New password", text: $newPassword)
                        .padding()
                        .background(Color.white)
                        .cornerRadius(10)

                    SecureField("Confirm new password", text: $confirmPassword)
                        .padding()
                        .background(Color.white)
                        .cornerRadius(10)
                }

                if let errorMessage = authManager.errorMessage {
                    Text(errorMessage)
                        .foregroundColor(.red)
                        .multilineTextAlignment(.center)
                        .padding()
                }

                Button(step == 1 ? "Send Code" : "Reset Password") {
                    Task {
                        if step == 1 {
                            await authManager.sendResetCode(email: email)
                            if authManager.resetCodeSent {
                                step = 2
                            }
                        } else {
                            guard newPassword == confirmPassword else {
                                authManager.errorMessage = "Passwords do not match"
                                return
                            }
                            await authManager.confirmResetPassword(email: email, code: code, newPassword: newPassword)
                            if authManager.isPasswordReset {
                                navigation.currentScreen = .login
                            }
                        }
                    }
                }
                .foregroundColor(.white)
                .padding()
                .frame(maxWidth: .infinity)
                .background(Color.blue)
                .cornerRadius(12)
                .disabled(authManager.isLoading)

                Spacer()
            }
            .padding()
        }
        .onAppear {
            authManager.clearError()
        }
    }
}
