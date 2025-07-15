import Foundation
import SwiftUI

// Explicit typealiases to resolve ambiguity with old APIModel.swift
typealias AuthUserResponse = UserResponse
typealias AuthRegisterRequest = RegisterRequest
typealias AuthAccountDeletionRequest = AccountDeletionRequest
typealias AuthDeletionSummary = DeletionSummary

extension Notification.Name {
    static let userDidLogout = Notification.Name("userDidLogout")
}

@MainActor
class AuthManager: ObservableObject {
    @Published var isAuthenticated = false
    @Published var isRegistered = false
    @Published var currentUser: AuthUserResponse?
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var resetCodeSent = false
    
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
            let user = try await APIClient.shared.getUserProfile()
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
    /// Step 1: Send verification code
    func startRegistration(username: String, email: String, fullName: String?, password: String) async {
        isLoading = true
        errorMessage = nil
        
        let request = StartRegistrationRequest(username: username, email: email, fullName: fullName, password: password)
        
        do {
            try await APIClient.shared.startRegistration(request)
            print("📧 Verification code sent to \(email)")
            isRegistered = true // mark step 1 as successful
        } catch {
            errorMessage = error.localizedDescription
            isRegistered = false
        }
        
        isLoading = false
    }
        /// Step 2: Confirm with code and register user
    func confirmRegistration(username: String, email: String, fullName: String?, password: String, code: String) async {
        isLoading = true
        errorMessage = nil

        let request = ConfirmRegistrationRequest(
            email: email,
            username: username,
            password: password,
            fullName: fullName,
            code: code
        )

        do {
            let user = try await APIClient.shared.confirmRegistration(request)
            currentUser = user

            // Save user data
            if let userData = try? JSONEncoder().encode(user) {
                UserDefaults.standard.set(userData, forKey: userKey)
            }

            // Auto-login after confirmation
            await login(username: username, password: password)
            
            if !isAuthenticated {
                errorMessage = "Confirmation succeeded but auto-login failed."
            }

            isRegistered = true
        } catch {
            errorMessage = error.localizedDescription
            isRegistered = false
            isAuthenticated = false
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
        
        // Notify other parts of the app
        NotificationCenter.default.post(name: .userDidLogout, object: nil)
    }
    func sendResetCode(email: String) async {
    isLoading = true
    errorMessage = nil
    resetCodeSent = false

    do {
        try await APIClient.shared.sendResetCode(email: email)
        print("📧 Reset code sent to \(email)")
        resetCodeSent = true
    } catch {
        errorMessage = error.localizedDescription
        resetCodeSent = false
    }

    isLoading = false
    }

    func resetPassword(email: String, code: String, newPassword: String) async -> Bool {
        isLoading = true
        errorMessage = nil

        do {
            try await APIClient.shared.confirmResetPassword(email: email, code: code, newPassword: newPassword)
            logout()
            return true
        } catch {
            errorMessage = error.localizedDescription
            return false
        }

        isLoading = false
    }
    
    func refreshUserProfile() async {
        guard let token = await getStoredToken() else {
            logout()
            return
        }
        
        do {
            let user = try await APIClient.shared.getUserProfile()
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
    func refreshAccessTokenIfNeeded() async {
        do {
            let newToken = try await APIClient.shared.refreshAccessToken()
            UserDefaults.standard.set(newToken, forKey: tokenKey)
            print("✅ Token refreshed and stored")
        } catch {
            print("❌ Failed to refresh token:", error.localizedDescription)
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
            
            let token = await getStoredToken()
            guard let token = token else {
                throw APIError.unauthorized
            }
            
            let summary = try await APIClient.shared.deleteAccount(confirmation: confirmation)
            
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
    func getStoredToken() async -> String? {
        var token = UserDefaults.standard.string(forKey: tokenKey)

        if token == nil || token!.isEmpty || token!.count < 10 {
            print("⚠️ Token invalid or missing — attempting refresh...")
            do {
                token = try await APIClient.shared.refreshAccessToken()
                UserDefaults.standard.set(token, forKey: tokenKey)
            } catch {
                print("❌ Refresh failed in getStoredToken():", error)
                return nil
            }
        }

        return token
    }



    func validateAndGetToken() async throws -> String {
        guard let token = await getStoredToken(), !token.isEmpty else {
            print("❌ No valid token found, even after refresh attempt")
            throw APIError.unauthorized
        }
        
        print("🔑 Retrieved token (validated or refreshed): ✅ Found")
        return token
    }
    
    
    
    func isTokenValid() async -> Bool {
        guard let token = await getStoredToken(), !token.isEmpty else {
            return false
        }
        return true
    }
    
    private func checkAuthStatus() {
        Task {
            let token = await getStoredToken()
            print("🔐 Checking auth status - token exists: \(token != nil)")
            await MainActor.run {
                if let token = token, !token.isEmpty {
                    isAuthenticated = true
                    print("✅ User authenticated with token: \(token.prefix(10))...")
                    
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
        }
    }
    
    
    func clearError() {
        errorMessage = nil
    }
    
    
}

#if DEBUG
extension AuthManager {
    static var preview: AuthManager {
        let manager = AuthManager()
        // Optionally set up mock state here
        return manager
    }
}
#endif
