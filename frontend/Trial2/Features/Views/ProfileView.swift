import SwiftUI

// MARK: - ProfileView
struct ProfileView: View {
    // Initialize the ViewModel as a StateObject. This makes the ViewModel
    // owned by the View and keeps it alive for the View's lifecycle.
    @StateObject var viewModel = ProfileViewModel()
    @ObservedObject var navigation: NavigationViewModel
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        VStack(spacing: 0) {
            ScrollView {
                VStack(spacing: 25) {
                    // Show a loading indicator if the ViewModel is busy
                    if viewModel.isLoading {
                        ProgressView("Loading Profile...")
                            .padding(.top, 40)
                            .foregroundColor(.white) // Adjust color for background
                    } else {
                        // Placeholder for User Avatar/Image
                        // You can use viewModel.profileImageUrl here once implemented
                        Image(systemName: "person.circle.fill")
                            .resizable()
                            .scaledToFit()
                            .frame(width: 120, height: 120)
                            .foregroundColor(.white)
                            .padding(.top, 40)
                            .shadow(radius: 10)

                        // Display user name from ViewModel
                        Text(viewModel.userName)
                            .font(.largeTitle)
                            .fontWeight(.bold)
                            .foregroundColor(.black)

                        // Display user email from ViewModel
                        Text(viewModel.userEmail)
                            .font(.headline)
                            .foregroundColor(.black.opacity(0.8))
                    }

                    // Display error message if any
                    if let errorMessage = viewModel.errorMessage {
                        Text(errorMessage)
                            .foregroundColor(Color(red: 1.0, green: 0.8, blue: 0.89))
                            .padding(.horizontal)
                    }

                    // Account Settings Section
                    VStack(alignment: .leading, spacing: 15) {
                        ProfileOptionRow(icon: "gearshape.fill", title: "Account Settings") {
                            print("Navigate to Account Settings - (ViewModel action needed)")
                            // You would call a viewModel method here or directly navigate
                            // For example: viewModel.navigateToAccountSettings()
                        }
                        ProfileOptionRow(icon: "lock.fill", title: "Privacy & Security") {
                            print("Navigate to Privacy Settings - (ViewModel action needed)")
                        }
                        ProfileOptionRow(icon: "bell.fill", title: "Notifications") {
                            print("Navigate to Notification Settings - (ViewModel action needed)")
                        }
                    }
                    .padding(.horizontal)
                    .padding(.top, 30)

                    // Content & History Section
                    VStack(alignment: .leading, spacing: 15) {
                        ProfileOptionRow(icon: "book.closed.fill", title: "My Comics Library") {
                            print("Navigate to My Comics Library - (ViewModel action needed)")
                        }
                        ProfileOptionRow(icon: "bookmark.fill", title: "Saved Ideas") {
                            print("Navigate to Saved Ideas - (ViewModel action needed)")
                        }
                    }
                    .padding(.horizontal)
                    .padding(.top, 20)

                    // Logout Button (example of ViewModel interaction)
                    Button(action: {
                        viewModel.logout()
                        // After successful logout, AppCoordinator would transition to WelcomeScreen
                    }) {
                        Text("Log Out")
                            .font(.headline)
                            .foregroundColor(.black)
                            .padding()
                            .frame(maxWidth: .infinity)
                            .background(Color(red: 1.0, green: 0.8, blue: 0.8))
                            .cornerRadius(10)
                    }
                    .padding(.top, 30)
                    .padding(.horizontal)


                    Spacer()
                }
                .padding(.bottom, 20)
                .frame(maxWidth: .infinity, minHeight: UIScreen.main.bounds.height - 150)
            }

            BottombarView(navigation: navigation)
                .frame(maxHeight: 80)
        }
        .background(LinearGradient(gradient: Gradient(colors: [Color.yellow.opacity(0.8), Color.white.opacity(0.8)]), startPoint: .topLeading, endPoint: .bottomTrailing).edgesIgnoringSafeArea(.all))
        .toolbar {
            CustomTopBarContent(title: "Profile", showBackButton: true, leadingAction: {
                navigation.currentScreen = .mainDashboard // Or previous screen
            })
        }
        .navigationBarTitleDisplayMode(.inline)
        // Call a ViewModel method when the view appears
        .onAppear {
            viewModel.loadUserProfile()
        }
    }
}

// MARK: - ProfileOptionRow (Reusable Helper View for list items) - No Change Here
struct ProfileOptionRow: View {
    let icon: String
    let title: String
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            HStack {
                Image(systemName: icon)
                    .font(.title2)
                    .foregroundColor(.purple)
                    .frame(width: 30)

                Text(title)
                    .font(.body)
                    .foregroundColor(.black)

                Spacer()

                Image(systemName: "chevron.right")
                    .foregroundColor(.gray)
            }
            .padding(.vertical, 10)
            .padding(.horizontal, 15)
            .background(Color.white.opacity(0.1))
            .cornerRadius(10)
            .shadow(color: Color.black.opacity(0.05), radius: 3, x: 0, y: 2)
        }
    }
}

// MARK: - Preview - No Change Here
#Preview {
    ProfileView(navigation: NavigationViewModel())
}
