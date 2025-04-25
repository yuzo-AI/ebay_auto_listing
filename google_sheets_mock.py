import os
import logging
import sys
from typing import Optional, List, Dict, Any, Union
import json

logger = logging.getLogger("ebay_listing.google_sheets_mock")

def read_spreadsheet_data_mock(row_index: Optional[int] = None) -> Union[Dict[str, str], List[Dict[str, str]], None]:
    """
    Google Sheetsからのデータ読み込みをモックする関数
    実際のAPIコールを行わずにテスト用のデータを返す
    
    Args:
        row_index (int, optional): 読み取る行のインデックス。Noneの場合は全行を取得
        
    Returns:
        Union[Dict[str, str], List[Dict[str, str]], None]: 
            単一行の場合は辞書、複数行の場合は辞書のリスト
    """
    logger.info("モックデータを使用してGoogle Sheetsからのデータ読み込みをシミュレートします")
    
    mock_data = [
        {
            "Item name": "Alya anime figure collectible",
            "image": "https://example.com/images/alya_figure.jpg",
            "Description": "Beautiful Alya anime figure from popular series",
            "Price": "29.99",
            "Quantity": "1",
            "CategoryID": "38323",
            "Brand": "Anime Collectibles",
            "Condition": "New"
        },
        {
            "Item name": "Manga collection volume 1-10",
            "image": "https://example.com/images/manga_collection.jpg",
            "Description": "Complete manga collection volumes 1-10",
            "Price": "99.99",
            "Quantity": "3",
            "CategoryID": "29792",
            "Brand": "Manga Press",
            "Condition": "Like New"
        },
        {
            "Item name": "Gaming keyboard mechanical RGB",
            "image": "https://example.com/images/keyboard.jpg",
            "Description": "RGB mechanical gaming keyboard with custom switches",
            "Price": "79.99",
            "Quantity": "5",
            "CategoryID": "33963",
            "Brand": "GamerTech",
            "Condition": "New"
        }
    ]
    
    if row_index is not None:
        if 0 <= row_index < len(mock_data):
            logger.info(f"モックデータから行 {row_index} を返します")
            return mock_data[row_index]
        else:
            logger.warning(f"指定された行 {row_index} はモックデータの範囲外です")
            return None
    
    logger.info(f"モックデータから {len(mock_data)} 行を返します")
    return mock_data

def patch_google_sheets_reader():
    """
    google_sheets_reader モジュールをモック関数でパッチする
    """
    import sys
    import google_sheets_reader
    
    original_read_spreadsheet_data = google_sheets_reader.read_spreadsheet_data
    
    google_sheets_reader.read_spreadsheet_data = read_spreadsheet_data_mock
    
    logger.info("google_sheets_reader.read_spreadsheet_data をモック関数で置き換えました")
    
    return original_read_spreadsheet_data

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(stream=sys.stdout)
        ]
    )
    
    all_data = read_spreadsheet_data_mock()
    print(f"全行のデータ: {len(all_data)} 行")
    
    row_data = read_spreadsheet_data_mock(row_index=0)
    print(f"行 0 のデータ: {row_data['Item name']}")
