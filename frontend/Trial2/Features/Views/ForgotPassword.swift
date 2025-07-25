import SwiftUI

struct ForgotPasswordView: View {
    @ObservedObject var authManager: AuthManager
    @ObservedObject var navigation: NavigationViewModel

    @State private var email = ""
    @State private var code = ""
    @State private var newPassword = ""
    @State private var confirmPassword = ""
    @State private var step = 1
    @Namespace private var animation

    var body: some View {
        ZStack {
            Color(red: 0.75, green: 0.67, blue: 0.95).ignoresSafeArea()
            PixelSkyView() // Same animated background

            VStack(spacing: 24) {
                Spacer(minLength: 20)

                Text(step == 1 ? "Forgot Password" : "Reset Password")
                    .font(.system(size: 32, weight: .heavy, design: .rounded))
                    .foregroundColor(.white)
                    .shadow(color: Color.purple.opacity(0.2), radius: 2, x: 0, y: 2)

                Group {
                    if step == 1 {
                        VStack(spacing: 16) {
                            CustomInputField(placeholder: "Enter your email", text: $email)
                                .foregroundColor(.black)
                                .background(Color.white.opacity(0.22))
                                .cornerRadius(14)
                        }
                        .colorScheme(.light)
                    } else {
                        VStack(spacing: 16) {
                            CustomInputField(placeholder: "Enter code", text: $code, keyboard: .numberPad)
                                .foregroundColor(.black)
                                .background(Color.white.opacity(0.22))
                                .cornerRadius(14)
                            CustomSecureField(placeholder: "New password", text: $newPassword)
                                .foregroundColor(.black)
                                .background(Color.white.opacity(0.22))
                                .cornerRadius(14)
                            CustomSecureField(placeholder: "Confirm new password", text: $confirmPassword)
                                .foregroundColor(.black)
                                .background(Color.white.opacity(0.22))
                                .cornerRadius(14)
                        }
                        .colorScheme(.light)
                    }
                }

                if let errorMessage = authManager.errorMessage {
                    Text(errorMessage)
                        .foregroundColor(.red)
                        .multilineTextAlignment(.center)
                        .padding(.horizontal)
                }

                Button(action: {
                    Task {
                        if step == 1 {
                            await authManager.sendResetCode(email: email)
                            if authManager.resetCodeSent {
                                withAnimation(.easeInOut) {
                                    step = 2
                                }
                            }
                        } else {
                            guard newPassword == confirmPassword else {
                                authManager.errorMessage = "Passwords do not match"
                                return
                            }
                            let success = await authManager.resetPassword(
                                email: email,
                                code: code,
                                newPassword: newPassword
                            )
                            if success {
                                DispatchQueue.main.async {
                                    authManager.clearError()
                                    navigation.currentScreen = .login
                                }
                            }
                        }
                    }
                }) {
                    Text(step == 1 ? "Send Code" : "Reset Password")
                        .font(.headline)
                        .foregroundColor(.white)
                        .padding(.vertical, 14)
                        .frame(maxWidth: .infinity)
                        .background(Color(red: 0.7, green: 0.4, blue: 0.9))
                        .cornerRadius(18)
                        .overlay(
                            RoundedRectangle(cornerRadius: 18)
                                .stroke(Color.white.opacity(0.7), lineWidth: 1.5)
                        )
                }
                .disabled(authManager.isLoading)
                .padding(.horizontal, 40)

                Button(action: {
                    navigation.currentScreen = .login
                }) {
                    Text("Back to Login")
                        .foregroundColor(.white)
                        .underline()
                }
                .padding(.top, 10)

                Spacer()
            }
            .padding(.horizontal, 30)
            .padding(.top, 40)
            .onAppear {
                authManager.clearError()
            }
        }
    }
}
