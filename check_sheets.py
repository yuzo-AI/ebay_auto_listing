import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

creds_path = os.environ.get('GOOGLE_SHEETS_CREDENTIALS_PATH')
sheet_id = os.environ.get('GOOGLE_SHEET_ID')
sheet_name = os.environ.get('GOOGLE_SHEET_NAME')

print(f'認証情報ファイルパス: {creds_path}')
print(f'スプレッドシートID: {sheet_id}')
print(f'シート名: {sheet_name}')

if not os.path.exists(creds_path):
    print(f'認証情報ファイルが見つかりません: {creds_path}')
    exit(1)

try:
    credentials = service_account.Credentials.from_service_account_file(
        creds_path,
        scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
    )

    service = build('sheets', 'v4', credentials=credentials)

    result = service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range=f'{sheet_name}!1:1'
    ).execute()
    
    headers = result.get('values', [[]])[0]
    print('スプレッドシートのヘッダー:')
    print(json.dumps(headers, ensure_ascii=False, indent=2))
    
    result = service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range=f'{sheet_name}!A1:Z5'
    ).execute()
    
    values = result.get('values', [])
    print('\nスプレッドシートの最初の数行:')
    print(json.dumps(values, ensure_ascii=False, indent=2))
    
except Exception as e:
    print(f'エラーが発生しました: {str(e)}')
