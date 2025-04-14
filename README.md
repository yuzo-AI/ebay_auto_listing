# eBay自動出品ツール

Google スプレッドシートからデータを読み込み、eBay Sandboxに商品を自動で出品するPythonツールです。タイトルに基づいたカテゴリID自動提案機能付き。

## 機能

- Google スプレッドシートからアイテムタイトルを読み込み
- 読み込んだタイトルに基づいてeBay APIからカテゴリIDを自動提案
- カスタムItem Specificsの自動設定
- eBay Sandboxへの商品出品
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

## インストール

1. リポジトリをクローン:
```bash
git clone https://github.com/yourusername/ebay-listing-tool.git
cd ebay-listing-tool
```

2. 必要なライブラリをインストール:
```bash
pip install -r requirements.txt
```

3. 設定ファイルを準備:
   - `.env.example` を `.env` にコピーし、eBay API認証情報を設定
   - Google API用のサービスアカウントキーファイルを配置

## 設定方法

### 1. eBay API設定

1. [eBay Developer Program](https://developer.ebay.com)に登録
2. アプリケーションを作成し、Sandbox環境のキーを取得
3. `.env`ファイルに以下の情報を設定:

```
EBAY_APP_ID=your_app_id
EBAY_DEV_ID=your_dev_id
EBAY_CERT_ID=your_cert_id
EBAY_AUTH_TOKEN=your_auth_token
```

### 2. Google Sheets API設定

1. [Google Cloud Console](https://console.cloud.google.com/)でプロジェクト作成
2. Google Sheets APIを有効化
3. サービスアカウントを作成し、JSONキーをダウンロード
4. JSONキーファイルをプロジェクトディレクトリに配置
5. `config.py`内の`GOOGLE_CREDENTIALS_FILE`を設定
6. 対象のスプレッドシートをサービスアカウントと共有

### 3. 出品設定のカスタマイズ

`config.py`内の`EBAY_LISTING_DEFAULTS`を編集して、出品する商品の基本情報を設定できます:

- カテゴリID
- 価格
- 配送方法
- 商品説明
- Item Specifics

## 使用方法

```bash
python main.py
```

成功すると、ターミナルとログファイル`ebay_listing.log`に結果が表示されます。

## ファイル構成

- `main.py`: メインプログラム
- `ebay_lister.py`: eBay API操作モジュール
- `google_sheets_reader.py`: Google Sheets連携モジュール
- `config.py`: 設定ファイル
- `.env`: API認証情報（作成必須）

## 注意事項

- このプログラムはeBay Sandboxのみで動作確認しています
- 本番環境で使用する場合は`ebay_lister.py`内のドメイン設定を変更してください
- API認証情報は`.env`ファイルで管理し、リポジトリにコミットしないでください
- カテゴリIDはeBayのカテゴリ体系に合わせて更新する必要があります

## ライセンス

MIT

## 開発者

Your Name 