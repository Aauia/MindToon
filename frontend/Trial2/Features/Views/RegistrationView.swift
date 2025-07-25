import SwiftUI

struct RegistrationView: View {
    @ObservedObject var navigation: NavigationViewModel
    @ObservedObject var authManager: AuthManager

    @State private var username = ""
    @State private var email = ""
    @State private var fullName = ""
    @State private var password = ""
    @State private var confirmPassword = ""
    @State private var verificationCode = ""

    @State private var step: Int = 1

    var body: some View {
        ZStack {
            Color(red: 0.75, green: 0.67, blue: 0.95).ignoresSafeArea()
            PixelSkyView(showMoon: false)

            VStack(spacing: 24) {
                Text(step == 1 ? "Register" : "Confirm Email")
                    .font(.largeTitle)
                    .fontWeight(.bold)
                    .foregroundColor(.white)
                    .shadow(color: Color.purple.opacity(0.2), radius: 2, x: 0, y: 2)
                    .padding(.top, 40)

                if step == 1 {
                    registrationFields
                } else {
                    confirmationFields
                }

                if let errorMessage = authManager.errorMessage, !authManager.isAuthenticated {
                    Text(errorMessage)
                        .foregroundColor(.pink)
                        .multilineTextAlignment(.center)
                        .padding(.horizontal)
                }

                actionButton
                    .disabled(authManager.isLoading || !isFormValid)
                    .opacity(authManager.isLoading || !isFormValid ? 0.6 : 1)

                if authManager.isLoading {
                    ProgressView().padding()
                }

                Button("Already have an account? Login") {
                    navigation.currentScreen = .login
                }
                .foregroundColor(Color(red: 1.0, green: 0.9, blue: 1.0))
                .padding(.top, 10)

                Button(action: {
                    if let url = URL(string: "https://github.com/Aauia/MindToonPrivacy/blob/main/privacy-policy.md") {
                        UIApplication.shared.open(url)
                    }
                }) {
                    Text("View Privacy Policy")
                        .font(.footnote)
                        .foregroundColor(.white.opacity(0.9))
                        .underline()
                }
                .padding(.top, 4)
            }
            .padding(.horizontal, 28)
            .padding(.bottom, 40)
        }
        .onAppear {
            authManager.clearError()
        }
    }

    // MARK: - Views

    private var registrationFields: some View {
        VStack(spacing: 16) {
            TextField("Username", text: $username)
                .padding()
                .background(Color.white.opacity(0.22))
                .cornerRadius(14)
                .overlay(RoundedRectangle(cornerRadius: 14).stroke(Color.white.opacity(0.4), lineWidth: 1))
                .foregroundColor(.black)
                .autocapitalization(.none)
                .disableAutocorrection(true)
            TextField("Email", text: $email)
                .padding()
                .background(Color.white.opacity(0.22))
                .cornerRadius(14)
                .overlay(RoundedRectangle(cornerRadius: 14).stroke(Color.white.opacity(0.4), lineWidth: 1))
                .foregroundColor(.black)
                .autocapitalization(.none)
                .disableAutocorrection(true)
            TextField("Full Name", text: $fullName)
                .padding()
                .background(Color.white.opacity(0.22))
                .cornerRadius(14)
                .overlay(RoundedRectangle(cornerRadius: 14).stroke(Color.white.opacity(0.4), lineWidth: 1))
                .foregroundColor(.black)
                .autocapitalization(.none)
                .disableAutocorrection(true)
            SecureField("Password", text: $password)
                .padding()
                .background(Color.white.opacity(0.22))
                .cornerRadius(14)
                .overlay(RoundedRectangle(cornerRadius: 14).stroke(Color.white.opacity(0.4), lineWidth: 1))
                .foregroundColor(.black)
                .autocapitalization(.none)
                .disableAutocorrection(true)
            SecureField("Confirm Password", text: $confirmPassword)
                .padding()
                .background(Color.white.opacity(0.22))
                .cornerRadius(14)
                .overlay(RoundedRectangle(cornerRadius: 14).stroke(Color.white.opacity(0.4), lineWidth: 1))
                .foregroundColor(.black)
                .autocapitalization(.none)
                .disableAutocorrection(true)
        }
        .colorScheme(.light)
    }

    private var confirmationFields: some View {
        VStack(spacing: 16) {
            Text("Enter the verification code sent to your email.")
                .foregroundColor(.primary)
                .multilineTextAlignment(.center)
            TextField("Verification Code", text: $verificationCode)
                .keyboardType(.numberPad)
                .padding()
                .background(Color.white.opacity(0.22))
                .cornerRadius(14)
                .overlay(RoundedRectangle(cornerRadius: 14).stroke(Color.white.opacity(0.4), lineWidth: 1))
                .foregroundColor(.black)
                .autocapitalization(.none)
        }
        .colorScheme(.light)
    }

    private var actionButton: some View {
        Button(step == 1 ? "Send Verification Code" : "Confirm & Register") {
            Task {
                if step == 1 {
                    await authManager.startRegistration(
                        username: username,
                        email: email,
                        fullName: fullName,
                        password: password
                    )
                    if authManager.isRegistered {
                        step = 2
                    }
                } else {
                    await authManager.confirmRegistration(
                        username: username,
                        email: email,
                        fullName: fullName,
                        password: password,
                        code: verificationCode
                    )
                    if authManager.isAuthenticated {
                        navigation.currentScreen = .mainDashboard
                    }
                }
            }
        }
        .font(.headline)
        .foregroundColor(.white)
        .padding()
        .frame(maxWidth: .infinity)
        .background(Color(red: 0.7, green: 0.4, blue: 0.9))
        .cornerRadius(15)
        .shadow(color: Color.purple.opacity(0.18), radius: 8, x: 0, y: 4)
        .padding(.horizontal)
    }

    // MARK: - Validation
    private var isFormValid: Bool {
        if step == 1 {
            return !username.isEmpty &&
                !email.isEmpty &&
                !fullName.isEmpty &&
                !password.isEmpty &&
                !confirmPassword.isEmpty &&
                password == confirmPassword
        } else {
            return !verificationCode.isEmpty
        }
    }
}
