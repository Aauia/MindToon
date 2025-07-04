import Foundation
import SwiftUI

// Explicit typealiases to resolve ambiguity with old APIModel.swift
typealias AuthUserResponse = UserResponse
typealias AuthRegisterRequest = RegisterRequest
typealias AuthAccountDeletionRequest = AccountDeletionRequest
typealias AuthDeletionSummary = DeletionSummary

@MainActor
class AuthManager: ObservableObject {
    @Published var isAuthenticated = false
    @Published var isRegistered = false
    @Published var currentUser: AuthUserResponse?
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    static let shared = AuthManager()
    
    private let tokenKey = "access_token"
    private let userKey = "current_user"
    
    private init() {
        checkAuthStatus()
    }
    
    // MARK: - Authentication Methods
    func login(username: String, password: String) async {
        isLoading = true
        errorMessage = nil
        
        do {
            let tokenResponse = try await APIClient.shared.login(username: username, password: password)
            
            // Store token
            UserDefaults.standard.set(tokenResponse.accessToken, forKey: tokenKey)
            print("🔑 Token stored successfully: \(tokenResponse.accessToken.prefix(10))...")
            
            // Fetch user profile
            let user = try await APIClient.shared.getUserProfile(token: tokenResponse.accessToken)
            currentUser = user
            
            // Store user data
            if let userData = try? JSONEncoder().encode(user) {
                UserDefaults.standard.set(userData, forKey: userKey)
            }
            
            isAuthenticated = true
        } catch {
            errorMessage = error.localizedDescription
            isAuthenticated = false
        }
        
        isLoading = false
    }
    
    func register(username: String, email: String, fullName: String, password: String) async {
        isLoading = true
        errorMessage = nil // <--- CRUCIAL: Clear error at the start of registration attempt
        
        do {
            let registerRequest = AuthRegisterRequest(
                username: username,
                email: email,
                fullName: fullName,
                password: password
            )
            
            let user = try await APIClient.shared.register(user: registerRequest)
            currentUser = user // Set current user on successful registration
            
            // Store user data
            if let userData = try? JSONEncoder().encode(user) {
                UserDefaults.standard.set(userData, forKey: userKey)
            }
            
            isRegistered = true // Indicate successful registration
            errorMessage = nil // <--- CRUCIAL: Clear any error message after successful registration API call
            
            // Auto-login after registration
            await login(username: username, password: password)
            
            // After successful login, `isAuthenticated` will be true, and `RootView` will navigate.
            // Ensure no error is set after this point unless login specifically fails.
            if !isAuthenticated { // If login failed after registration
                errorMessage = "Registration successful but auto-login failed. Please try logging in."
            }
            
        } catch {
            // This block is is for actual errors during the `APIClient.shared.register` call
            errorMessage = error.localizedDescription
            isRegistered = false // Registration failed
            isAuthenticated = false // Not authenticated if registration failed
        }
        
        isLoading = false
    }
    
    func logout() {
        UserDefaults.standard.removeObject(forKey: tokenKey)
        UserDefaults.standard.removeObject(forKey: userKey)
        isAuthenticated = false
        isRegistered = false
        currentUser = nil
        errorMessage = nil
    }
    
    func refreshUserProfile() async {
        guard let token = getStoredToken() else {
            logout()
            return
        }
        
        do {
            let user = try await APIClient.shared.getUserProfile(token: token)
            currentUser = user
            
            // Update stored user data
            if let userData = try? JSONEncoder().encode(user) {
                UserDefaults.standard.set(userData, forKey: userKey)
            }
        } catch {
            // If token is invalid, logout
            logout()
        }
    }
    
    // MARK: - Account Deletion (New functionality as per cursor rules)
    func deleteAccount(usernameConfirmation: String) async throws -> AuthDeletionSummary? {
        guard let currentUser = currentUser else {
            throw APIError.unauthorized
        }
        
        isLoading = true
        errorMessage = nil
        
        do {
            let confirmation = AuthAccountDeletionRequest(
                confirmDeletion: true,
                usernameConfirmation: usernameConfirmation,
                understandingAcknowledgment: "I understand this action is permanent and irreversible"
            )
            
            let token = getStoredToken()
            guard let token = token else {
                throw APIError.unauthorized
            }
            
            let summary = try await APIClient.shared.deleteAccount(confirmation: confirmation, token: token)
            
            // Clear local data
            logout()
            
            isLoading = false
            return summary // summary is now optional
        } catch {
            isLoading = false
            errorMessage = error.localizedDescription
            throw error
        }
    }
    
    // MARK: - Helper Methods
    func getStoredToken() -> String? {
        let token = UserDefaults.standard.string(forKey: tokenKey)
        print("🔑 Getting stored token: \(token != nil ? "✅ Found" : "❌ Nil")")
        return token
    }
    
    private func checkAuthStatus() {
        let token = getStoredToken()
        print("🔐 Checking auth status - token exists: \(token != nil)")
        if let token = token, !token.isEmpty {
            isAuthenticated = true
            print("✅ User authenticated with token: \(token.prefix(10))...")
            
            // Load stored user data
            if let userData = UserDefaults.standard.data(forKey: userKey),
               let user = try? JSONDecoder().decode(AuthUserResponse.self, from: userData) {
                currentUser = user
                print("👤 User data loaded: \(user.username)")
            }
        } else {
            print("❌ No valid token found")
            isAuthenticated = false
            currentUser = nil
        }
    }
    
    func clearError() {
        errorMessage = nil
    }
} 
