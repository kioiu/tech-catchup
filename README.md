# Tech Catchup

初心者〜若手エンジニアが、朝の3〜5分で「今日見るべき情報」を選べる、GitHub Pages向けの軽量なテックニュースまとめです。Vanilla HTML/CSS/JavaScriptで動作し、ニュースは`data/news.json`から読み込みます。

## ローカル実行

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/fetch_news.py
python -m http.server 8000
```

ブラウザで http://localhost:8000/ を開きます。`file://`ではJSON取得が制限されるため、HTTPサーバーを使ってください。

## ニュース取得

`scripts/fetch_news.py`がRSS、Hacker News公式Firebase API、Xを順に取得します。RSSは`scripts/sources/rss.py`、Hacker Newsは`scripts/sources/hackernews.py`、Xは`scripts/sources/x.py`に分離しています。RSS/HNの一部が失敗しても他の取得とJSON生成は継続し、Xは認証情報がない・APIが失敗した場合もスキップします。

RSSソースを増やす場合は、`RSS_SOURCES`に`表示名: RSS URL`を追加してください。記事はタイトル・URLで重複除去され、80件まで保存されます。

## X取得設定

X API v2のBearer Tokenを、リポジトリの Settings → Secrets and variables → Actions → New repository secret から`X_BEARER_TOKEN`として登録します。検索条件を変える場合はActions variableの`X_QUERY`に設定できます。トークンはサーバー側のActionsだけで使い、ブラウザへ渡しません。Xを設定しなくてもRSS/HN更新は動作します。

## beginner_scoreとカテゴリ

`scripts/fetch_news.py`上部の`BEGINNER_KEYWORDS`でキーワードと加点を変更できます。`CATEGORIES`でカテゴリ判定語を変更できます。ランキングは初心者スコアに新しさを加味しています。

## GitHub Actions / Pages

`.github/workflows/update-news.yml`は毎日UTC 21:30（日本時間06:30）に実行され、`workflow_dispatch`から手動実行もできます。Actionsが`data/news.json`を更新してコミットします。

GitHubリポジトリの Settings → Pages で Source を「GitHub Actions」に設定してください。静的ファイルは相対パスで参照しているため、Project Pages（`https://USERNAME.github.io/tech-catchup/`）でも動作します。Actionsがコミットするには、ワークフローの`contents: write`権限が必要です。

## 必要なSecrets

- 必須: なし（RSS/Hacker Newsのみで稼働）
- 任意: `X_BEARER_TOKEN`（X API v2）
- 任意: `X_QUERY`（Actions Variable。Secretではありません）
