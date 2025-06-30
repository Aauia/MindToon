import SwiftUI

// MARK: - MainDashboardView
struct MainDashboardView: View {
    @ObservedObject var navigation: NavigationViewModel

    var body: some View {
        NavigationView { // Still needed to host the toolbar
            VStack(spacing: 0) { // Set spacing to 0 for controlled layout
                ScrollView { // Make the content scrollable if it gets long
                    VStack(spacing: 20) {
                        Spacer()

                        Image(systemName: "brain.head.profile")
                            .resizable()
                            .scaledToFit()
                            .frame(width: 150, height: 150)
                            .foregroundColor(.blue)
                            .padding(.bottom, 20)

                        Text("Welcome to MindToon!")
                            .font(.largeTitle)
                            .fontWeight(.bold)
                            .foregroundColor(.primary)

                        Text("How can I help you today?")
                            .font(.title2)
                            .foregroundColor(.secondary)

                        // Test Image Generator Button
                        VStack(spacing: 12) {
                            Text("🧪 Testing Features")
                                .font(.headline)
                                .foregroundColor(.primary)
                            
                            Button(action: {
                                navigation.navigateTo(.imageGenerator)
                            }) {
                                HStack {
                                    Image(systemName: "photo.badge.plus")
                                        .font(.title2)
                                    Text("Test Image Generator")
                                        .font(.headline)
                                }
                                .foregroundColor(.white)
                                .padding()
                                .frame(maxWidth: .infinity)
                                .background(Color.green)
                                .cornerRadius(15)
                            }
                        }
                        .padding(.horizontal)
                        .padding(.top, 20)

                        Spacer() // Pushes content up, allowing bottom bar to stick
                    }
                    // Ensure content fills screen height minus the bottom bar's estimated height
                    .frame(maxWidth: .infinity, minHeight: 600) // Fixed minimum height
                }
                .padding(.bottom, -8) // Adjust to prevent extra padding above custom tab bar

                // Integrate the separate BottombarView here
                BottombarView(navigation: navigation)
                    .frame(maxHeight: 80) // Give it a fixed height or minHeight
            }

            .navigationBarTitleDisplayMode(.inline)
            // Remove .navigationBarHidden(true) as we are using the toolbar for the top bar
            .background(Color(red: 1.0, green: 1.0, blue: 1.0)) // Fixed invalid color values
        }
    }
}

// MARK: - Helper Views for Dashboard (WorldButton unchanged)

// MARK: - Preview
#Preview {
    MainDashboardView(navigation: NavigationViewModel())
}
