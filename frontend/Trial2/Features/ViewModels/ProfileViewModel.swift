import Foundation
import Combine

// MARK: - ProfileViewModel
@MainActor
class ProfileViewModel: ObservableObject {
    // MARK: - Published Properties (View State)
    @Published var userName: String = ""
    @Published var userEmail: String = ""
    @Published var userFullName: String = ""
    @Published var profileImageUrl: URL? = nil
    @Published var isLoading: Bool = false
    @Published var errorMessage: String? = nil

    private let authManager = AuthManager.shared

    // MARK: - Initialization
    init() {
        loadUserProfile()
    }

    // MARK: - Data Fetching and Business Logic

    /// Loads the user's profile data from AuthManager
    func loadUserProfile() {
        isLoading = true
        errorMessage = nil
        
        if let user = authManager.currentUser {
            userName = user.username
            userEmail = user.email
            userFullName = user.fullName ?? user.username
            isLoading = false
        } else {
            // Try to refresh user profile from backend
            Task {
                await refreshUserProfile()
            }
        }
    }

    /// Refreshes user profile from the backend
    func refreshUserProfile() async {
        isLoading = true
        errorMessage = nil
        
        await authManager.refreshUserProfile()
        
        if let user = authManager.currentUser {
            userName = user.username
            userEmail = user.email
            userFullName = user.fullName ?? user.username
        } else {
            errorMessage = "Failed to load user profile"
        }
        
        isLoading = false
    }

    /// Updates a user setting (placeholder for future implementation)
    func updateSetting(settingName: String, newValue: String) {
        isLoading = true
        errorMessage = nil
        print("Updating \(settingName) to \(newValue)...")

        // This would be implemented when backend supports user settings
        Task {
            do {
                try await Task.sleep(nanoseconds: 1_000_000_000) // Simulate delay
                
                DispatchQueue.main.async {
                    self.isLoading = false
                    print("Setting '\(settingName)' updated successfully.")
                }
            } catch {
                DispatchQueue.main.async {
                    self.errorMessage = "Failed to update setting: \(error.localizedDescription)"
                    self.isLoading = false
                    print("Error updating setting: \(error.localizedDescription)")
                }
            }
        }
    }

    /// Logs out the user
    func logout() {
        isLoading = true
        errorMessage = nil
        print("Logging out user...")

        authManager.logout()
        
        // Clear local data
        userName = ""
        userEmail = ""
        userFullName = ""
        
        isLoading = false
        print("User logged out successfully.")
    }
    
    /// Clears any error messages
    func clearError() {
        errorMessage = nil
    }
}
