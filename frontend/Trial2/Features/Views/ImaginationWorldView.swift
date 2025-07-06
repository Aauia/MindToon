import SwiftUI

struct ImaginationWorldView: View {
    @ObservedObject var navigation: NavigationViewModel
    @StateObject private var viewModel = WorldViewModel()
    
    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                // Main content area
                ZStack {
                    // Background gradient for fantasy theme
                    LinearGradient(
                        gradient: Gradient(colors: [Color.orange.opacity(0.6), Color.purple.opacity(0.4)]),
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    )
                    .edgesIgnoringSafeArea(.all)
                    
                    ScrollView {
                        VStack(alignment: .leading, spacing: 20) {
                            // Header section
                            VStack(spacing: 10) {
                                Text("Planet of Fantasy")
                                    .font(.largeTitle)
                                    .fontWeight(.bold)
                                    .foregroundColor(.white)
                                    .shadow(radius: 5)
                                
                                Text("Your comic projects, manga pages, and visual drafts")
                                    .foregroundColor(.white.opacity(0.9))
                                    .multilineTextAlignment(.center)
                                    .padding(.horizontal)
                            }
                            .padding(.top, 20)
                            
                            // Stats section
                            if let stats = viewModel.worldStats[.imaginationWorld] {
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
                                    title: "New Comic",
                                    icon: "plus.circle.fill",
                                    color: .blue
                                ) {
                                    navigation.currentScreen = .comicGenerator
                                }
                                
                                QuickActionButton(
                                    title: "View All",
                                    icon: "square.grid.2x2",
                                    color: .green
                                ) {
                                    // Toggle to show all comics
                                    viewModel.showFavoritesOnly.toggle()
                                }
                                
                                QuickActionButton(
                                    title: "Favorites",
                                    icon: "heart.fill",
                                    color: .pink
                                ) {
                                    viewModel.showFavoritesOnly = true
                                }
                            }
                            .padding(.horizontal)
                            
                            // Comics grid
                            if viewModel.isLoading {
                                ProgressView("Loading comics...")
                                    .frame(maxWidth: .infinity)
                                    .padding()
                            } else if viewModel.filteredComics.isEmpty {
                                VStack {
                                    Image(systemName: "sparkles")
                                        .font(.system(size: 60))
                                        .foregroundColor(.white.opacity(0.5))
                                    Text("No comics yet")
                                        .font(.title2)
                                        .foregroundColor(.white.opacity(0.8))
                                    Text("Create your first comic adventure!")
                                        .font(.body)
                                        .foregroundColor(.white.opacity(0.6))
                                    
                                    Button("Create Comic") {
                                        navigation.currentScreen = .comicGenerator
                                    }
                                    .padding()
                                    .background(Color.blue)
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
                                    .background(Color.white.opacity(0.8))
                                    .cornerRadius(10)
                                    .padding(.horizontal)
                            }
                        }
                        .padding(.vertical)
                    }
                }
                
                // Bottom bar
                BottombarView(navigation: navigation)
                    .frame(maxHeight: 80)
            }
            .toolbar {
                CustomTopBarContent(title: "", showBackButton: true, leadingAction: {
                    navigation.currentScreen = .worlds
                })
            }
            .navigationBarTitleDisplayMode(.inline)
            .onAppear {
                viewModel.selectedWorld = .imaginationWorld
                Task {
                    await viewModel.loadInitialData()
                }
            }
        }
    }
}

// MARK: - Supporting Views

struct StatCard: View {
    let title: String
    let value: String
    let icon: String
    
    var body: some View {
        VStack {
            Image(systemName: icon)
                .font(.title2)
                .foregroundColor(.white)
            Text(value)
                .font(.title3)
                .fontWeight(.bold)
                .foregroundColor(.white)
            Text(title)
                .font(.caption)
                .foregroundColor(.white.opacity(0.8))
        }
        .frame(maxWidth: .infinity)
        .padding()
        .background(Color.white.opacity(0.2))
        .cornerRadius(10)
    }
}

