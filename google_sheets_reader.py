import os
import logging
import sys
from typing import Optional, List, Dict, Any, Union
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account

from config import SPREADSHEET_ID, SHEET_NAME, CELL_RANGE, GOOGLE_CREDENTIALS_FILE

# ロガーの取得
logger = logging.getLogger("ebay_listing.google_sheets")

def read_cell_value() -> Optional[str]:
    """
    Google Sheetsの指定されたセルから値を読み取る関数
    
    Returns:
        Optional[str]: セルの値、エラー時はNone
    """
    try:
        # サービスアカウントの資格情報を使用して認証
        logger.debug(f"Google認証情報ファイル '{GOOGLE_CREDENTIALS_FILE}' を使用して認証します")
        credentials = service_account.Credentials.from_service_account_file(
            GOOGLE_CREDENTIALS_FILE,
            scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
        )

        # Sheets APIクライアントを構築
        logger.debug("Google Sheets APIクライアントを構築しています")
        service = build('sheets', 'v4', credentials=credentials)

        # 値の範囲を取得するAPI呼び出し
        sheet_range = f'{SHEET_NAME}!{CELL_RANGE}'
        logger.debug(f"スプレッドシート '{SPREADSHEET_ID}' の範囲 '{sheet_range}' を取得します")
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=sheet_range
        ).execute()
        
        values = result.get('values', [])
        
        if not values:
            logger.warning('スプレッドシートにデータが見つかりませんでした')
            return None
        
        # 単一のセルなので、values[0][0]で値を取得
        logger.debug(f"セルの値を取得しました: {values[0][0]}")
        return values[0][0]
    
    except HttpError as err:
        logger.error(f"Google Sheets APIエラー: {err}")
        return None
    except Exception as e:
        logger.error(f"エラーが発生しました: {str(e)}")
        return None

def read_spreadsheet_data(row_index: Optional[int] = None, 
                         sheet_name: Optional[str] = None, 
                         spreadsheet_id: Optional[str] = None) -> Union[Dict[str, str], List[Dict[str, str]], None]:
    """
    Google Sheetsから商品データを読み取る関数
    
    Args:
        row_index (int, optional): 読み取る行のインデックス。Noneの場合は全行を取得
        sheet_name (str, optional): シート名。Noneの場合はconfig.pyのSHEET_NAMEを使用
        spreadsheet_id (str, optional): スプレッドシートID。Noneの場合はconfig.pyのSPREADSHEET_IDを使用
        
    Returns:
        Union[Dict[str, str], List[Dict[str, str]], None]: 
            単一行の場合は辞書、複数行の場合は辞書のリスト、エラー時はNone
    """
    try:
        sheet_name = sheet_name or SHEET_NAME
        spreadsheet_id = spreadsheet_id or SPREADSHEET_ID
        
        # サービスアカウントの資格情報を使用して認証
        logger.debug(f"Google認証情報ファイル '{GOOGLE_CREDENTIALS_FILE}' を使用して認証します")
        credentials = service_account.Credentials.from_service_account_file(
            GOOGLE_CREDENTIALS_FILE,
            scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
        )

        # Sheets APIクライアントを構築
        logger.debug("Google Sheets APIクライアントを構築しています")
        service = build('sheets', 'v4', credentials=credentials)

        # 値の範囲を取得するAPI呼び出し
        header_range = f'{sheet_name}!1:1'
        logger.debug(f"スプレッドシート '{spreadsheet_id}' のヘッダー '{header_range}' を取得します")
        header_result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=header_range
        ).execute()
        
        headers = header_result.get('values', [[]])[0]
        
        if not headers:
            logger.warning('スプレッドシートにヘッダーが見つかりませんでした')
            return None
            
        if row_index is not None:
            data_range = f'{sheet_name}!A{row_index+2}:{chr(65+len(headers)-1)}{row_index+2}'
        else:
            data_range = f'{sheet_name}!A2:{chr(65+len(headers)-1)}'
            
        logger.debug(f"スプレッドシート '{spreadsheet_id}' のデータ '{data_range}' を取得します")
        data_result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=data_range
        ).execute()
        
        values = data_result.get('values', [])
        
        if not values:
            logger.warning('スプレッドシートにデータが見つかりませんでした')
            return None
        
        result = []
        for row in values:
            row_data = row + [''] * (len(headers) - len(row))
            item_data = {headers[i]: row_data[i] for i in range(len(headers))}
            result.append(item_data)
        
        if row_index is not None and result:
            return result[0]
        
        return result
        
    except HttpError as err:
        logger.error(f"Google Sheets APIエラー: {err}")
        return None
    except Exception as e:
        logger.error(f"エラーが発生しました: {str(e)}")
        return None

if __name__ == "__main__":
    # テスト用コード
    # ログ設定
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("google_sheets_test.log", encoding='utf-8'),
            logging.StreamHandler(stream=sys.stdout)
        ]
    )
    
    value = read_cell_value()
    if value:
        print(f"セルの値: {value}")
    else:
        print("セルの値を取得できませんでした")  