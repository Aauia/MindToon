import SwiftUI

struct DetailedScenarioView: View {
    let scenario: DetailedScenario
    @StateObject private var scenarioViewModel = ScenarioViewModel()
    @Environment(\.dismiss) private var dismiss
    @State private var showingEditView = false
    @State private var selectedTab: ScenarioTab = .overview
    
    enum ScenarioTab: String, CaseIterable {
        case overview = "Overview"
        case characters = "Characters"
        case plot = "Plot"
        case themes = "Themes"
        case analysis = "Analysis"
        
        var icon: String {
            switch self {
            case .overview: return "doc.text"
            case .characters: return "person.2"
            case .plot: return "list.bullet"
            case .themes: return "lightbulb"
            case .analysis: return "chart.bar"
            }
        }
    }
    
    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                // Header
                ScenarioHeader(scenario: scenario)
                
                // Tab Navigation
                TabNavigationView(selectedTab: $selectedTab)
                
                // Content based on selected tab
                ScrollView {
                    switch selectedTab {
                    case .overview:
                        OverviewContent(scenario: scenario)
                    case .characters:
                        CharactersContent(scenario: scenario)
                    case .plot:
                        PlotContent(scenario: scenario)
                    case .themes:
                        ThemesContent(scenario: scenario)
                    case .analysis:
                        AnalysisContent(scenario: scenario)
                    }
                }
                .background(Color(.systemGroupedBackground))
            }
            .navigationTitle("Scenario")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Close") {
                        dismiss()
                    }
                }
                
                ToolbarItem(placement: .navigationBarTrailing) {
                    Menu {
                        Button(action: {
                            showingEditView = true
                        }) {
                            Label("Edit Scenario", systemImage: "pencil")
                        }
                        
                        Button(action: {
                            shareScenario()
                        }) {
                            Label("Share", systemImage: "square.and.arrow.up")
                        }
                        
                        Button(action: {
                            exportScenario()
                        }) {
                            Label("Export", systemImage: "doc.badge.arrow.up")
                        }
                    } label: {
                        Image(systemName: "ellipsis.circle")
                    }
                }
            }
        }
        .sheet(isPresented: $showingEditView) {
            EditScenarioView(scenario: scenario, viewModel: scenarioViewModel)
        }
    }
    
    private func shareScenario() {
        print("Sharing scenario: \(scenario.plotSummary)")
    }
    
    private func exportScenario() {
        print("Exporting scenario: \(scenario.plotSummary)")
    }
}

struct ScenarioHeader: View {
    let scenario: DetailedScenario
    
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text("Scenario #\(scenario.id)")
                        .font(.title)
                        .fontWeight(.bold)
                        .foregroundColor(.primary)
                    
                    Text("World: \(scenario.worldType.displayName)")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                }
                
                Spacer()
                
                VStack(alignment: .trailing, spacing: 4) {
                    ComplexityBadge(complexity: scenario.complexity)
                    
                    Text("Audience: \(scenario.targetAudience.displayName)")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            
            if !scenario.plotSummary.isEmpty {
                Text(scenario.plotSummary)
                    .font(.body)
                    .foregroundColor(.secondary)
                    .lineLimit(3)
            }
            
            // Metadata
            HStack(spacing: 16) {
                HStack(spacing: 4) {
                    Image(systemName: "person.2")
                        .font(.caption)
                    Text("\(scenario.characterRoles.count) characters")
                        .font(.caption)
                }
                .foregroundColor(.secondary)
                
                HStack(spacing: 4) {
                    Image(systemName: "list.bullet")
                        .font(.caption)
                    Text("\(scenario.plotPoints.count) plot points")
                        .font(.caption)
                }
                .foregroundColor(.secondary)
                
                HStack(spacing: 4) {
                    Image(systemName: "lightbulb")
                        .font(.caption)
                    Text("\(scenario.themes.count) themes")
                        .font(.caption)
                }
                .foregroundColor(.secondary)
                
                Spacer()
                
                Text(formatDate(scenario.createdAt))
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(color: .black.opacity(0.05), radius: 2, x: 0, y: 1)
        .padding(.horizontal)
        .padding(.top)
    }
    
    private func formatDate(_ dateString: String) -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd'T'HH:mm:ss.SSSSSS"
        
        if let date = formatter.date(from: dateString) {
            formatter.dateStyle = .short
            return formatter.string(from: date)
        }
        
        return dateString
    }
}

