# ebay_lister.py

import os
import time
import logging
import json
import sys
# typing に Optional を追加
from typing import Tuple, Dict, Any, Union, List, Optional
from ebaysdk.exception import ConnectionError
from ebaysdk.trading import Connection as Trading

from config import (
    EBAY_APP_ID, 
    EBAY_DEV_ID, 
    EBAY_CERT_ID, 
    EBAY_AUTH_TOKEN, 
    EBAY_LISTING_DEFAULTS,
    get_env_var
)
from ebay_env import EbayEnvironment

# ロガーの取得
logger = logging.getLogger("ebay_listing.ebay_api")

def validate_credentials() -> bool:
    """
    API認証情報の検証
    
    Returns:
        bool: 認証情報が有効かどうか
    """
    if not all([EBAY_APP_ID, EBAY_DEV_ID, EBAY_CERT_ID, EBAY_AUTH_TOKEN]):
        logger.error("eBay API認証情報が正しく設定されていません")
        return False
    return True

def _extract_error_message(errors) -> str:
    """
    エラーメッセージを抽出する補助関数
    
    Args:
        errors: APIからのエラーレスポンス
        
    Returns:
        str: フォーマットされたエラーメッセージ
    """
    if not errors:
        return "不明なエラー"
        
    if isinstance(errors, dict):
        # 単一エラーの場合
        error_code = errors.get('ErrorCode', 'Unknown')
        error_message = errors.get('LongMessage', 'Unknown error').replace('\xa0', ' ')
        return f"コード={error_code}, メッセージ={error_message}"
    elif isinstance(errors, list) and errors:
        # 複数エラーの場合
        error_codes = [err.get('ErrorCode', 'Unknown') for err in errors]
        error_messages = [err.get('LongMessage', 'Unknown error').replace('\xa0', ' ') for err in errors]
        return f"コード={', '.join(error_codes)}, メッセージ={', '.join(error_messages)}"
    else:
        return str(errors)

# --- 新しい関数: カテゴリID提案 ---
def get_suggested_category(title: str, environment: Optional[EbayEnvironment] = None) -> Optional[str]:
    """
    商品タイトルに基づいて、eBayにカテゴリIDを提案させる関数

    Args:
        title (str): 商品タイトル
        environment (EbayEnvironment, optional): eBay環境オブジェクト。Noneの場合は新しく作成。

    Returns:
        Optional[str]: 提案されたカテゴリIDのうち最初のもの。失敗した場合はNone。
    """
    if not validate_credentials():
        logger.error("カテゴリ提案API呼び出し前に認証情報エラー")
        return None

    try:
        env = environment or EbayEnvironment()
        api_config = env.get_api_config()
        
        env_name = "本番" if env.is_production() else "サンドボックス"
        logger.info(f"タイトル '{title}' に基づいてeBay {env_name} 環境でカテゴリIDを提案させています...")
        
        # APIに接続
        api = Trading(**api_config)
        response = api.execute('GetSuggestedCategories', {'Query': title})
        response_dict = response.dict()

        ack_status = response_dict.get('Ack', 'Failure')
        if ack_status == 'Failure':
            errors = response_dict.get('Errors', [])
            error_message = _extract_error_message(errors) # 以前追加した補助関数を使う
            logger.error(f"GetSuggestedCategories APIエラー: {error_message}")
            return None

        suggested_categories = response_dict.get('SuggestedCategoryArray', {}).get('SuggestedCategory', [])

        if not suggested_categories:
            logger.warning(f"タイトル '{title}' に対するカテゴリ提案が見つかりませんでした。")
            return None

        # suggested_categoriesが辞書の場合（候補が1つ）とリストの場合（複数）に対応
        first_category = None
        if isinstance(suggested_categories, list):
            first_category = suggested_categories[0]
        elif isinstance(suggested_categories, dict):
            first_category = suggested_categories
        else:
            logger.warning("予期しないカテゴリ提案の形式です。")
            return None

        category_id = first_category.get('Category', {}).get('CategoryID')

        if category_id:
            category_name = first_category.get('Category', {}).get('CategoryName', 'N/A')
            percent_match = first_category.get('PercentItemFound', 'N/A')
            logger.info(f"提案されたカテゴリID: {category_id} (名前: {category_name}, 一致率: {percent_match}%)")
            return category_id
        else:
            logger.warning("カテゴリ提案レスポンスにCategoryIDが含まれていません。")
            return None

    except ConnectionError as e:
        # エラーハンドリング
        logger.error(f"GetSuggestedCategories API接続エラーが発生しました: {e}")
        try:
            error_response = e.response.dict()
            errors = error_response.get('Errors', [])
            error_message = _extract_error_message(errors)
            logger.error(f"APIエラー詳細: {error_message}")
            return None
        except Exception as parse_error:
            logger.error(f"エラーレスポンスの解析中にさらにエラー: {parse_error}")
            return None
    except Exception as e:
        logger.exception(f"カテゴリ提案取得中に予期しないエラーが発生しました。", exc_info=True)
        return None

