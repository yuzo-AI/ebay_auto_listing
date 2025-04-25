import os
import logging
import sys
from ebaysdk.trading import Connection as Trading
from ebay_env import EbayEnvironment

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(stream=sys.stdout)
    ]
)
logger = logging.getLogger("ebay_creds_check")

def check_ebay_credentials(env_type="sandbox"):
    """
    eBay API認証情報をチェックする関数
    
    Args:
        env_type (str): 環境タイプ。"sandbox"または"production"
    """
    logger.info(f"eBay {env_type.upper()} 環境の認証情報をチェックしています...")
    
    env = EbayEnvironment(env_type)
    api_config = env.get_api_config()
    
    logger.info(f"APP_ID: {api_config.get('appid')}")
    logger.info(f"DEV_ID: {api_config.get('devid')}")
    logger.info(f"CERT_ID: {api_config.get('certid')}")
    token = api_config.get('token', '')
    if token:
        logger.info(f"AUTH_TOKEN: {token[:10]}... (最初の10文字のみ表示)")
    else:
        logger.warning("AUTH_TOKENが設定されていません")
    
    try:
        api = Trading(**api_config)
        
        response = api.execute('GeteBayOfficialTime', {})
        
        logger.info(f"API接続成功！ eBay公式時間: {response.reply.Timestamp}")
        return True
        
    except Exception as e:
        logger.error(f"API接続エラー: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("=== サンドボックス環境のチェック ===")
    check_ebay_credentials("sandbox")
    
    logger.info("\n=== 本番環境のチェック ===")
    check_ebay_credentials("production")
