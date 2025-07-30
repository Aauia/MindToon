import Foundation
import Combine

class AnalyticsViewModel: ObservableObject {
    static let shared = AnalyticsViewModel() // Singleton for analytics caching
    
    @Published var comicRecommendations: ComicRecommendationsResponse?
    @Published var weeklyInsight: WeeklyInsight?
    @Published var isLoading = false
    @Published var error: String?
    @Published var selectedWorld: String = "imagination_world"
    @Published var isRefreshingRecommendations = false
    
    // Persistent caching properties
    private let userDefaults = UserDefaults.standard
    private let cacheKeyPrefix = "cached_recommendations_"

    func fetchAllAnalytics(userId: Int, worldType: String) {
        // Immediately clear old data and show loading state
        isLoading = true
        error = nil
        weeklyInsight = nil
        selectedWorld = worldType
        
        // Load cached recommendations for this world
        loadCachedRecommendations(for: worldType)
        
        let group = DispatchGroup()

        group.enter()
        AnalyticsService.shared.fetchWeeklyInsight(userId: userId) { result in
            DispatchQueue.main.async {
                switch result {
                case .success(let data): self.weeklyInsight = data
                case .failure(let err): self.error = err.localizedDescription
                }
                group.leave()
            }
        }

        group.notify(queue: .main) {
            self.isLoading = false
        }
    }
    
    func switchWorld(userId: Int, worldType: String) {
        // Immediately clear old data and show loading state
        isLoading = true
        error = nil
        comicRecommendations = nil
        weeklyInsight = nil
        selectedWorld = worldType
        
        fetchAllAnalytics(userId: userId, worldType: worldType)
    }
    
    func fetchAnalyticsWithPeriod(userId: Int, period: String, worldType: String) {
        // Only clear digest data, keep recommendations unchanged
        isLoading = true
        error = nil
        weeklyInsight = nil // Only clear the time-period dependent data
        
        // Load cached recommendations for this world (if world changed)
        if selectedWorld != worldType {
            loadCachedRecommendations(for: worldType)
        }
        
        selectedWorld = worldType
        
        let group = DispatchGroup()

        // Always fetch period-specific insight data
        group.enter()
        AnalyticsService.shared.fetchInsightByPeriod(userId: userId, period: period) { result in
            DispatchQueue.main.async {
                switch result {
                case .success(let data): self.weeklyInsight = data
                case .failure(let err): self.error = err.localizedDescription
                }
                group.leave()
            }
        }

        group.notify(queue: .main) {
            self.isLoading = false
        }
    }
    
    // MARK: - Persistent Caching Logic
    
    /// Load cached recommendations for a specific world
    private func loadCachedRecommendations(for worldType: String) {
        let cacheKey = cacheKeyPrefix + worldType
        
        if let cachedData = userDefaults.data(forKey: cacheKey) {
            do {
                let cachedRecommendations = try JSONDecoder().decode(ComicRecommendationsResponse.self, from: cachedData)
                comicRecommendations = cachedRecommendations
                print("📦 [Analytics] Loaded cached recommendations for \(worldType): \(cachedRecommendations.recommendations.count) items")
            } catch {
                print("❌ [Analytics] Failed to decode cached recommendations for \(worldType): \(error)")
                comicRecommendations = nil
            }
        } else {
            print("📦 [Analytics] No cached recommendations found for \(worldType)")
            comicRecommendations = nil
        }
    }
    
    /// Save recommendations to persistent cache for a specific world
    private func saveRecommendationsToCache(_ recommendations: ComicRecommendationsResponse, for worldType: String) {
        let cacheKey = cacheKeyPrefix + worldType
        
        do {
            let encodedData = try JSONEncoder().encode(recommendations)
            userDefaults.set(encodedData, forKey: cacheKey)
            print("💾 [Analytics] Saved recommendations to cache for \(worldType): \(recommendations.recommendations.count) items")
        } catch {
            print("❌ [Analytics] Failed to save recommendations to cache for \(worldType): \(error)")
        }
    }
    
    /// Check if we have cached recommendations for a world
    func hasCachedRecommendations(for worldType: String) -> Bool {
        let cacheKey = cacheKeyPrefix + worldType
        return userDefaults.data(forKey: cacheKey) != nil
    }
    
    /// Manually refresh recommendations for the current world
    func refreshRecommendations(userId: Int) {
        guard !isRefreshingRecommendations else { return }
        
        isRefreshingRecommendations = true
        print("🔄 [Analytics] Manually refreshing recommendations for \(selectedWorld)")
        
        AnalyticsService.shared.fetchComicRecommendations(userId: userId, world: selectedWorld, limit: 5) { result in
            DispatchQueue.main.async {
                switch result {
                case .success(let data):
                    self.comicRecommendations = data
                    self.saveRecommendationsToCache(data, for: self.selectedWorld)
                    print("✅ [Analytics] Successfully refreshed and cached recommendations for \(self.selectedWorld)")
                case .failure(let err):
                    self.error = "Failed to refresh recommendations: \(err.localizedDescription)"
                    print("❌ [Analytics] Failed to refresh recommendations: \(err)")
                }
                self.isRefreshingRecommendations = false
            }
        }
    }
    
    /// Clear all cached recommendations (for debugging/reset)
    func clearAllCachedRecommendations() {
        let worlds = ["imagination_world", "mind_world", "dream_world"]
        for world in worlds {
            let cacheKey = cacheKeyPrefix + world
            userDefaults.removeObject(forKey: cacheKey)
        }
        comicRecommendations = nil
        print("🗑️ [Analytics] Cleared all cached recommendations")
    }
}
//
//  AnalyticsViewModel.swift
//  MindToon
//
//  Created by Aiaulym Abduohapova on 30.07.2025.
//

