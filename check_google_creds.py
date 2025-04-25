import os
import json

creds_path = os.environ.get('GOOGLE_SHEETS_CREDENTIALS_PATH')
print(f'認証情報ファイルパス: {creds_path}')

if os.path.exists(creds_path):
    print(f'認証情報ファイルが存在します: {creds_path}')
    try:
        with open(creds_path, 'r') as f:
            content = f.read()
            print(f'ファイル内容: {content[:100]}...')  # 最初の100文字だけ表示
    except Exception as e:
        print(f'ファイル読み込みエラー: {str(e)}')
else:
    print(f'認証情報ファイルが見つかりません: {creds_path}')
    
    print('\n環境変数:')
    for key, value in os.environ.items():
        if key.startswith('GOOGLE_'):
            print(f'{key}: {value}')
