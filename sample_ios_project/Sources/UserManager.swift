import Foundation

/// Manages user-related operations
public class UserManager {
    private let networkService: NetworkService
    private let cacheService: CacheService
    private(set) var currentUser: User?
    
    public init(networkService: NetworkService, cacheService: CacheService) {
        self.networkService = networkService
        self.cacheService = cacheService
    }
    
    /// Fetches a user by ID
    public func fetchUser(id: String) async throws -> User {
        if let cached = cacheService.get(key: id) {
            currentUser = cached
            return cached
        }
        let user = try await networkService.get("/users/\(id)")
        cacheService.set(key: id, value: user)
        currentUser = user
        return user
    }
    
    /// Updates user profile
    public func updateProfile(name: String, email: String) async throws -> User {
        guard let user = currentUser else {
            throw UserManagerError.noCurrentUser
        }
        let updated = try await networkService.put("/users/\(user.id)", body: ["name": name, "email": email])
        currentUser = updated
        return updated
    }
    
    /// Logs out the current user
    public func logout() {
        currentUser = nil
        cacheService.clear()
    }
}

enum UserManagerError: Error {
    case noCurrentUser
    case invalidResponse
    case networkTimeout
}

/// Protocol for network operations
public protocol NetworkService {
    func get(_ path: String) async throws -> User
    func put(_ path: String, body: [String: String]) async throws -> User
}

/// Protocol for caching operations
public protocol CacheService {
    func get(key: String) -> User?
    func set(key: String, value: User)
    func clear()
}

struct User: Codable {
    let id: String
    var name: String
    var email: String
}