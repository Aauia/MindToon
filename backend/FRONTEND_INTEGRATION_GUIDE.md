# MindToon Analytics Frontend Integration Guide

## Overview

This guide helps SwiftUI developers integrate the MindToon Analytics system into the iOS app. The Analyst system provides comprehensive user behavior tracking and insights without modifying the core comic generation logic.

## Key Integration Points

### 1. Comic Generation Tracking

Add analytics tracking when a comic is generated:

```swift
// In your ComicGeneratorViewModel or similar
func generateComic(prompt: String, genre: String, artStyle: String, worldType: WorldType) async {
    // Existing comic generation logic...
    
    // Add analytics tracking
    await trackComicGeneration(
        prompt: prompt,
        genre: genre,
        artStyle: artStyle,
        worldType: worldType,
        comicId: generatedComic.id
    )
}

private func trackComicGeneration(
    prompt: String,
    genre: String,
    artStyle: String,
    worldType: WorldType,
    comicId: Int?
) async {
    let analyticsEntry = AnalyticsEntryCreate(
        prompt: prompt,
        genre: genre,
        art_style: artStyle,
        world_type: worldType.rawValue,
        comic_id: comicId
    )
    
    do {
        let response = try await apiClient.post(
            endpoint: "/api/analytics/entry",
            body: analyticsEntry
        )
        print("Analytics entry added: \(response)")
    } catch {
        print("Failed to add analytics entry: \(error)")
    }
}
```

### 2. Analytics Dashboard View

Create a comprehensive analytics dashboard:

```swift
struct AnalyticsDashboardView: View {
    @StateObject private var viewModel = AnalyticsDashboardViewModel()
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 20) {
                    // Summary Cards
                    SummaryCardsView(summary: viewModel.summary)
                    
                    // Charts
                    if !viewModel.summary.genre_distribution.isEmpty {
                        GenreChartView(data: viewModel.genreChartData)
                    }
                    
                    if !viewModel.summary.art_style_distribution.isEmpty {
                        ArtStyleChartView(data: viewModel.artStyleChartData)
                    }
                    
                    if !viewModel.summary.world_distribution.isEmpty {
                        WorldChartView(data: viewModel.worldChartData)
                    }
                    
                    // Time Series
                    if !viewModel.summary.time_series.isEmpty {
                        TimeSeriesChartView(data: viewModel.timeSeriesData)
                    }
                    
                    // Insights Section
                    if viewModel.summary.insights_available {
                        InsightsSectionView(viewModel: viewModel)
                    }
                }
                .padding()
            }
            .navigationTitle("Your Analytics")
            .refreshable {
                await viewModel.loadAnalytics()
            }
        }
        .task {
            await viewModel.loadAnalytics()
        }
    }
}
```

### 3. Chart Components

#### Genre Distribution Bar Chart

```swift
struct GenreChartView: View {
    let data: ChartData
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Your Genre Preferences")
                .font(.headline)
            
            // Using Swift Charts (iOS 16+)
            Chart {
                ForEach(Array(zip(data.labels, data.data).enumerated()), id: \.offset) { index, item in
                    BarMark(
                        x: .value("Genre", item.0),
                        y: .value("Count", item.1)
                    )
                    .foregroundStyle(Color.blue.gradient)
                }
            }
            .frame(height: 200)
            
            // Legend
            LazyVGrid(columns: Array(repeating: GridItem(.flexible()), count: 2)) {
                ForEach(Array(zip(data.labels, data.percentages).enumerated()), id: \.offset) { index, item in
                    HStack {
                        Circle()
                            .fill(Color.blue)
                            .frame(width: 8, height: 8)
                        Text(item.0)
                            .font(.caption)
                        Spacer()
                        Text("\(item.1, specifier: "%.1f")%")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(radius: 2)
    }
}
```

#### Art Style Pie Chart

```swift
struct ArtStyleChartView: View {
    let data: ChartData
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Your Art Style Preferences")
                .font(.headline)
            
            // Using Swift Charts for pie chart
            Chart {
                ForEach(Array(zip(data.labels, data.data).enumerated()), id: \.offset) { index, item in
                    SectorMark(
                        angle: .value("Count", item.1),
                        innerRadius: .ratio(0.5),
                        angularInset: 2
                    )
                    .foregroundStyle(by: .value("Style", item.0))
                }
            }
            .frame(height: 200)
            
            // Legend
            LazyVGrid(columns: Array(repeating: GridItem(.flexible()), count: 2)) {
                ForEach(Array(zip(data.labels, data.percentages).enumerated()), id: \.offset) { index, item in
                    HStack {
                        Circle()
                            .fill(chartColors[index % chartColors.count])
                            .frame(width: 8, height: 8)
                        Text(item.0)
                            .font(.caption)
                        Spacer()
                        Text("\(item.1, specifier: "%.1f")%")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(radius: 2)
    }
    
    private let chartColors: [Color] = [.blue, .green, .orange, .purple, .red, .yellow]
}
```

