import os
import sys
import logging
import json
from google_sheets_reader import read_spreadsheet_data

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(stream=sys.stdout)
    ]
)
logger = logging.getLogger("google_sheets_test")

def test_google_sheets_connection():
    """
    Google Sheets APIへの接続をテストする関数
    """
    logger.info("Google Sheets APIへの接続をテストしています...")
    
    creds_path = os.environ.get('GOOGLE_SHEETS_CREDENTIALS_PATH')
    sheet_id = os.environ.get('GOOGLE_SHEET_ID')
    sheet_name = os.environ.get('GOOGLE_SHEET_NAME')
    
    logger.info(f"認証情報ファイルパス: {creds_path}")
    logger.info(f"スプレッドシートID: {sheet_id}")
    logger.info(f"シート名: {sheet_name}")
    
    if not all([creds_path, sheet_id, sheet_name]):
        logger.error("必要な環境変数が設定されていません")
        return False
    
    if not os.path.exists(creds_path):
        logger.error(f"認証情報ファイルが見つかりません: {creds_path}")
        return False
    
    try:
        with open(creds_path, 'r') as f:
            creds_content = json.load(f)
            logger.info(f"認証情報ファイルの形式: {type(creds_content)}")
            if isinstance(creds_content, dict) and 'type' in creds_content:
                logger.info(f"認証情報タイプ: {creds_content['type']}")
            else:
                logger.warning("認証情報ファイルの形式が不正です")
    except Exception as e:
        logger.error(f"認証情報ファイル読み込みエラー: {str(e)}")
        return False
    
    return True

def test_read_spreadsheet_data():
    """
    スプレッドシートからのデータ読み込みをテストする関数
    """
    logger.info("スプレッドシートからのデータ読み込みをテストしています...")
    
    if not test_google_sheets_connection():
        logger.error("Google Sheets APIへの接続テストに失敗しました")
        return False
    
    try:
        logger.info("全行のデータを読み込みます...")
        all_data = read_spreadsheet_data()
        
        if not all_data:
            logger.error("データの読み込みに失敗しました")
            return False
        
        logger.info(f"読み込んだデータ数: {len(all_data)}行")
        
        if all_data:
            first_item = all_data[0]
            logger.info(f"最初の行のデータ:")
            for key, value in first_item.items():
                logger.info(f"  {key}: {value}")
        
        logger.info("特定の行のデータを読み込みます...")
        row_data = read_spreadsheet_data(row_index=0)  # 最初の行
        
        if not row_data:
            logger.error("特定の行のデータ読み込みに失敗しました")
            return False
        
        logger.info(f"特定の行のデータ:")
        for key, value in row_data.items():
            logger.info(f"  {key}: {value}")
        
        return True
        
    except Exception as e:
        logger.error(f"データ読み込み中にエラーが発生しました: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("=== Google Sheets 連携テスト ===")
    
    connection_result = test_google_sheets_connection()
    logger.info(f"接続テスト結果: {'成功' if connection_result else '失敗'}")
    
    if connection_result:
        read_result = test_read_spreadsheet_data()
        logger.info(f"データ読み込みテスト結果: {'成功' if read_result else '失敗'}")
    else:
        logger.error("接続テストに失敗したため、データ読み込みテストをスキップします")
