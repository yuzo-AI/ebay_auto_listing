import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("ebay_listing.ebay_env")

class EbayEnvironment:
    """
    eBay環境設定を管理するクラス
    サンドボックスと本番環境の切り替えを容易にする
    """
    
    def __init__(self, env_type: str = "sandbox"):
        """
        初期化
        
        Args:
            env_type (str): 環境タイプ。"sandbox"または"production"
        """
        self.env_type = env_type.lower()
        if self.env_type not in ["sandbox", "production"]:
            logger.warning(f"不明な環境タイプ: {env_type}。サンドボックス環境を使用します。")
            self.env_type = "sandbox"
            
        self.prefix = f"EBAY_{self.env_type.upper()}_"
        self.credentials = self._load_credentials()
        self.domain = "api.sandbox.ebay.com" if self.env_type == "sandbox" else "api.ebay.com"
        
        logger.info(f"eBay {self.env_type.upper()} 環境を使用します。ドメイン: {self.domain}")
    
    def _load_credentials(self) -> Dict[str, str]:
        """
        環境変数から認証情報を読み込む
        
        Returns:
            Dict[str, str]: 認証情報の辞書
        """
        credentials = {
            "appid": os.environ.get(f"{self.prefix}APP_ID", ""),
            "devid": os.environ.get(f"{self.prefix}DEV_ID", ""),
            "certid": os.environ.get(f"{self.prefix}CERT_ID", ""),
            "token": os.environ.get(f"{self.prefix}AUTH_TOKEN", "")
        }
        
        missing_creds = [key for key, value in credentials.items() if not value]
        if missing_creds:
            logger.error(f"以下の認証情報が不足しています: {', '.join(missing_creds)}")
        else:
            logger.debug("すべての認証情報が設定されています")
            
        return credentials
    
    def get_api_config(self) -> Dict[str, Any]:
        """
        API設定を取得
        
        Returns:
            Dict[str, Any]: API設定の辞書
        """
        return {
            "domain": self.domain,
            "appid": self.credentials["appid"],
            "devid": self.credentials["devid"],
            "certid": self.credentials["certid"],
            "token": self.credentials["token"],
            "config_file": None
        }
    
    def is_sandbox(self) -> bool:
        """
        サンドボックス環境かどうかを確認
        
        Returns:
            bool: サンドボックス環境の場合はTrue
        """
        return self.env_type == "sandbox"
    
    def is_production(self) -> bool:
        """
        本番環境かどうかを確認
        
        Returns:
            bool: 本番環境の場合はTrue
        """
        return self.env_type == "production"
    
    def validate_credentials(self) -> bool:
        """
        認証情報が有効かどうかを確認
        
        Returns:
            bool: 認証情報が有効な場合はTrue
        """
        return all(self.credentials.values())

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    sandbox_env = EbayEnvironment("sandbox")
    print(f"サンドボックス環境の設定: {sandbox_env.get_api_config()}")
    
    production_env = EbayEnvironment("production")
    print(f"本番環境の設定: {production_env.get_api_config()}")
