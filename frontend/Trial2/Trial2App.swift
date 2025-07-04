//
//  Trial2App.swift
//  Trial2
//
//  Created by Aiaulym Abduohapova on 23.06.2025.
//

import SwiftUI

@main
struct Trial2App: App {
    @StateObject private var navigation = NavigationViewModel()
    @StateObject private var authManager = AuthManager.shared

    var body: some Scene {
        WindowGroup {
            RootView(navigation: navigation, authManager: authManager)
        }
    }
}

