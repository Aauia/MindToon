import SwiftUI

struct AccountDeletionView: View {
    @ObservedObject var profileViewModel: ProfileViewModel
    @ObservedObject var navigation: NavigationViewModel
    @Environment(\.dismiss) private var dismiss
    @State private var usernameConfirmation = ""
    @State private var showingConfirmationAlert = false
    
    var body: some View {
        NavigationView {
            VStack(spacing: 24) {
                // Warning Header
                VStack(spacing: 16) {
                    Image(systemName: "exclamationmark.triangle.fill")
                        .font(.system(size: 60))
                        .foregroundColor(.red)
                    
                    Text("Delete Account")
                        .font(.largeTitle)
                        .fontWeight(.bold)
                        .foregroundColor(.red)
                    
                    Text("This action is permanent and irreversible")
                        .font(.headline)
                        .foregroundColor(.secondary)
                        .multilineTextAlignment(.center)
                }
                .padding(.vertical)
                
                // Warning Information
                VStack(alignment: .leading, spacing: 12) {
                    Text("What will be deleted:")
                        .font(.headline)
                        .foregroundColor(.primary)
                    
                    VStack(alignment: .leading, spacing: 8) {
                        HStack {
                            Image(systemName: "photo.on.rectangle")
                                .foregroundColor(.red)
                            Text("All your comics and generated content")
                        }
                        
                        HStack {
                            Image(systemName: "folder")
                                .foregroundColor(.red)
                            Text("All your collections and organization")
                        }
                        
                        HStack {
                            Image(systemName: "doc.text")
                                .foregroundColor(.red)
                            Text("All your detailed scenarios")
                        }
                        
                        HStack {
                            Image(systemName: "icloud")
                                .foregroundColor(.red)
                            Text("All cloud storage data")
                        }
                        
                        HStack {
                            Image(systemName: "person.circle")
                                .foregroundColor(.red)
                            Text("Your user account and profile")
                        }
                    }
                    .font(.body)
                    .foregroundColor(.secondary)
                }
                .padding()
                .background(Color(.systemGray6))
                .cornerRadius(12)
                
                // Confirmation Input
                VStack(alignment: .leading, spacing: 8) {
                    Text("To confirm deletion, type your username: **\(profileViewModel.userName)**")
                        .font(.body)
                        .foregroundColor(.primary)
                    
                    TextField("Enter your username", text: $usernameConfirmation)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                        .autocapitalization(.none)
                        .disableAutocorrection(true)
                }
                
                Spacer()
                
                // Error Message
                if let errorMessage = profileViewModel.errorMessage {
                    Text(errorMessage)
                        .font(.caption)
                        .foregroundColor(.red)
                        .padding(.horizontal)
                        .multilineTextAlignment(.center)
                }
                
                // Deletion Summary (if account was deleted)
                if let summary = profileViewModel.deletionSummary {
                    DeletionSummaryView(summary: summary)
                        .padding()
                        .background(Color(.systemGreen).opacity(0.1))
                        .cornerRadius(12)
                }
                
                // Action Buttons
                VStack(spacing: 12) {
                    Button(action: {
                        showingConfirmationAlert = true
                    }) {
                        HStack {
                            if profileViewModel.isDeletingAccount {
                                ProgressView()
                                    .scaleEffect(0.8)
                                    .progressViewStyle(CircularProgressViewStyle(tint: .white))
                            }
                            Text(profileViewModel.isDeletingAccount ? "Deleting..." : "Delete My Account")
                        }
                        .font(.headline)
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(
                            usernameConfirmation == profileViewModel.userName && !profileViewModel.isDeletingAccount
                            ? Color.red
                            : Color.gray
                        )
                        .cornerRadius(12)
                    }
                    .disabled(usernameConfirmation != profileViewModel.userName || profileViewModel.isDeletingAccount)
                    
                    Button("Cancel") {
                        dismiss()
                    }
                    .font(.body)
                    .foregroundColor(.blue)
                }
                .padding(.bottom)
            }
            .padding()
            .navigationTitle("Account Deletion")
            .navigationBarTitleDisplayMode(.inline)
            .navigationBarBackButtonHidden(true)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Cancel") {
                        dismiss()
                    }
                }
            }
        }
        .alert("Final Confirmation", isPresented: $showingConfirmationAlert) {
            Button("Cancel", role: .cancel) { }
            Button("Delete Forever", role: .destructive) {
                Task {
                    await profileViewModel.deleteAccount(usernameConfirmation: usernameConfirmation, navigation: navigation)
                }
            }
        } message: {
            Text("Are you absolutely sure you want to delete your account? This action cannot be undone and all your data will be permanently lost.")
        }
        .onAppear {
            profileViewModel.clearError()
        }
    }
}

struct DeletionSummaryView: View {
    let summary: DeletionSummary
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Account Successfully Deleted")
                .font(.headline)
                .foregroundColor(.green)
            
            VStack(alignment: .leading, spacing: 6) {
                HStack {
                    Text("Username:")
                    Spacer()
                    Text(summary.username)
                        .fontWeight(.semibold)
                }
                
                HStack {
                    Text("Comics Deleted:")
                    Spacer()
                    Text("\(summary.comicsDeleted)")
                        .fontWeight(.semibold)
                }
                
                HStack {
                    Text("Collections Deleted:")
                    Spacer()
                    Text("\(summary.collectionsDeleted)")
                        .fontWeight(.semibold)
                }
                
                HStack {
                    Text("Scenarios Deleted:")
                    Spacer()
                    Text("\(summary.scenariosDeleted)")
                        .fontWeight(.semibold)
                }
                
                HStack {
                    Text("Storage Cleared:")
                    Spacer()
                    Text(summary.storageCleared)
                        .fontWeight(.semibold)
                }
                
                HStack {
                    Text("Deleted At:")
                    Spacer()
                    Text(formatDate(summary.deletedAt))
                        .fontWeight(.semibold)
                        .font(.caption)
                }
            }
            .font(.body)
            .foregroundColor(.secondary)
        }
    }
    
    private func formatDate(_ dateString: String) -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd'T'HH:mm:ss.SSSSSS"
        
        if let date = formatter.date(from: dateString) {
            formatter.dateStyle = .medium
            formatter.timeStyle = .short
            return formatter.string(from: date)
        }
        
        return dateString
    }
}

#Preview {
    AccountDeletionView(profileViewModel: ProfileViewModel(), navigation: NavigationViewModel())
} 