def upload_image_to_ebay(image_path: str, environment: Optional[EbayEnvironment] = None) -> Optional[str]:
    """
    eBayに画像をアップロードする関数
    
    Args:
        image_path (str): アップロードする画像のパス
        environment (EbayEnvironment, optional): eBay環境オブジェクト。Noneの場合は新しく作成。
        
    Returns:
        str: アップロードされた画像のURL。失敗した場合はNone。
    """
    logger.info(f"画像 '{image_path}' をeBayにアップロードしています...")
    
    if not validate_credentials():
        logger.error("API認証情報が無効です")
        return None

    try:
        if not os.path.exists(image_path):
            logger.error(f"画像ファイルが見つかりません: {image_path}")
            return None
            
        env = environment or EbayEnvironment()
        api_config = env.get_api_config()
        
        api = Trading(**api_config)
        
        logger.info(f"画像 '{image_path}' をアップロードしています...")
        
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        request_data = {
            'PictureName': os.path.basename(image_path),
            'PictureData': image_data
        }
        
        response = api.execute('UploadSiteHostedPictures', request_data)
        
        # 成功した場合
        response_dict = response.dict()
        
        site_hosted_picture_details = response_dict.get('SiteHostedPictureDetails', {})
        full_url = site_hosted_picture_details.get('FullURL')
        
        if full_url:
            logger.info(f"画像のアップロードに成功しました。URL: {full_url}")
            return full_url
        else:
            logger.error("画像URLが見つかりません")
            return None
            
    except ConnectionError as e:
        # APIエラーの場合
        logger.error(f"eBay API接続エラー: {str(e)}")
        try:
            error_response = e.response.dict()
            errors = error_response.get('Errors', [])
            error_message = _extract_error_message(errors)
            logger.error(f"APIエラー詳細: {error_message}")
        except Exception:
            pass
        return None
    except Exception as e:
        # その他のエラー
        logger.error(f"画像アップロード中に予期しないエラーが発生しました: {str(e)}")
        return None

