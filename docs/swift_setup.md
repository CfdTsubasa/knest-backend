# SwiftUI開発セットアップガイド

## 1. Info.plistの設定

ローカル開発環境でAPIを使用するために、以下の設定を追加してください：

```xml
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <true/>
    <key>NSExceptionDomains</key>
    <dict>
        <key>localhost</key>
        <dict>
            <key>NSExceptionAllowsInsecureHTTPLoads</key>
            <true/>
            <key>NSIncludesSubdomains</key>
            <true/>
        </dict>
    </dict>
</dict>
```

## 2. APIクライアントの実装例

```swift
import Foundation

enum APIError: Error {
    case invalidURL
    case networkError(Error)
    case invalidResponse
    case decodingError(Error)
}

class APIClient {
    static let shared = APIClient()
    private let baseURL = "http://localhost:8000/api"
    private var token: String?
    
    func setToken(_ token: String) {
        self.token = token
    }
    
    func request<T: Decodable>(
        endpoint: String,
        method: String = "GET",
        body: Data? = nil
    ) async throws -> T {
        guard let url = URL(string: "\(baseURL)\(endpoint)") else {
            throw APIError.invalidURL
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = method
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        if let token = token {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        
        if let body = body {
            request.httpBody = body
        }
        
        do {
            let (data, response) = try await URLSession.shared.data(for: request)
            
            guard let httpResponse = response as? HTTPURLResponse,
                  (200...299).contains(httpResponse.statusCode) else {
                throw APIError.invalidResponse
            }
            
            let decoder = JSONDecoder()
            decoder.keyDecodingStrategy = .convertFromSnakeCase
            return try decoder.decode(T.self, from: data)
        } catch let error as DecodingError {
            throw APIError.decodingError(error)
        } catch {
            throw APIError.networkError(error)
        }
    }
}

// 使用例：
struct CircleResponse: Codable {
    let id: String
    let name: String
    let description: String
    let iconUrl: String?
    let coverUrl: String?
    let memberCount: Int
    let postCount: Int
    let lastActivity: Date
}

// サークル一覧を取得
func fetchCircles() async throws -> [CircleResponse] {
    let response: PaginatedResponse<CircleResponse> = try await APIClient.shared.request(endpoint: "/circles/circles/")
    return response.results
}
```

## 3. WebSocket接続の実装例

```swift
import Foundation

class WebSocketManager: ObservableObject {
    private var webSocket: URLSessionWebSocketTask?
    private let baseURL = "ws://localhost:8000/ws"
    
    @Published var messages: [ChatMessage] = []
    @Published var isConnected = false
    
    func connect(to circleId: String) {
        guard let url = URL(string: "\(baseURL)/circle/\(circleId)/chat/") else { return }
        
        let session = URLSession(configuration: .default)
        webSocket = session.webSocketTask(with: url)
        
        webSocket?.resume()
        isConnected = true
        receiveMessage()
    }
    
    func disconnect() {
        webSocket?.cancel(with: .normalClosure, reason: nil)
        isConnected = false
    }
    
    private func receiveMessage() {
        webSocket?.receive { [weak self] result in
            switch result {
            case .success(let message):
                switch message {
                case .string(let text):
                    if let data = text.data(using: .utf8),
                       let chatMessage = try? JSONDecoder().decode(ChatMessage.self, from: data) {
                        DispatchQueue.main.async {
                            self?.messages.append(chatMessage)
                        }
                    }
                default:
                    break
                }
                self?.receiveMessage()
            case .failure(let error):
                print("WebSocket error: \(error)")
                self?.isConnected = false
            }
        }
    }
    
    func send(message: String) {
        let messageData = [
            "type": "message",
            "content": message
        ]
        
        if let jsonData = try? JSONEncoder().encode(messageData),
           let jsonString = String(data: jsonData, encoding: .utf8) {
            webSocket?.send(.string(jsonString)) { error in
                if let error = error {
                    print("Error sending message: \(error)")
                }
            }
        }
    }
}

// 使用例：
class ChatViewModel: ObservableObject {
    @Published private(set) var messages: [ChatMessage] = []
    private let webSocketManager = WebSocketManager()
    
    func connect(to circleId: String) {
        webSocketManager.connect(to: circleId)
    }
    
    func sendMessage(_ content: String) {
        webSocketManager.send(message: content)
    }
}
```

## 4. 開発時の注意点

1. **ネットワーク設定**
   - macOSのファイアウォール設定で、必要なポートを開放してください
   - シミュレーターでテストする場合は、`localhost`を使用できます
   - 実機でテストする場合は、同じWiFiネットワーク上でDjangoサーバーのIPアドレスを指定してください

2. **セキュリティ**
   - 開発時のみ`NSAllowsArbitraryLoads`を使用し、本番環境では適切なSSL証明書を使用してください
   - APIキーやトークンは`Keychain`に保存することを推奨します

3. **エラーハンドリング**
   - ネットワークエラー
   - WebSocket接続の切断
   - トークンの有効期限切れ
   - デコードエラー
   などの適切なエラーハンドリングを実装してください 