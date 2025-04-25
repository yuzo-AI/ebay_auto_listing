import os
import logging
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

logger = logging.getLogger("ebay_listing.config")

DEFAULT_ENVIRONMENT = "sandbox"  # デフォルトはサンドボックス環境

# Google Sheetsの設定
SPREADSHEET_ID = os.getenv("GOOGLE_SHEET_ID", "15hBsS4XTVit5Su_a0BnIzgdfvQF0aNaCg6pjPnun8pM")
SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "sales-tast-page")
CELL_RANGE = "A2"
GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH", "auto-sales-input-2b5d0118f65a.json")

def get_env_var(var_name, env_type=None):
    """
    指定された環境タイプに基づいて環境変数を取得する
    
    Args:
        var_name (str): 環境変数名（"APP_ID", "DEV_ID", "CERT_ID", "AUTH_TOKEN"など）
        env_type (str, optional): 環境タイプ。"sandbox"または"production"
                                 Noneの場合はDEFAULT_ENVIRONMENTを使用
    
    Returns:
        str: 環境変数の値
    """
    if env_type is None:
        env_type = os.getenv("EBAY_ENVIRONMENT", DEFAULT_ENVIRONMENT)
        
    prefix = f"EBAY_{env_type.upper()}_"
    return os.getenv(f"{prefix}{var_name}")

def get_current_environment():
    """
    現在の環境タイプを取得する
    
    Returns:
        str: 環境タイプ（"sandbox"または"production"）
    """
    return os.getenv("EBAY_ENVIRONMENT", DEFAULT_ENVIRONMENT)

# eBay APIの設定（後方互換性のため）
EBAY_APP_ID = get_env_var("APP_ID")
EBAY_DEV_ID = get_env_var("DEV_ID")
EBAY_CERT_ID = get_env_var("CERT_ID")
EBAY_AUTH_TOKEN = get_env_var("AUTH_TOKEN")

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