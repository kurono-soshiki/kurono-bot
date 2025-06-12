# Comment Connector Usage Guide

## 設定手順

### 1. 環境変数の設定

`.env`ファイルを作成し、以下の設定を追加：

```env
# Discord Bot Token
DISCORD_TOKEN=your_discord_bot_token_here

# GitHub Personal Access Token (repo権限が必要)
GITHUB_TOKEN=your_github_personal_access_token

# GitHub Organization name
GITHUB_ORGANIZATION=kurono-soshiki

# Discord設定
DISCORD_GUILD_ID=your_discord_server_id
DISCORD_CATEGORY_ID=your_discord_category_id

# WebHook設定
WEBHOOK_PORT=8000
```

### 2. GitHub Personal Access Tokenの作成

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. "Generate new token (classic)"をクリック
3. 以下の権限を選択：
   - `repo` (Full control of private repositories)
   - `read:org` (Read org and team membership, read org projects)
4. トークンを生成してコピー

### 3. GitHub WebHookの設定

各リポジトリで以下の設定：

1. Repository → Settings → Webhooks → Add webhook
2. Payload URL: `http://your-server-ip:8000/webhook/github`
3. Content type: `application/json`
4. Events: 以下を選択
   - Issues
   - Issue comments  
   - Pull requests
   - Pull request reviews
   - Pull request review comments
5. Active にチェックを入れて保存

### 4. Discord Bot権限

Bot に以下の権限を付与：

- Send Messages
- Create Public Threads
- Send Messages in Threads
- Use Slash Commands
- Add Reactions
- Read Message History

## 使用方法

### 初期設定コマンド

```
# リポジトリとチャンネルを紐づけ
/link_channel test-repo #github-notifications

# ユーザーを紐づけ  
/link_user your-github-username @your-discord-user

# 設定状況確認
/connector_status
```

### 通常の使用

1. GitHubでIssueやPRを作成すると、Discordに通知とスレッドが作成される
2. スレッド内でbotにメンション `@bot コメント内容` でGitHubにコメント投稿
3. GitHub側でコメントが追加されると、Discord側にも通知される

## トラブルシューティング

### よくある問題

1. **WebHookが受信されない**
   - ポート8000が開いているか確認
   - GitHubのWebHook設定のPayload URLが正しいか確認
   - ファイアウォール設定を確認

2. **GitHub APIエラー**
   - GITHUB_TOKENが正しく設定されているか確認
   - トークンに必要な権限があるか確認

3. **Discord通知が来ない**
   - /link_channel でリポジトリとチャンネルが紐づけされているか確認
   - Botにチャンネルへの書き込み権限があるか確認

4. **コメント投稿が失敗する**
   - スレッドがGitHubのissue/PRに対応しているか確認
   - GitHub APIの権限を確認

### ログの確認

```bash
# Botの実行ログを確認
poetry run python src/main.py

# テストの実行
poetry run python scripts/test_comment_connector.py
```
