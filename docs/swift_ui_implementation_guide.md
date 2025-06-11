# Swift UI 実装ガイド

## 1. 環境セットアップ

### 必要なツール
```bash
# OpenAPI Generator のインストール
brew install openapi-generator

# SwiftLint（コード品質管理）
brew install swiftlint

# Swift Package Manager（依存関係管理）
# Xcodeに同梱
```

### 推奨ライブラリ
```swift
dependencies: [
    .package(url: "https://github.com/Alamofire/Alamofire.git", .upToNextMajor(from: "5.0.0")),
    .package(url: "https://github.com/kishikawakatsumi/KeychainAccess.git", .upToNextMajor(from: "4.0.0")),
    .package(url: "https://github.com/SwiftyJSON/SwiftyJSON.git", .upToNextMajor(from: "5.0.0"))
]
```

## 2. プロジェクト構造

```
KnestApp/
├── Sources/
│   ├── API/            # 自動生成されるAPIクライアント
│   ├── Models/         # データモデル
│   ├── Views/          # UI コンポーネント
│   │   ├── Auth/      # 認証関連
│   │   ├── Profile/   # プロフィール
│   │   ├── Interest/  # 興味関連
│   │   ├── Chat/      # メッセージ
│   │   └── Common/    # 共通コンポーネント
│   ├── ViewModels/    # ビジネスロジック
│   ├── Services/      # ユーティリティ
│   └── Config/        # 設定
└── Tests/             # テストコード
```

## 3. APIクライアント生成手順

1. OpenAPI仕様書の生成
```bash
# Django側で実行
python manage.py generateschema > openapi.yaml
```

2. Swift コード生成
```bash
openapi-generator generate -i openapi.yaml \
  -g swift5 \
  -o KnestApp/Sources/API \
  --additional-properties=responseAs=AsyncAwait
```

## 4. 実装順序

1. 基本設定
   - プロジェクト作成
   - 依存関係の設定
   - 環境変数の設定（開発/本番）

2. 認証フロー
   ```swift
   // AuthManager.swift
   class AuthManager: ObservableObject {
       @Published var isAuthenticated = false
       @Published var currentUser: User?
       
       func login(username: String, password: String) async throws {
           // ログイン処理
       }
       
       func logout() {
           // ログアウト処理
       }
   }
   ```

3. 基本的なビュー
   - ログイン画面
   - サインアップ画面
   - プロフィール画面
   - 興味一覧画面

4. データモデル
   ```swift
   // Interest.swift
   struct Interest: Identifiable, Codable {
       let id: UUID
       let name: String
       let description: String?
       let category: InterestCategory
       let isOfficial: Bool
       
       enum InterestCategory: String, Codable {
           case hobby = "hobby"
           case lifestyle = "lifestyle"
           case emotion = "emotion"
           case skill = "skill"
       }
   }
   ```

## 5. 画面仕様

### ログイン画面
```swift
struct LoginView: View {
    @StateObject private var viewModel = LoginViewModel()
    
    var body: some View {
        VStack {
            TextField("ユーザー名", text: $viewModel.username)
            SecureField("パスワード", text: $viewModel.password)
            Button("ログイン") {
                Task {
                    await viewModel.login()
                }
            }
        }
    }
}
```

### プロフィール画面
```swift
struct ProfileView: View {
    @StateObject private var viewModel = ProfileViewModel()
    
    var body: some View {
        List {
            Section("基本情報") {
                TextField("表示名", text: $viewModel.displayName)
                TextField("自己紹介", text: $viewModel.bio)
            }
            
            Section("興味") {
                ForEach(viewModel.interests) { interest in
                    InterestRow(interest: interest)
                }
            }
        }
    }
}
```

## 6. エラーハンドリング

```swift
enum AppError: LocalizedError {
    case network(String)
    case authentication(String)
    case validation(String)
    case unexpected(String)
    
    var errorDescription: String? {
        switch self {
        case .network(let message): return "ネットワークエラー: \(message)"
        case .authentication(let message): return "認証エラー: \(message)"
        case .validation(let message): return "入力エラー: \(message)"
        case .unexpected(let message): return "予期せぬエラー: \(message)"
        }
    }
}
```

## 7. テスト実装

```swift
import XCTest
@testable import KnestApp

final class ProfileViewModelTests: XCTestCase {
    var viewModel: ProfileViewModel!
    
    override func setUp() {
        super.setUp()
        viewModel = ProfileViewModel()
    }
    
    func testUpdateProfile() async throws {
        // テストケース
    }
}
```

## 8. セキュリティ対策

1. キーチェーンでの認証情報保存
```swift
import KeychainAccess

class SecurityManager {
    static let shared = SecurityManager()
    private let keychain = Keychain(service: "com.knest.app")
    
    func saveToken(_ token: String) {
        keychain["authToken"] = token
    }
}
```

2. SSL証明書のピンニング
```swift
class APIClient {
    private let session: URLSession = {
        let configuration = URLSessionConfiguration.default
        configuration.urlCredentialStorage = nil
        return URLSession(configuration: configuration,
                         delegate: CertificatePinningDelegate(),
                         delegateQueue: nil)
    }()
}
```

## 9. パフォーマンス最適化

1. 画像キャッシュ
```swift
final class ImageCache {
    static let shared = ImageCache()
    private let cache = NSCache<NSString, UIImage>()
    
    func image(for url: URL) -> UIImage? {
        cache.object(forKey: url.absoluteString as NSString)
    }
}
```

2. ページネーション
```swift
final class PaginatedList<T: Identifiable>: ObservableObject {
    @Published private(set) var items: [T] = []
    private var currentPage = 1
    
    func loadNextPage() async throws {
        // ページネーション処理
    }
}
```

## 10. アクセシビリティ

```swift
extension View {
    func accessibilitySupport() -> some View {
        self
            .accessibilityLabel("説明的なラベル")
            .accessibilityHint("操作方法のヒント")
            .accessibilityValue("現在の値")
    }
}
```

## 11. デプロイメント

1. ビルド設定
   - Development
   - Staging
   - Production

2. 環境変数
```swift
enum Environment {
    static let apiBaseURL: URL = {
        #if DEBUG
        return URL(string: "http://localhost:8000")!
        #else
        return URL(string: "https://api.knest.app")!
        #endif
    }()
}
```

## 12. CI/CD設定

```yaml
# .github/workflows/ios.yml
name: iOS CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: macos-latest
    steps:
    - uses: actions/checkout@v2
    - name: Build
      run: xcodebuild -scheme KnestApp -destination 'platform=iOS Simulator,name=iPhone 14'
    - name: Test
      run: xcodebuild test -scheme KnestApp -destination 'platform=iOS Simulator,name=iPhone 14'
``` 