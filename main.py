#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Google スプレッドシートからデータを読み込み、eBayに出品するプログラム
サンドボックス環境と本番環境の両方をサポート
"""

import os
import sys
import logging
import time
import argparse
from typing import Optional, List, Dict, Any, Union
from dotenv import load_dotenv

from ebay_env import EbayEnvironment
from google_sheets_reader import read_spreadsheet_data
from ebay_lister import (
    list_item_on_ebay, 
    get_suggested_category, 
    upload_image_to_ebay
)

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
    
    env_type = os.environ.get("EBAY_ENVIRONMENT", "sandbox")
    prefix = f"EBAY_{env_type.upper()}_"
    
    # 必要な環境変数の確認
    required_env_vars = [
        f"{prefix}APP_ID", 
        f"{prefix}DEV_ID", 
        f"{prefix}CERT_ID", 
        f"{prefix}AUTH_TOKEN"
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



def process_item(item_data: Dict[str, str], ebay_env: EbayEnvironment, max_retries: int = 2) -> bool:
    """
    eBayに商品を出品する関数
    
    Args:
        item_data (dict): 商品データ
        ebay_env (EbayEnvironment): eBay環境オブジェクト
        max_retries (int): 最大リトライ回数
        
    Returns:
        bool: 出品が成功したかどうか
    """
    title = item_data.get('Item name')  # Column A header is "Item name"
    if not title:
        logger.error("商品タイトルがありません")
        return False
        
    category_id = item_data.get('CategoryID')
    if not category_id:
        logger.info(f"カテゴリIDの自動取得を試みます: '{title}'")
        category_id = get_suggested_category(title, ebay_env)
        if not category_id:
            logger.warning("カテゴリIDの自動取得に失敗しました。デフォルト値を使用します。")
    
    item_specifics = []
    for key, value in item_data.items():
        if key not in ['Item name', 'image', 'Description', 'Price', 'Quantity', 'CategoryID'] and value:
            item_specifics.append({"Name": key, "Value": value})
    
    picture_urls = []
    image_ref = item_data.get('image')  # Column B header is "image"
    if image_ref:
        for ref in image_ref.split(','):
            ref = ref.strip()
            if not ref:
                continue
                
            if ref.startswith(('http://', 'https://')):
                from utils import download_image_from_url
                image_path = download_image_from_url(ref)
            else:
                image_path = ref
                
            if image_path and os.path.exists(image_path):
                ebay_image_url = upload_image_to_ebay(image_path, ebay_env)
                if ebay_image_url:
                    picture_urls.append(ebay_image_url)
    
    retry_count = 0
    while retry_count < max_retries:
        try:
            env_name = "本番" if ebay_env.is_production() else "サンドボックス"
            logger.info(f"eBay {env_name} 環境に出品しています... (カテゴリID: {category_id or 'デフォルト'})")
            
            success, result = list_item_on_ebay(
                title,
                category_id=category_id,
                item_specifics=item_specifics,
                picture_urls=picture_urls,
                environment=ebay_env
            )

            if success:
                logger.info(f"出品成功: アイテムID = {result}")
                return True
            else:
                logger.warning(f"出品リトライ対象: {result}")
                retry_count += 1
                if retry_count < max_retries:
                    wait_time = 2 ** retry_count
                    logger.info(f"{wait_time}秒後にリトライします（{retry_count}/{max_retries}）")
                    time.sleep(wait_time)

        except Exception as e:
            logger.error(f"eBay出品処理中に予期しないエラーが発生しました: {str(e)}")
            retry_count += 1
            if retry_count < max_retries:
                wait_time = 2 ** retry_count
                logger.info(f"{wait_time}秒後にリトライします（{retry_count}/{max_retries}）")
                time.sleep(wait_time)

    # リトライ上限に達した場合
    logger.error("リトライ上限に達したため、出品を断念します。")
    return False

def main() -> int:
    """
    メイン関数
    
    Returns:
        int: 終了コード（0: 成功, 1: 失敗）
    """
    parser = argparse.ArgumentParser(description='eBay出品自動化ツール')
    parser.add_argument('--env', choices=['sandbox', 'production'], default='sandbox',
                       help='使用する環境（sandbox/production）')
    parser.add_argument('--row', type=int, help='処理する特定の行番号（0から始まる）')
    args = parser.parse_args()
    
    os.environ['EBAY_ENVIRONMENT'] = args.env
    
    logger.info(f"プログラムを開始します（環境: {args.env}）")
    
    # 環境設定
    if not setup_environment():
        return 1
    
    ebay_env = EbayEnvironment(args.env)
    if not ebay_env.validate_credentials():
        logger.error(f"eBay {args.env} 環境の認証情報が無効です")
        return 1
    
    # データ取得
    if args.row is not None:
        item_data = read_spreadsheet_data(row_index=args.row)
        if not item_data:
            logger.error(f"スプレッドシートの行 {args.row} からのデータ取得に失敗しました")
            return 1
        items = [item_data]
    else:
        items = read_spreadsheet_data()
        if not items:
            logger.error("スプレッドシートからのデータ取得に失敗しました")
            return 1
    
    success_count = 0
    failure_count = 0
    
    for i, item in enumerate(items):
        logger.info(f"商品 {i+1}/{len(items)} を処理しています...")
        
        if process_item(item, ebay_env):
            success_count += 1
        else:
            failure_count += 1
    
    logger.info(f"処理が完了しました。成功: {success_count}, 失敗: {failure_count}")
    return 0 if failure_count == 0 else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
