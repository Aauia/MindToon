import SwiftUI

// MARK: - ComicGeneratorView
struct ComicGeneratorView: View {
    @StateObject var viewModel: ComicGeneratorViewModel
    @ObservedObject var navigation: NavigationViewModel
    @Environment(\.dismiss) private var dismiss // For the back arrow in the top bar
    
    // Add world selection state
    @State private var selectedWorld: WorldType = .imaginationWorld
    @State private var showingWorldPicker = false
    
    // Genre and Art Style options
    private let genres = ["adventure", "comedy", "horror", "romance", "sci-fi", "fantasy", "mystery", "drama", "action", "slice of life"]
    private let artStyles = ["comic book", "manga", "cartoon", "realistic", "watercolor", "sketch", "pixel art", "minimalist", "vintage", "anime"]

    init(viewModel: ComicGeneratorViewModel, navigation: NavigationViewModel) {
        _viewModel = StateObject(wrappedValue: viewModel)
        _navigation = ObservedObject(wrappedValue: navigation)
        viewModel.navigation = navigation
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
                        
                        // World Selection Section
                        VStack(alignment: .leading, spacing: 10) {
                            Text("Save to World")
                                .font(.headline)
                                .foregroundColor(.secondary)
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
                                            .foregroundColor(.primary)
                                        Text(selectedWorld.description)
                                            .font(.caption)
                                            .foregroundColor(.secondary)
                                    }
                                    
                                    Spacer()
                                    
                                    Image(systemName: "chevron.down")
                                        .foregroundColor(.secondary)
                                }
                                .padding()
                                .background(Color.white.opacity(0.8))
                                .cornerRadius(10)
                                .shadow(color: Color.black.opacity(0.05), radius: 5, x: 0, y: 5)
                            }
                            .padding(.horizontal)
                        }

                        // Genre Selection Section
                        VStack(alignment: .leading, spacing: 10) {
                            Text("Genre")
                                .font(.headline)
                                .foregroundColor(.secondary)
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
                                        .foregroundColor(.primary)
                                    Spacer()
                                    Image(systemName: "chevron.down")
                                        .foregroundColor(.secondary)
                                }
                                .padding()
                                .background(Color.white.opacity(0.8))
                                .cornerRadius(10)
                                .shadow(color: Color.black.opacity(0.05), radius: 5, x: 0, y: 5)
                            }
                            .padding(.horizontal)
                        }

                        // Art Style Selection Section
                        VStack(alignment: .leading, spacing: 10) {
                            Text("Art Style")
                                .font(.headline)
                                .foregroundColor(.secondary)
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
                                        .foregroundColor(.primary)
                                    Spacer()
                                    Image(systemName: "chevron.down")
                                        .foregroundColor(.secondary)
                                }
                                .padding()
                                .background(Color.white.opacity(0.8))
                                .cornerRadius(10)
                                .shadow(color: Color.black.opacity(0.05), radius: 5, x: 0, y: 5)
                            }
                            .padding(.horizontal)
                        }

                        // Detailed Scenario Toggle Section
                        VStack(alignment: .leading, spacing: 10) {
                            Text("Advanced Options")
                                .font(.headline)
                                .foregroundColor(.secondary)
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
                                            .foregroundColor(.primary)
                                        Text("Generate a rich, detailed story with character development and plot structure")
                                            .font(.caption)
                                            .foregroundColor(.secondary)
                                            .multilineTextAlignment(.leading)
                                    }
                                    
                                    Spacer()
                                    
                                    Toggle("", isOn: $viewModel.includeDetailedScenario)
                                        .toggleStyle(SwitchToggleStyle(tint: .purple))
                                }
                                .padding()
                                .background(Color.white.opacity(0.8))
                                .cornerRadius(10)
                                .shadow(color: Color.black.opacity(0.05), radius: 5, x: 0, y: 5)
                            }
                            .padding(.horizontal)
                        }

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
                            ActionButton(title: "Enhance Scenario", iconName: "text.bubble.fill") {
                                Task {
                                    await viewModel.generateScenario()
                                }
                            }
                            ActionButton(title: "Add Tone/Mood Suggestions", iconName: "sparkles", action: viewModel.addToneMoodSuggestions)
                            ActionButton(title: "Generate Comic", iconName: "arrow.forward.circle.fill", isPrimary: true) {
                                Task { // Use Task to call async function
                                    await viewModel.generateComicWithWorld(worldType: selectedWorld)
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
                    .frame(maxWidth: .infinity, minHeight: 600) // Fixed minimum height instead of UIScreen calculation
                }

                // Persistent Bottom Bar View
                BottombarView(navigation: navigation)
                    .frame(maxHeight: 80) // Fixed height for bottom bar
            }
            .background(Color(red: 1.0, green: 1.0, blue: 0.9)) // Light background
            .sheet(isPresented: $showingWorldPicker) {
                WorldPickerView(selectedWorld: $selectedWorld)
            }
            .navigationBarTitleDisplayMode(.inline)
        }
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
