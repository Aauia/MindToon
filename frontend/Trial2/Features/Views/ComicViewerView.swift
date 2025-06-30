import SwiftUI

// MARK: - ComicViewerView
struct ComicViewerView: View {
    @ObservedObject var navigation: NavigationViewModel
    @Environment(\.dismiss) private var dismiss
    
    // State for save functionality
    @State private var isSaved = false
    @State private var isFavorite = false
    @State private var isLoading = false
    @State private var showAlert = false
    @State private var alertMessage = ""
    
    private let apiClient = APIClient.shared
    
    var body: some View {
        Group {
            if let comic = navigation.generatedComic {
                VStack(spacing: 0) {
                    // Custom Navigation Bar
                    HStack {
                        Button(action: {
                            dismiss()
                        }) {
                            Image(systemName: "arrow.left.circle.fill")
                                .font(.title2)
                                .foregroundColor(.black)
                        }
                        
                        Spacer()
                        
                        Button("Edit") {
                            navigation.navigateTo(.comicGenerator)
                            dismiss()
                        }
                        .foregroundColor(.blue)
                    }
                    .padding(.horizontal)
                    .padding(.top, 8)
                    .background(Color.white)
                    
                    // Comic Display Area
                    ScrollView {
                        VStack(spacing: 16) {
                            // MAIN COMIC DISPLAY - Prioritize Complete Comic Sheet
                            ComicImageView(comic: comic)
                            
                            Spacer(minLength: 120) // Space for bottom section
                        }
                    }
                    
                    // Bottom Comic Information Section
                    VStack(spacing: 0) {
                        // Comic Title Header with World Info
                        VStack(alignment: .leading, spacing: 8) {
                            HStack {
                                Text(comic.title)
                                    .font(.title2)
                                    .fontWeight(.bold)
                                    .foregroundColor(.black)
                                Spacer()
                            }
                            
                            // World Information
                            HStack {
                                Circle()
                                    .fill(worldColor(for: comic.worldType))
                                    .frame(width: 20, height: 20)
                                    .overlay(
                                        Image(systemName: worldIcon(for: comic.worldType))
                                            .font(.system(size: 10))
                                            .foregroundColor(.white)
                                    )
                                
                                Text("Saved to \(comic.worldType.displayName)")
                                    .font(.caption)
                                    .foregroundColor(.black.opacity(0.7))
                                
                                Spacer()
                            }
                        }
                        
                        // Action Buttons
                        HStack(spacing: 20) {
                            // Save to World Button
                            Button(action: {
                                saveComicToWorld()
                            }) {
                                if isLoading {
                                    ProgressView()
                                        .scaleEffect(0.8)
                                } else {
                                    Image(systemName: isSaved ? "checkmark.circle.fill" : "plus.circle")
                                        .font(.title2)
                                        .foregroundColor(isSaved ? .green : .blue)
                                }
                            }
                            .disabled(isLoading || isSaved)
                            
                            // Favorite Button
                            Button(action: {
                                toggleFavorite()
                            }) {
                                Image(systemName: isFavorite ? "heart.fill" : "heart")
                                    .font(.title2)
                                    .foregroundColor(isFavorite ? .red : .black)
                            }
                            .disabled(!isSaved) // Can only favorite saved comics
                            
                            Button(action: {
                                downloadComic()
                            }) {
                                Image(systemName: "arrow.down")
                                    .font(.title2)
                                    .foregroundColor(.black)
                            }
                            
                            Button(action: {
                                shareComic()
                            }) {
                                Image(systemName: "paperplane")
                                    .font(.title2)
                                    .foregroundColor(.black)
                            }
                        }
                        .padding(.horizontal)
                        .padding(.top, 16)
                        
                        // Script Section - Expanded
                        VStack(alignment: .leading, spacing: 12) {
                            Text("Your script")
                                .font(.title2)
                                .fontWeight(.semibold)
                                .foregroundColor(.black)
                            
                            ScrollView {
                                Text(comic.concept)
                                    .font(.body)
                                    .lineSpacing(4)
                                    .foregroundColor(.black.opacity(0.8))
                                    .multilineTextAlignment(.leading)
                                    .frame(maxWidth: .infinity, alignment: .leading)
                                    .padding(.horizontal, 4)
                            }
                            .frame(minHeight: 120, maxHeight: 200) // Increased from 80-120 to 120-200
                            .background(Color.clear)
                        }
                        .padding(.horizontal, 20)
                        .padding(.bottom, 20)
                    }
                    .background(Color(red: 1.0, green: 0.9, blue: 0.7)) // Sandy/yellow background
                    .cornerRadius(16, corners: [.topLeft, .topRight])
                }
                .background(Color.white)
                .navigationBarHidden(true)
                .alert("Comic Status", isPresented: $showAlert) {
                    Button("OK") { }
                } message: {
                    Text(alertMessage)
                }
                .onAppear {
                    print("🎬 ComicViewerView appeared - Title: '\(comic.title)'")
                    print("🎬 ImageBase64 length: \(comic.imageBase64.count)")
                }
            } else {
                // Show error when no comic is available
                VStack {
                    Image(systemName: "exclamationmark.triangle")
                        .font(.system(size: 50))
                        .foregroundColor(.orange)
                    Text("No comic to display")
                        .font(.title2)
                        .padding()
                    Button("Go Back") {
                        dismiss()
                    }
                    .padding()
                    .background(Color.blue)
                    .foregroundColor(.white)
                    .cornerRadius(10)
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity)
                .background(Color.white)
            }
        }
    }
    
