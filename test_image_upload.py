import os
import logging
import sys
from ebaysdk.trading import Connection as Trading
from ebaysdk.exception import ConnectionError

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(stream=sys.stdout)
    ]
)
logger = logging.getLogger("ebay_image_upload")

def upload_image_to_ebay(image_path, env_type="sandbox"):
    """
    eBayに画像をアップロードする関数
    
    Args:
        image_path (str): アップロードする画像のパス
        env_type (str): 環境タイプ。"sandbox"または"production"
        
    Returns:
        str: アップロードされた画像のURL。失敗した場合はNone。
    """
    logger.info(f"eBay {env_type.upper()} 環境に画像をアップロードしています...")
    
    prefix = f"EBAY_{env_type.upper()}_"
    
    app_id = os.environ.get(f"{prefix}APP_ID")
    dev_id = os.environ.get(f"{prefix}DEV_ID")
    cert_id = os.environ.get(f"{prefix}CERT_ID")
    auth_token = os.environ.get(f"{prefix}AUTH_TOKEN")
    
    if not all([app_id, dev_id, cert_id, auth_token]):
        logger.error("eBay API認証情報が不足しています")
        return None
    
    domain = "api.sandbox.ebay.com" if env_type == "sandbox" else "api.ebay.com"
    
    try:
        if not os.path.exists(image_path):
            logger.error(f"画像ファイルが見つかりません: {image_path}")
            return None
            
        api = Trading(
            domain=domain,
            appid=app_id,
            devid=dev_id,
            certid=cert_id,
            token=auth_token,
            config_file=None
        )
        
        logger.info(f"画像 '{image_path}' をアップロードしています...")
        
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        request_data = {
            'PictureName': os.path.basename(image_path),
            'PictureData': image_data
        }
        
        response = api.execute('UploadSiteHostedPictures', request_data)
        
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
        logger.error(f"eBay API接続エラー: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"画像アップロード中に予期しないエラーが発生しました: {str(e)}")
        return None

if __name__ == "__main__":
    test_image_path = "test_image.jpg"
    
    image_url = upload_image_to_ebay(test_image_path, "sandbox")
    
    if image_url:
        print(f"アップロードされた画像のURL: {image_url}")
    else:
        print("画像のアップロードに失敗しました")
