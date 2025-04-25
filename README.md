# eBay自動出品ツール

Google スプレッドシートからデータを読み込み、eBayに商品を自動で出品するPythonツールです。サンドボックス環境と本番環境の両方に対応しています。

## 機能

- Google スプレッドシートから複数商品データを読み込み
- 読み込んだタイトルに基づいてeBay APIからカテゴリIDを自動提案
- 画像URLまたはローカルパスからの画像アップロード
- カスタムItem Specificsの自動設定
- サンドボックス環境と本番環境の切り替え
- 複数商品の一括処理
- リトライ機能付き
- 詳細なログ記録

## 必要条件

- Python 3.8以上
- 以下のPythonライブラリ:
  - `ebaysdk`
  - `google-api-python-client`
  - `google-auth-httplib2`
  - `google-auth-oauthlib`
  - `python-dotenv`
  - `requests`

## インストール

1. リポジトリをクローン:
```bash
git clone https://github.com/yuzo-AI/ebay_auto_listing.git
cd ebay_auto_listing
```

2. 必要なライブラリをインストール:
```bash
pip install -r requirements.txt
```

3. 設定ファイルを準備:
   - `.env.example` を `.env` にコピーし、eBay API認証情報とGoogle Sheets設定を入力
   - Google API用のサービスアカウントキーファイルを配置

## 設定方法

### 1. eBay API設定

1. [eBay Developer Program](https://developer.ebay.com)に登録
2. アプリケーションを作成し、Sandbox環境と本番環境のキーを取得
3. `.env`ファイルに以下の情報を設定:

```
# eBay サンドボックス環境用
EBAY_SANDBOX_APP_ID=your_sandbox_app_id
EBAY_SANDBOX_DEV_ID=your_sandbox_dev_id
EBAY_SANDBOX_CERT_ID=your_sandbox_cert_id
EBAY_SANDBOX_AUTH_TOKEN=your_sandbox_auth_token

# eBay 本番環境用
EBAY_PRODUCTION_APP_ID=your_production_app_id
EBAY_PRODUCTION_DEV_ID=your_production_dev_id
EBAY_PRODUCTION_CERT_ID=your_production_cert_id
EBAY_PRODUCTION_AUTH_TOKEN=your_production_auth_token

# 環境設定（sandbox または production）
EBAY_ENVIRONMENT=sandbox
```

### 2. Google Sheets API設定

1. [Google Cloud Console](https://console.cloud.google.com/)でプロジェクト作成
2. Google Sheets APIを有効化
3. サービスアカウントを作成し、JSONキーをダウンロード
4. JSONキーファイルをプロジェクトディレクトリに配置
5. `.env`ファイルに以下の情報を設定:

```
GOOGLE_SHEETS_CREDENTIALS_PATH=path/to/your/credentials.json
GOOGLE_SHEET_ID=your_spreadsheet_id
GOOGLE_SHEET_NAME=sales-tast-page
```

6. 対象のスプレッドシートをサービスアカウントと共有

### 3. Google スプレッドシートの構造

スプレッドシートは以下の列構造を持つ必要があります:

- `Item name`: 商品タイトル（必須）
- `image`: 画像URL/パス（カンマ区切りで複数指定可能）
- `Description`: 商品説明
- `Price`: 価格
- `Quantity`: 数量
- `CategoryID`: カテゴリID（空の場合は自動取得を試みます）

その他の列は自動的にItem Specificsとして処理されます。

### 4. 出品設定のカスタマイズ

`config.py`内の`EBAY_LISTING_DEFAULTS`を編集して、出品する商品の基本情報を設定できます:

- カテゴリID
- 価格
- 配送方法
- 商品説明
- Item Specifics

## 使用方法

### 基本的な使用方法

```bash
# サンドボックス環境で実行（デフォルト）
python main.py

# 本番環境で実行
python main.py --env production

# 特定の行のみ処理（0から始まる行番号）
python main.py --row 0

# 本番環境で特定の行のみ処理
python main.py --env production --row 0
```

成功すると、ターミナルとログファイル`ebay_listing.log`に結果が表示されます。

## ファイル構成

- `main.py`: メインプログラム
- `ebay_lister.py`: eBay API操作モジュール
- `google_sheets_reader.py`: Google Sheets連携モジュール
- `ebay_env.py`: eBay環境管理モジュール
- `utils.py`: ユーティリティ関数（画像ダウンロードなど）
- `config.py`: 設定ファイル
- `.env`: API認証情報（作成必須）

## 注意事項

### 本番環境に関する重要な注意事項

- **出品手数料**: 本番環境では出品手数料が発生する可能性があります
- **アカウントへの影響**: 本番環境での操作はセラーアカウントの評価に直接影響します
- **意図しない購入**: 本番の出品はすぐに購入される可能性があります
- **安全性**: 本番環境で実行する前に、必ずサンドボックス環境でテストしてください

### その他の注意事項

- API認証情報は`.env`ファイルで管理し、リポジトリにコミットしないでください
- カテゴリIDはeBayのカテゴリ体系に合わせて更新する必要があります
- 画像URLが正しく設定されていることを確認してください
- 本番環境で実行する場合は、`--env production`オプションを明示的に指定してください

## ライセンス

MIT

## 開発者

yuzo-AI
