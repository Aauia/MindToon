import SwiftUI

// MARK: - ComicGeneratorView
struct ComicGeneratorView: View {
    @StateObject var viewModel: ComicGeneratorViewModel
    @ObservedObject var navigation: NavigationViewModel
    @Environment(\.dismiss) private var dismiss // For the back arrow in the top bar
    @FocusState private var isTextEditorFocused: Bool // For keyboard dismissal
    @FocusState private var isTitleFieldFocused: Bool // For title field keyboard dismissal
    
    // Add world selection state
    @State private var selectedWorld: WorldType = .imaginationWorld
    @State private var showingWorldPicker = false
    @State private var showLeavingInfo = true 
    
    // Genre and Art Style options
    private let genres = ["adventure", "comedy", "horror", "romance", "sci-fi", "fantasy", "mystery", "drama", "action", "slice of life"]
    private let artStyles = ["comic book", "manga", "cartoon", "realistic", "watercolor", "sketch", "pixel art", "minimalist", "vintage", "anime"]

    init(viewModel: ComicGeneratorViewModel, navigation: NavigationViewModel) {
        _viewModel = StateObject(wrappedValue: viewModel)
        _navigation = ObservedObject(wrappedValue: navigation)
        viewModel.navigation = navigation
    }

    var body: some View {
    ZStack {
        LinearGradient(
            gradient: Gradient(colors: [
                Color(red: 0.85, green: 0.73, blue: 0.94), // lavender
                Color(red: 0.99, green: 0.85, blue: 0.92)  // blush
            ]),
            startPoint: .topLeading,
            endPoint: .bottomTrailing
        )
        .edgesIgnoringSafeArea(.all)

        NavigationView {
            VStack(spacing: 0) {
                ScrollView {
                    VStack(alignment: .leading, spacing: 20) {
                        Text("Comic Title")
                            .font(.headline)
                            .foregroundColor(.black)
                            .padding(.horizontal)

                        TextField("Enter comic title", text: $viewModel.comicTitle)
                            .padding()
                            .foregroundColor(.black)
                            .background(Color.white)
                            .cornerRadius(10)
                            .shadow(color: Color.black.opacity(0.05), radius: 5, x: 0, y: 5)
                            .focused($isTitleFieldFocused)
                            .padding(.horizontal)

                        // World Section
                        VStack(alignment: .leading, spacing: 10) {
                            Text("Save to World")
                                .font(.headline)
                                .foregroundColor(.black)
                                .padding(.horizontal)

                            Button(action: {
                                showingWorldPicker = true
                            }) {
                                HStack {
                                    Circle()
                                        .fill(worldColor(for: selectedWorld))
                                        .frame(width: 30, height: 30)
                                        .overlay(
                                            Image(systemName: worldIcon(for: selectedWorld))
                                                .font(.system(size: 14))
                                                .foregroundColor(.white)
                                        )

                                    VStack(alignment: .leading) {
                                        Text(selectedWorld.displayName)
                                            .font(.body)
                                            .fontWeight(.medium)
                                            .foregroundColor(.black)
                                        Text(selectedWorld.description)
                                            .font(.caption)
                                            .foregroundColor(.gray)
                                    }

                                    Spacer()
                                    Image(systemName: "chevron.down")
                                        .foregroundColor(.gray)
                                }
                                .padding()
                                .background(Color.white)
                                .cornerRadius(10)
                                .shadow(color: Color.black.opacity(0.05), radius: 5, x: 0, y: 5)
                            }
                            .padding(.horizontal)
                        }

                        // Genre Section
                        VStack(alignment: .leading, spacing: 10) {
                            Text("Genre")
                                .font(.headline)
                                .foregroundColor(.black)
                                .padding(.horizontal)

                            Menu {
                                ForEach(genres, id: \.self) { genre in
                                    Button(genre.capitalized) {
                                        viewModel.selectedGenre = genre
                                    }
                                }
                            } label: {
                                HStack {
                                    Text(viewModel.selectedGenre.capitalized)
                                        .font(.body)
                                        .foregroundColor(.black)
                                    Spacer()
                                    Image(systemName: "chevron.down")
                                        .foregroundColor(.gray)
                                }
                                .padding()
                                .background(Color.white)
                                .cornerRadius(10)
                                .shadow(color: Color.black.opacity(0.05), radius: 5, x: 0, y: 5)
                            }
                            .padding(.horizontal)
                        }

                        // Art Style Section
                        VStack(alignment: .leading, spacing: 10) {
                            Text("Art Style")
                                .font(.headline)
                                .foregroundColor(.black)
                                .padding(.horizontal)

                            Menu {
                                ForEach(artStyles, id: \.self) { style in
                                    Button(style.capitalized) {
                                        viewModel.selectedArtStyle = style
                                    }
                                }
                            } label: {
                                HStack {
                                    Text(viewModel.selectedArtStyle.capitalized)
                                        .font(.body)
                                        .foregroundColor(.black)
                                    Spacer()
                                    Image(systemName: "chevron.down")
                                        .foregroundColor(.gray)
                                }
                                .padding()
                                .background(Color.white)
                                .cornerRadius(10)
                                .shadow(color: Color.black.opacity(0.05), radius: 5, x: 0, y: 5)
                            }
                            .padding(.horizontal)
                        }

                        // Advanced Options
                        VStack(alignment: .leading, spacing: 10) {
                            Text("Advanced Options")
                                .font(.headline)
                                .foregroundColor(.black)
                                .padding(.horizontal)

                            VStack(alignment: .leading, spacing: 8) {
                                HStack {
                                    Image(systemName: "text.book.closed.fill")
                                        .foregroundColor(.purple)
                                        .font(.title3)

                                    VStack(alignment: .leading, spacing: 2) {
                                        Text("Include Detailed Scenario")
                                            .font(.body)
                                            .fontWeight(.medium)
                                            .foregroundColor(.black)
                                        Text("Generate a rich, detailed story with character development and plot structure")
                                            .font(.caption)
                                            .foregroundColor(.gray)
                                            .multilineTextAlignment(.leading)
                                    }

                                    Spacer()
                                    Toggle("", isOn: $viewModel.includeDetailedScenario)
                                        .toggleStyle(SwitchToggleStyle(tint: .purple))
                                }
                                .padding()
                                .background(Color.white)
                                .cornerRadius(10)
                                .shadow(color: Color.black.opacity(0.05), radius: 5, x: 0, y: 5)
                            }
                            .padding(.horizontal)
                        }

                        // Script TextEditor
                        ZStack(alignment: .topLeading) {
                            TextEditor(text: $viewModel.scriptText)
                                .frame(minHeight: 200)
                                .padding(10)
                                .foregroundColor(.black)
                                .background(Color.white)
                                .cornerRadius(10)
                                .shadow(color: Color.black.opacity(0.05), radius: 5, x: 0, y: 5)
                                .focused($isTextEditorFocused)
                            if viewModel.scriptText.isEmpty {
                                Text("Enter your script or story idea...")
                                    .foregroundColor(.gray.opacity(0.6))
                                    .padding(.horizontal, 20)
                                    .padding(.vertical, 16)
                                    .onTapGesture {
                                        isTextEditorFocused = true
                                    }
                            }
                        }
                        .padding(.horizontal)

                        // Generate Button
                        VStack(spacing: 25) {
                            ActionButton(
                                title: "Generate Comic",
                                iconName: "arrow.forward.circle.fill",
                                isPrimary: true,
                                isLoading: viewModel.isLoading,
                                isDisabled: viewModel.comicTitle.isEmpty
                            ) {
                                // Dismiss keyboard before generating
                                isTextEditorFocused = false
                                isTitleFieldFocused = false
                                
                                Task {
                                    await viewModel.generateComicWithWorld(worldType: selectedWorld)
                                }
                            }
                        }
                        .padding(.top, 30)
                        .padding(.horizontal)

                        if viewModel.isLoading {
                            VStack(spacing: 16) {
                                Text("Generation may take some time, please wait...")
                                    .foregroundColor(.black)
                                    .padding()

                                if showLeavingInfo {
                                    HStack(alignment: .top, spacing: 12) {
                                        Image(systemName: "info.circle")
                                            .foregroundColor(.blue)
                                        VStack(alignment: .leading, spacing: 4) {
                                            Text("If you close the app or leave the screen.")
                                                .font(.headline)
                                                .foregroundColor(.black)
                                            Text("Just wait a while, your comics will be generated and saved")
                                                .font(.subheadline)
                                                .foregroundColor(.gray)
                                        }
                                        Spacer()
                                        Button(action: {
                                            withAnimation {
                                                showLeavingInfo = false
                                            }
                                        }) {
                                            Image(systemName: "xmark.circle.fill")
                                                .foregroundColor(.gray)
                                        }
                                    }
                                    .padding()
                                    .background(Color(.systemGray6))
                                    .cornerRadius(12)
                                    .padding(.horizontal)
                                }
                            }
                        }

                        if viewModel.isLongLoading {
                            VStack(spacing: 16) {
                                ProgressView()
                                Text(viewModel.errorMessage ?? "")
                                    .font(.headline)
                                    .foregroundColor(.black)
                                    .multilineTextAlignment(.center)
                            }
                            .padding()
                        } else if let errorMessage = viewModel.errorMessage {
                            Text(errorMessage)
                                .foregroundColor(.green)
                                .padding()
                        }
                    }
                    .padding(.vertical)
                    .frame(maxWidth: .infinity, minHeight: 600)
                    // Disable all form fields when loading
                    .disabled(viewModel.isLoading)
                }
                .onTapGesture {
                    // Dismiss keyboard when tapping outside text fields
                    isTextEditorFocused = false
                    isTitleFieldFocused = false
                }
                .onChange(of: viewModel.isLoading) { isLoading in
                    // Automatically dismiss keyboard when generation starts
                    if isLoading {
                        isTextEditorFocused = false
                        isTitleFieldFocused = false
                    }
                }

                BottombarView(navigation: navigation)
                    .ignoresSafeArea(.keyboard, edges: .bottom)
                    .disabled(viewModel.isLoading)
            }
            .background(Color(red: 0.87, green: 0.80, blue: 1.0)) // muted purple
            .sheet(isPresented: $showingWorldPicker) {
                WorldPickerView(selectedWorld: $selectedWorld)
            }
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button(action: {
                        navigation.currentScreen = .mainDashboard
                    }) {
                        Image(systemName: "chevron.left")
                            .font(.title2)
                            .foregroundColor(.black)
                    }
                }
            }
            // Disable navigation bar button when loading
            .disabled(viewModel.isLoading)
        }
        // Overlay a blocking view when loading
        if viewModel.isLoading {
            Color.black.opacity(0.25)
                .ignoresSafeArea()
            VStack(spacing: 16) {
                ProgressView()
                    .scaleEffect(1.5)
                Text("Generating your comic...\nThis may take some time, please wait.")
                    .multilineTextAlignment(.center)
                    .foregroundColor(.white)
                    .font(.headline)
            }
            .padding(32)
            .background(Color.black.opacity(0.7))
            .cornerRadius(20)
            .shadow(radius: 10)
        }
    }
    .colorScheme(.light) // 👈 Force light mode for all content
}

    
    // Helper functions for world UI
    private func worldColor(for world: WorldType) -> Color {
        switch world {
        case .dreamWorld:
            return Color.pink.opacity(0.7)
        case .mindWorld:
            return Color.green.opacity(0.7)
        case .imaginationWorld:
            return Color.orange.opacity(0.7)
        }
    }
    
    private func worldIcon(for world: WorldType) -> String {
        switch world {
        case .dreamWorld:
            return "moon.stars.fill"
        case .mindWorld:
            return "brain.head.profile"
        case .imaginationWorld:
            return "sparkles"
        }
    }
}

