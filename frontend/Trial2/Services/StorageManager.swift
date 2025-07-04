import Foundation
import Combine

// MARK: - Storage Manager
@MainActor
class StorageManager: ObservableObject {
    static let shared = StorageManager()
    
    // Published properties
    @Published var storageUsage: StorageUsage?
    @Published var uploadProgress: [String: Double] = [:]
    @Published var isUploading: Bool = false
    @Published var errorMessage: String?
    
    // Private properties
    private let apiClient = APIClient.shared
    private var cancellables: Set<AnyCancellable> = []
    
    // Constants
    private let bucketName = "comic-images"
    private let maxFileSize: Int64 = 10 * 1024 * 1024 // 10MB
    private let allowedExtensions = ["png", "jpg", "jpeg", "webp"]
    
    private init() {}
    
    // MARK: - Storage Usage
    func loadStorageUsage() async {
        do {
            let token = await AuthManager.shared.getStoredToken()
            guard let token = token else {
                throw APIError.unauthorized
            }
            
            let usage = try await apiClient.getStorageUsage(token: token)
            storageUsage = usage
            
            print("✅ Storage usage loaded: \(usage.usedBytes) / \(usage.limitBytes) bytes")
            
        } catch {
            ErrorLogger.shared.log(
                error as? APIError ?? APIError.networkError(error),
                context: "loadStorageUsage"
            )
            errorMessage = (error as? APIError)?.userFriendlyMessage ?? error.localizedDescription
        }
    }
    
    // MARK: - File Upload
    func uploadComicImage(
        imageData: Data,
        fileName: String,
        comicId: Int,
        onProgress: @escaping (Double) -> Void = { _ in }
    ) async throws -> String {
        
        // Validate file size
        guard imageData.count <= maxFileSize else {
            throw APIError.validationError(["File size exceeds 10MB limit"])
        }
        
        // Validate file extension
        let fileExtension = (fileName as NSString).pathExtension.lowercased()
        guard allowedExtensions.contains(fileExtension) else {
            throw APIError.validationError(["Unsupported file format. Use PNG, JPG, JPEG, or WebP"])
        }
        
        isUploading = true
        errorMessage = nil
        
        do {
            let token = await AuthManager.shared.getStoredToken()
            guard let token = token else {
                throw APIError.unauthorized
            }
            
            let uploadRequest = StorageUploadRequest(
                fileName: fileName,
                bucketName: bucketName,
                imageData: imageData,
                comicId: comicId,
                contentType: getContentType(for: fileExtension)
            )
            
            let response = try await apiClient.uploadFile(request: uploadRequest, token: token)
            
            // Update storage usage
            await loadStorageUsage()
            
            // Clear progress
            uploadProgress.removeValue(forKey: fileName)
            
            print("✅ Successfully uploaded \(fileName) to \(response.publicUrl)")
            return response.publicUrl
            
        } catch {
            uploadProgress.removeValue(forKey: fileName)
            
            ErrorLogger.shared.log(
                error as? APIError ?? APIError.networkError(error),
                context: "uploadComicImage - \(fileName)"
            )
            
            throw error
        }
        
        isUploading = false
    }
    
    // MARK: - File Download
    func downloadComicImage(url: String) async throws -> Data {
        do {
            let token = await AuthManager.shared.getStoredToken()
            guard let token = token else {
                throw APIError.unauthorized
            }
            
            return try await apiClient.downloadFile(url: url, token: token)
            
        } catch {
            ErrorLogger.shared.log(
                error as? APIError ?? APIError.networkError(error),
                context: "downloadComicImage - \(url)"
            )
            throw error
        }
    }
    
    // MARK: - File Management
    func deleteComicImage(url: String) async throws {
        do {
            let token = await AuthManager.shared.getStoredToken()
            guard let token = token else {
                throw APIError.unauthorized
            }
            
            try await apiClient.deleteFile(url: url, token: token)
            
            // Update storage usage
            await loadStorageUsage()
            
            print("✅ Successfully deleted image: \(url)")
            
        } catch {
            ErrorLogger.shared.log(
                error as? APIError ?? APIError.networkError(error),
                context: "deleteComicImage - \(url)"
            )
            throw error
        }
    }
    
    func deleteComicImages(for comicId: Int) async throws {
        do {
            let token = await AuthManager.shared.getStoredToken()
            guard let token = token else {
                throw APIError.unauthorized
            }
            
            try await apiClient.deleteFiles(comicId: comicId, token: token)
            
            // Update storage usage
            await loadStorageUsage()
            
            print("✅ Successfully deleted all images for comic \(comicId)")
            
        } catch {
            ErrorLogger.shared.log(
                error as? APIError ?? APIError.networkError(error),
                context: "deleteComicImages - comic \(comicId)"
            )
            throw error
        }
    }
    
    // MARK: - Storage Cleanup
    func cleanupOrphanedImages() async throws -> StorageCleanupResult {
        do {
            let token = await AuthManager.shared.getStoredToken()
            guard let token = token else {
                throw APIError.unauthorized
            }
            
            let result = try await apiClient.cleanupStorage(token: token)
            
            // Update storage usage
            await loadStorageUsage()
            
            print("✅ Cleanup completed: \(result.deletedFiles) files removed, \(result.freedBytes) bytes freed")
            return result
            
        } catch {
            ErrorLogger.shared.log(
                error as? APIError ?? APIError.networkError(error),
                context: "cleanupOrphanedImages"
            )
            throw error
        }
    }
    
