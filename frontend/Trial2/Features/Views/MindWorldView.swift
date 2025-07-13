import SwiftUI

struct MindWorldView: View {
    @ObservedObject var navigation: NavigationViewModel
    @StateObject private var viewModel = WorldViewModel()

    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                // Main content area
                ZStack {
                    // Background gradient for mind theme
                    LinearGradient(
                        gradient: Gradient(colors: [
                            Color(red: 0.78, green: 0.85, blue: 0.97), // soft blue-lavender
                            Color(red: 0.80, green: 0.97, blue: 0.92)  // minty aqua
                        ]),
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    )
                    .edgesIgnoringSafeArea(.all)
                    
                    ScrollView {
                        VStack(alignment: .leading, spacing: 20) {
                            // Header section
                            VStack(spacing: 10) {
                                Text("Planet of Mind")
                                    .font(.largeTitle)
                                    .fontWeight(.bold)
                                    .foregroundColor(.white)
                                    .shadow(radius: 5)
                                
                                Text("Your graphic essays & reflections")
                                    .foregroundColor(.white.opacity(0.9))
                                    .multilineTextAlignment(.center)
                                    .padding(.horizontal)
                            }
                            .padding(.top, 20)
                            
                            // Stats section
                            if let stats = viewModel.worldStats[.mindWorld] {
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
                                    title: "New Essay",
                                    icon: "plus.circle.fill",
                                    color: Color(red: 0.7, green: 0.4, blue: 0.9) // muted purple
                                ) {
                                    navigation.currentScreen = .comicGenerator
                                }
                              
                                
                            }
                            .padding(.horizontal)
                            
                            // Comics grid
                            if viewModel.isLoading {
                                ProgressView("Loading thoughts...")
                                    .frame(maxWidth: .infinity)
                                    .padding()
                            } else if viewModel.filteredComics.isEmpty {
                                VStack {
                                    Image(systemName: "brain.head.profile")
                                        .font(.system(size: 60))
                                        .foregroundColor(.white.opacity(0.5))
                                    Text("No mind comics yet")
                                        .font(.title2)
                                        .foregroundColor(.white.opacity(0.8))
                                    Text("Create your first reflective story!")
                                        .font(.body)
                                        .foregroundColor(.white.opacity(0.6))
                                    
                                    Button("Create Mind Comic") {
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
            .onAppear {
                viewModel.selectedWorld = .mindWorld
                Task {
                    await viewModel.loadInitialData()
                }
            }
        }
    }
}

#Preview {
    MindWorldView(navigation: NavigationViewModel())
}
