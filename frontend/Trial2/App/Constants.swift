import UIKit // For UI elements and UIKit framework
import Foundation // For basic types like URL, Data, etc.

// MARK: - App/Constants.swift
// Global constants for the application, such as base URLs.
struct Constants {
    static let backendBaseURL = URL(string: "http://localhost:8000")! // Your FastAPI backend
    // static let geminiAPIKey = "YOUR_GEMINI_API_KEY" // In a real app, securely fetch this from backend or environment
}