struct QuickActionButton: View {
    let title: String
    let icon: String
    let color: Color
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            VStack {
                Image(systemName: icon)
                    .font(.title2)
                    .foregroundColor(.white)
                Text(title)
                    .font(.caption)
                    .foregroundColor(.white)
            }
            .frame(maxWidth: .infinity)
            .padding()
            .background(color.opacity(0.7))
            .cornerRadius(10)
        }
    }
}

struct ComicCardView: View {
    let comic: ComicGenerationResponse
    let navigation: NavigationViewModel
    @State private var showFullScreen = false
    
    var body: some View {
        Button(action: {
            navigation.showComicViewer(with: comic)
        }) {
            VStack(alignment: .leading, spacing: 8) {
                // Comic image
                if let urlString = comic.imageUrl, let url = URL(string: urlString) {
                    AsyncImage(url: url) { phase in
                        switch phase {
                        case .empty:
                            ProgressView()
                                .frame(height: 120)
                        case .success(let image):
                            image
                                .resizable()
                                .aspectRatio(contentMode: .fill)
                                .frame(height: 120)
                                .clipShape(RoundedRectangle(cornerRadius: 10))
                                .onTapGesture {
                                    showFullScreen = true
                                }
                        case .failure:
                            RoundedRectangle(cornerRadius: 10)
                                .fill(Color.gray.opacity(0.3))
                                .frame(height: 120)
                                .overlay(
                                    Image(systemName: "photo")
                                        .font(.title)
                                        .foregroundColor(.gray)
                                )
                        @unknown default:
                            EmptyView()
                        }
                    }
                } else if let base64 = comic.imageBase64, !base64.isEmpty, let imageData = Data(base64Encoded: base64), let uiImage = UIImage(data: imageData) {
                    Image(uiImage: uiImage)
                        .resizable()
                        .aspectRatio(contentMode: .fill)
                        .frame(height: 120)
                        .clipShape(RoundedRectangle(cornerRadius: 10))
                        .onTapGesture {
                            showFullScreen = true
                        }
                } else {
                    RoundedRectangle(cornerRadius: 10)
                        .fill(Color.gray.opacity(0.3))
                        .frame(height: 120)
                        .overlay(
                            Image(systemName: "photo")
                                .font(.title)
                                .foregroundColor(.gray)
                        )
                }
                
                // Comic details
                VStack(alignment: .leading, spacing: 4) {
                    Text(comic.title)
                        .font(.headline)
                        .foregroundColor(.white)
                        .lineLimit(1)
                    
                    Text(comic.concept)
                        .font(.caption)
                        .foregroundColor(.white.opacity(0.8))
                        .lineLimit(2)
                    
                    HStack {
                        Text(comic.genre.capitalized)
                            .font(.caption2)
                            .padding(.horizontal, 6)
                            .padding(.vertical, 2)
                            .background(Color.blue.opacity(0.7))
                            .foregroundColor(.white)
                            .cornerRadius(4)
                        
                        Spacer()
                        
                        Text(formatDate(comic.createdAt))
                            .font(.caption2)
                            .foregroundColor(.white.opacity(0.6))
                    }
                }
                .padding(.horizontal, 8)
                .padding(.bottom, 8)
            }
            .background(Color.white.opacity(0.1))
            .cornerRadius(12)
            .overlay(
                RoundedRectangle(cornerRadius: 12)
                    .stroke(Color.white.opacity(0.2), lineWidth: 1)
            )
        }
        .buttonStyle(PlainButtonStyle())
        .fullScreenCover(isPresented: $showFullScreen) {
            FullScreenComicView(comic: comic)
        }
    }
    
    private func formatDate(_ dateString: String) -> String {
        let formatter = ISO8601DateFormatter()
        guard let date = formatter.date(from: dateString) else { return "" }
        
        let displayFormatter = DateFormatter()
        displayFormatter.dateStyle = .short
        return displayFormatter.string(from: date)
    }
}

#Preview {
    ImaginationWorldView(navigation: NavigationViewModel())
}
