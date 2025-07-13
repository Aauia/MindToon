import SwiftUI

struct DreamWorldView: View {
    @ObservedObject var navigation: NavigationViewModel
    @State private var reloadToken = UUID()

    var body: some View {
        DreamWorldInternalView(navigation: navigation, reloadToken: reloadToken) {
            reloadToken = UUID()
        }
        .id(reloadToken)
    }
}

private struct DreamWorldInternalView: View {
    @ObservedObject var navigation: NavigationViewModel
    let reloadToken: UUID
    let reloadAction: () -> Void
    @StateObject private var viewModel = WorldViewModel()

    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                ZStack {
                    LinearGradient(
                        gradient: Gradient(colors: [
                            Color(red: 0.85, green: 0.73, blue: 0.94),
                            Color(red: 0.99, green: 0.85, blue: 0.92)
                        ]),
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    )
                    .edgesIgnoringSafeArea(.all)

                    ScrollView {
                        VStack(alignment: .leading, spacing: 20) {
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
                            
                            if let stats = viewModel.worldStats[.dreamWorld] {
                                HStack(spacing: 20) {
                                    StatCard(title: "Total Comics", value: "\(stats.totalComics)", icon: "book.fill")
                                    
                                }
                                .padding(.horizontal)
                            }

                            HStack(spacing: 15) {
                                QuickActionButton(
                                    title: "New Dream",
                                    icon: "plus.circle.fill",
                                    color: Color.purple
                                ) {
                                    navigation.currentScreen = .comicGenerator
                                }
                            }
                            .padding(.horizontal)

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
                                    .background(Color.purple)
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

                            if let errorMessage = viewModel.errorMessage {
                                Text(errorMessage)
                                    .foregroundColor(.red)
                                    .padding(.horizontal)
                            }
                        }
                        .padding(.vertical)
                    }
                }

                BottombarView(navigation: navigation)
            }
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button(action: {
                        navigation.currentScreen = .worlds
                    }) {
                        Image(systemName: "chevron.left")
                            .font(.title2)
                            .foregroundColor(.primary)
                    }
                }

                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: {
                        Task {
                            await viewModel.loadInitialData(refresh: true)
                        }
                    }) {
                        Image(systemName: "arrow.clockwise")
                            .foregroundColor(.primary)
                    }
                }
            }
            .navigationBarTitleDisplayMode(.inline)
            .onAppear {
                viewModel.selectedWorld = .dreamWorld
                Task {
                    await viewModel.loadInitialData(refresh: true)
                }
            }
        }
    }
}