// MARK: - World Picker View
struct WorldPickerView: View {
    @Binding var selectedWorld: WorldType
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                Text("Choose Your World")
                    .font(.title2)
                    .fontWeight(.bold)
                    .padding(.top)
                
                Spacer()
                
                ForEach(WorldType.allCases, id: \.self) { world in
                    WorldSelectionRow(
                        world: world,
                        isSelected: selectedWorld == world
                    ) {
                        selectedWorld = world
                        dismiss()
                    }
                }
                
                Spacer()
            }
            .padding()
            .navigationTitle("Select World")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Cancel") {
                        dismiss()
                    }
                }
            }
        }
    }
}

// MARK: - World Selection Row
struct WorldSelectionRow: View {
    let world: WorldType
    let isSelected: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            HStack {
                Circle()
                    .fill(worldColor(for: world))
                    .frame(width: 50, height: 50)
                    .overlay(
                        Image(systemName: worldIcon(for: world))
                            .font(.title3)
                            .foregroundColor(.white)
                    )
                    .shadow(color: worldColor(for: world).opacity(0.5), radius: 10, x: 0, y: 5)
                
                VStack(alignment: .leading, spacing: 4) {
                    Text(world.displayName)
                        .font(.headline)
                        .foregroundColor(.primary)
                    Text(world.description)
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                        .multilineTextAlignment(.leading)
                }
                
                Spacer()
                
                if isSelected {
                    Image(systemName: "checkmark.circle.fill")
                        .font(.title2)
                        .foregroundColor(.blue)
                }
            }
            .padding()
            .background(Color.white.opacity(0.8))
            .cornerRadius(15)
            .overlay(
                RoundedRectangle(cornerRadius: 15)
                    .stroke(isSelected ? Color.blue : Color.clear, lineWidth: 2)
            )
        }
    }
    
    private func worldColor(for world: WorldType) -> Color {
        switch world {
        case .dreamWorld:
            return Color.pink.opacity(0.7)
        case .mindWorld:
            return Color.green.opacity(0.7)
        case .imaginationWorld:
            return Color.orange.opacity(0.7)
        }
    }
    
    private func worldIcon(for world: WorldType) -> String {
        switch world {
        case .dreamWorld:
            return "moon.stars.fill"
        case .mindWorld:
            return "brain.head.profile"
        case .imaginationWorld:
            return "sparkles"
        }
    }
}

