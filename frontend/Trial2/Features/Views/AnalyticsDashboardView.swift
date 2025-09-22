import SwiftUI

struct AnalyticsDashboardView: View {
    @ObservedObject var navigation: NavigationViewModel
    @StateObject private var viewModel = AnalyticsViewModel()
    @State private var twinkleToggle = false
    @State private var selectedDigestPeriod: String = "weekly" // Default to weekly
    let userId: Int = 1 // TODO: Replace with actual user id from auth/session
    
   
    private let digestPeriods = [
        ("weekly", "Weekly", "calendar"),
        ("monthly", "Monthly", "calendar.circle"),
        ("all_time", "All Time", "clock.arrow.circlepath")
    ]
    
   
    private let availableWorlds = [
        ("imagination_world", "Imagination World", "wand.and.stars", Color.purple),
        ("mind_world", "Mind World", "brain.head.profile", Color.blue),
        ("dream_world", "Dream World", "moon.stars.fill", Color.indigo)
    ]

    var body: some View {
        ZStack {
            // Gradient Background matching app theme
            LinearGradient(
                gradient: Gradient(colors: [
                    Color(red: 0.85, green: 0.73, blue: 0.94), // lavender
                    Color(red: 0.99, green: 0.85, blue: 0.85)  // peach
                ]),
                startPoint: .top,
                endPoint: .bottom
            )
            .ignoresSafeArea()

            // Animated stars
            ForEach(0..<20, id: \.self) { _ in
                Circle()
                    .fill(Color.white.opacity(twinkleToggle ? 0.8 : 0.3))
                    .frame(width: 2, height: 2)
                    .position(
                        x: CGFloat.random(in: 0...UIScreen.main.bounds.width),
                        y: CGFloat.random(in: 0...UIScreen.main.bounds.height * 0.6)
                    )
                    .animation(.easeInOut(duration: 1.2), value: twinkleToggle)
            }
            
            VStack(spacing: 0) {
               
                HStack {
                    Button(action: {
                        navigation.navigateTo(.mainDashboard)
                    }) {
                        HStack(spacing: 8) {
                            Image(systemName: "chevron.left")
                                .font(.system(size: 18, weight: .semibold))
                            
                        }
                        .foregroundColor(Color.black.opacity(0.8))
                        .padding(.horizontal, 16)
                        .padding(.vertical, 8)
                        .background(Color.white.opacity(0.2))
                        .cornerRadius(20)
                    }
                    
                    Spacer()
                    
                    Text("Analytics Dashboard")
                        .font(.system(size: 22, weight: .bold))
                        .foregroundColor(.black)
                    
                    Spacer()
                    
                   
                    Color.clear
                        .frame(width: 80, height: 36)
                }
                .padding(.horizontal, 20)
                .padding(.top, 10)
              
                DigestPeriodSelector(
                    selectedPeriod: $selectedDigestPeriod,
                    digestPeriods: digestPeriods,
                    onPeriodChange: { newPeriod in
                        viewModel.fetchAnalyticsWithPeriod(userId: userId, period: newPeriod, worldType: viewModel.selectedWorld)
                    }
                )
                .padding(.horizontal, 20)
                .padding(.top, 10)
                
                ScrollView {
                    VStack(spacing: 0) {
                
                    VStack(spacing: 16) {
                            if let weekly = viewModel.weeklyInsight {
                                PersistentWeeklyInsightSection(weekly: weekly, periodName: getPeriodDisplayName())
                            } else if viewModel.isLoading {
                                WeeklyInsightsLoadingView(periodName: getPeriodDisplayName())
                            } else if let error = viewModel.error {
                                WeeklyInsightsErrorView(error: error, periodName: getPeriodDisplayName())
                            }
                        }
                        .padding(.horizontal, 20)
                        .padding(.bottom, 20)
                        
                        
                        VStack(spacing: 16) {
                        
                            RecommendationsWorldSelector(
                                selectedWorld: $viewModel.selectedWorld,
                                availableWorlds: availableWorlds,
                                onWorldChange: { newWorld in
                                    viewModel.switchWorld(userId: userId, worldType: newWorld)
                                }
                            )
                            
                          
                            if viewModel.isLoading {
                                RecommendationsLoadingView()
                            } else if let recommendations = viewModel.comicRecommendations {
                                ThemedComicRecommendationsSection(
                                    recommendations: recommendations,
                                    worldType: viewModel.selectedWorld,
                                    isRefreshing: viewModel.isRefreshingRecommendations,
                                    onRefresh: {
                                        viewModel.refreshRecommendations(userId: userId)
                                    }
                                )
                            } else {
                                NoRecommendationsView(
                                    worldType: viewModel.selectedWorld,
                                    isGenerating: viewModel.isRefreshingRecommendations,
                                    onGenerate: {
                                        viewModel.refreshRecommendations(userId: userId)
                                    }
                                )
                            }
                        }
                        .padding(.horizontal, 20)
                        .padding(.bottom, 100) 
                    }
                }
                
                Spacer()
            }
            
            // Bottom Navigation Bar
            VStack {
                Spacer()
                BottombarView(navigation: navigation)
                    .background(Color(hex: "#5A3FA0"))
            }
        }
        .onAppear { 
            viewModel.fetchAnalyticsWithPeriod(userId: userId, period: selectedDigestPeriod, worldType: viewModel.selectedWorld) 
      
            Timer.scheduledTimer(withTimeInterval: 1.2, repeats: true) { _ in
                twinkleToggle.toggle()
            }
        }
    }
    
