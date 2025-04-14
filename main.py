#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Google スプレッドシートからデータを読み込み、eBay Sandboxに出品するプログラム
(カテゴリID自動取得版)
"""

import os
import sys
import logging
import time
from typing import Optional
from dotenv import load_dotenv

from google_sheets_reader import read_cell_value
# ebay_lister から get_suggested_category もインポート
from ebay_lister import list_item_on_ebay, get_suggested_category

# ロガー設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ebay_listing.log", encoding='utf-8'),
        logging.StreamHandler(stream=sys.stdout)
    ]
)
logger = logging.getLogger("ebay_listing")

def setup_environment() -> bool:
    """
    環境設定を行う関数

    Returns:
        bool: 環境設定が成功したかどうか
    """
    logger.info("環境設定を開始します。")
    
    # .env ファイルの読み込み
    load_dotenv()
    
    # 必要な環境変数の確認
    required_env_vars = [
        "EBAY_APP_ID", 
        "EBAY_DEV_ID", 
        "EBAY_CERT_ID", 
        "EBAY_AUTH_TOKEN"
    ]
    
    missing_vars = []
    for var in required_env_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"以下の環境変数が設定されていません: {', '.join(missing_vars)}")
        logger.error(".env ファイルの確認、または環境変数の設定を行ってください。")
        return False
    
    logger.info("環境設定が完了しました。")
    return True

def fetch_sheet_data() -> Optional[str]:
    """
    Google スプレッドシートからデータを取得する関数

    Returns:
        Optional[str]: 取得したタイトル。取得に失敗した場合は None。
    """
    logger.info("Google スプレッドシートからデータを取得します。")
    
    # ここでスプレッドシートのIDやシート名などを指定して、データを取得する
    # 今回はサンプルとして "Alya anime figure collectible" を返す
    # 本来はread_cell_valueを使って実際のデータを取得する
    # 例: title = read_cell_value(spreadsheet_id, sheet_name, cell_range)
    
    title = "Alya anime figure collectible"
    if title:
        logger.info(f"データの取得に成功しました: タイトル = {title}")
        return title
    else:
        logger.error("データの取得に失敗しました。")
        return None

# --- post_to_ebay 関数の修正 ---
# 引数に category_id を追加
def post_to_ebay(title: str, category_id: Optional[str], max_retries: int = 2) -> bool:
    """
    eBayに出品する関数（リトライ機能付き、カテゴリID指定）

    Args:
        title: 出品するアイテムのタイトル
        category_id: 使用するカテゴリID (Noneの場合、lister側でデフォルトを使用)
        max_retries: 最大リトライ回数

    Returns:
        bool: 出品が成功したかどうか
    """
    retry_count = 0

    while retry_count < max_retries:
        try:
            logger.info(f"eBay Sandboxに出品しています... (カテゴリID: {category_id or 'デフォルト'})")
            # タイトルからAlya/フィギュアを検出し、カスタムのItem Specificsを設定
            # (このロジックは維持するが、カテゴリに合わせて変更する方が望ましい可能性あり)
            custom_specifics = None
            if "Alya" in title and "figure" in title.lower(): # より具体的に
                custom_specifics = [
                    {"Name": "Character", "Value": "Alya"},
                    {"Name": "Type", "Value": "Figure"}, # カテゴリによっては不要かも
                    {"Name": "Brand", "Value": "Unbranded"}, # スプレッドシートから取るべき
                    {"Name": "Material", "Value": "PVC"} # スプレッドシートから取るべき
                ]

            # ↓↓↓ category_id を list_item_on_ebay に渡す ↓↓↓
            success, result = list_item_on_ebay(title, category_id=category_id, item_specifics=custom_specifics)

            if success:
                logger.info(f"出品成功: アイテムID = {result}")
                return True
            else:
                # 出品失敗時のログは list_item_on_ebay 内で詳細が出力されるはず
                logger.warning(f"出品リトライ対象: {result}") # 簡潔に
                retry_count += 1
                if retry_count < max_retries:
                    wait_time = 2 ** retry_count
                    logger.info(f"{wait_time}秒後にリトライします（{retry_count}/{max_retries}）")
                    time.sleep(wait_time)

        except Exception as e:
            # こちらも詳細エラーはlister側でログ出力される想定
            logger.error(f"eBay出品処理中に予期しないエラーが発生しました: {str(e)}")
            retry_count += 1
            if retry_count < max_retries:
                wait_time = 2 ** retry_count
                logger.info(f"{wait_time}秒後にリトライします（{retry_count}/{max_retries}）")
                time.sleep(wait_time)

    # リトライ上限に達した場合
    logger.error("リトライ上限に達したため、出品を断念します。")
    return False

# --- main 関数の修正 ---
def main() -> int:
    """
    メイン関数

    Returns:
        int: 終了コード（0: 成功, 1: 失敗）
    """
    logger.info("プログラムを開始します")

    # 環境設定
    if not setup_environment():
        return 1

    # データ取得
    title = fetch_sheet_data()
    if not title:
        logger.error("スプレッドシートからのデータ取得に失敗しました")
        return 1

    # --- カテゴリIDをタイトルから取得 ---
    suggested_category_id = get_suggested_category(title)
    if not suggested_category_id:
        logger.warning("カテゴリIDの自動取得に失敗しました。config.pyのデフォルト値で試行します。")
        # デフォルト値を使う場合は None を渡す
        suggested_category_id = None
    # ------------------------------------

    # eBayに出品 (取得したカテゴリIDを渡す)
    if not post_to_ebay(title, suggested_category_id): # category_idを渡す
        logger.error("eBayへの出品に失敗しました")
        return 1

    logger.info("処理が正常に完了しました")
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)