// MARK: - ActionButton (Reusable Helper View)
struct ActionButton: View {
    let title: String
    let iconName: String
    var isPrimary: Bool = false
    var isLoading: Bool = false
    var isDisabled: Bool = false
    let action: () -> Void

    var body: some View {
        Button(action: {
            if !isLoading && !isDisabled {
                action()
            }
        }) {
            HStack {
                Spacer()
                if isLoading {
                    ProgressView()
                        .progressViewStyle(CircularProgressViewStyle(tint: isPrimary ? .white : .purple))
                } else {
                    Image(systemName: iconName)
                        .font(isPrimary ? .title : .title2)
                        .foregroundColor(isPrimary ? .white : .purple)
                    Text(title)
                        .font(isPrimary ? .headline : .body)
                        .fontWeight(isPrimary ? .bold : .medium)
                        .foregroundColor(isPrimary ? .white : .primary)
                }
                Spacer()
            }
            .padding(.vertical, 15)
            .background(isPrimary ? Color.purple : Color.white)
            .cornerRadius(10)
            .shadow(color: Color.black.opacity(0.1), radius: 5, x: 0, y: 5)
            .opacity(isDisabled ? 0.5 : 1.0)
        }
        .disabled(isLoading || isDisabled)
    }
}

// MARK: - Preview
#Preview {
    ComicGeneratorView(viewModel: ComicGeneratorViewModel(), navigation: NavigationViewModel())
}

extension WorldType {
    var gradient: Gradient {
        switch self {
        case .dreamWorld: return Gradient(colors: [.purple.opacity(0.3), .blue.opacity(0.3)])
        case .mindWorld: return Gradient(colors: [.indigo.opacity(0.3), .cyan.opacity(0.3)])
        case .imaginationWorld: return Gradient(colors: [.pink.opacity(0.3), .orange.opacity(0.3)])
        }
    }

    var linearGradient: LinearGradient {
        LinearGradient(
            gradient: self.gradient,
            startPoint: .topLeading,
            endPoint: .bottomTrailing
        )
    }
}
 