    private func getPeriodDisplayName() -> String {
        switch selectedDigestPeriod {
        case "weekly": return "Weekly"
        case "monthly": return "Monthly"
        case "all_time": return "All Time"
        default: return "Weekly"
        }
    }
}


struct PersistentWeeklyInsightSection: View {
    let weekly: WeeklyInsight
    let periodName: String
 
    private var consolidatedGenres: [GenreStats] {
        var genreMap: [String: GenreStats] = [:]
        
        for genre in weekly.topGenres {
            let normalizedKey = genre.genre.lowercased()
            
            if let existing = genreMap[normalizedKey] {
                let newCount = existing.count + genre.count
                let newPercentage = existing.percentage + genre.percentage
                genreMap[normalizedKey] = GenreStats(
                    genre: normalizedKey.capitalized,
                    count: newCount,
                    percentage: newPercentage
                )
            } else {
                genreMap[normalizedKey] = GenreStats(
                    genre: normalizedKey.capitalized,
                    count: genre.count,
                    percentage: genre.percentage
                )
            }
        }
        
     
        return Array(genreMap.values).sorted { $0.count > $1.count }
    }
    
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {

            HStack {
                Image(systemName: "chart.line.uptrend.xyaxis")
                    .font(.system(size: 24))
                    .foregroundColor(.white)
                
                                        Text("\(periodName) Digest")
                            .font(.system(size: 24, weight: .bold))
                            .foregroundColor(.white)
                
                Spacer()
                
                Text("\(weekly.totalComics)")
                    .font(.system(size: 18, weight: .bold))
                    .foregroundColor(.white)
                    .padding(.horizontal, 16)
                    .padding(.vertical, 6)
                    .background(Color.white.opacity(0.2))
                    .cornerRadius(16)
            }
            .padding(.horizontal, 20)
            .padding(.top, 20)
            
            VStack(alignment: .leading, spacing: 16) {
              
                HStack {
                    Image(systemName: "calendar")
                        .font(.system(size: 16))
                        .foregroundColor(.white.opacity(0.8))
                    
                    Text("Week: \(weekly.weekStart) - \(weekly.weekEnd)")
                        .font(.system(size: 16, weight: .medium))
                        .foregroundColor(.white.opacity(0.9))
                }
                
        
                LazyVGrid(columns: Array(repeating: GridItem(.flexible()), count: 1), spacing: 16) {
                    
                
                    if !consolidatedGenres.isEmpty {
                        VStack(alignment: .leading, spacing: 8) {
                            HStack {
                                Image(systemName: "tag.fill")
                                    .font(.system(size: 14))
                                    .foregroundColor(.white)
                                
                                Text("Popular Genres \(periodName)")
                                    .font(.system(size: 16, weight: .semibold))
                                    .foregroundColor(.white)
                            }
                            
                            ForEach(consolidatedGenres.prefix(3), id: \.genre) { genre in
                                HStack {
                                    Circle()
                                        .fill(Color.white.opacity(0.6))
                                        .frame(width: 6, height: 6)
                                    
                                    Text("\(genre.genre)")
                                        .font(.system(size: 14, weight: .medium))
                                        .foregroundColor(.white.opacity(0.9))
                                    
                                    Spacer()
                                    
                                    Text("\(genre.count) (\(String(format: "%.1f", genre.percentage))%)")
                                        .font(.system(size: 13, weight: .semibold))
                                        .foregroundColor(.white)
                                }
                            }
                        }
                        .padding(16)
                        .background(
                            RoundedRectangle(cornerRadius: 12)
                                .fill(Color.white.opacity(0.1))
                        )
                    }
                    
         
                    if !weekly.topArtStyles.isEmpty {
                        VStack(alignment: .leading, spacing: 8) {
                            HStack {
                                Image(systemName: "paintbrush.fill")
                                    .font(.system(size: 14))
                                    .foregroundColor(.white)
                                
                                Text("Popular Art Styles")
                                    .font(.system(size: 16, weight: .semibold))
                                    .foregroundColor(.white)
                            }
                            
                            ForEach(weekly.topArtStyles.prefix(3), id: \.artStyle) { style in
                                HStack {
                                    Circle()
                                        .fill(Color.white.opacity(0.6))
                                        .frame(width: 6, height: 6)
                                    
                                    Text("\(style.artStyle)")
                                        .font(.system(size: 14, weight: .medium))
                                        .foregroundColor(.white.opacity(0.9))
                                    
                                    Spacer()
                                    
                                    Text("\(style.count) (\(String(format: "%.1f", style.percentage))%)")
                                        .font(.system(size: 13, weight: .semibold))
                                        .foregroundColor(.white)
                                }
                            }
                        }
                        .padding(16)
                        .background(
                            RoundedRectangle(cornerRadius: 12)
                                .fill(Color.white.opacity(0.1))
                        )
                    }
                    
      
                    if !weekly.worldDistribution.isEmpty {
                        VStack(alignment: .leading, spacing: 8) {
                            HStack {
                                Image(systemName: "globe.americas.fill")
                                    .font(.system(size: 14))
                                    .foregroundColor(.white)
                                
                                Text("World Exploration")
                                    .font(.system(size: 16, weight: .semibold))
                                    .foregroundColor(.white)
                            }
                            
                            ForEach(weekly.worldDistribution, id: \.worldType) { world in
                                HStack {
                                    Circle()
                                        .fill(Color.white.opacity(0.6))
                                        .frame(width: 6, height: 6)
                                    
                                    Text("\(world.worldType.replacingOccurrences(of: "_", with: " ").capitalized)")
                                        .font(.system(size: 14, weight: .medium))
                                        .foregroundColor(.white.opacity(0.9))
                                    
                                    Spacer()
                                    
                                    Text("\(world.count) (\(String(format: "%.1f", world.percentage))%)")
                                        .font(.system(size: 13, weight: .semibold))
                                        .foregroundColor(.white)
                                }
                            }
                        }
                        .padding(16)
                        .background(
                            RoundedRectangle(cornerRadius: 12)
                                .fill(Color.white.opacity(0.1))
                        )
                    }
                }
            }
            .padding(.horizontal, 20)
            .padding(.bottom, 20)
        }
        .background(
            RoundedRectangle(cornerRadius: 20)
                .fill(Color.black.opacity(0.4))
        )
    }
}


