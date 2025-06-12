# Comment Connector Module

DiscordとGitHubのコメント/チャットを相互運用できるようにするbotモジュール

## 機能

### GitHub → Discord 通知
- Githubの指定されたorganizationのリポジトリのイベントをDiscordのチャンネルに通知
  - Issue作成、コメント、プルリクエスト作成、その他通知etc
- IssueやPRはスレッド化して管理
- レビューコメントやレビュー結果の通知

### Discord → GitHub コメント投稿
- DiscordでissueやPRのスレッドにbotへメンションしてコメントを送信すると、GitHubのissueやPRにコメントを投稿
- ユーザー紐づけ機能により、GitHubのメンションとDiscordのメンションを相互変換

### ユーザー・チャンネル管理
- GithubのユーザーとDiscordのユーザーを紐づけて、メンションを相互変換
- GitHubリポジトリとDiscordチャンネルを紐づけて通知先を設定

## セットアップ

### 1. 環境変数設定

`.env`ファイルに以下の設定を追加：

```env
# GitHub Personal Access Token (repo権限が必要)
GITHUB_TOKEN=your_github_personal_access_token

# GitHub Organization/User name
GITHUB_ORGANIZATION=your_github_org_or_username

# WebHook受信ポート (デフォルト: 8000)
WEBHOOK_PORT=8000
```

### 2. GitHub WebHook設定

GitHubリポジトリの設定でWebHookを追加：

- Payload URL: `http://your-server:8000/webhook/github`
- Content type: `application/json`
- Events: `Issues`, `Issue comments`, `Pull requests`, `Pull request reviews`, `Pull request review comments`

### 3. Discord側設定

1. **チャンネル紐づけ**: GitHubリポジトリと通知先Discordチャンネルを紐づけ
   ```
   /link_channel repo_name #channel
   ```

2. **ユーザー紐づけ**: GitHubユーザーとDiscordユーザーを紐づけ
   ```
   /link_user github_username @discord_user
   ```

## 使用方法

### スラッシュコマンド

#### `/link_channel <repo_name> [channel]`
GitHubリポジトリとDiscordチャンネルを紐づけ

- `repo_name`: GitHubリポジトリ名
- `channel`: 通知先チャンネル（省略時は現在のチャンネル）

#### `/link_user <github_username> [discord_user]`
GitHubユーザーとDiscordユーザーを紐づけ

- `github_username`: GitHubユーザー名
- `discord_user`: Discordユーザー（省略時は実行者）

#### `/unlink_user <github_username>`
GitHubユーザーとDiscordユーザーの紐づけを解除

#### `/connector_status`
現在の設定状況を表示

### Discord → GitHub コメント投稿

1. GitHubでIssueまたはPRが作成されると、Discordのチャンネルに通知とスレッドが作成される
2. スレッド内でbotにメンションしてコメントを送信
3. botがGitHub側にコメントを投稿し、✅リアクションで確認

例：
```
@bot これはDiscordからのコメントです
```

## WebHookイベント対応表

| GitHubイベント | Discord通知 | スレッド作成 |
|---|---|---|
| Issue opened | ✅ | ✅ |
| Issue closed | ✅ | - |
| Issue comment created | ✅ | - |
| Pull request opened | ✅ | ✅ |
| Pull request closed/merged | ✅ | - |
| Pull request review submitted | ✅ | - |
| Pull request review comment created | ✅ | - |

## ファイル構成

```
comment_connecter/
├── __init__.py          # モジュール初期化
├── comment_connecter.py # メイン機能
├── utils.py            # ユーティリティ関数
├── exceptions.py       # 例外クラス
├── README.md           # このファイル
└── test_comment_connecter.py # テストファイル
```

## トラブルシューティング

### GitHub API エラー
- `GITHUB_TOKEN`が正しく設定されているか確認
- トークンに`repo`権限があるか確認
- Organization/リポジトリへのアクセス権限を確認

### WebHook が受信されない
- `WEBHOOK_PORT`設定を確認
- ファイアウォール設定を確認
- GitHubのWebHook設定でPayload URLが正しいか確認

### Discord通知が来ない
- チャンネル紐づけが正しく設定されているか確認（`/connector_status`で確認）
- botに該当チャンネルへの書き込み権限があるか確認

### スレッドでのコメント投稿が失敗する
- GitHub APIトークンの権限を確認
- スレッドがGitHubのissue/PRに対応しているか確認