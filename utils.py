import os
import logging
import requests
from typing import Optional

logger = logging.getLogger("ebay_listing.utils")

def download_image_from_url(url: str, save_dir: str = "images") -> Optional[str]:
    """
    URLから画像をダウンロードして保存する関数
    
    Args:
        url (str): 画像のURL
        save_dir (str, optional): 保存先ディレクトリ
        
    Returns:
        Optional[str]: 保存されたファイルのパス。失敗した場合はNone。
    """
    try:
        os.makedirs(save_dir, exist_ok=True)
        
        filename = os.path.basename(url.split('?')[0])
        if not filename:
            filename = f"image_{hash(url)}.jpg"
        
        save_path = os.path.join(save_dir, filename)
        
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        logger.info(f"画像をダウンロードしました: {url} -> {save_path}")
        return save_path
        
    except requests.exceptions.RequestException as e:
        logger.error(f"画像のダウンロード中にリクエストエラーが発生しました: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"画像のダウンロード中に予期しないエラーが発生しました: {str(e)}")
        return None