struct ComplexityBadge: View {
    let complexity: ScenarioComplexity
    
    var body: some View {
        HStack(spacing: 4) {
            ForEach(0..<5, id: \.self) { index in
                Circle()
                    .fill(index < complexityLevel ? complexity.color : Color(.systemGray5))
                    .frame(width: 6, height: 6)
            }
            
            Text(complexity.displayName)
                .font(.caption2)
                .fontWeight(.medium)
        }
        .padding(.horizontal, 8)
        .padding(.vertical, 4)
        .background(complexity.color.opacity(0.1))
        .cornerRadius(8)
    }
    
    private var complexityLevel: Int {
        switch complexity {
        case .simple: return 1
        case .moderate: return 2
        case .complex: return 3
        case .advanced: return 4
        case .masterful: return 5
        }
    }
}

struct TabNavigationView: View {
    @Binding var selectedTab: DetailedScenarioView.ScenarioTab
    
    var body: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 20) {
                ForEach(DetailedScenarioView.ScenarioTab.allCases, id: \.self) { tab in
                    TabButton(
                        tab: tab,
                        isSelected: selectedTab == tab
                    ) {
                        withAnimation(.easeInOut(duration: 0.2)) {
                            selectedTab = tab
                        }
                    }
                }
            }
            .padding(.horizontal)
        }
        .padding(.vertical, 12)
        .background(Color(.systemBackground))
    }
}

struct TabButton: View {
    let tab: DetailedScenarioView.ScenarioTab
    let isSelected: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            VStack(spacing: 4) {
                Image(systemName: tab.icon)
                    .font(.title3)
                
                Text(tab.rawValue)
                    .font(.caption)
                    .fontWeight(.medium)
            }
            .foregroundColor(isSelected ? .blue : .secondary)
            .scaleEffect(isSelected ? 1.1 : 1.0)
        }
        .animation(.easeInOut(duration: 0.2), value: isSelected)
    }
}

// MARK: - Content Views

struct OverviewContent: View {
    let scenario: DetailedScenario
    
    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            // Summary Card
            VStack(alignment: .leading, spacing: 12) {
                Text("Summary")
                    .font(.headline)
                    .fontWeight(.bold)
                
                Text(scenario.detailedScenario ?? "No detailed scenario available")
                    .font(.body)
                    .foregroundColor(.secondary)
            }
            .padding()
            .background(Color(.systemBackground))
            .cornerRadius(12)
            
            // Quick Stats
            LazyVGrid(columns: [
                GridItem(.flexible()),
                GridItem(.flexible())
            ], spacing: 12) {
                StatCard(
                    title: "Characters",
                    value: "\(scenario.characterRoles.count)",
                    icon: "person.2"
                )
                
                StatCard(
                    title: "Plot Points",
                    value: "\(scenario.plotPoints.count)",
                    icon: "list.bullet"
                )
                
                StatCard(
                    title: "Themes",
                    value: "\(scenario.themes.count)",
                    icon: "lightbulb"
                )
                
                StatCard(
                    title: "Complexity",
                    value: scenario.complexity.displayName,
                    icon: "chart.bar"
                )
            }
            
            // Key Highlights
            if !scenario.themes.isEmpty {
                VStack(alignment: .leading, spacing: 12) {
                    Text("Key Themes")
                        .font(.headline)
                        .fontWeight(.bold)
                    
                    LazyVGrid(columns: [
                        GridItem(.adaptive(minimum: 120))
                    ], spacing: 8) {
                        ForEach(scenario.themes.prefix(6), id: \.self) { theme in
                            ThemeChip(theme: theme)
                        }
                    }
                }
                .padding()
                .background(Color(.systemBackground))
                .cornerRadius(12)
            }
        }
        .padding()
    }
}

// StatCard is already defined in ImaginationWorldView.swift

struct CharactersContent: View {
    let scenario: DetailedScenario
    
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            ForEach(scenario.characterRoles, id: \.id) { character in
                CharacterCard(character: character)
            }
        }
        .padding()
    }
}

