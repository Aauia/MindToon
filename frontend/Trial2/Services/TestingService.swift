import Foundation


typealias TestingHealthResponse = HealthResponse
typealias TestingComicRequest = ComicRequest


class TestingService {
    static let shared = TestingService()
    
    private let apiClient = APIClient.shared
    private var testResults: [TestResult] = []
    
    private init() {}
    
    // MARK: - Comic Generation Testing
    func testComicGeneration(concept: String) async throws -> Data {
        let request = TestingComicRequest(
            concept: concept,
            genre: "adventure",
            artStyle: "cartoon",
            includeDetailedScenario: false
        )
        
        let startTime = Date()
        
        do {
            let result = try await apiClient.testGenerateComic(request: request)
            
            let testResult = TestResult(
                testName: "Comic Generation",
                success: true,
                duration: Date().timeIntervalSince(startTime),
                details: "Generated comic for concept: '\(concept)'",
                dataSize: result.count
            )
            testResults.append(testResult)
            
            return result
            
        } catch {
            let testResult = TestResult(
                testName: "Comic Generation",
                success: false,
                duration: Date().timeIntervalSince(startTime),
                details: "Failed: \(error.localizedDescription)",
                error: error.localizedDescription
            )
            testResults.append(testResult)
            
            throw error
        }
    }
    

    func testBackendHealth() async throws -> TestingHealthResponse {
        let startTime = Date()
        
        do {
            let health = try await apiClient.testHealth()
            
            let testResult = TestResult(
                testName: "Backend Health",
                success: true,
                duration: Date().timeIntervalSince(startTime),
                details: "Status: \(health.status), Timestamp: \(health.timestamp)"
            )
            testResults.append(testResult)
            
            return health
            
        } catch {
            let testResult = TestResult(
                testName: "Backend Health",
                success: false,
                duration: Date().timeIntervalSince(startTime),
                details: "Health check failed",
                error: error.localizedDescription
            )
            testResults.append(testResult)
            
            throw error
        }
    }
    
    
    func runComprehensiveTests() async -> TestingSummary {
        let startTime = Date()
        var totalTests = 0
        var passedTests = 0
        var testErrors: [String] = []
        
        // Test 1: Backend Health
        do {
            _ = try await testBackendHealth()
            passedTests += 1
        } catch {
            testErrors.append("Health check failed: \(error.localizedDescription)")
        }
        totalTests += 1
        
        // Test 2: Basic Comic Generation
        do {
            _ = try await testComicGeneration(concept: "A simple test comic about friendship")
            passedTests += 1
        } catch {
            testErrors.append("Basic comic generation failed: \(error.localizedDescription)")
        }
        totalTests += 1
        
        // Test 3: Complex Comic Generation
        do {
            _ = try await testComicGeneration(concept: "A complex multi-character adventure with dragons, wizards, and epic battles across multiple kingdoms")
            passedTests += 1
        } catch {
            testErrors.append("Complex comic generation failed: \(error.localizedDescription)")
        }
        totalTests += 1
        
        // Test 4: Edge Case - Empty Concept
        do {
            _ = try await testComicGeneration(concept: "")
            testErrors.append("Empty concept should have failed but didn't")
        } catch {
            // This is expected to fail
            passedTests += 1
        }
        totalTests += 1
        
        // Test 5: Edge Case - Very Long Concept
        do {
            let longConcept = String(repeating: "This is a very long concept that should test the system's limits. ", count: 100)
            _ = try await testComicGeneration(concept: longConcept)
            passedTests += 1
        } catch {
            testErrors.append("Long concept test failed: \(error.localizedDescription)")
        }
        totalTests += 1
        
        // Test 6: Different Genres
        let genres = ["adventure", "comedy", "drama", "fantasy", "sci-fi"]
        for genre in genres {
            do {
                let request = TestingComicRequest(
                    concept: "A \(genre) story about friendship",
                    genre: genre,
                    artStyle: "cartoon",
                    includeDetailedScenario: false
                )
                _ = try await apiClient.testGenerateComic(request: request)
                passedTests += 1
            } catch {
                testErrors.append("Genre \(genre) test failed: \(error.localizedDescription)")
            }
            totalTests += 1
        }
        
        // Test 7: Different Art Styles
        let artStyles = ["cartoon", "realistic", "anime", "comic book", "watercolor"]
        for artStyle in artStyles {
            do {
                let request = TestingComicRequest(
                    concept: "A story with \(artStyle) art style",
                    genre: "adventure",
                    artStyle: artStyle,
                    includeDetailedScenario: false
                )
                _ = try await apiClient.testGenerateComic(request: request)
                passedTests += 1
            } catch {
                testErrors.append("Art style \(artStyle) test failed: \(error.localizedDescription)")
            }
            totalTests += 1
        }
        
        // Test 8: Detailed Scenario Generation
        do {
            let request = TestingComicRequest(
                concept: "A hero's journey with detailed character development",
                genre: "fantasy",
                artStyle: "comic book",
                includeDetailedScenario: true
            )
            _ = try await apiClient.testGenerateComic(request: request)
            passedTests += 1
        } catch {
            testErrors.append("Detailed scenario test failed: \(error.localizedDescription)")
        }
        totalTests += 1
        
        let totalDuration = Date().timeIntervalSince(startTime)
        
        let summary = TestingSummary(
            totalTests: totalTests,
            passedTests: passedTests,
            failedTests: totalTests - passedTests,
            totalDuration: totalDuration,
            errors: testErrors,
            timestamp: Date().ISO8601Format()
        )
        
        let summaryResult = TestResult(
            testName: "Comprehensive Test Suite",
            success: passedTests == totalTests,
            duration: totalDuration,
            details: "\(passedTests)/\(totalTests) tests passed"
        )
        testResults.append(summaryResult)
        
        return summary
    }
    