struct RecommendationsWorldSelector: View {
    @Binding var selectedWorld: String
    let availableWorlds: [(String, String, String, Color)]
    let onWorldChange: (String) -> Void
    
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("AI Recommendations")
                .font(.system(size: 22, weight: .bold))
                .foregroundColor(.white)
                .padding(.leading, 4)
            
            Text("Get personalized comic concepts for each world")
                .font(.system(size: 14))
                .foregroundColor(.white.opacity(0.7))
                .padding(.leading, 4)
            
            HStack(spacing: 12) {
                ForEach(availableWorlds, id: \.0) { world in
                    RecommendationWorldButton(
                        worldId: world.0,
                        worldName: world.1,
                        iconName: world.2,
                        color: world.3,
                        isSelected: selectedWorld == world.0
                    ) {
                        selectedWorld = world.0
                        onWorldChange(world.0)
                    }
                }
            }
        }
    }
}


struct RecommendationWorldButton: View {
    let worldId: String
    let worldName: String
    let iconName: String
    let color: Color
    let isSelected: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            VStack(spacing: 8) {
                Image(systemName: iconName)
                    .font(.system(size: 20, weight: .bold))
                    .foregroundColor(isSelected ? .white : color)
                
                Text(worldName.replacingOccurrences(of: " World", with: ""))
                    .font(.system(size: 11, weight: .semibold))
                    .foregroundColor(isSelected ? .white : .white.opacity(0.7))
                    .multilineTextAlignment(.center)
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 12)
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(isSelected ? color : Color.white.opacity(0.1))
                    .overlay(
                        RoundedRectangle(cornerRadius: 12)
                            .stroke(color, lineWidth: isSelected ? 0 : 1)
                    )
            )
        }
        .scaleEffect(isSelected ? 1.05 : 1.0)
        .animation(.spring(response: 0.3, dampingFraction: 0.6), value: isSelected)
    }
}