    // MARK: - Helper Functions
    private func downloadComic() {
        print("📥 Download comic initiated")
        
        guard let comic = navigation.generatedComic else {
            print("❌ No comic available for download")
            return
        }
        
        guard !comic.imageBase64.isEmpty else {
            print("❌ No image data available for download")
            return
        }
        
        guard let imageData = decodeComicImage(),
              let image = UIImage(data: imageData) else {
            print("❌ Failed to decode comic image for download")
            return
        }
        
        UIImageWriteToSavedPhotosAlbum(image, nil, nil, nil)
        print("✅ Comic saved to Photos library")
    }
    
    private func shareComic() {
        print("📤 Share comic initiated")
        
        guard let comic = navigation.generatedComic else {
            print("❌ No comic available for sharing")
            return
        }
        
        guard !comic.imageBase64.isEmpty else {
            print("❌ No image data available for sharing")
            return
        }
        
        guard let imageData = decodeComicImage(),
              let image = UIImage(data: imageData) else {
            print("❌ Failed to decode comic image for sharing")
            return
        }
        
        let activityItems: [Any] = [
            image,
            "Check out my comic: \(comic.title)"
        ]
        
        let activityViewController = UIActivityViewController(activityItems: activityItems, applicationActivities: nil)
        
        if let windowScene = UIApplication.shared.connectedScenes.first as? UIWindowScene,
           let window = windowScene.windows.first,
           let rootViewController = window.rootViewController {
            
            if let popover = activityViewController.popoverPresentationController {
                popover.sourceView = rootViewController.view
                popover.sourceRect = CGRect(x: rootViewController.view.bounds.midX,
                                         y: rootViewController.view.bounds.midY,
                                         width: 0, height: 0)
                popover.permittedArrowDirections = []
            }
            
            rootViewController.present(activityViewController, animated: true)
            print("✅ Share sheet presented")
        }
    }
    
    private func decodeComicImage() -> Data? {
        guard let comic = navigation.generatedComic else { return nil }
        
        let cleanBase64 = comic.imageBase64
            .replacingOccurrences(of: "data:image/png;base64,", with: "")
            .replacingOccurrences(of: "data:image/jpeg;base64,", with: "")
            .replacingOccurrences(of: "data:image/jpg;base64,", with: "")
            .replacingOccurrences(of: "data:image/webp;base64,", with: "")
            .trimmingCharacters(in: .whitespacesAndNewlines)
        
        return Data(base64Encoded: cleanBase64)
    }
    
    // MARK: - World-Based Save Functions
    
    private func saveComicToWorld() {
        Task {
            await performSaveToWorld()
        }
    }
    
    @MainActor
    private func performSaveToWorld() async {
        guard let comic = navigation.generatedComic else {
            alertMessage = "Cannot save comic: No comic available"
            showAlert = true
            return
        }
        
        guard !comic.imageBase64.isEmpty else {
            alertMessage = "Cannot save comic: No image data available"
            showAlert = true
            return
        }
        
        isLoading = true
        
        do {
            let saveRequest = ComicSaveRequest(
                title: comic.title,
                concept: comic.concept,
                genre: comic.genre,
                artStyle: comic.artStyle,
                worldType: comic.worldType, // Save to the comic's original world
                imageBase64: comic.imageBase64,
                panelsData: comic.panelsData,
                isFavorite: false,
                isPublic: false
            )
            
            print("🌍 Saving comic '\(comic.title)' to \(comic.worldType.displayName)")
            
            let response = try await apiClient.generateComicWithData(request: saveRequest, token: AuthManager.shared.getStoredToken() ?? "")
            
            isSaved = true
            alertMessage = "Comic saved successfully to \(comic.worldType.displayName)! ✨"
            showAlert = true
            
            print("✅ Comic saved successfully to \(comic.worldType.displayName)")
            
        } catch {
            alertMessage = "Failed to save comic: \(error.localizedDescription)"
            showAlert = true
            print("❌ Failed to save comic: \(error)")
        }
        
        isLoading = false
    }
    
    private func toggleFavorite() {
        guard isSaved else { return }
        
        Task {
            await performToggleFavorite()
        }
    }
    
    @MainActor
    private func performToggleFavorite() async {
        guard let comic = navigation.generatedComic else { return }
        
        // Note: This is a placeholder since we need the comic ID from the backend
        // In a real implementation, you'd need to store the comic ID after saving
        // and then use apiClient.toggleFavorite(comicId:currentStatus:token:)
        
        isFavorite.toggle()
        let status = isFavorite ? "Added to" : "Removed from"
        alertMessage = "\(status) favorites in \(comic.worldType.displayName)! ❤️"
        showAlert = true
        
        print("❤️ Comic favorite status toggled: \(isFavorite)")
    }
    
