// ComicViewerView.swift (Fixed)
import SwiftUI
import UIKit

struct ComicViewerView: View {
    @ObservedObject var navigation: NavigationViewModel
    @Environment(\.dismiss) private var dismiss

    @State private var isSaved = false
    @State private var isFavorite = false
    @State private var isLoading = false
    @State private var showAlert = false
    @State private var alertMessage = ""
    @State private var detailedScenarioText: String? = nil
    @State private var isLoadingDetailedScenario: Bool = false
    @State private var showFullScreenComic = false
    @State private var loadedComicImage: UIImage? = nil

    var body: some View {
        ZStack(alignment: .topLeading) {
            if let comic = navigation.generatedComic {
                comicContent(comic)
            } else {
                emptyComicView
            }

            Button(action: { navigation.navigateTo(.worlds) }) {
                Image(systemName: "chevron.left")
                    .font(.title2)
                    .foregroundColor(Color(hex: "#5A3FA0"))
                    .padding(8)
                    .background(Color.white.opacity(0.8))
                    .clipShape(Circle())
            }
            .padding(.leading, 16)
            .padding(.top, 24)
        }
    }

    @ViewBuilder
    private func comicContent(_ comic: ComicGenerationResponse) -> some View {
        ZStack {
            LinearGradient(
                gradient: Gradient(colors: [Color(hex: "#D7A8F0"), Color(hex: "#FCDADA")]),
                startPoint: .top, endPoint: .bottom
            ).ignoresSafeArea()

            VStack(spacing: 0) {
                comicImageSection(comic)
                comicInfoSection(comic)
            }
            .alert("Comic Status", isPresented: $showAlert) {
                Button("OK") {}
            } message: {
                Text(alertMessage)
            }
            .onAppear {
                loadScenario(for: comic)
            }
            .onChange(of: navigation.generatedComic) { oldComic, newComic in
                if let comic = newComic {
                    loadScenario(for: comic)
                }
            }

            .sheet(isPresented: $showFullScreenComic) {
                if let image = loadedComicImage {
                    FullScreenZoomComicView(image: image, isPresented: $showFullScreenComic)
                }
            }
        }
    }

    private func comicImageSection(_ comic: ComicGenerationResponse) -> some View {
        ZStack(alignment: .bottomTrailing) {
            if let image = loadedComicImage {
                Image(uiImage: image)
                    .resizable()
                    .aspectRatio(contentMode: .fit)
                    .frame(maxWidth: .infinity, maxHeight: UIScreen.main.bounds.height * 0.45)
                    .onTapGesture { showFullScreenComic = true }
            } else {
                ComicImageView(comic: comic, onImageLoaded: { loadedComicImage = $0 })
                    .frame(maxWidth: .infinity, maxHeight: UIScreen.main.bounds.height * 0.45)
            }

            if loadedComicImage != nil {
                Button(action: { showFullScreenComic = true }) {
                    Image(systemName: "magnifyingglass")
                        .font(.title)
                        .padding(10)
                        .background(Color.white.opacity(0.7))
                        .clipShape(Circle())
                }
                .padding(16)
            }
        }
    }

    private func comicInfoSection(_ comic: ComicGenerationResponse) -> some View {
        VStack(spacing: 20) {
            VStack(alignment: .leading, spacing: 12) {
                HStack {
                    Text(comic.title)
                        .font(.title2)
                        .fontWeight(.bold)
                        .foregroundColor(Color(hex: "#5A3FA0"))
                    Spacer()
                }
                .padding(.horizontal, 30)
                .padding(.top, 16) 
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
                .padding(.horizontal, 30)
            }

            // HStack(spacing: 32) {

            HStack {
                Spacer()
                Button(action: { shareComic(comic) }) {
                    Image(systemName: "paperplane")
                        .font(.title2)
                        .foregroundColor(.black)
                }
            }
            .padding(.horizontal, 30)

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
                    }
                    .frame(minHeight: 120, maxHeight: 200)
                }
            }
            .padding(.horizontal, 25)
        }
        .padding(.bottom, 8)
        .background(Color.white.opacity(0.95))
        .cornerRadius(16)
        .shadow(color: Color(hex: "#D7A8F0").opacity(0.15), radius: 8, x: 0, y: -2)
    }

    private var emptyComicView: some View {
        VStack {
            Image(systemName: "exclamationmark.triangle")
                .font(.system(size: 50))
                .foregroundColor(.orange)
            Text("No comic to display")
                .font(.title2)
                .padding()
            Button("Go Back") { dismiss() }
                .padding()
                .background(Color.blue)
                .foregroundColor(.white)
                .cornerRadius(10)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color.white)
    }

    private func loadScenario(for comic: ComicGenerationResponse) {
        detailedScenarioText = nil
        isLoadingDetailedScenario = comic.hasDetailedScenario
        if comic.hasDetailedScenario {
            Task {
                defer { isLoadingDetailedScenario = false }
                do {
                    if let token = await AuthManager.shared.getStoredToken() {
                        detailedScenarioText = try await APIClient.shared.getScenarioByComic(comicId: comic.id)
                    } else {
                        detailedScenarioText = comic.concept
                    }
                } catch {
                    detailedScenarioText = comic.concept
                }
            }
        } else {
            detailedScenarioText = comic.concept
        }
    }

    private func worldColor(for worldType: WorldType) -> Color {
        switch worldType {
        case .dreamWorld: return Color.purple
        case .mindWorld: return Color.blue
        case .imaginationWorld: return Color.orange
        }
    }

    private func worldIcon(for worldType: WorldType) -> String {
        switch worldType {
        case .dreamWorld: return "moon.stars"
        case .mindWorld: return "brain.head.profile"
        case .imaginationWorld: return "sparkles"
        }
    }

    private func shareComic(_ comic: ComicGenerationResponse) {
        guard let urlString = comic.imageUrl, let url = URL(string: urlString) else { return }
        let activityVC = UIActivityViewController(activityItems: [url], applicationActivities: nil)

        if let windowScene = UIApplication.shared.connectedScenes.first as? UIWindowScene,
           let rootVC = windowScene.windows.first?.rootViewController {
            rootVC.present(activityVC, animated: true)
        }
    }
}

// Other views like ComicImageView, FullScreenZoomComicView, etc. must be in separate files or placed below this if not already included


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
