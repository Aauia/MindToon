import SwiftUI

struct CollectionsView: View {
    @StateObject private var collectionViewModel = CollectionViewModel()
    @StateObject private var worldViewModel = WorldViewModel()
    @State private var showingCreateCollection = false
    @State private var selectedWorld: WorldType = .imaginationWorld
    
    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                // World Selection
                WorldSelectionHeader(selectedWorld: $selectedWorld) { world in
                    selectedWorld = world
                    Task {
                        await loadCollections()
                    }
                }
                
                // Search and Filter Bar
                SearchAndFilterBar(
                    searchText: $collectionViewModel.searchText,
                    showingFilters: $collectionViewModel.showingFilters
                )
                
                // Filter Panel
                if collectionViewModel.showingFilters {
                    FilterPanel(viewModel: collectionViewModel)
                        .transition(.slide)
                }
                
                // Collections Content
                if collectionViewModel.isLoading {
                    LoadingView()
                } else if collectionViewModel.filteredCollections.isEmpty {
                    EmptyCollectionsView(selectedWorld: selectedWorld) {
                        showingCreateCollection = true
                    }
                } else {
                    CollectionsGrid(
                        collections: collectionViewModel.filteredCollections,
                        viewModel: collectionViewModel
                    )
                }
                
                Spacer()
            }
            .navigationTitle("Collections")
            .navigationBarTitleDisplayMode(.large)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: {
                        showingCreateCollection = true
                    }) {
                        Image(systemName: "plus")
                            .font(.title2)
                    }
                }
            }
            .sheet(isPresented: $showingCreateCollection) {
                CreateCollectionView(
                    viewModel: collectionViewModel,
                    selectedWorld: selectedWorld
                )
            }
            .onAppear {
                Task {
                    await loadCollections()
                }
            }
            .refreshable {
                await loadCollections()
            }
        }
    }
    
    private func loadCollections() async {
        collectionViewModel.selectedWorldFilter = selectedWorld
        await collectionViewModel.loadCollections(refresh: true)
    }
}

struct WorldSelectionHeader: View {
    @Binding var selectedWorld: WorldType
    let onWorldSelected: (WorldType) -> Void
    
    var body: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 12) {
                ForEach(WorldType.allCases, id: \.self) { world in
                    WorldChip(
                        world: world,
                        isSelected: selectedWorld == world
                    ) {
                        selectedWorld = world
                        onWorldSelected(world)
                    }
                }
            }
            .padding(.horizontal)
        }
        .padding(.vertical, 8)
        .background(Color(.systemGray6))
    }
}

struct WorldChip: View {
    let world: WorldType
    let isSelected: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            HStack(spacing: 8) {
                Image(systemName: world.icon)
                    .font(.caption)
                Text(world.displayName)
                    .font(.caption)
                    .fontWeight(.medium)
            }
            .padding(.horizontal, 12)
            .padding(.vertical, 6)
            .background(
                isSelected ? world.primaryColor : Color(.systemGray5)
            )
            .foregroundColor(
                isSelected ? .white : .primary
            )
            .cornerRadius(16)
        }
        .scaleEffect(isSelected ? 1.05 : 1.0)
        .animation(.easeInOut(duration: 0.2), value: isSelected)
    }
}

struct SearchAndFilterBar: View {
    @Binding var searchText: String
    @Binding var showingFilters: Bool
    
    var body: some View {
        HStack(spacing: 12) {
            HStack {
                Image(systemName: "magnifyingglass")
                    .foregroundColor(.secondary)
                
                TextField("Search collections...", text: $searchText)
                    .autocapitalization(.none)
                    .disableAutocorrection(true)
                
                if !searchText.isEmpty {
                    Button(action: {
                        searchText = ""
                    }) {
                        Image(systemName: "xmark.circle.fill")
                            .foregroundColor(.secondary)
                    }
                }
            }
            .padding(.horizontal, 12)
            .padding(.vertical, 8)
            .background(Color(.systemGray6))
            .cornerRadius(10)
            
            Button(action: {
                withAnimation(.easeInOut) {
                    showingFilters.toggle()
                }
            }) {
                Image(systemName: showingFilters ? "line.3.horizontal.decrease.circle.fill" : "line.3.horizontal.decrease.circle")
                    .font(.title2)
                    .foregroundColor(.blue)
            }
        }
        .padding(.horizontal)
        .padding(.vertical, 8)
    }
}

struct FilterPanel: View {
    @ObservedObject var viewModel: CollectionViewModel
    