struct WeeklyInsightsLoadingView: View {
    let periodName: String
    
    var body: some View {
        VStack(spacing: 16) {
            HStack {
                Image(systemName: "chart.line.uptrend.xyaxis")
                    .font(.system(size: 24))
                    .foregroundColor(.white.opacity(0.6))
                
                Text("\(periodName) Digest")
                    .font(.system(size: 24, weight: .bold))
                    .foregroundColor(.white.opacity(0.6))
                
                Spacer()
            }
            .padding(.horizontal, 20)
            .padding(.top, 20)
            
            VStack(spacing: 12) {
                ProgressView()
                    .scaleEffect(1.2)
                    .progressViewStyle(CircularProgressViewStyle(tint: .white))
                
                Text("Loading your weekly insights...")
                    .font(.system(size: 16, weight: .medium))
                    .foregroundColor(.white.opacity(0.8))
            }
            .padding(.vertical, 40)
        }
        .background(
            RoundedRectangle(cornerRadius: 20)
                .fill(Color.black.opacity(0.4))
        )
    }
}


struct WeeklyInsightsErrorView: View {
    let error: String
    let periodName: String
    
    var body: some View {
        VStack(spacing: 16) {
            HStack {
                Image(systemName: "chart.line.uptrend.xyaxis")
                    .font(.system(size: 24))
                    .foregroundColor(.white.opacity(0.6))
                
                Text("\(periodName) Digest")
                    .font(.system(size: 24, weight: .bold))
                    .foregroundColor(.white.opacity(0.6))
                
                Spacer()
            }
            .padding(.horizontal, 20)
            .padding(.top, 20)
            
            VStack(spacing: 12) {
                Image(systemName: "exclamationmark.triangle.fill")
                    .font(.system(size: 28))
                    .foregroundColor(.red.opacity(0.8))
                
                Text("Unable to load weekly insights")
                    .font(.system(size: 16, weight: .bold))
                    .foregroundColor(.white)
                
                Text(error)
                    .font(.system(size: 14))
                    .foregroundColor(.white.opacity(0.7))
                    .multilineTextAlignment(.center)
            }
            .padding(.vertical, 30)
        }
        .background(
            RoundedRectangle(cornerRadius: 20)
                .fill(Color.black.opacity(0.4))
        )
    }
}


struct RecommendationsLoadingView: View {
    var body: some View {
        VStack(spacing: 16) {
            ProgressView()
                .scaleEffect(1.2)
                .progressViewStyle(CircularProgressViewStyle(tint: .white))
            
            Text("Loading personalized recommendations...")
                .font(.system(size: 16, weight: .medium))
                .foregroundColor(.white.opacity(0.8))
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 40)
        .background(
            RoundedRectangle(cornerRadius: 20)
                .fill(Color.black.opacity(0.4))
        )
    }
}