struct CharacterCard: View {
    let character: CharacterRole
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text(character.name)
                        .font(.headline)
                        .fontWeight(.semibold)
                    
                    Text(character.role.displayName)
                        .font(.subheadline)
                        .foregroundColor(character.role.color)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 2)
                        .background(character.role.color.opacity(0.1))
                        .cornerRadius(6)
                }
                
                Spacer()
                
                Image(systemName: "person.circle")
                    .font(.title2)
                    .foregroundColor(character.role.color)
            }
            
            Text(character.description)
                .font(.body)
                .foregroundColor(.secondary)
                .fixedSize(horizontal: false, vertical: true)
            
            if !character.personality.isEmpty {
                LazyVGrid(columns: [
                    GridItem(.adaptive(minimum: 80))
                ], spacing: 6) {
                    ForEach(character.personality, id: \.self) { trait in
                        Text(trait)
                            .font(.caption)
                            .padding(.horizontal, 8)
                            .padding(.vertical, 4)
                            .background(Color(.systemGray6))
                            .cornerRadius(8)
                    }
                }
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
    }
}

struct PlotContent: View {
    let scenario: DetailedScenario
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            ForEach(scenario.plotPoints.indices, id: \.self) { index in
                PlotPointCard(
                    plotPoint: scenario.plotPoints[index],
                    index: index + 1
                )
            }
        }
        .padding()
    }
}

struct PlotPointCard: View {
    let plotPoint: PlotPoint
    let index: Int
    
    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            // Step Number
            ZStack {
                Circle()
                    .fill(Color.blue)
                    .frame(width: 24, height: 24)
                
                Text("\(index)")
                    .font(.caption)
                    .fontWeight(.bold)
                    .foregroundColor(.white)
            }
            
            VStack(alignment: .leading, spacing: 8) {
                Text(plotPoint.title)
                    .font(.headline)
                    .fontWeight(.semibold)
                
                Text(plotPoint.description)
                    .font(.body)
                    .foregroundColor(.secondary)
                    .fixedSize(horizontal: false, vertical: true)
                
                if !plotPoint.characters.isEmpty {
                    HStack {
                        Text("Characters:")
                            .font(.caption)
                            .fontWeight(.medium)
                        
                        Text(plotPoint.characters.joined(separator: ", "))
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
            }
            
            Spacer()
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
    }
}

struct ThemesContent: View {
    let scenario: DetailedScenario
    
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            LazyVGrid(columns: [
                GridItem(.adaptive(minimum: 150))
            ], spacing: 12) {
                ForEach(scenario.themes, id: \.self) { theme in
                    ThemeCard(theme: theme)
                }
            }
        }
        .padding()
    }
}

struct ThemeCard: View {
    let theme: String
    
    var body: some View {
        VStack(spacing: 8) {
            Image(systemName: "lightbulb.fill")
                .font(.title2)
                .foregroundColor(.orange)
            
            Text(theme)
                .font(.subheadline)
                .fontWeight(.medium)
                .multilineTextAlignment(.center)
                .fixedSize(horizontal: false, vertical: true)
        }
        .frame(maxWidth: .infinity)
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
    }
}

struct ThemeChip: View {
    let theme: String
    
    var body: some View {
        Text(theme)
            .font(.caption)
            .padding(.horizontal, 8)
            .padding(.vertical, 4)
            .background(Color.orange.opacity(0.1))
            .foregroundColor(.orange)
            .cornerRadius(8)
    }
}

struct AnalysisContent: View {
    let scenario: DetailedScenario
    
    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            // Complexity Analysis
            VStack(alignment: .leading, spacing: 12) {
                Text("Complexity Analysis")
                    .font(.headline)
                    .fontWeight(.bold)
                
                HStack {
                    ComplexityBadge(complexity: scenario.complexity)
                    Spacer()
                }
                
                Text(complexityDescription)
                    .font(.body)
                    .foregroundColor(.secondary)
            }
            .padding()
            .background(Color(.systemBackground))
            .cornerRadius(12)
            