    var body: some View {
        VStack(spacing: 12) {
            HStack {
                Text("Filters")
                    .font(.headline)
                Spacer()
                Button("Clear All") {
                    viewModel.clearFilters()
                }
                .font(.caption)
                .foregroundColor(.blue)
            }
            
            // Sort Options
            VStack(alignment: .leading, spacing: 8) {
                Text("Sort by")
                    .font(.subheadline)
                    .fontWeight(.medium)
                
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 8) {
                        ForEach(CollectionSortOption.allCases, id: \.self) { option in
                            FilterChip(
                                title: option.rawValue.capitalized,
                                isSelected: viewModel.sortOption == option
                            ) {
                                viewModel.sortOption = option
                            }
                        }
                    }
                    .padding(.horizontal, 4)
                }
            }
            
            // Comic Count Filter
            VStack(alignment: .leading, spacing: 8) {
                Text("Minimum Comics")
                    .font(.subheadline)
                    .fontWeight(.medium)
                
                HStack {
                    Text("0")
                    Slider(value: Binding(
                        get: { Double(viewModel.minComicsFilter) },
                        set: { viewModel.minComicsFilter = Int($0) }
                    ), in: 0...20, step: 1)
                    Text("20+")
                }
                .font(.caption)
                
                Text("\(viewModel.minComicsFilter) comics minimum")
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(12)
        .padding(.horizontal)
    }
}

struct FilterChip: View {
    let title: String
    let isSelected: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            Text(title)
                .font(.caption)
                .fontWeight(.medium)
                .padding(.horizontal, 12)
                .padding(.vertical, 6)
                .background(
                    isSelected ? Color.blue : Color(.systemGray5)
                )
                .foregroundColor(
                    isSelected ? .white : .primary
                )
                .cornerRadius(16)
        }
    }
}

struct CollectionsGrid: View {
    let collections: [ComicCollectionResponse]
    @ObservedObject var viewModel: CollectionViewModel
    
    let columns = [
        GridItem(.adaptive(minimum: 160), spacing: 16)
    ]
    
    var body: some View {
        ScrollView {
            LazyVGrid(columns: columns, spacing: 16) {
                ForEach(collections) { collection in
                    CollectionCard(collection: collection, viewModel: viewModel)
                }
            }
            .padding()
        }
    }
}

struct CollectionCard: View {
    let collection: ComicCollectionResponse
    @ObservedObject var viewModel: CollectionViewModel
    @State private var showingDetails = false
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // Collection Preview
            if let firstComicImage = collection.previewImages.first {
                AsyncImage(url: URL(string: firstComicImage)) { image in
                    image
                        .resizable()
                        .aspectRatio(contentMode: .fill)
                } placeholder: {
                    Rectangle()
                        .fill(Color(.systemGray5))
                        .overlay(
                            Image(systemName: "photo")
                                .font(.title2)
                                .foregroundColor(.secondary)
                        )
                }
                .frame(height: 120)
                .clipShape(RoundedRectangle(cornerRadius: 8))
            } else {
                Rectangle()
                    .fill(LinearGradient(
                        gradient: collection.worldType.gradient,
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    ))
                    .frame(height: 120)
                    .overlay(
                        VStack {
                            Image(systemName: collection.worldType.icon)
                                .font(.title2)
                                .foregroundColor(.white)
                            Text("Empty")
                                .font(.caption)
                                .foregroundColor(.white.opacity(0.8))
                        }
                    )
                    .clipShape(RoundedRectangle(cornerRadius: 8))
            }
            
            // Collection Info
            VStack(alignment: .leading, spacing: 4) {
                Text(collection.name)
                    .font(.headline)
                    .fontWeight(.semibold)
                    .lineLimit(2)
                
                if let description = collection.description {
                    Text(description)
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .lineLimit(2)
                }
                
                HStack {
                    HStack(spacing: 4) {
                        Image(systemName: "photo.on.rectangle")
                            .font(.caption2)
                        Text("\(collection.comicsCount)")
                            .font(.caption2)
                    }
                    .foregroundColor(.secondary)
                    
                    Spacer()
                    
                    HStack(spacing: 4) {
                        Image(systemName: collection.worldType.icon)
                            .font(.caption2)
                        Text(collection.worldType.displayName)
                            .font(.caption2)
                    }
                    .foregroundColor(collection.worldType.primaryColor)
                }
            }
        }
        .padding(12)
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(color: .black.opacity(0.1), radius: 2, x: 0, y: 1)
        .onTapGesture {
            showingDetails = true
        }
        .sheet(isPresented: $showingDetails) {
            CollectionDetailView(collection: collection, viewModel: viewModel)
        }
    }
}

struct EmptyCollectionsView: View {
    let selectedWorld: WorldType
    let onCreateCollection: () -> Void
    
