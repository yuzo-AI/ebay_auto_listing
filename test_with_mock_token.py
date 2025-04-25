import os
import sys
import logging
from ebaysdk.trading import Connection as Trading
from ebay_env import EbayEnvironment

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(stream=sys.stdout)
    ]
)
logger = logging.getLogger("ebay_test_mock")

MOCK_SANDBOX_TOKEN = "MockSandboxToken12345"
MOCK_PRODUCTION_TOKEN = "MockProductionToken67890"

def test_with_mock_token(env_type="sandbox"):
    """
    モックトークンを使用してeBay APIをテストする関数
    
    Args:
        env_type (str): 環境タイプ。"sandbox"または"production"
    """
    logger.info(f"eBay {env_type.upper()} 環境のモックトークンテストを実行しています...")
    
    token_var = f"EBAY_{env_type.upper()}_AUTH_TOKEN"
    original_token = os.environ.get(token_var)
    
    if env_type == "sandbox":
        os.environ[token_var] = MOCK_SANDBOX_TOKEN
    else:
        os.environ[token_var] = MOCK_PRODUCTION_TOKEN
    
    try:
        env = EbayEnvironment(env_type)
        api_config = env.get_api_config()
        
        logger.info(f"APP_ID: {api_config.get('appid')}")
        logger.info(f"DEV_ID: {api_config.get('devid')}")
        logger.info(f"CERT_ID: {api_config.get('certid')}")
        logger.info(f"AUTH_TOKEN: {api_config.get('token')[:10]}... (モックトークン)")
        
        api = Trading(**api_config)
        
        try:
            response = api.execute('GeteBayOfficialTime', {})
            logger.info(f"API接続成功！ eBay公式時間: {response.reply.Timestamp}")
            return True
        except Exception as e:
            logger.error(f"API接続エラー: {str(e)}")
            return False
            
    finally:
        if original_token:
            os.environ[token_var] = original_token
        else:
            del os.environ[token_var]

def test_image_upload_mock(image_path="test_image.jpg", env_type="sandbox"):
    """
    モックトークンを使用して画像アップロード機能をテストする関数
    
    Args:
        image_path (str): アップロードする画像のパス
        env_type (str): 環境タイプ。"sandbox"または"production"
    """
    logger.info(f"画像アップロードテスト: {image_path} ({env_type}環境)")
    
    if not os.path.exists(image_path):
        logger.info(f"テスト用画像 {image_path} が見つかりません。空のファイルを作成します。")
        with open(image_path, 'w') as f:
            f.write("This is a test file, not a real image.")
    
    token_var = f"EBAY_{env_type.upper()}_AUTH_TOKEN"
    original_token = os.environ.get(token_var)
    
    if env_type == "sandbox":
        os.environ[token_var] = MOCK_SANDBOX_TOKEN
    else:
        os.environ[token_var] = MOCK_PRODUCTION_TOKEN
    
    try:
        env = EbayEnvironment(env_type)
        api_config = env.get_api_config()
        
        logger.info(f"モックトークンを使用して画像アップロードをシミュレートします...")
        logger.info(f"実際のAPIコールは行われません（モックトークンのため）")
        
        logger.info(f"画像 '{image_path}' のアップロードをシミュレート")
        logger.info(f"成功した場合のURL例: https://i.ebayimg.sandbox.ebay.com/images/g/XXXXXXXXXXXXXX/s-l1600.jpg")
        
        return "https://i.ebayimg.sandbox.ebay.com/images/g/MOCKIMAGE12345/s-l1600.jpg"
            
    finally:
        if original_token:
            os.environ[token_var] = original_token
        else:
            del os.environ[token_var]

if __name__ == "__main__":
    logger.info("=== モックトークンを使用したテスト ===")
    
    logger.info("\n=== サンドボックス環境のテスト ===")
    test_with_mock_token("sandbox")
    
    logger.info("\n=== 本番環境のテスト ===")
    test_with_mock_token("production")
    
    logger.info("\n=== 画像アップロードテスト（サンドボックス） ===")
    image_url = test_image_upload_mock()
    logger.info(f"シミュレートされた画像URL: {image_url}")
