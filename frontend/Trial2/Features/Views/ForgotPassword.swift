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
            Color.purple.opacity(0.15).ignoresSafeArea()

            VStack(spacing: 24) {
                Text(step == 1 ? "Forgot Password" : "Reset Password")
                    .font(.largeTitle)
                    .fontWeight(.bold)
                    .transition(.opacity.combined(with: .move(edge: .top)))

                if step == 1 {
                    Group {
                        TextField("Enter your email", text: $email)
                            .padding()
                            .background(Color.white)
                            .cornerRadius(10)
                            .autocapitalization(.none)
                    }
                    .transition(.move(edge: .leading).combined(with: .opacity))
                } else {
                    Group {
                        TextField("Enter code", text: $code)
                            .keyboardType(.numberPad)
                            .padding()
                            .background(Color.white)
                            .cornerRadius(10)

                        SecureField("New password", text: $newPassword)
                            .textContentType(.newPassword) // explicitly say it's a new password
                            .keyboardType(.asciiCapable)
                            .autocorrectionDisabled(true)
                            .textInputAutocapitalization(.never)
                            .disableAutocorrection(true)
                            .padding()
                            .background(Color.white)
                            .cornerRadius(10)

                        SecureField("Confirm new password", text: $confirmPassword)
                            .textContentType(.newPassword)
                            .keyboardType(.asciiCapable)
                            .autocorrectionDisabled(true)
                            .textInputAutocapitalization(.never)
                            .disableAutocorrection(true)
                            .padding()
                            .background(Color.white)
                            .cornerRadius(10)

                    }
                    .transition(.move(edge: .trailing).combined(with: .opacity))
                }

                if let errorMessage = authManager.errorMessage {
                    Text(errorMessage)
                        .foregroundColor(.red)
                        .multilineTextAlignment(.center)
                        .padding()
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
                            let success = await authManager.resetPassword(email: email, code: code, newPassword: newPassword)
                            if success {
                                 DispatchQueue.main.async {
                                    // Clear fields explicitly on navigation
                                    authManager.clearError()
                                    navigation.currentScreen = .login
                                    
                                 
                                 }
                            }
                        }
                    }
                }) {
                    Text(step == 1 ? "Send Code" : "Reset Password")
                        .foregroundColor(.white)
                        .padding()
                        .frame(maxWidth: .infinity)
                        .background(Color.blue)
                        .cornerRadius(12)
                }
                .disabled(authManager.isLoading)

                Spacer()
            }
            Button("Back to login") {
                navigation.currentScreen = .login
            }
            .padding()
            .animation(.easeInOut, value: step)
        }
        .onAppear {
            authManager.clearError()
        }
     
        .foregroundColor(.black)
        .padding(.top, 10)
    }
}
