import SwiftUI

// MARK: - Shared Components for World Views

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
    }
    
    private func formatDate(_ dateString: String) -> String {
        let formatter = ISO8601DateFormatter()
        guard let date = formatter.date(from: dateString) else { return "" }
        
        let displayFormatter = DateFormatter()
        displayFormatter.dateStyle = .short
        return displayFormatter.string(from: date)
    }
}

// MARK: - Preview
#Preview {
    VStack(spacing: 20) {
        StatCard(title: "Total Comics", value: "15", icon: "book.fill")
        QuickActionButton(title: "New Comic", icon: "plus.circle.fill", color: .blue) {}
        ComicCardView(
            comic: ComicGenerationResponse(
                title: "Sample Comic",
                concept: "A sample comic for preview",
                genre: "adventure",
                artStyle: "comic book",
                worldType: .imaginationWorld,
                imageBase64: "",
                panelsData: "",
                createdAt: "2024-01-01T00:00:00Z",
                hasDetailedScenario: false
            ),
            navigation: NavigationViewModel()
        )
    }
    .padding()
    .background(Color.black)
} 