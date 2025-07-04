//
//  ContentView.swift
//  Trial2
//
//  Created by Aiaulym Abduohapova on 23.06.2025.
//

import SwiftUI

struct ContentView: View {
    @StateObject private var navigation = NavigationViewModel()
    @StateObject private var authManager = AuthManager.shared
    
    var body: some View {
        // Redirect to the proper app entry point
        RootView(navigation: navigation, authManager: authManager)
            .onAppear {
                print("📱 ContentView: Redirecting to RootView with proper navigation")
            }
    }
}

#Preview {
    ContentView()
}