            // Character Analysis
            if !scenario.characterRoles.isEmpty {
                VStack(alignment: .leading, spacing: 12) {
                    Text("Character Distribution")
                        .font(.headline)
                        .fontWeight(.bold)
                    
                    let roleDistribution = Dictionary(grouping: scenario.characterRoles, by: \.role)
                    
                    ForEach(Array(roleDistribution.keys), id: \.self) { role in
                        HStack {
                            HStack(spacing: 8) {
                                Image(systemName: "person.circle")
                                    .foregroundColor(role.color)
                                Text(role.displayName)
                                    .font(.subheadline)
                            }
                            
                            Spacer()
                            
                            Text("\(roleDistribution[role]?.count ?? 0)")
                                .font(.subheadline)
                                .fontWeight(.semibold)
                                .foregroundColor(role.color)
                        }
                        .padding(.vertical, 4)
                    }
                }
                .padding()
                .background(Color(.systemBackground))
                .cornerRadius(12)
            }
            
            // Plot Structure
            VStack(alignment: .leading, spacing: 12) {
                Text("Plot Structure")
                    .font(.headline)
                    .fontWeight(.bold)
                
                VStack(alignment: .leading, spacing: 8) {
                    AnalysisRow(title: "Total Plot Points", value: "\(scenario.plotPoints.count)")
                    AnalysisRow(title: "Estimated Reading Time", value: estimatedReadingTime)
                    AnalysisRow(title: "World Type", value: scenario.worldType.displayName)
                    AnalysisRow(title: "Target Audience", value: scenario.targetAudience.displayName)
                }
            }
            .padding()
            .background(Color(.systemBackground))
            .cornerRadius(12)
        }
        .padding()
    }
    
    private var complexityDescription: String {
        switch scenario.complexity {
        case .simple:
            return "This scenario has a straightforward structure with minimal complexity, making it easy to follow and understand."
        case .moderate:
            return "This scenario presents a balanced level of complexity with multiple elements that interact in interesting ways."
        case .complex:
            return "This scenario features intricate plotting with sophisticated character development and thematic depth."
        case .advanced:
            return "This scenario demonstrates high-level storytelling with complex narrative structures and deep thematic exploration."
        case .masterful:
            return "This scenario represents the pinnacle of narrative complexity with masterful integration of all storytelling elements."
        }
    }
    
    private var estimatedReadingTime: String {
        let wordsPerMinute = 200
        let averageWordsPerPlotPoint = 50
        let totalWords = scenario.plotPoints.count * averageWordsPerPlotPoint
        let minutes = max(1, totalWords / wordsPerMinute)
        return "\(minutes) min"
    }
}

struct AnalysisRow: View {
    let title: String
    let value: String
    
    var body: some View {
        HStack {
            Text(title)
                .font(.subheadline)
                .foregroundColor(.secondary)
            
            Spacer()
            
            Text(value)
                .font(.subheadline)
                .fontWeight(.semibold)
        }
        .padding(.vertical, 2)
    }
}

// MARK: - Supporting Views

struct EditScenarioView: View {
    let scenario: DetailedScenario
    @ObservedObject var viewModel: ScenarioViewModel
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("Basic Information")) {
                    TextField("Plot Summary", text: .constant(scenario.plotSummary), axis: .vertical)
                        .lineLimit(3...6)
                }
                
                Section(header: Text("Settings")) {
                    Picker("World Type", selection: .constant(scenario.worldType)) {
                        ForEach(WorldType.allCases, id: \.self) { worldType in
                            Text(worldType.displayName).tag(worldType)
                        }
                    }
                    
                    Picker("Target Audience", selection: .constant(scenario.targetAudience)) {
                        ForEach(TargetAudience.allCases, id: \.self) { audience in
                            Text(audience.displayName).tag(audience)
                        }
                    }
                    
                    Picker("Complexity", selection: .constant(scenario.complexity)) {
                        ForEach(ScenarioComplexity.allCases, id: \.self) { complexity in
                            Text(complexity.displayName).tag(complexity)
                        }
                    }
                }
            }
            .navigationTitle("Edit Scenario")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Cancel") {
                        dismiss()
                    }
                }
                
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Save") {
                        dismiss()
                    }
                }
            }
        }
    }
}

#Preview {
    DetailedScenarioView(scenario: DetailedScenario.preview)
} 
