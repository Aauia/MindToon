import Foundation
import SwiftUI

@MainActor
class AuthManager: ObservableObject {
    @Published var isAuthenticated = false
    @Published var currentUser: UserResponse?
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
        errorMessage = nil
        
        do {
            let registerRequest = RegisterRequest(
                username: username,
                email: email,
                fullName: fullName,
                password: password
            )
            
            let user = try await APIClient.shared.register(user: registerRequest)
            currentUser = user
            
            // Store user data
            if let userData = try? JSONEncoder().encode(user) {
                UserDefaults.standard.set(userData, forKey: userKey)
            }
            
            // Auto-login after registration
            await login(username: username, password: password)
        } catch {
            errorMessage = error.localizedDescription
        }
        
        isLoading = false
    }
    
    func logout() {
        UserDefaults.standard.removeObject(forKey: tokenKey)
        UserDefaults.standard.removeObject(forKey: userKey)
        isAuthenticated = false
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
    
    // MARK: - Helper Methods
    func getStoredToken() -> String? {
        return UserDefaults.standard.string(forKey: tokenKey)
    }
    
    private func checkAuthStatus() {
        let token = getStoredToken()
        if let token = token, !token.isEmpty {
            isAuthenticated = true
            
            // Load stored user data
            if let userData = UserDefaults.standard.data(forKey: userKey),
               let user = try? JSONDecoder().decode(UserResponse.self, from: userData) {
                currentUser = user
            }
        } else {
            isAuthenticated = false
            currentUser = nil
        }
    }
    
    func clearError() {
        errorMessage = nil
    }
} 