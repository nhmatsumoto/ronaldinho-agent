# Ronaldinho-Agent 🚀（オープンソース版）

> [!IMPORTANT]
> **コードネームに関する注意**: 「Ronaldinho-Agent」は現在プロジェクトのコードネームです。正式な製品名ではありません。

- [English (EN)](README.md)
- [Português (PT-BR)](README_pt-br.md)

Ronaldinho-Agent は、以下で構成される自律型エンジニアリング基盤です。
- **.NET 9 NeuralCore**（API/オーケストレーション）
- **.NET Bridge ワーカー**（Telegram 連携）
- **React + Vite + Chakra UI ConfigUI**
- **Keycloak + Postgres**（OIDC 認証）

この README は日本語版の概要ガイドです。

---

## 1. アーキテクチャ

1. **NeuralCore**（`services/Ronaldinho.NeuralCore`）
   - メイン API（`http://localhost:5000`）
   - ルート `.env` とローカル Vault を読み込み
   - `/api/settings` 系を JWT/OIDC で保護

2. **Bridge**（`services/Ronaldinho.Bridge`）
   - Telegram 連携ワーカー
   - トークンはローカル secrets または環境変数から取得
   - **最近の変更**: トークンがない場合でも安全に起動し、Telegram ポーリングジョブを登録しません。

3. **ConfigUI**（`services/Ronaldinho.ConfigUI`）
   - 管理 UI（開発時 `http://localhost:5173`）
   - Keycloak OIDC ログイン
   - **最近の変更**: 認証後のみ設定取得。API エラーをモック成功で隠しません。

4. **Keycloak + Postgres**
   - 認証/認可の基盤

---

## 2. 前提条件

- .NET SDK 9.0
- Node.js 18+
- Docker / Docker Compose
- Git

---

## 3. 環境変数（`.env`）

リポジトリには現在 `.env.example` がありません。ルートに `.env` を手動作成してください。

```env
GEMINI_API_KEY=
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
TELEGRAM_BOT_TOKEN=
LLM_PROVIDER=gemini
ENABLE_AUTO_FALLBACK=true
ALLOW_LOCAL_TOOLS=false

AUTH_AUTHORITY=http://localhost:8080/realms/ronaldinho
AUTH_AUDIENCE=account

VITE_AUTH_AUTHORITY=http://localhost:8080/realms/ronaldinho
VITE_AUTH_CLIENT_ID=configui-client
VITE_AUTH_REDIRECT_URI=http://localhost:5173
VITE_API_BASE_URL=http://localhost:5000/api

DB_NAME=keycloak
DB_USER=keycloak
DB_PASSWORD=password
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=admin
KC_HOSTNAME=localhost
```

---

## 4. 実行方法

### クイック起動

Linux/macOS:

```bash
chmod +x start_neural.sh ./dev_scripts/*.sh
./start_neural.sh
```

Windows (PowerShell):

```powershell
./start_neural.ps1
```

### サービス別起動

```bash
# NeuralCore
dotnet run --project services/Ronaldinho.NeuralCore/Ronaldinho.NeuralCore.csproj

# Bridge
dotnet run --project services/Ronaldinho.Bridge/Ronaldinho.Bridge.csproj

# ConfigUI
cd services/Ronaldinho.ConfigUI
npm install
npm run dev
```

### Docker 起動

```bash
docker compose up -d --build
```

---

## 5. 開発チェック

```bash
# Backend
dotnet build services/Ronaldinho.NeuralCore/Ronaldinho.NeuralCore.csproj
dotnet build services/Ronaldinho.Bridge/Ronaldinho.Bridge.csproj

# Frontend
cd services/Ronaldinho.ConfigUI
npm run lint
npm run build
```

---

## 6. セキュリティ

- `.env`、API キー、トークンをコミットしない
- `SECURITY.md` と `docs/security_model.md` を参照

---

## 7. 参考ドキュメント

- `docs/architecture.md`
- `docs/security_model.md`
- `CONTRIBUTING.md`

ライセンス: **MIT**（`LICENSE`）