struct NoRecommendationsView: View {
    let worldType: String
    let isGenerating: Bool
    let onGenerate: () -> Void
    
    var worldColor: Color {
        switch worldType {
        case "imagination_world": return .purple
        case "mind_world": return .blue
        case "dream_world": return .indigo
        default: return .purple
        }
    }
    
    var worldIcon: String {
        switch worldType {
        case "imagination_world": return "wand.and.stars"
        case "mind_world": return "brain.head.profile"
        case "dream_world": return "moon.stars.fill"
        default: return "wand.and.stars"
        }
    }
    
    var body: some View {
        VStack(spacing: 16) {
            Image(systemName: worldIcon)
                .font(.system(size: 32))
                .foregroundColor(worldColor.opacity(0.6))
            
            Text("No Recommendations Available")
                .font(.system(size: 18, weight: .bold))
                .foregroundColor(.white)
            
            Text("Generate AI-powered comic recommendations for \(worldType.replacingOccurrences(of: "_", with: " ").capitalized)!")
                .font(.system(size: 14))
                .foregroundColor(.white.opacity(0.7))
                .multilineTextAlignment(.center)
            
            // Generate Button
            Button(action: onGenerate) {
                HStack(spacing: 8) {
                    if isGenerating {
                        ProgressView()
                            .scaleEffect(0.8)
                            .progressViewStyle(CircularProgressViewStyle(tint: .white))
                    } else {
                        Image(systemName: "sparkles")
                            .font(.system(size: 16, weight: .semibold))
                    }
                    Text(isGenerating ? "Generating..." : "Generate Recommendations")
                        .font(.system(size: 16, weight: .semibold))
                }
                .foregroundColor(.white)
                .padding(.horizontal, 20)
                .padding(.vertical, 12)
                .background(worldColor.opacity(0.8))
                .cornerRadius(12)
            }
            .disabled(isGenerating)
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 40)
        .background(
            RoundedRectangle(cornerRadius: 20)
                .fill(Color.black.opacity(0.4))
        )
    }
}




struct ThemedComicRecommendationsSection: View {
    let recommendations: ComicRecommendationsResponse
    let worldType: String
    let isRefreshing: Bool
    let onRefresh: () -> Void
    
    var worldColor: Color {
        switch worldType {
        case "imagination_world": return .purple
        case "mind_world": return .blue
        case "dream_world": return .indigo
        default: return .purple
        }
    }
    
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            // Section Header
            HStack {
                Image(systemName: "lightbulb.fill")
                    .font(.system(size: 20))
                    .foregroundColor(worldColor)
                
                Text("AI-Generated Comic Concepts")
                    .font(.system(size: 20, weight: .bold))
                    .foregroundColor(.white)
                
                Spacer()
                
                // Refresh Button
                Button(action: onRefresh) {
                    HStack(spacing: 4) {
                        if isRefreshing {
                            ProgressView()
                                .scaleEffect(0.8)
                                .progressViewStyle(CircularProgressViewStyle(tint: .white))
                        } else {
                            Image(systemName: "arrow.clockwise")
                                .font(.system(size: 14, weight: .semibold))
                        }
                        Text("Refresh")
                            .font(.system(size: 12, weight: .medium))
                    }
                    .foregroundColor(.white)
                    .padding(.horizontal, 10)
                    .padding(.vertical, 6)
                    .background(worldColor.opacity(0.6))
                    .cornerRadius(8)
                }
                .disabled(isRefreshing)
                
                Text("\(recommendations.totalRecommendations)")
                    .font(.system(size: 16, weight: .bold))
                    .foregroundColor(.white)
                    .padding(.horizontal, 12)
                    .padding(.vertical, 4)
                    .background(worldColor.opacity(0.8))
                    .cornerRadius(12)
            }
            .padding(.horizontal, 20)
            .padding(.top, 20)
            
