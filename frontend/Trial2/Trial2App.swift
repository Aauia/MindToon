//
//  Trial2App.swift
//  Trial2
//
//  Created by Aiaulym Abduohapova on 23.06.2025.
//

import SwiftUI

@main
struct Trial2App: App {
    @StateObject private var navigation = NavigationViewModel()
    @StateObject private var authManager = AuthManager.shared

    var body: some Scene {
        WindowGroup {
            RootView(navigation: navigation, authManager: authManager)
        }
    }
}

struct RootView: View {
    @ObservedObject var navigation: NavigationViewModel
    @ObservedObject var authManager: AuthManager

    var body: some View {
        Group {
            if authManager.isAuthenticated {
                // User is authenticated, show main app
                switch navigation.currentScreen {
                case .welcome:
                    WelcomeView(viewModel: WelcomeViewModel(), navigation: navigation)
                case .mainDashboard:
                    MainDashboardView(navigation: navigation)
                case .create:
                    ComicGeneratorView(viewModel: ComicGeneratorViewModel(), navigation: navigation)
                case .worlds:
                    WorldsView(navigation: navigation)
                case .profile:
                    ProfileView(navigation: navigation)
                case .dreamWorld:
                    DreamWorldView(navigation: navigation)
                case .mindWorld:
                    MindWorldView(navigation: navigation)
                case .imaginationWorld:
                    ImaginationWorldView(navigation: navigation)
                case .login, .register:
                    // If authenticated, redirect to main dashboard
                    MainDashboardView(navigation: navigation)
                }
            } else {
                // User is not authenticated, show auth screens
                switch navigation.currentScreen {
                case .welcome:
                    WelcomeView(viewModel: WelcomeViewModel(), navigation: navigation)
                case .login:
                    LoginView(navigation: navigation, authManager: authManager)
                case .register:
                    RegistrationView(navigation: navigation, authManager: authManager)
                default:
                    // Default to welcome screen if not authenticated
                    WelcomeView(viewModel: WelcomeViewModel(), navigation: navigation)
                }
            }
        }
        .onReceive(authManager.$isAuthenticated) { isAuthenticated in
            if isAuthenticated {
                navigation.currentScreen = .mainDashboard
            }
        }
    }
}

// Updated LoginView with backend integration
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

// Updated RegistrationView with backend integration
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
                .textFieldStyle(RoundedBorderTextFieldStyle())
                .padding(.horizontal)
                .autocapitalization(.none)
                .disableAutocorrection(true)
            
            TextField("Email", text: $email)
                .textFieldStyle(RoundedBorderTextFieldStyle())
                .padding(.horizontal)
                .autocapitalization(.none)
                .keyboardType(.emailAddress)
            
            TextField("Full Name", text: $fullName)
                .textFieldStyle(RoundedBorderTextFieldStyle())
                .padding(.horizontal)
            
            SecureField("Password", text: $password)
                .textFieldStyle(RoundedBorderTextFieldStyle())
                .padding(.horizontal)
            
            SecureField("Confirm Password", text: $confirmPassword)
                .textFieldStyle(RoundedBorderTextFieldStyle())
                .padding(.horizontal)
            
            if let errorMessage = authManager.errorMessage {
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
    }
    
    private var isFormValid: Bool {
        !username.isEmpty && !email.isEmpty && !fullName.isEmpty &&
        !password.isEmpty && !confirmPassword.isEmpty && password == confirmPassword
    }
}
