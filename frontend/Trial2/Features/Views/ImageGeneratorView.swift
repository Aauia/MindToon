import SwiftUI

// MARK: - ImageGeneratorView
struct ImageGeneratorView: View {
    @ObservedObject var navigation: NavigationViewModel
    @State private var prompt: String = ""
    @State private var isLoading: Bool = false
    @State private var errorMessage: String? = nil
    @State private var generatedImageData: Data? = nil
    @State private var generatedImage: UIImage? = nil
    
    private let apiClient = APIClient.shared
    
    var body: some View {
        VStack(spacing: 20) {
            // Header
            Text("Image Generator")
                .font(.title)
                .fontWeight(.bold)
                .padding(.top)
            
            Text("Test single image generation from prompts")
                .font(.subheadline)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal)
            
            // Prompt Input
            VStack(alignment: .leading, spacing: 8) {
                Text("Enter your image prompt:")
                    .font(.headline)
                
                TextEditor(text: $prompt)
                    .frame(minHeight: 100)
                    .padding(8)
                    .background(Color.gray.opacity(0.1))
                    .cornerRadius(8)
                    .overlay(
                        RoundedRectangle(cornerRadius: 8)
                            .stroke(Color.gray.opacity(0.3), lineWidth: 1)
                    )
            }
            .padding(.horizontal)
            
            // Generate Button
            Button(action: {
                Task {
                    await generateImage()
                }
            }) {
                HStack {
                    if isLoading {
                        ProgressView()
                            .scaleEffect(0.8)
                    }
                    Text(isLoading ? "Generating..." : "Generate Image")
                }
                .font(.headline)
                .foregroundColor(.white)
                .padding()
                .frame(maxWidth: .infinity)
                .background(isLoading ? Color.gray : Color.blue)
                .cornerRadius(15)
            }
            .disabled(isLoading || prompt.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
            .padding(.horizontal)
            
            // Error Message
            if let errorMessage = errorMessage {
                Text(errorMessage)
                    .foregroundColor(.red)
                    .multilineTextAlignment(.center)
                    .padding(.horizontal)
            }
            
            // Generated Image Display
            ScrollView {
                VStack(spacing: 16) {
                    if let image = generatedImage {
                        VStack(spacing: 12) {
                            Text("Generated Image")
                                .font(.headline)
                            
                            Image(uiImage: image)
                                .resizable()
                                .aspectRatio(contentMode: .fit)
                                .frame(maxHeight: 400)
                                .cornerRadius(12)
                                .shadow(radius: 4)
                            
                            if let imageData = generatedImageData {
                                Text("Size: \(Int(Double(imageData.count) / 1024.0))KB")
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                            }
                        }
                        .padding(.horizontal)
                    } else if !prompt.isEmpty && !isLoading {
                        VStack(spacing: 12) {
                            Image(systemName: "photo.badge.plus")
                                .font(.system(size: 60))
                                .foregroundColor(.gray)
                            
                            Text("Enter a prompt and tap 'Generate Image' to see results")
                                .font(.headline)
                                .foregroundColor(.gray)
                                .multilineTextAlignment(.center)
                        }
                        .padding()
                    }
                }
            }
            
            Spacer()
        }
        .navigationTitle("Image Generator")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .navigationBarLeading) {
                Button("Back") {
                    navigation.navigateTo(.mainDashboard)
                }
            }
        }
    }
    
    @MainActor
    private func generateImage() async {
        let trimmedPrompt = prompt.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmedPrompt.isEmpty else {
            errorMessage = "Please enter a prompt"
            return
        }
        
        isLoading = true
        errorMessage = nil
        generatedImage = nil
        generatedImageData = nil
        
        do {
            print("🖼️ Starting image generation for prompt: '\(trimmedPrompt)'")
            
            let imageData = try await apiClient.generateImage(prompt: trimmedPrompt)
            
            if let uiImage = UIImage(data: imageData) {
                generatedImage = uiImage
                generatedImageData = imageData
                print("✅ Image generation successful!")
                print("📊 Image size: \(uiImage.size.width) x \(uiImage.size.height)")
                print("📊 Data size: \(imageData.count) bytes")
            } else {
                errorMessage = "Failed to create image from response data"
                print("❌ Failed to create UIImage from response data")
            }
            
        } catch APIError.unauthorized {
            errorMessage = "Please log in to generate images"
        } catch APIError.serverError(let code) {
            errorMessage = "Server error (\(code)). Please try again."
        } catch APIError.serverErrorMessage(let message) {
            errorMessage = "Error: \(message)"
        } catch {
            errorMessage = "Failed to generate image: \(error.localizedDescription)"
            print("❌ Image generation error: \(error)")
        }
        
        isLoading = false
    }
}

// MARK: - Preview
struct ImageGeneratorView_Previews: PreviewProvider {
    static var previews: some View {
        NavigationView {
            ImageGeneratorView(navigation: NavigationViewModel())
        }
    }
} 
