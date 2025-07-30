import SwiftUI

struct RootView: View {
    @ObservedObject var navigation: NavigationViewModel
    @ObservedObject var authManager: AuthManager

    var body: some View {
        Group {
            if authManager.isAuthenticated { // Simplified condition
                // User is authenticated, show main app
                switch navigation.currentScreen {
                case .welcome:
                    WelcomeView(viewModel: WelcomeViewModel(), navigation: navigation)
                case .mainDashboard:
                    MainDashboardView(navigation: navigation)
                case .create:
                    ComicGeneratorView(viewModel: ComicGeneratorViewModel(), navigation: navigation)
                case .comicGenerator:
                    ComicGeneratorView(viewModel: ComicGeneratorViewModel(), navigation: navigation)
                case .comicViewer:
                    ComicViewerView(navigation: navigation)
                        .onAppear {
                            print("🔍 RootView: comicViewer case reached")
                            if let comic = navigation.generatedComic {
                                print("🔍 Comic data available for viewer:")
                                print("🔍 - Title: '\(comic.title)'")
                                print("🔍 - About to display ComicViewerView")
                            } else {
                                print("⚠️ No comic available in navigation")
                                // Redirect to main dashboard if no comic data
                                DispatchQueue.main.async {
                                    navigation.currentScreen = .mainDashboard
                                }
                            }
                        }
                case .imageGenerator:
                    ImageGeneratorView(navigation: navigation)
                case .worlds:
                    WorldsView(navigation: navigation)
                case .profile:
                    ProfileView(navigation: navigation)
                case .dreamWorld:
                    DreamWorldView(navigation: navigation)
                case .mindWorld:
                    MindWorldView(navigation: navigation)
                case .imaginationWorld:
                    ImaginationWorldView(navigation: navigation)
                case .collections:
                    CollectionsView()
                case .scenarios:
                    // Future implementation: ScenariosView(navigation: navigation)
                    Text("Scenarios View - Coming Soon")
                        .font(.title)
                        .navigationTitle("Scenarios")
                case .detailedScenario:
                    if let scenario = navigation.selectedScenario {
                        Text("Detailed Scenario View")
                            .font(.title)
                            .navigationTitle("Scenario")
                    } else {
                        Text("No scenario selected")
                            .font(.title)
                            .navigationTitle("Scenario")
                    }
                case .accountDeletion:
                    // AccountDeletion is handled via sheet in ProfileView
                    ProfileView(navigation: navigation)
                case .login, .register:
                    // If authenticated, redirect to main dashboard
                    MainDashboardView(navigation: navigation)
                case .forgotPassword:
                    WelcomeView(viewModel: WelcomeViewModel(), navigation: navigation)
                case .analyticsDashboard:
                    AnalyticsDashboardView(navigation: navigation)
                @unknown default:
                    // Handle any future cases safely
                    
                    MainDashboardView(navigation: navigation)
                }
            } else {
                // User is not authenticated, show auth screens
                switch navigation.currentScreen {
                case .welcome:
                    WelcomeView(viewModel: WelcomeViewModel(), navigation: navigation)
                case .login:
                    LoginView(navigation: navigation, authManager: authManager)
                case .register:
                    RegistrationView(navigation: navigation, authManager: authManager)
                case .forgotPassword:
                    ForgotPasswordView(authManager: authManager, navigation: navigation)
                default:
                    // Default to welcome screen if not authenticated or explicitly handled
                    WelcomeView(viewModel: WelcomeViewModel(), navigation: navigation)
                }
            }
        }
        .onAppear {
            print("🔍 RootView appeared - Auth: \(authManager.isAuthenticated), Screen: \(navigation.currentScreen)")
        }
        .onReceive(authManager.$isAuthenticated) { isAuthenticated in
            print("🔍 Auth state changed: \(isAuthenticated)")
            if isAuthenticated {
                // Ensure we're on the main thread when updating navigation
                DispatchQueue.main.async {
                    navigation.currentScreen = .mainDashboard
                }
            }
        }
        .onReceive(navigation.$currentScreen) { screen in
            print("🔍 Screen changed to: \(screen)")
        }
    }
}