    // MARK: - Performance Testing
    func runPerformanceTests(iterations: Int = 5) async -> PerformanceTestResult {
        var durations: [TimeInterval] = []
        var successCount = 0
        
        for i in 1...iterations {
            let startTime = Date()
            
            do {
                _ = try await testComicGeneration(concept: "Performance test iteration \(i)")
                let duration = Date().timeIntervalSince(startTime)
                durations.append(duration)
                successCount += 1
            } catch {
                print("❌ Performance test iteration \(i) failed: \(error)")
            }
        }
        
        let averageDuration = durations.isEmpty ? 0 : durations.reduce(0, +) / Double(durations.count)
        let minDuration = durations.min() ?? 0
        let maxDuration = durations.max() ?? 0
        
        let result = PerformanceTestResult(
            iterations: iterations,
            successfulIterations: successCount,
            averageDuration: averageDuration,
            minDuration: minDuration,
            maxDuration: maxDuration,
            durations: durations
        )
        
        let testResult = TestResult(
            testName: "Performance Test (\(iterations) iterations)",
            success: successCount > 0,
            duration: durations.reduce(0, +),
            details: "Average: \(String(format: "%.2f", averageDuration))s, Success rate: \(successCount)/\(iterations)"
        )
        testResults.append(testResult)
        
        return result
    }
    
    // MARK: - Load Testing
    func runLoadTest(concurrentRequests: Int = 3) async -> LoadTestResult {
        let startTime = Date()
        var results: [Bool] = []
        
        await withTaskGroup(of: Bool.self) { group in
            for i in 1...concurrentRequests {
                group.addTask {
                    do {
                        _ = try await self.testComicGeneration(concept: "Load test request \(i)")
                        return true
                    } catch {
                        return false
                    }
                }
            }
            
            for await result in group {
                results.append(result)
            }
        }
        
        let totalDuration = Date().timeIntervalSince(startTime)
        let successCount = results.filter { $0 }.count
        
        let result = LoadTestResult(
            concurrentRequests: concurrentRequests,
            successfulRequests: successCount,
            totalDuration: totalDuration,
            requestsPerSecond: Double(successCount) / totalDuration
        )
        
        let testResult = TestResult(
            testName: "Load Test (\(concurrentRequests) concurrent)",
            success: successCount > 0,
            duration: totalDuration,
            details: "\(successCount)/\(concurrentRequests) successful, \(String(format: "%.2f", result.requestsPerSecond)) req/sec"
        )
        testResults.append(testResult)
        
        return result
    }
    
    // MARK: - Test Results Management
    func getTestResults() -> [TestResult] {
        return testResults
    }
    
    func clearTestResults() {
        testResults.removeAll()
    }
    
    func getTestSummary() -> TestResultSummary {
        let totalTests = testResults.count
        let passedTests = testResults.filter { $0.success }.count
        let failedTests = totalTests - passedTests
        let averageDuration = testResults.isEmpty ? 0 : testResults.reduce(0) { $0 + $1.duration } / Double(totalTests)
        
        return TestResultSummary(
            totalTests: totalTests,
            passedTests: passedTests,
            failedTests: failedTests,
            averageDuration: averageDuration,
            lastTestDate: testResults.last?.timestamp
        )
    }
    

