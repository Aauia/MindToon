import SwiftUI

struct DreamWorldView: View {
    @ObservedObject var navigation: NavigationViewModel
    @StateObject private var viewModel = WorldViewModel()

    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                // Main content area
                ZStack {
                    // Background gradient for dream theme
                    LinearGradient(
                        gradient: Gradient(colors: [
                            Color(red: 0.85, green: 0.73, blue: 0.94), // lavender
                            Color(red: 0.99, green: 0.85, blue: 0.92)  // blush (slightly pinker than peach)
                        ]),
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    )
                    .edgesIgnoringSafeArea(.all)

                    ScrollView {
                        VStack(alignment: .leading, spacing: 20) {
                            // Header section
                            VStack(spacing: 10) {
                                Text("Planet of Dreams")
                                    .font(.largeTitle)
                                    .fontWeight(.bold)
                                    .foregroundColor(.white)
                                    .shadow(radius: 5)

                                Text("Your dream novels & dreamboards")
                                    .foregroundColor(.white.opacity(0.9))
                                    .multilineTextAlignment(.center)
                                    .padding(.horizontal)
                            }
                            .padding(.top, 20)

                            // Stats section
                            if let stats = viewModel.worldStats[.dreamWorld] {
                                HStack(spacing: 20) {
                                    StatCard(title: "Total Comics", value: "\(stats.totalComics)", icon: "book.fill")
                                    StatCard(title: "Favorites", value: "\(stats.favoriteComics)", icon: "heart.fill")
                                    StatCard(title: "Public", value: "\(stats.publicComics)", icon: "globe")
                                }
                                .padding(.horizontal)
                            }

                            // Quick actions
                            HStack(spacing: 15) {
                                QuickActionButton(
                                    title: "New Dream",
                                    icon: "plus.circle.fill",
                                    color: Color(red: 0.7, green: 0.4, blue: 0.9) // muted purple
                                ) {
                                    navigation.currentScreen = .comicGenerator
                                }

                            }
                            .padding(.horizontal)

                            // Comics grid
                            if viewModel.isLoading {
                                ProgressView("Loading dreams...")
                                    .frame(maxWidth: .infinity)
                                    .padding()
                            } else if viewModel.filteredComics.isEmpty {
                                VStack {
                                    Image(systemName: "moon.stars.fill")
                                        .font(.system(size: 60))
                                        .foregroundColor(.white.opacity(0.5))
                                    Text("No dream comics yet")
                                        .font(.title2)
                                        .foregroundColor(.white.opacity(0.8))
                                    Text("Create your first dream story!")
                                        .font(.body)
                                        .foregroundColor(.white.opacity(0.6))

                                    Button("Create Dream Comic") {
                                        navigation.currentScreen = .comicGenerator
                                    }
                                    .padding()
                                    .background(Color(red: 0.7, green: 0.4, blue: 0.9)) // muted purple
                                    .foregroundColor(.white)
                                    .cornerRadius(10)
                                    .padding(.top)
                                }
                                .frame(maxWidth: .infinity)
                                .padding(.vertical, 40)
                            } else {
                                LazyVGrid(columns: [
                                    GridItem(.flexible()),
                                    GridItem(.flexible())
                                ], spacing: 15) {
                                    ForEach(viewModel.filteredComics, id: \.id) { comic in
                                        ComicCardView(comic: comic, navigation: navigation)
                                    }
                                }
                                .padding(.horizontal)
                            }

                            // Error message
                            if let errorMessage = viewModel.errorMessage {
                                Text(errorMessage)
                                    .foregroundColor(.red)
                                    .padding()
                                    .background(Color.clear)
                                    .cornerRadius(10)
                                    .padding(.horizontal)
                            }
                        }
                        .padding(.vertical)
                    }
                }

                // Bottom bar
                BottombarView(navigation: navigation)
            }
            // ✅ Proper native navigation bar toolbar
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button(action: { navigation.currentScreen = .worlds }) {
                        Image(systemName: "chevron.left")
                            .font(.title2)
                            .foregroundColor(.primary)
                    }
                }
            }
            .navigationBarTitleDisplayMode(.inline)
            // ❌ Don't hide navigation bar if you want toolbar to show
            .onAppear {
                viewModel.selectedWorld = .dreamWorld
                Task {
                    await viewModel.loadInitialData()
                }
            }
        }
    }
}

#Preview {
    DreamWorldView(navigation: NavigationViewModel())
}