    var body: some View {
        VStack(spacing: 24) {
            Image(systemName: selectedWorld.icon)
                .font(.system(size: 60))
                .foregroundColor(selectedWorld.primaryColor)
            
            VStack(spacing: 8) {
                Text("No Collections Yet")
                    .font(.title2)
                    .fontWeight(.bold)
                
                Text("Create your first collection to organize your \(selectedWorld.displayName.lowercased()) comics")
                    .font(.body)
                    .foregroundColor(.secondary)
                    .multilineTextAlignment(.center)
                    .padding(.horizontal)
            }
            
            Button(action: onCreateCollection) {
                HStack {
                    Image(systemName: "plus")
                    Text("Create Collection")
                }
                .font(.headline)
                .foregroundColor(.white)
                .padding()
                .background(selectedWorld.primaryColor)
                .cornerRadius(12)
            }
        }
        .padding()
    }
}

struct LoadingView: View {
    var body: some View {
        VStack {
            ProgressView()
                .scaleEffect(1.2)
            Text("Loading collections...")
                .font(.caption)
                .foregroundColor(.secondary)
                .padding(.top, 8)
        }
        .padding()
    }
}

// MARK: - Supporting Views

struct CreateCollectionView: View {
    @ObservedObject var viewModel: CollectionViewModel
    let selectedWorld: WorldType
    @Environment(\.dismiss) private var dismiss
    
    @State private var name = ""
    @State private var description = ""
    @State private var isPrivate = false
    
    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("Collection Details")) {
                    TextField("Collection Name", text: $name)
                    TextField("Description (Optional)", text: $description, axis: .vertical)
                        .lineLimit(3...6)
                }
                
                Section(header: Text("Settings")) {
                    HStack {
                        Image(systemName: selectedWorld.icon)
                            .foregroundColor(selectedWorld.primaryColor)
                        Text("World: \(selectedWorld.displayName)")
                        Spacer()
                    }
                    
                    Toggle("Private Collection", isOn: $isPrivate)
                }
                
                Section(footer: Text("You can add comics to this collection after creating it.")) {
                    // Empty section for footer text
                }
            }
            .navigationTitle("New Collection")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Cancel") {
                        dismiss()
                    }
                }
                
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Create") {
                        Task {
                            await createCollection()
                        }
                    }
                    .disabled(name.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
                }
            }
        }
    }
    
    private func createCollection() async {
        let request = ComicCollectionRequest(
            name: name.trimmingCharacters(in: .whitespacesAndNewlines),
            description: description.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty ? nil : description.trimmingCharacters(in: .whitespacesAndNewlines),
            worldType: selectedWorld,
            isPublic: !isPrivate,
            tags: []
        )
        
        await viewModel.createCollection()
        dismiss()
    }
}

struct CollectionDetailView: View {
    let collection: ComicCollectionResponse
    @ObservedObject var viewModel: CollectionViewModel
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    // Collection Header
                    VStack(alignment: .leading, spacing: 12) {
                        HStack {
                            Image(systemName: collection.worldType.icon)
                                .font(.title2)
                                .foregroundColor(collection.worldType.primaryColor)
                            
                            Text(collection.name)
                                .font(.title)
                                .fontWeight(.bold)
                            
                            Spacer()
                        }
                        
                        if let description = collection.description {
                            Text(description)
                                .font(.body)
                                .foregroundColor(.secondary)
                        }
                        
                        HStack {
                            Label("\(collection.comicsCount) comics", systemImage: "photo.on.rectangle")
                            Spacer()
                            Label(collection.worldType.displayName, systemImage: collection.worldType.icon)
                                .foregroundColor(collection.worldType.primaryColor)
                        }
                        .font(.caption)
                        .foregroundColor(.secondary)
                    }
                    .padding()
                    .background(Color(.systemGray6))
                    .cornerRadius(12)
                    
                    // Comics Grid
                    if !collection.previewImages.isEmpty {
                        Text("Comics")
                            .font(.headline)
                            .padding(.horizontal)
                        
                        LazyVGrid(columns: [
                            GridItem(.adaptive(minimum: 100), spacing: 12)
                        ], spacing: 12) {
                            ForEach(collection.previewImages.indices, id: \.self) { index in
                                AsyncImage(url: URL(string: collection.previewImages[index])) { image in
                                    image
                                        .resizable()
                                        .aspectRatio(contentMode: .fill)
                                } placeholder: {
                                    Rectangle()
                                        .fill(Color(.systemGray5))
                                        .overlay(
                                            ProgressView()
                                        )
                                }
                                .frame(width: 100, height: 100)
                                .clipShape(RoundedRectangle(cornerRadius: 8))
                            }
                        }
                        .padding(.horizontal)
                    }
                }
            }
            .navigationTitle("Collection")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") {
                        dismiss()
                    }
                }
            }
        }
    }
}

#Preview {
    CollectionsView()
} 