    // MARK: - World Helper Functions
    
    private func worldColor(for worldType: WorldType) -> Color {
        switch worldType {
        case .dreamWorld:
            return Color.purple
        case .mindWorld:
            return Color.blue
        case .imaginationWorld:
            return Color.orange
        }
    }
    
    private func worldIcon(for worldType: WorldType) -> String {
        switch worldType {
        case .dreamWorld:
            return "moon.stars"
        case .mindWorld:
            return "brain.head.profile"
        case .imaginationWorld:
            return "sparkles"
        }
    }
}

// MARK: - Comic Image View Component
struct ComicImageView: View {
    let comic: ComicGenerationResponse
    
    var body: some View {
        // Debug info
        let _ = print("🔍 ComicImageView - imageBase64.isEmpty: \(comic.imageBase64.isEmpty)")
        let _ = print("🔍 ComicImageView - imageBase64.count: \(comic.imageBase64.count)")
        let _ = !comic.imageBase64.isEmpty ? print("🔍 First 50 chars: \(String(comic.imageBase64.prefix(50)))") : ()
        
        return VStack(spacing: 16) {
            if !comic.imageBase64.isEmpty {
                // Clean the base64 string (remove data URL prefix if present)
                let cleanBase64 = comic.imageBase64
                    .replacingOccurrences(of: "data:image/png;base64,", with: "")
                    .replacingOccurrences(of: "data:image/jpeg;base64,", with: "")
                    .replacingOccurrences(of: "data:image/jpg;base64,", with: "")
                    .replacingOccurrences(of: "data:image/webp;base64,", with: "")
                    .trimmingCharacters(in: .whitespacesAndNewlines)
                
                let _ = print("🧹 Cleaned base64 length: \(cleanBase64.count)")
                let _ = print("🧹 First 50 chars after cleaning: \(String(cleanBase64.prefix(50)))")
                
                if let imageData = Data(base64Encoded: cleanBase64) {
                    let _ = print("✅ Successfully decoded base64 to Data: \(imageData.count) bytes")
                    
                    if let uiImage = UIImage(data: imageData) {
                        let _ = print("✅ Successfully created UIImage: \(uiImage.size)")
                        
                        // SUCCESS: Display the PNG image - More compact
                        Image(uiImage: uiImage)
                            .resizable()
                            .aspectRatio(contentMode: .fit)
                            .frame(maxWidth: .infinity)
                            .frame(maxHeight: 450) // Reduced from 800 to 450 for more compact display
                            .cornerRadius(12)
                            .shadow(color: .black.opacity(0.1), radius: 8, x: 0, y: 4)
                            .padding(.horizontal)
                        
                    } else {
                        let _ = print("❌ Failed to create UIImage from Data")
                        showErrorMessage("Failed to create image from data")
                    }
                } else {
                    let _ = print("❌ Failed to decode base64 string")
                    showErrorMessage("Failed to decode base64 string")
                }
            } else {
                let _ = print("❌ No image data provided")
                showErrorMessage("No image data provided")
            }
        }
    }
    
    private func showErrorMessage(_ message: String) -> some View {
        VStack(spacing: 16) {
            Image(systemName: "photo.circle.fill")
                .font(.system(size: 50))
                .foregroundColor(.red)
            
            Text("Unable to display comic image")
                .font(.headline)
                .foregroundColor(.red)
            
            Text(message)
                .font(.body)
                .foregroundColor(.gray)
            
            if !comic.imageBase64.isEmpty {
                Text("Base64 data: \(comic.imageBase64.count) characters")
                    .font(.caption)
                    .foregroundColor(.blue)
            }
        }
        .padding()
    }
}

// MARK: - Corner Radius Extension
extension View {
    func cornerRadius(_ radius: CGFloat, corners: UIRectCorner) -> some View {
        clipShape(RoundedCorner(radius: radius, corners: corners))
    }
}

struct RoundedCorner: Shape {
    var radius: CGFloat = 10.0
    var corners: UIRectCorner = .allCorners

    func path(in rect: CGRect) -> Path {
        let safeRadius = radius.isFinite && radius > 0 ? min(radius, min(rect.width, rect.height) / 2) : 10.0
        let path = UIBezierPath(
            roundedRect: rect,
            byRoundingCorners: corners,
            cornerRadii: CGSize(width: safeRadius, height: safeRadius)
        )
        return Path(path.cgPath)
    }
}

// MARK: - Preview
struct ComicViewerView_Previews: PreviewProvider {
    static var previews: some View {
        let previewComic = ComicGenerationResponse(
            title: "Ocean Dreams",
            concept: "I used to love the water. The way it moved, the way it felt. But now...",
            genre: "adventure",
            artStyle: "comic book",
            worldType: .dreamWorld,
            imageBase64: "",
            panelsData: "{\"panel1\":{\"description\":\"A person standing by the ocean\",\"dialogue\":\"I used to love the water\"}}",
            createdAt: "2024-01-01T00:00:00Z"
        )
        
        let navigation = NavigationViewModel()
        navigation.generatedComic = previewComic
        
        return ComicViewerView(navigation: navigation)
    }
} 
