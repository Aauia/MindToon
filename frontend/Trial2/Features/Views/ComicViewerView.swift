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
    @State private var hasDetailedScenario = false
    @State private var isLoadingScenario = false
    @State private var loadedComicImage: UIImage? = nil
    // Add this property to optionally receive the scenario from the view model
    @State var detailedScenarioText: String? = nil
    @State private var isLoadingDetailedScenario: Bool = false
    @State private var showFullScreenComic = false
    
    private let apiClient = APIClient.shared
    
    var body: some View {
        ZStack(alignment: .topLeading) {
            // Main content
            ZStack {
                // Updated background to match MainDashboardView
                LinearGradient(
                    gradient: Gradient(colors: [
                        Color(hex: "#D7A8F0"), // lavender (matches MainDashboardView)
                        Color(hex: "#FCDADA")  // peach (matches MainDashboardView)
                    ]),
                    startPoint: .top,
                    endPoint: .bottom
                )
                .ignoresSafeArea()
                
                if let comic = navigation.generatedComic {
                    VStack(spacing: 0) {
                        ZStack(alignment: .bottomTrailing) {
                            if let image = loadedComicImage {
                                Image(uiImage: image)
                                    .resizable()
                                    .aspectRatio(contentMode: .fit)
                                    .frame(maxWidth: .infinity, maxHeight: UIScreen.main.bounds.height * 0.45)
                                    .background(Color.clear)
                                    .onTapGesture {
                                        showFullScreenComic = true
                                    }
                            } else {
                                ComicImageView(comic: comic, onImageLoaded: { image in
                                    print("Comic image loaded for zoom")
                                    loadedComicImage = image
                                })
                                .frame(maxWidth: .infinity, maxHeight: UIScreen.main.bounds.height * 0.45)
                                .background(Color.clear)
                            }
                            if loadedComicImage != nil {
                                Button(action: { showFullScreenComic = true }) {
                                    Image(systemName: "magnifyingglass")
                                        .font(.title)
                                        .padding(10)
                                        .background(Color.white.opacity(0.7))
                                        .clipShape(Circle())
                                        .shadow(radius: 2)
                                }
                                .padding(16)
                            }
                        }
                    
                        // Info card below
                        VStack(spacing: 20) { // Increased spacing between name and script
                            // Comic Title Header with World Info
                            VStack(alignment: .leading, spacing: 12) {
                                HStack {
                                    Text(comic.title)
                                        .font(.title2)
                                        .fontWeight(.bold)
                                        .foregroundColor(Color(hex: "#5A3FA0"))
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
                                        .foregroundColor(Color(hex: "#5A3FA0").opacity(0.7))
                                    Spacer()
                                }
                            }
                            // Action Buttons
                            HStack(spacing: 32) {
                                // Favorite Button
                                // Download Button
                             
                                // Share Button
                                Button(action: {
                                    shareComic()
                                }) {
                                    Image(systemName: "paperplane")
                                        .font(.title2)
                                        .foregroundColor(.black)
                                }
                            }
                            .padding(.horizontal)
                            .padding(.top, 8)
                            // Script Section - Expanded
                            VStack(alignment: .leading, spacing: 12) {
                                Text("Story")
                                    .font(.title2)
                                    .fontWeight(.semibold)
                                    .foregroundColor(Color(hex: "#5A3FA0"))
                                if isLoadingDetailedScenario {
                                    ProgressView("Loading detailed scenario...")
                                        .frame(minHeight: 120, maxHeight: 200)
                                } else {
                                    ScrollView {
                                        Text(detailedScenarioText ?? comic.concept)
                                            .font(.body)
                                            .lineSpacing(4)
                                            .foregroundColor(Color(hex: "#5A3FA0").opacity(0.8))
                                            .multilineTextAlignment(.leading)
                                            .frame(maxWidth: .infinity, alignment: .leading)
                                            .padding(.horizontal, 4)
                                    }
                                    .frame(minHeight: 120, maxHeight: 200)
                                    .background(Color.clear)
                                }
                            }
                            .padding(.horizontal, 8)
                            .padding(.bottom, 8)
                        }
                        .background(Color.white.opacity(0.95))
                        .cornerRadius(16, corners: [.topLeft, .topRight])
                        .shadow(color: Color(hex: "#D7A8F0").opacity(0.15), radius: 8, x: 0, y: -2)
                        .padding(.horizontal, 0)
                    }
                    .background(Color.clear)
                    // Remove default toolbar back button
                    .toolbar { ToolbarItem(placement: .navigationBarLeading) { EmptyView() } }
                    .alert("Comic Status", isPresented: $showAlert) {
                        Button("OK") { }
                    } message: {
                        Text(alertMessage)
                    }
                    .onAppear {
                        guard let comic = navigation.generatedComic else { return }
                        detailedScenarioText = nil
                        if comic.hasDetailedScenario {
                            isLoadingDetailedScenario = true
                            Task {
                                do {
                                    let token = await AuthManager.shared.getStoredToken()
                                    if let token = token {
                                        let premise = try await APIClient.shared.getScenarioByComic(comicId: comic.id, token: token)
                                        detailedScenarioText = premise
                                    } else {
                                        detailedScenarioText = comic.concept
                                    }
                                } catch {
                                    detailedScenarioText = comic.concept
                                }
                                isLoadingDetailedScenario = false
                            }
                        } else {
                            detailedScenarioText = comic.concept
                        }
                    }
                    .onChange(of: navigation.generatedComic) { comic in
                        guard let comic = comic else { return }
                        detailedScenarioText = nil
                        if comic.hasDetailedScenario {
                            isLoadingDetailedScenario = true
                            Task {
                                do {
                                    let token = await AuthManager.shared.getStoredToken()
                                    if let token = token {
                                        let premise = try await APIClient.shared.getScenarioByComic(comicId: comic.id, token: token)
                                        detailedScenarioText = premise
                                    } else {
                                        detailedScenarioText = comic.concept
                                    }
                                } catch {
                                    detailedScenarioText = comic.concept
                                }
                                isLoadingDetailedScenario = false
                            }
                        } else {
                            detailedScenarioText = comic.concept
                        }
                    }
                    .sheet(isPresented: $showFullScreenComic) {
                        if let image = loadedComicImage {
                            FullScreenZoomComicView(image: image, isPresented: $showFullScreenComic)
                        }
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
            // Back button overlays the entire view, always visible
            Button(action: {
                navigation.navigateTo(.worlds)
            }) {
                Image(systemName: "chevron.left")
                    .font(.title2)
                    .foregroundColor(Color(hex: "#5A3FA0"))
                    .padding(8)
                    .background(Color.white.opacity(0.8))
                    .clipShape(Circle())
                    .shadow(color: Color.black.opacity(0.08), radius: 2, x: 0, y: 2)
            }
            .padding(.leading, 16)
            .padding(.top, 24)
        }
        
    }
    
    // MARK: - Helper Functions
    private func downloadComic() {
        print("📥 Download comic initiated")
        
        guard let comic = navigation.generatedComic else {
            print("❌ No comic available for download")
            return
        }
        
        guard let base64 = comic.imageBase64, !base64.isEmpty else {
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
        
        guard let urlString = comic.imageUrl, let url = URL(string: urlString) else {
            print("❌ No comic URL available for sharing")
            return
        }
        
        let activityItems: [Any] = [url]
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
        
        let cleanBase64 = comic.imageBase64 ?? ""
        
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
        
        guard let base64 = comic.imageBase64, !base64.isEmpty else {
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
                includeDetailedScenario: comic.hasDetailedScenario,
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
    
    // MARK: - Detailed Scenario Functions
    
    @MainActor
    private func checkForDetailedScenario() async {
        guard let comic = navigation.generatedComic else { return }
        
        // Use the hasDetailedScenario field from the comic response
        hasDetailedScenario = comic.hasDetailedScenario
        
        if hasDetailedScenario {
            print("✅ Comic has detailed scenario: \(comic.title)")
        } else {
            print("ℹ️ Comic does not have detailed scenario: \(comic.title)")
        }
    }
    

 
}

// MARK: - Comic Image View Component
struct ComicImageView: View {
    let comic: ComicGenerationResponse
    var onImageLoaded: (UIImage?) -> Void
    @State private var asyncImage: UIImage? = nil
    var body: some View {
        VStack(spacing: 0) {
            if let urlString = comic.imageUrl, let url = URL(string: urlString) {
                AsyncImage(url: url) { phase in
                    switch phase {
                    case .empty:
                        ProgressView()
                            .frame(maxHeight: 500)
                    case .success(let image):
                        let uiImage = image.asUIImage()
                        Color.clear.onAppear { onImageLoaded(uiImage) }
                        image
                            .resizable()
                            .aspectRatio(contentMode: .fill)
                            .frame(maxWidth: .infinity, maxHeight: 500)
                            .clipped()
                    case .failure:
                        placeholderView
                    @unknown default:
                        EmptyView()
                    }
                }
            } else if let base64 = comic.imageBase64, !base64.isEmpty, let imageData = Data(base64Encoded: base64), let uiImage = UIImage(data: imageData) {
                Color.clear.onAppear { onImageLoaded(uiImage) }
                Image(uiImage: uiImage)
                    .resizable()
                    .aspectRatio(contentMode: .fill)
                    .frame(maxWidth: .infinity, maxHeight: 500)
                    .clipped()
            } else {
                Color.clear.onAppear { onImageLoaded(nil) }
                placeholderView
            }
        }
    }
    private var placeholderView: some View {
        ZStack {
            RoundedRectangle(cornerRadius: 18)
                .fill(Color.gray.opacity(0.18))
                .frame(maxWidth: .infinity, maxHeight: 500)
                .aspectRatio(1, contentMode: .fit)
            Image(systemName: "photo")
                .font(.system(size: 64, weight: .regular))
                .foregroundColor(Color.gray.opacity(0.45))
        }
        .padding(.horizontal, 8)
    }
}

extension Image {
    func asUIImage() -> UIImage? {
        #if canImport(UIKit)
        let controller = UIHostingController(rootView: self.resizable())
        let view = controller.view
        let targetSize = CGSize(width: 1024, height: 1024)
        view?.bounds = CGRect(origin: .zero, size: targetSize)
        view?.backgroundColor = .clear
        let renderer = UIGraphicsImageRenderer(size: targetSize)
        return renderer.image { _ in
            view?.drawHierarchy(in: view?.bounds ?? .zero, afterScreenUpdates: true)
        }
        #else
        return nil
        #endif
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
            createdAt: "2024-01-01T00:00:00Z",
            hasDetailedScenario: true
        )
        
        let navigation = NavigationViewModel()
        navigation.generatedComic = previewComic
        
        return ComicViewerView(navigation: navigation)
    }
} 

// Add a full screen zoomable comic view
import UIKit

struct FullScreenComicView: View {
    let image: UIImage?
    @Binding var isPresented: Bool

    var body: some View {
        ZStack(alignment: .topTrailing) {
            Color.black.ignoresSafeArea()
            if let image = image {
                ZoomableComicImage(image: image)
            } else {
                Image(systemName: "photo")
                    .resizable()
                    .aspectRatio(contentMode: .fit)
                    .foregroundColor(.gray)
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
            }
            Button(action: { isPresented = false }) {
                Image(systemName: "xmark.circle.fill")
                    .font(.system(size: 32))
                    .foregroundColor(.white)
                    .shadow(radius: 8)
                    .padding()
            }
        }
    }
}

struct ZoomableComicImage: UIViewRepresentable {
    let image: UIImage

    func makeUIView(context: Context) -> UIScrollView {
        let scrollView = UIScrollView()
        scrollView.minimumZoomScale = 1.0
        scrollView.maximumZoomScale = 5.0
        scrollView.backgroundColor = .black
        scrollView.delegate = context.coordinator

        let imageView = UIImageView(image: image)
        imageView.contentMode = .scaleAspectFit
        imageView.clipsToBounds = true
        imageView.translatesAutoresizingMaskIntoConstraints = false

        scrollView.addSubview(imageView)
        context.coordinator.imageView = imageView

        NSLayoutConstraint.activate([
            imageView.leadingAnchor.constraint(equalTo: scrollView.leadingAnchor),
            imageView.trailingAnchor.constraint(equalTo: scrollView.trailingAnchor),
            imageView.topAnchor.constraint(equalTo: scrollView.topAnchor),
            imageView.bottomAnchor.constraint(equalTo: scrollView.bottomAnchor),
            imageView.widthAnchor.constraint(equalTo: scrollView.widthAnchor),
            imageView.heightAnchor.constraint(equalTo: scrollView.heightAnchor)
        ])

        return scrollView
    }

    func updateUIView(_ uiView: UIScrollView, context: Context) {
        // No update needed, image is static
    }

    func makeCoordinator() -> Coordinator {
        Coordinator()
    }

    class Coordinator: NSObject, UIScrollViewDelegate {
        var imageView: UIImageView?
        func viewForZooming(in scrollView: UIScrollView) -> UIView? {
            return imageView
        }
    }
} 

struct ZoomableComicImageView: View {
    let image: UIImage
    @State private var scale: CGFloat = 1.0
    @State private var lastScale: CGFloat = 1.0
    @State private var offset: CGSize = .zero
    @State private var lastOffset: CGSize = .zero

    var body: some View {
        Image(uiImage: image)
            .resizable()
            .aspectRatio(contentMode: .fit)
            .scaleEffect(scale)
            .offset(offset)
            .gesture(
                SimultaneousGesture(
                    MagnificationGesture()
                        .onChanged { value in
                            scale = lastScale * value
                        }
                        .onEnded { value in
                            lastScale = scale
                        },
                    DragGesture()
                        .onChanged { value in
                            offset = CGSize(width: lastOffset.width + value.translation.width, height: lastOffset.height + value.translation.height)
                        }
                        .onEnded { value in
                            lastOffset = offset
                        }
                )
            )
            .onTapGesture(count: 2) {
                if scale > 1 {
                    scale = 1
                    lastScale = 1
                    offset = .zero
                    lastOffset = .zero
                } else {
                    scale = 2
                    lastScale = 2
                }
            }
            .animation(.easeInOut, value: scale)
    }
} 

struct FullScreenZoomComicView: View {
    let image: UIImage
    @Binding var isPresented: Bool

    var body: some View {
        ZStack(alignment: .topTrailing) {
            Color.black.ignoresSafeArea()
            ZoomableComicImageView(image: image)
                .padding()
            Button(action: { isPresented = false }) {
                Image(systemName: "xmark.circle.fill")
                    .font(.system(size: 32))
                    .foregroundColor(.white)
                    .shadow(radius: 8)
                    .padding()
            }
        }
    }
} 
