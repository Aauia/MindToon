import Foundation
import Combine


@MainActor
class ProfileViewModel: ObservableObject {

    @Published var userName: String = ""
    @Published var userEmail: String = ""
    @Published var userFullName: String = ""
    @Published var profileImageUrl: URL? = nil
    @Published var isLoading: Bool = false
    @Published var errorMessage: String? = nil

    @Published var showingAccountDeletion = false
    @Published var isDeletingAccount = false
    @Published var deletionSummary: DeletionSummary? = nil

    private let authManager = AuthManager.shared


    init() {
        NotificationCenter.default.addObserver(self, selector: #selector(handleLogout), name: .userDidLogout, object: nil)
        loadUserProfile()
    }
    
    @objc private func handleLogout() {
        userName = ""
        userEmail = ""
        userFullName = ""
        profileImageUrl = nil
        isLoading = false
        errorMessage = nil
        deletionSummary = nil
        showingAccountDeletion = false
        isDeletingAccount = false
    }
    
    deinit {
        NotificationCenter.default.removeObserver(self)
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
    

    
    /// Shows the account deletion confirmation dialog
    func showAccountDeletion() {
        showingAccountDeletion = true
    }
    
    /// Hides the account deletion dialog
    func hideAccountDeletion() {
        showingAccountDeletion = false
        deletionSummary = nil
        errorMessage = nil
    }
    
    /// Deletes the user account with confirmation
    func deleteAccount(usernameConfirmation: String, navigation: NavigationViewModel) async {
        guard !usernameConfirmation.isEmpty else {
            errorMessage = "Please enter your username to confirm deletion"
            return
        }
        
        guard usernameConfirmation == userName else {
            errorMessage = "Username confirmation does not match your actual username"
            return
        }
        
        isDeletingAccount = true
        errorMessage = nil
        
        do {
            let summary = try await authManager.deleteAccount(usernameConfirmation: usernameConfirmation)
            deletionSummary = summary
            
            // Clear local profile data
            userName = ""
            userEmail = ""
            userFullName = ""
            
            print("✅ Account successfully deleted: \(summary?.username ?? "")")
            
            // Log out and navigate to welcome screen
            authManager.logout()
            navigation.currentScreen = .welcome
        } catch {
            errorMessage = error.localizedDescription
            print("❌ Account deletion failed: \(error.localizedDescription)")
        }
        
        isDeletingAccount = false
    }
    
    /// Clears any error messages
    func clearError() {
        errorMessage = nil
    }
}
