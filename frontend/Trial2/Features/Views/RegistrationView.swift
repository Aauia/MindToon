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
        ZStack {
            Color(red: 0.75, green: 0.67, blue: 0.95).ignoresSafeArea()
            PixelSkyView(showMoon: false)
       

VStack(spacing: 24) {
    Text("Register")
        .font(.largeTitle)
        .fontWeight(.bold)
        .foregroundColor(.white)
        .shadow(color: Color.purple.opacity(0.2), radius: 2, x: 0, y: 2)
        .padding(.top, 40)

    Group {
        TextField("Username", text: $username)
        TextField("Email", text: $email)
        TextField("Full Name", text: $fullName)
        SecureField("Password", text: $password)
        SecureField("Confirm Password", text: $confirmPassword)
    }
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

    if let errorMessage = authManager.errorMessage, !authManager.isAuthenticated {
        Text(errorMessage)
            .foregroundColor(.pink)
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
    .background(authManager.isLoading ? Color.gray : Color(red: 0.7, green: 0.4, blue: 0.9))
    .cornerRadius(15)
    .shadow(color: Color.purple.opacity(0.18), radius: 8, x: 0, y: 4)
    .padding(.horizontal)
    .disabled(authManager.isLoading || !isFormValid)

    if authManager.isLoading {
        ProgressView()
            .padding()
    }

    Button("Already have an account? Login") {
        navigation.currentScreen = .login
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

struct RegistrationView_Previews: PreviewProvider {
    static var previews: some View {
        NavigationView {
            RegistrationView(navigation: NavigationViewModel(), authManager: .preview)
        }
    }
}
