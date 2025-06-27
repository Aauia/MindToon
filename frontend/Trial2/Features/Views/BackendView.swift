import SwiftUI

struct BackendTestView: View {
    @State private var healthStatus: String = "Not tested"
    @State private var configStatus: String = "Not tested"
    @State private var isLoading = false
    @State private var errorMessage: String?
    
    var body: some View {
        VStack(spacing: 20) {
            Text("Backend Connection Test")
                .font(.largeTitle)
                .fontWeight(.bold)
            
            VStack(alignment: .leading, spacing: 10) {
                Text("Health Check: \(healthStatus)")
                    .font(.headline)
                
                Text("iOS Config: \(configStatus)")
                    .font(.headline)
                
                if let error = errorMessage {
                    Text("Error: \(error)")
                        .foregroundColor(.red)
                        .font(.caption)
                }
            }
            .padding()
            .background(Color.gray.opacity(0.1))
            .cornerRadius(10)
            
            Button("Test Backend Connection") {
                Task {
                    await testBackendConnection()
                }
            }
            .font(.headline)
            .foregroundColor(.white)
            .padding()
            .frame(maxWidth: .infinity)
            .background(isLoading ? Color.gray : Color.blue)
            .cornerRadius(15)
            .disabled(isLoading)
            
            if isLoading {
                ProgressView()
                    .padding()
            }
            
            Spacer()
        }
        .padding()
    }
    
    private func testBackendConnection() async {
        isLoading = true
        errorMessage = nil
        
        do {
            // Test health endpoint
            let health = try await APIClient.shared.healthCheck()
            healthStatus = "✅ \(health.status)"
            
            // Test iOS config endpoint
            let config = try await APIClient.shared.getIOSConfig()
            configStatus = "✅ Version \(config.version)"
            
        } catch {
            errorMessage = error.localizedDescription
            healthStatus = "❌ Failed"
            configStatus = "❌ Failed"
        }
        
        isLoading = false
    }
}

#Preview {
    BackendTestView()
} 