    func optimizeStorage() async throws -> StorageOptimizationResult {
        do {
            let token = await AuthManager.shared.getStoredToken()
            guard let token = token else {
                throw APIError.unauthorized
            }
            
            let result = try await apiClient.optimizeStorage(token: token)
            
            // Update storage usage
            await loadStorageUsage()
            
            print("✅ Storage optimization completed: \(result.compressedImages) images compressed, \(result.freedBytes) bytes saved")
            return result
            
        } catch {
            ErrorLogger.shared.log(
                error as? APIError ?? APIError.networkError(error),
                context: "optimizeStorage"
            )
            throw error
        }
    }
    
    // MARK: - Utility Methods
    private func getContentType(for fileExtension: String) -> String {
        switch fileExtension {
        case "png": return "image/png"
        case "jpg", "jpeg": return "image/jpeg"
        case "webp": return "image/webp"
        default: return "image/png"
        }
    }
    
    func isStorageQuotaExceeded() -> Bool {
        guard let usage = storageUsage else { return false }
        return usage.usedBytes >= usage.limitBytes
    }
    
    func getStorageUsagePercentage() -> Double {
        guard let usage = storageUsage, usage.limitBytes > 0 else { return 0 }
        return Double(usage.usedBytes) / Double(usage.limitBytes) * 100
    }
    
    func getRemainingStorage() -> Int64 {
        guard let usage = storageUsage else { return 0 }
        return max(0, usage.limitBytes - usage.usedBytes)
    }
    
    func formatBytes(_ bytes: Int64) -> String {
        let formatter = ByteCountFormatter()
        formatter.allowedUnits = [.useKB, .useMB, .useGB]
        formatter.countStyle = .file
        return formatter.string(fromByteCount: bytes)
    }
    
    func canUploadFile(size: Int64) -> Bool {
        guard let usage = storageUsage else { return false }
        return (usage.usedBytes + size) <= usage.limitBytes
    }
    
    func clearError() {
        errorMessage = nil
    }
    
    // MARK: - Background Tasks
    func scheduleCleanup() async {
        // This could be used to schedule periodic cleanup tasks
        print("📅 Scheduling background storage cleanup...")
        
        // Example: Clean up orphaned images every week
        Timer.scheduledTimer(withTimeInterval: 7 * 24 * 60 * 60, repeats: true) { _ in
            Task {
                do {
                    _ = try await self.cleanupOrphanedImages()
                } catch {
                    print("❌ Scheduled cleanup failed: \(error)")
                }
            }
        }
    }
}

// MARK: - Storage Models
struct StorageUsage: Codable {
    let usedBytes: Int64
    let limitBytes: Int64
    let fileCount: Int
    let lastUpdated: String
    
    enum CodingKeys: String, CodingKey {
        case usedBytes = "used_bytes"
        case limitBytes = "limit_bytes"
        case fileCount = "file_count"
        case lastUpdated = "last_updated"
    }
    
    var usagePercentage: Double {
        guard limitBytes > 0 else { return 0 }
        return Double(usedBytes) / Double(limitBytes) * 100
    }
    
    var remainingBytes: Int64 {
        return max(0, limitBytes - usedBytes)
    }
}

struct StorageUploadRequest: Codable {
    let fileName: String
    let bucketName: String
    let imageData: Data
    let comicId: Int
    let contentType: String
    
    enum CodingKeys: String, CodingKey {
        case fileName = "file_name"
        case bucketName = "bucket_name"
        case imageData = "image_data"
        case comicId = "comic_id"
        case contentType = "content_type"
    }
}

struct StorageUploadResponse: Codable {
    let fileName: String
    let publicUrl: String
    let fileSize: Int64
    let uploadedAt: String
    
    enum CodingKeys: String, CodingKey {
        case fileName = "file_name"
        case publicUrl = "public_url"
        case fileSize = "file_size"
        case uploadedAt = "uploaded_at"
    }
}

struct StorageCleanupResult: Codable {
    let deletedFiles: Int
    let freedBytes: Int64
    let processedAt: String
    
    enum CodingKeys: String, CodingKey {
        case deletedFiles = "deleted_files"
        case freedBytes = "freed_bytes"
        case processedAt = "processed_at"
    }
}

struct StorageOptimizationResult: Codable {
    let compressedImages: Int
    let freedBytes: Int64
    let processedAt: String
    
    enum CodingKeys: String, CodingKey {
        case compressedImages = "compressed_images"
        case freedBytes = "freed_bytes"
        case processedAt = "processed_at"
    }
}

// MARK: - Preview Data
#if DEBUG
extension StorageUsage {
    static let preview = StorageUsage(
        usedBytes: 150 * 1024 * 1024, // 150MB
        limitBytes: 500 * 1024 * 1024, // 500MB
        fileCount: 47,
        lastUpdated: "2024-01-15T10:30:00Z"
    )
    
    static let nearLimitPreview = StorageUsage(
        usedBytes: 480 * 1024 * 1024, // 480MB
        limitBytes: 500 * 1024 * 1024, // 500MB
        fileCount: 156,
        lastUpdated: "2024-01-15T14:20:00Z"
    )
}

extension StorageCleanupResult {
    static let preview = StorageCleanupResult(
        deletedFiles: 12,
        freedBytes: 25 * 1024 * 1024, // 25MB
        processedAt: "2024-01-15T10:30:00Z"
    )
}

extension StorageOptimizationResult {
    static let preview = StorageOptimizationResult(
        compressedImages: 28,
        freedBytes: 45 * 1024 * 1024, // 45MB
        processedAt: "2024-01-15T10:30:00Z"
    )
}
#endif 
