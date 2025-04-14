import os
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# Google Sheetsの設定
SPREADSHEET_ID = "15hBsS4XTVit5Su_a0BnIzgdfvQF0aNaCg6pjPnun8pM"
SHEET_NAME = "test"
CELL_RANGE = "A2"
GOOGLE_CREDENTIALS_FILE = "auto-sales-input-2b5d0118f65a.json"

# eBay APIの設定
EBAY_APP_ID = os.getenv("EBAY_APP_ID")
EBAY_DEV_ID = os.getenv("EBAY_DEV_ID")
EBAY_CERT_ID = os.getenv("EBAY_CERT_ID")
EBAY_AUTH_TOKEN = os.getenv("EBAY_AUTH_TOKEN")

# eBay出品の基本情報（ダミー値）
EBAY_LISTING_DEFAULTS = {
    "currency": "USD",
    "price": "10.00",
    "quantity": 1,
    "listing_duration": "GTC",  # Good Til Cancelled - 固定価格リスティングで必須
    "country": "US",
    "location": "San Jose, CA",
    # payment_methodsは削除（マネージドペイメント対応）
    "description": "This is a test item listed via eBay API.",
    "category_id": "38323",  # Toys & Hobbies > Action Figures > Anime & Manga - リーフカテゴリIDに修正
    "condition_id": "1000",  # New - 商品状態は必須項目
    "dispatch_time_max": 3,  # 3 business days handling time
    "shipping_service": "USPSMedia",
    "shipping_cost": "2.00",
    # Item Specificsの追加
    "item_specifics": [
        {"Name": "Brand", "Value": "Unbranded"},
        {"Name": "Type", "Value": "Action Figure"},
        {"Name": "Character", "Value": "Alya"}
    ]
} 