import SwiftUI

// MARK: - ComicGeneratorView
struct ComicGeneratorView: View {
    @StateObject var viewModel: ComicGeneratorViewModel
    @ObservedObject var navigation: NavigationViewModel
    @Environment(\.dismiss) private var dismiss // For the back arrow in the top bar

    init(viewModel: ComicGeneratorViewModel, navigation: NavigationViewModel) {
        _viewModel = StateObject(wrappedValue: viewModel)
        _navigation = ObservedObject(wrappedValue: navigation)
    }

    var body: some View {
        NavigationView { // Needed for the top bar and navigation stack behavior
            VStack(spacing: 0) { // Stack content and bottom bar
                ScrollView { // Make the content area scrollable
                    VStack(alignment: .leading, spacing: 20) {
                        Text("Comic Title")
                            .font(.headline)
                            .foregroundColor(.secondary)
                            .padding(.horizontal)

                        // Comic Title Input Field
                        TextField("Enter comic title", text: $viewModel.comicTitle)
                            .padding()
                            .background(Color.white.opacity(0.8))
                            .cornerRadius(10)
                            .shadow(color: Color.black.opacity(0.05), radius: 5, x: 0, y: 5)
                            .padding(.horizontal)

                        // Large Script Text Input Area
                        TextEditor(text: $viewModel.scriptText)
                            .frame(minHeight: 200, maxHeight: .infinity) // Flexible height with a minimum
                            .padding(.horizontal, 10)
                            .padding(.vertical, 8)
                            .background(Color.white.opacity(0.8))
                            .cornerRadius(10)
                            .shadow(color: Color.black.opacity(0.05), radius: 5, x: 0, y: 5)
                            .padding(.horizontal)
                            .overlay(
                                Group {
                                    if viewModel.scriptText.isEmpty {
                                        Text("Enter your script or story idea...")
                                            .foregroundColor(Color.gray.opacity(0.6))
                                            .padding(.horizontal, 20)
                                            .padding(.vertical, 16)
                                            .allowsHitTesting(false) // Allows tapping through to the TextEditor
                                    }
                                }
                                , alignment: .topLeading
                            )

                        // Action Buttons as per screenshot
                        VStack(spacing: 25) {
                            ActionButton(title: "Edit Script", iconName: "pencil.circle.fill", action: viewModel.editScript)
                            ActionButton(title: "Add Tone/Mood Suggestions", iconName: "sparkles", action: viewModel.addToneMoodSuggestions)
                            ActionButton(title: "Generate Comic", iconName: "arrow.forward.circle.fill", isPrimary: true) {
                                Task { // Use Task to call async function
                                    await viewModel.generateComic()
                                }
                            }
                        }
                        .padding(.top, 30)
                        .padding(.horizontal)

                        // Loading Indicator during AI generation
                        if viewModel.isLoading {
                            ProgressView("Generating...")
                                .padding()
                                .frame(maxWidth: .infinity)
                        }

                        // Error Message display
                        if let errorMessage = viewModel.errorMessage {
                            Text(errorMessage)
                                .foregroundColor(.red)
                                .padding()
                                .frame(maxWidth: .infinity)
                        }
                    }
                    .padding(.vertical) // Vertical padding for content within ScrollView
                    .frame(maxWidth: .infinity, minHeight: UIScreen.main.bounds.height - 150) // Ensure content pushes bottom bar down
                }

                // Persistent Bottom Bar View
                BottombarView(navigation: navigation)
                    .frame(maxHeight: 80) // Fixed height for bottom bar
            }
            .background(Color(red: 1.0, green: 2.0, blue: 0.9)) // Light background
            
            .navigationBarTitleDisplayMode(.inline)
            // Respond to comic generation completion (e.g., navigate to comic viewer)
            .onReceive(viewModel.didGenerateComicPublisher) { _ in
                // This is where you would navigate to display the generated comic
                // For example: appCoordinator.showGeneratedComicView(comicData)
                print("Comic generated! Navigation to a viewer screen would happen here.")
            }
        }
    }
}

// MARK: - ActionButton (Reusable Helper View)
struct ActionButton: View {
    let title: String
    let iconName: String
    var isPrimary: Bool = false
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            HStack {
                Spacer()
                Image(systemName: iconName)
                    .font(isPrimary ? .title : .title2)
                    .foregroundColor(isPrimary ? .white : .purple)
                Text(title)
                    .font(isPrimary ? .headline : .body)
                    .fontWeight(isPrimary ? .bold : .medium)
                    .foregroundColor(isPrimary ? .white : .primary)
                Spacer()
            }
            .padding(.vertical, 15)
            .background(isPrimary ? Color.purple : Color.white)
            .cornerRadius(10)
            .shadow(color: Color.black.opacity(0.1), radius: 5, x: 0, y: 5)
        }
    }
}

// MARK: - Preview
#Preview {
    ComicGeneratorView(viewModel: ComicGeneratorViewModel(), navigation: NavigationViewModel())
}