### 4. Insights Integration

#### Pattern Analysis Modal

```swift
struct PatternAnalysisModal: View {
    @Binding var isPresented: Bool
    @StateObject private var viewModel = PatternAnalysisViewModel()
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    // Themes Section
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Your Creative Themes")
                            .font(.headline)
                        
                        LazyVGrid(columns: Array(repeating: GridItem(.flexible()), count: 2)) {
                            ForEach(viewModel.patternAnalysis?.themes ?? [], id: \.self) { theme in
                                Text(theme)
                                    .padding(.horizontal, 12)
                                    .padding(.vertical, 6)
                                    .background(Color.blue.opacity(0.1))
                                    .cornerRadius(8)
                            }
                        }
                    }
                    
                    // Emotions Section
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Emotional Patterns")
                            .font(.headline)
                        
                        LazyVGrid(columns: Array(repeating: GridItem(.flexible()), count: 2)) {
                            ForEach(viewModel.patternAnalysis?.emotions ?? [], id: \.self) { emotion in
                                Text(emotion)
                                    .padding(.horizontal, 12)
                                    .padding(.vertical, 6)
                                    .background(Color.green.opacity(0.1))
                                    .cornerRadius(8)
                            }
                        }
                    }
                    
                    // Summary
                    if let summary = viewModel.patternAnalysis?.summary {
                        VStack(alignment: .leading, spacing: 8) {
                            Text("Creative Summary")
                                .font(.headline)
                            
                            Text(summary)
                                .font(.body)
                                .foregroundColor(.secondary)
                        }
                    }
                }
                .padding()
            }
            .navigationTitle("Your Creative Patterns")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") {
                        isPresented = false
                    }
                }
            }
        }
        .task {
            await viewModel.generatePatternAnalysis()
        }
    }
}
```

### 5. View Models

#### Analytics Dashboard ViewModel

```swift
@MainActor
class AnalyticsDashboardViewModel: ObservableObject {
    @Published var summary: AnalyticsSummary = AnalyticsSummary.empty
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    var genreChartData: ChartData {
        ChartData(
            labels: summary.genre_distribution.map { $0.genre },
            data: summary.genre_distribution.map { $0.count },
            percentages: summary.genre_distribution.map { $0.percentage }
        )
    }
    
    var artStyleChartData: ChartData {
        ChartData(
            labels: summary.art_style_distribution.map { $0.art_style },
            data: summary.art_style_distribution.map { $0.count },
            percentages: summary.art_style_distribution.map { $0.percentage }
        )
    }
    
    var worldChartData: ChartData {
        ChartData(
            labels: summary.world_distribution.map { $0.world_type },
            data: summary.world_distribution.map { $0.count },
            percentages: summary.world_distribution.map { $0.percentage }
        )
    }
    
    var timeSeriesData: TimeSeriesChartData {
        TimeSeriesChartData(
            labels: summary.time_series.map { $0.date },
            data: summary.time_series.map { $0.count },
            genres: summary.time_series.map { $0.genres },
            artStyles: summary.time_series.map { $0.art_styles }
        )
    }
    
    func loadAnalytics() async {
        isLoading = true
        errorMessage = nil
        
        do {
            summary = try await apiClient.get(endpoint: "/api/analytics/summary")
        } catch {
            errorMessage = "Failed to load analytics: \(error.localizedDescription)"
        }
        
        isLoading = false
    }
    
    func generatePatternAnalysis() async {
        do {
            let insight = try await apiClient.post(endpoint: "/api/analytics/insights/patterns")
            // Handle insight response
        } catch {
            errorMessage = "Failed to generate pattern analysis: \(error.localizedDescription)"
        }
    }
}
```

#### Pattern Analysis ViewModel