            // Recommendations List
                ForEach(Array(recommendations.recommendations.enumerated()), id: \.offset) { index, recommendation in
                ThemedRecommendationCard(
                    recommendation: recommendation,
                    index: index + 1,
                    worldColor: worldColor
                )
            }
        }
        .background(
            RoundedRectangle(cornerRadius: 20)
                .fill(Color.black.opacity(0.75))
        )
    }
}


struct ThemedRecommendationCard: View {
    let recommendation: ComicRecommendation
    let index: Int
    let worldColor: Color
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
      
                        HStack {
                Text("\(index). \(recommendation.title)")
                    .font(.system(size: 18, weight: .bold))
                    .foregroundColor(.white)
                
                            Spacer()
                
                            VStack(spacing: 2) {
                                Text("\(Int(recommendation.confidenceScore * 100))%")
                                    .font(.system(size: 14, weight: .bold))
                                    .foregroundColor(.white)
                                Text("Compatible")
                                    .font(.system(size: 10, weight: .medium))
                                    .foregroundColor(.white.opacity(0.8))
                            }
                            .padding(.horizontal, 8)
                            .padding(.vertical, 4)
                            .background(worldColor.opacity(0.6))
                            .cornerRadius(8)
            }
            
            // Author
            HStack {
                Text("Author:")
                    .font(.system(size: 13, weight: .semibold))
                    .foregroundColor(.white.opacity(0.7))
                Text(recommendation.suggestedAuthor)
                    .font(.system(size: 13))
                    .foregroundColor(.white.opacity(0.9))
            }
                        
                        // Plot Summary
            VStack(alignment: .leading, spacing: 4) {
                        Text("Plot Summary:")
                    .font(.system(size: 13, weight: .semibold))
                    .foregroundColor(.white.opacity(0.7))
                
                        Text(recommendation.plotSummary)
                    .font(.system(size: 13))
                    .foregroundColor(.white.opacity(0.9))
                    .lineLimit(nil)
            }
            
            // Genre and Style Tags
            HStack(spacing: 8) {
                            Text("Genre: \(recommendation.genre)")
                    .font(.system(size: 12, weight: .semibold))
                    .foregroundColor(.white)
                    .padding(.horizontal, 10)
                    .padding(.vertical, 4)
                    .background(Color.green.opacity(0.6))
                    .cornerRadius(8)
                            
                            Text("Style: \(recommendation.artStyle)")
                    .font(.system(size: 12, weight: .semibold))
                    .foregroundColor(.white)
                    .padding(.horizontal, 10)
                    .padding(.vertical, 4)
                    .background(Color.orange.opacity(0.6))
                    .cornerRadius(8)
                        }

            
            // Why this concept
            VStack(alignment: .leading, spacing: 4) {
                        Text("Why this concept:")
                    .font(.system(size: 13, weight: .semibold))
                    .foregroundColor(.white.opacity(0.7))
                        
                        Text(recommendation.reasoning)
                    .font(.system(size: 13))
                    .foregroundColor(.white.opacity(0.9))
                    .lineLimit(nil)
            }

        }
        .padding(16)
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(Color.black.opacity(0.4))
        )
        .padding(.horizontal, 20)
    }
}





struct DigestPeriodSelector: View {
    @Binding var selectedPeriod: String
    let digestPeriods: [(String, String, String)]
    let onPeriodChange: (String) -> Void
    
    var body: some View {
        HStack(spacing: 12) {
            ForEach(digestPeriods, id: \.0) { period in
                Button(action: {
                    selectedPeriod = period.0
                    onPeriodChange(period.0)
                }) {
                    HStack(spacing: 6) {
                        Image(systemName: period.2)
                            .font(.system(size: 14, weight: .medium))
                        Text(period.1)
                            .font(.system(size: 14, weight: .medium))
                    }
                    .foregroundColor(selectedPeriod == period.0 ? .white : .black.opacity(0.7))
                    .padding(.horizontal, 16)
                    .padding(.vertical, 10)
                    .background(
                        RoundedRectangle(cornerRadius: 20)
                            .fill(selectedPeriod == period.0 ? 
                                  Color.black.opacity(0.8) : 
                                  Color.white.opacity(0.3))
                    )
                }
            }
        }
    }
}

#Preview {
    AnalyticsDashboardView(navigation: NavigationViewModel())
}