    func exportTestResults() -> String {
        let summary = getTestSummary()
        var report = """
        MindToon Testing Report
        =====================
        Generated: \(Date().ISO8601Format())
        
        Summary:
        - Total Tests: \(summary.totalTests)
        - Passed: \(summary.passedTests)
        - Failed: \(summary.failedTests)
        - Success Rate: \(String(format: "%.1f", Double(summary.passedTests) / Double(summary.totalTests) * 100))%
        - Average Duration: \(String(format: "%.2f", summary.averageDuration))s
        
        Detailed Results:
        ================
        
        """
        
        for (index, result) in testResults.enumerated() {
            report += """
            Test \(index + 1): \(result.testName)
            Status: \(result.success ? "✅ PASSED" : "❌ FAILED")
            Duration: \(String(format: "%.2f", result.duration))s
            Details: \(result.details)
            \(result.error.map { "Error: \($0)" } ?? "")
            \(result.dataSize.map { "Data Size: \($0) bytes" } ?? "")
            Timestamp: \(result.timestamp)
            
            """
        }
        
        return report
    }
    

    func scheduleAutomatedTests(interval: TimeInterval = 3600) { // Default: every hour
        Timer.scheduledTimer(withTimeInterval: interval, repeats: true) { _ in
            Task {
                print("🤖 Running automated backend tests...")
                let summary = await self.runComprehensiveTests()
                
                if summary.failedTests > 0 {
                    print("⚠️ Automated tests detected issues:")
                    for error in summary.errors {
                        print("   - \(error)")
                    }
                }
            }
        }
    }
}


struct TestResult {
    let testName: String
    let success: Bool
    let duration: TimeInterval
    let details: String
    let error: String?
    let dataSize: Int?
    let timestamp: String
    
    init(testName: String, success: Bool, duration: TimeInterval, details: String, error: String? = nil, dataSize: Int? = nil) {
        self.testName = testName
        self.success = success
        self.duration = duration
        self.details = details
        self.error = error
        self.dataSize = dataSize
        self.timestamp = Date().ISO8601Format()
    }
}

struct TestingSummary {
    let totalTests: Int
    let passedTests: Int
    let failedTests: Int
    let totalDuration: TimeInterval
    let errors: [String]
    let timestamp: String
    
    var successRate: Double {
        guard totalTests > 0 else { return 0 }
        return Double(passedTests) / Double(totalTests) * 100
    }
}

struct PerformanceTestResult {
    let iterations: Int
    let successfulIterations: Int
    let averageDuration: TimeInterval
    let minDuration: TimeInterval
    let maxDuration: TimeInterval
    let durations: [TimeInterval]
    
    var successRate: Double {
        guard iterations > 0 else { return 0 }
        return Double(successfulIterations) / Double(iterations) * 100
    }
}

struct LoadTestResult {
    let concurrentRequests: Int
    let successfulRequests: Int
    let totalDuration: TimeInterval
    let requestsPerSecond: Double
    
    var successRate: Double {
        guard concurrentRequests > 0 else { return 0 }
        return Double(successfulRequests) / Double(concurrentRequests) * 100
    }
}

struct TestResultSummary {
    let totalTests: Int
    let passedTests: Int
    let failedTests: Int
    let averageDuration: TimeInterval
    let lastTestDate: String?
    
    var successRate: Double {
        guard totalTests > 0 else { return 0 }
        return Double(passedTests) / Double(totalTests) * 100
    }
}


#if DEBUG
extension TestResult {
    static let passedPreview = TestResult(
        testName: "Comic Generation",
        success: true,
        duration: 2.45,
        details: "Successfully generated comic for concept: 'A hero's adventure'",
        dataSize: 1024000
    )
    
    static let failedPreview = TestResult(
        testName: "Backend Health",
        success: false,
        duration: 0.12,
        details: "Health check endpoint unreachable",
        error: "Network connection failed"
    )
}

extension TestingSummary {
    static let preview = TestingSummary(
        totalTests: 15,
        passedTests: 12,
        failedTests: 3,
        totalDuration: 45.6,
        errors: [
            "Empty concept test failed: Network timeout",
            "Load test failed: Rate limit exceeded"
        ],
        timestamp: "2024-01-15T10:30:00Z"
    )
}

extension PerformanceTestResult {
    static let preview = PerformanceTestResult(
        iterations: 5,
        successfulIterations: 4,
        averageDuration: 2.34,
        minDuration: 1.87,
        maxDuration: 3.21,
        durations: [2.12, 1.87, 3.21, 2.45, 2.05]
    )
}
#endif 