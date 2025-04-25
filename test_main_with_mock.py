
"""
eBay出品自動化ツールのテストスクリプト
モックデータを使用してメイン機能をテストする
"""

import os
import sys
import logging
import argparse
from typing import Optional, List, Dict, Any, Union

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(stream=sys.stdout)
    ]
)
logger = logging.getLogger("ebay_test_main")

from google_sheets_mock import patch_google_sheets_reader, read_spreadsheet_data_mock

from ebay_env import EbayEnvironment

def setup_mock_environment():
    """
    テスト用のモック環境をセットアップする関数
    
    Returns:
        bool: セットアップが成功したかどうか
    """
    logger.info("モック環境をセットアップしています...")
    
    os.environ["EBAY_SANDBOX_AUTH_TOKEN"] = "MockSandboxToken12345"
    os.environ["EBAY_PRODUCTION_AUTH_TOKEN"] = "MockProductionToken67890"
    
    original_read_spreadsheet_data = patch_google_sheets_reader()
    
    logger.info("モック環境のセットアップが完了しました")
    return True, original_read_spreadsheet_data

def test_process_item(env_type="sandbox"):
    """
    process_item関数をテストする関数
    
    Args:
        env_type (str): 環境タイプ。"sandbox"または"production"
    """
    logger.info(f"process_item関数のテスト（{env_type}環境）を開始します...")
    
    try:
        from main import process_item
    except ImportError:
        logger.error("main.pyからprocess_item関数をインポートできませんでした")
        return False
    
    ebay_env = EbayEnvironment(env_type)
    
    item_data = read_spreadsheet_data_mock(row_index=0)
    
    if not item_data:
        logger.error("モックデータの取得に失敗しました")
        return False
    
    logger.info(f"テスト対象の商品データ: {item_data['Item name']}")
    
    try:
        result = process_item(item_data, ebay_env)
        
        logger.info(f"process_item関数の実行結果: {result}")
        logger.info("注意: モックトークンを使用しているため、実際のAPIコールは失敗します")
        
        return True
    except Exception as e:
        logger.error(f"process_item関数の実行中にエラーが発生しました: {str(e)}")
        return False

def test_main_script(env_type="sandbox", row=None):
    """
    main.py スクリプトをテストする関数
    
    Args:
        env_type (str): 環境タイプ。"sandbox"または"production"
        row (int, optional): 処理する特定の行番号
    """
    logger.info(f"main.pyスクリプトのテスト（{env_type}環境）を開始します...")
    
    cmd_args = ["--env", env_type]
    if row is not None:
        cmd_args.extend(["--row", str(row)])
    
    original_argv = sys.argv
    
    try:
        sys.argv = [sys.argv[0]] + cmd_args
        
        from main import main
        exit_code = main()
        
        logger.info(f"main関数の実行結果: 終了コード = {exit_code}")
        logger.info("注意: モックトークンを使用しているため、実際のAPIコールは失敗します")
        
        return exit_code == 0
    except Exception as e:
        logger.error(f"main関数の実行中にエラーが発生しました: {str(e)}")
        return False
    finally:
        sys.argv = original_argv

if __name__ == "__main__":
    logger.info("=== eBay出品自動化ツールのテスト ===")
    
    setup_success, original_func = setup_mock_environment()
    
    if not setup_success:
        logger.error("モック環境のセットアップに失敗しました")
        sys.exit(1)
    
    try:
        logger.info("\n=== process_item関数のテスト（サンドボックス環境） ===")
        process_item_sandbox_result = test_process_item("sandbox")
        
        logger.info("\n=== process_item関数のテスト（本番環境） ===")
        process_item_production_result = test_process_item("production")
        
        logger.info("\n=== main.pyスクリプトのテスト（サンドボックス環境） ===")
        main_sandbox_result = test_main_script("sandbox")
        
        logger.info("\n=== main.pyスクリプトのテスト（本番環境） ===")
        main_production_result = test_main_script("production")
        
        logger.info("\n=== 特定の行のテスト（サンドボックス環境） ===")
        row_test_result = test_main_script("sandbox", row=0)
        
        logger.info("\n=== テスト結果のサマリー ===")
        logger.info(f"process_item関数（サンドボックス）: {'成功' if process_item_sandbox_result else '失敗'}")
        logger.info(f"process_item関数（本番環境）: {'成功' if process_item_production_result else '失敗'}")
        logger.info(f"main.pyスクリプト（サンドボックス）: {'成功' if main_sandbox_result else '失敗'}")
        logger.info(f"main.pyスクリプト（本番環境）: {'成功' if main_production_result else '失敗'}")
        logger.info(f"特定の行のテスト: {'成功' if row_test_result else '失敗'}")
        
    finally:
        import google_sheets_reader
        google_sheets_reader.read_spreadsheet_data = original_func
        logger.info("Google Sheetsリーダーを元の実装に戻しました")