```swift
@MainActor
class PatternAnalysisViewModel: ObservableObject {
    @Published var patternAnalysis: PromptAnalysis?
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    func generatePatternAnalysis() async {
        isLoading = true
        errorMessage = nil
        
        do {
            let response: InsightResponse = try await apiClient.post(
                endpoint: "/api/analytics/insights/patterns"
            )
            
            // Parse the pattern analysis from the response
            if let data = response.data as? [String: Any],
               let themes = data["themes"] as? [String],
               let emotions = data["emotions"] as? [String],
               let languageStyle = data["language_style"] as? String,
               let creativityIndicators = data["creativity_indicators"] as? [String],
               let summary = data["summary"] as? String {
                
                patternAnalysis = PromptAnalysis(
                    themes: themes,
                    emotions: emotions,
                    language_style: languageStyle,
                    creativity_indicators: creativityIndicators,
                    summary: summary
                )
            }
        } catch {
            errorMessage = "Failed to generate pattern analysis: \(error.localizedDescription)"
        }
        
        isLoading = false
    }
}
```

### 6. Data Models

```swift
// Analytics Data Models
struct AnalyticsSummary: Codable {
    let total_entries: Int
    let genre_distribution: [GenreStats]
    let art_style_distribution: [ArtStyleStats]
    let world_distribution: [WorldStats]
    let time_series: [TimeSeriesData]
    let recent_prompts: [String]
    let insights_available: Bool
    
    static let empty = AnalyticsSummary(
        total_entries: 0,
        genre_distribution: [],
        art_style_distribution: [],
        world_distribution: [],
        time_series: [],
        recent_prompts: [],
        insights_available: false
    )
}

struct GenreStats: Codable {
    let genre: String
    let count: Int
    let percentage: Double
}

struct ArtStyleStats: Codable {
    let art_style: String
    let count: Int
    let percentage: Double
}

struct WorldStats: Codable {
    let world_type: String
    let count: Int
    let percentage: Double
}

struct TimeSeriesData: Codable {
    let date: String
    let count: Int
    let genres: [String]
    let art_styles: [String]
}

struct PromptAnalysis: Codable {
    let themes: [String]
    let emotions: [String]
    let language_style: String
    let creativity_indicators: [String]
    let summary: String
}

// Chart Data Models
struct ChartData {
    let labels: [String]
    let data: [Int]
    let percentages: [Double]
}

struct TimeSeriesChartData {
    let labels: [String]
    let data: [Int]
    let genres: [[String]]
    let artStyles: [[String]]
}

// API Request Models
struct AnalyticsEntryCreate: Codable {
    let prompt: String
    let genre: String
    let art_style: String
    let world_type: String
    let comic_id: Int?
}
```

### 7. Navigation Integration

Add analytics to your main navigation:

```swift
struct MainTabView: View {
    var body: some View {
        TabView {
            // Existing tabs...
            
            AnalyticsDashboardView()
                .tabItem {
                    Image(systemName: "chart.bar.fill")
                    Text("Analytics")
                }
        }
    }
}
```

### 8. Notification Integration

Show insights when available:

```swift
// In your main app or dashboard
.onReceive(NotificationCenter.default.publisher(for: .analyticsInsightAvailable)) { _ in
    showInsightNotification()
}

private func showInsightNotification() {
    let content = UNMutableNotificationContent()
    content.title = "New Insight Available!"
    content.body = "Discover your creative patterns and preferences."
    content.sound = .default
    
    let request = UNNotificationRequest(
        identifier: UUID().uuidString,
        content: content,
        trigger: nil
    )
    
    UNUserNotificationCenter.current().add(request)
}
```

## Best Practices

1. **Lazy Loading**: Load analytics data only when the dashboard is accessed
2. **Error Handling**: Provide fallback UI when analytics data is unavailable
3. **Caching**: Cache analytics data to reduce API calls
4. **Privacy**: Ensure users understand what data is being tracked
5. **Performance**: Use background tasks for analytics tracking to avoid blocking UI

## Testing

Test the integration with sample data:

```swift
// In your preview provider
struct AnalyticsDashboardView_Previews: PreviewProvider {
    static var previews: some View {
        AnalyticsDashboardView()
            .environmentObject(MockAnalyticsViewModel())
    }
}

class MockAnalyticsViewModel: ObservableObject {
    @Published var summary = AnalyticsSummary(
        total_entries: 15,
        genre_distribution: [
            GenreStats(genre: "action", count: 5, percentage: 33.33),
            GenreStats(genre: "fantasy", count: 3, percentage: 20.0)
        ],
        art_style_distribution: [
            ArtStyleStats(art_style: "comic book", count: 8, percentage: 53.33)
        ],
        world_distribution: [
            WorldStats(world_type: "imagination_world", count: 10, percentage: 66.67)
        ],
        time_series: [],
        recent_prompts: ["Sample prompt 1", "Sample prompt 2"],
        insights_available: true
    )
}
```

This integration provides a complete analytics experience for users while maintaining the existing comic generation functionality. 