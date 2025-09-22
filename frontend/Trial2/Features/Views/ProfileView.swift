import SwiftUI


struct ProfileView: View {

    @StateObject var viewModel = ProfileViewModel()
    @ObservedObject var navigation: NavigationViewModel
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        ZStack {
            LinearGradient(
                gradient: Gradient(colors: [
                    Color(red: 0.85, green: 0.73, blue: 0.94), // lavender
                    Color(red: 0.99, green: 0.85, blue: 0.92)  // blush
                ]),
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .edgesIgnoringSafeArea(.all)
            VStack(spacing: 0) {
                ScrollView {
                    VStack(spacing: 25) {
                 
                        if viewModel.isLoading {
                            ProgressView("Loading Profile...")
                                .padding(.top, 40)
                                .foregroundColor(.white) // Adjust color for background
                        } else {
                        
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

               
                        
                        // About Section (New)
                        VStack(alignment: .leading, spacing: 15) {
                            Text("About")
                                .font(.headline)
                                .fontWeight(.bold)
                                .foregroundColor(.black)
                            ProfileOptionRow(icon: "lock.shield", title: "Privacy Policy") {
                                if let url = URL(string: "https://github.com/Aauia/MindToonPrivacy/blob/main/privacy-policy.md") {
                                    UIApplication.shared.open(url)
                                }
                            }
                        }
                        .padding(.horizontal)
                        .padding(.top, 20)

                        // Account Management Section (New)
                        VStack(alignment: .leading, spacing: 15) {
                            Text("Account Management")
                                .font(.headline)
                                .fontWeight(.bold)
                                .foregroundColor(.black)
                            ProfileOptionRow(icon: "trash.fill", title: "Delete Account", isDestructive: true) {
                                viewModel.showAccountDeletion()
                            }
                        }
                        .padding(.horizontal)
                        .padding(.top, 20)

                        Button(action: {
                            viewModel.logout()

                        }) {
                            Text("Log Out")
                                .font(.headline)
                                .foregroundColor(.black)
                                .padding()
                                .frame(maxWidth: .infinity)
                                .background(Color(red: 0.7, green: 0.4, blue: 0.9)) // muted purple
                                .cornerRadius(10)
                        }
                        .padding(.top, 30)
                        .padding(.horizontal)


                        Spacer()
                    }
                    .padding(.bottom, 20)
                    .frame(maxWidth: .infinity, minHeight: 600)
                }

                BottombarView(navigation: navigation)
                    
            }
        }
        .toolbar {
            ToolbarItem(placement: .navigationBarLeading) {
                Button(action: { navigation.currentScreen = .mainDashboard }) {
                    Image(systemName: "chevron.left")
                        .font(.title2)
                        .foregroundColor(.primary)
                }
            }
        }
        .navigationBarTitleDisplayMode(.inline)
        // Call a ViewModel method when the view appears
        .onAppear {
            viewModel.loadUserProfile()
        }
        .sheet(isPresented: $viewModel.showingAccountDeletion) {
            AccountDeletionView(profileViewModel: viewModel, navigation: navigation)
        }
    }
}


struct ProfileOptionRow: View {
    let icon: String
    let title: String
    let isDestructive: Bool
    let action: () -> Void
    
    init(icon: String, title: String, isDestructive: Bool = false, action: @escaping () -> Void) {
        self.icon = icon
        self.title = title
        self.isDestructive = isDestructive
        self.action = action
    }

    var body: some View {
        Button(action: action) {
            HStack {
                Image(systemName: icon)
                    .font(.title2)
                    .foregroundColor(isDestructive ? .red : .purple)
                    .frame(width: 30)

                Text(title)
                    .font(.body)
                    .foregroundColor(isDestructive ? .red : .black)

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


#Preview {
    ProfileView(navigation: NavigationViewModel())
}