# --- 既存関数の修正: list_item_on_ebay ---
def list_item_on_ebay(title: str,
                      category_id: Optional[str] = None,
                      item_specifics: List[Dict[str, str]] = None,
                      picture_urls: List[str] = None,
                      environment: Optional[EbayEnvironment] = None) -> Tuple[bool, str]:
    """
    eBayに商品を出品する関数
    
    Args:
        title (str): 出品するアイテムのタイトル
        category_id (Optional[str], optional): 使用するカテゴリID。Noneの場合はconfigのデフォルト値を使用。
        item_specifics (List[Dict[str, str]], optional): カスタムのItem Specifics。Noneの場合はデフォルト値を使用。
        picture_urls (List[str], optional): 商品画像のURL。Noneの場合はデフォルト値を使用。
        environment (EbayEnvironment, optional): eBay環境オブジェクト。Noneの場合は新しく作成。
        
    Returns:
        Tuple[bool, str]: (成功したかどうかのブール値, アイテムIDまたはエラーメッセージ)
    """
    if not validate_credentials():
        return False, "API認証情報が無効です"

    try:
        env = environment or EbayEnvironment()
        api_config = env.get_api_config()
        
        env_name = "本番" if env.is_production() else "サンドボックス"
        logger.debug(f"eBay {env_name} 環境のTrading APIに接続しています...")
        
        # APIに接続
        api = Trading(**api_config)
        
        # カテゴリIDの決定
        target_category_id = category_id # 引数で渡されたIDを優先
        if not target_category_id:
            # 引数で渡されなかったら、configのデフォルト値を使用
            target_category_id = EBAY_LISTING_DEFAULTS.get("category_id")
            if not target_category_id:
                logger.error("configにcategory_idが設定されておらず、引数も指定されていません。")
                return False, "設定エラー: category_idがありません。"
            logger.info(f"引数でカテゴリIDが指定されなかったため、デフォルト値を使用します: {target_category_id}")
        else:
            logger.info(f"引数で指定されたカテゴリIDを使用します: {target_category_id}")
            
        # Item Specificsの準備
        name_value_list = []
        
        # configからのデフォルトItem Specificsを追加
        default_specifics = EBAY_LISTING_DEFAULTS.get("item_specifics", [])
        if default_specifics:
            name_value_list.extend(default_specifics)
            
        # 引数で渡されたカスタムItem Specificsがあれば追加（上書き）
        if item_specifics:
            # 重複する名前のItem Specificsは上書き
            existing_names = [item.get("Name") for item in name_value_list]
            for specific in item_specifics:
                name = specific.get("Name")
                if name in existing_names:
                    # 同名の項目を削除
                    name_value_list = [item for item in name_value_list if item.get("Name") != name]
                # 新しい項目を追加
                name_value_list.append(specific)
        
        # リクエストパラメータの作成
        logger.debug(f"出品リクエストを作成しています。タイトル: {title}, カテゴリID: {target_category_id}")
        request_data = {
            'Item': {
                'Title': title,
                'Description': EBAY_LISTING_DEFAULTS.get("description", "No description provided."),
                'PrimaryCategory': {'CategoryID': target_category_id},
                'StartPrice': EBAY_LISTING_DEFAULTS.get("price", "9.99"),
                'Country': EBAY_LISTING_DEFAULTS.get("country", "US"),
                'Currency': EBAY_LISTING_DEFAULTS.get("currency", "USD"),
                'DispatchTimeMax': EBAY_LISTING_DEFAULTS.get("dispatch_time_max", 3),
                'ListingDuration': EBAY_LISTING_DEFAULTS.get("listing_duration", "GTC"),
                'ListingType': 'FixedPriceItem',
                'Quantity': EBAY_LISTING_DEFAULTS.get("quantity", 1),
                'ReturnPolicy': {
                    'ReturnsAcceptedOption': 'ReturnsAccepted',
                    'RefundOption': 'MoneyBack',
                    'ReturnsWithinOption': 'Days_30',
                    'ShippingCostPaidByOption': 'Buyer'
                },
                'ShippingDetails': {
                    'ShippingType': 'Flat',
                    'ShippingServiceOptions': {
                        'ShippingServicePriority': '1',
                        'ShippingService': EBAY_LISTING_DEFAULTS.get("shipping_service", "USPSMedia"),
                        'ShippingServiceCost': EBAY_LISTING_DEFAULTS.get("shipping_cost", "2.00")
                    }
                },
                'Site': 'US',
                'PostalCode': '95125'
            }
        }
        
        # Item Specificsを追加（存在する場合のみ）
        if name_value_list:
            request_data['Item']['ItemSpecifics'] = {'NameValueList': name_value_list}

        # 画像URLの設定
        image_urls = picture_urls if picture_urls else ['https://via.placeholder.com/300x200']
        request_data['Item']['PictureDetails'] = {'PictureURL': image_urls}
        
        # ConditionIDがあれば追加（一部のカテゴリでは非対応）
        condition_id = EBAY_LISTING_DEFAULTS.get("condition_id")
        if condition_id:
            request_data['Item']['ConditionID'] = condition_id
            
        # APIリクエストを送信
        logger.debug("eBay APIにリクエストを送信しています...")
        response = api.execute('AddItem', request_data)
        
        # 成功した場合
        response_dict = response.dict()
        item_id = response_dict.get('ItemID')
        if not item_id:
            logger.warning("APIレスポンスにItemIDが含まれていません")
            return False, "APIレスポンスにItemIDが含まれていません"
            
        logger.info(f"商品が正常に出品されました。ItemID: {item_id}")
        return True, item_id
    
    except ConnectionError as e:
        # APIエラーの場合
        try:
            error_response = e.response.dict()
            # Unicode文字のエスケープを防ぐためにensure_ascii=Falseを指定
            error_detail = json.dumps(error_response, indent=2, ensure_ascii=False)
            logger.error(f"eBay API接続エラー: {error_detail}")
            
            errors = error_response.get('Errors', [])
            error_message = _extract_error_message(errors)
            return False, f"eBay APIエラー: {error_message}"
        except Exception as parse_error:
            logger.error(f"エラーレスポンスのパース中にエラーが発生しました: {str(parse_error)}")
            return False, f"eBay API接続エラー: {str(e)}"
    
    except Exception as e:
        # その他のエラー
        logger.error(f"出品処理中に予期しないエラーが発生しました: {str(e)}")
        return False, f"エラーが発生しました: {str(e)}"

if __name__ == "__main__":
    # テスト用コード
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("ebay_test.log", encoding='utf-8'),
            logging.StreamHandler(stream=sys.stdout)
        ]
    )
    
    # カテゴリIDの提案をテスト
    test_title = "Alya anime figure collectible"
    logger.info(f"タイトル '{test_title}' に基づくカテゴリ提案をテストします")
    
    suggested_category = get_suggested_category(test_title)
    if suggested_category:
        logger.info(f"提案されたカテゴリID: {suggested_category}")
    else:
        logger.warning("カテゴリ提案が取得できませんでした")
    
    # 出品をテスト
    logger.info(f"'{test_title}'を出品テストします")
    success, result = list_item_on_ebay(
        test_title,
        category_id=suggested_category,
        item_specifics=[
            {"Name": "Character", "Value": "Alya"},
            {"Name": "Type", "Value": "Figure"}
        ]
    )
    
    if success:
        print(f"出品成功: アイテムID = {result}")
    else:
        print(f"出品失敗: {result}")
