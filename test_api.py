#!/usr/bin/env python3
"""
GNews API 測試腳本
用於驗證 API 連接並測試抓取印度的財經新聞
"""

import requests
import json
from datetime import datetime

# API 設定
API_KEY = "6dd86b625d672e20b4e70730c39f51aa"
API_ENDPOINT = "https://gnews.io/api/v4/search"

def test_api():
    """測試 GNews API 並抓取印度的財經新聞"""
    
    print("=" * 60)
    print("GNews API 測試")
    print("=" * 60)
    print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 設定查詢參數
    params = {
        "q": "finance",  # 搜尋關鍵字：財經
        "country": "in",  # 國家：印度
        "lang": "en",     # 語言：英文
        "max": 5,         # 返回 5 篇文章
        "sortby": "publishedAt",  # 按發布時間排序
        "apikey": API_KEY
    }
    
    print("查詢參數:")
    print(f"  - 關鍵字: {params['q']}")
    print(f"  - 國家: 印度 ({params['country']})")
    print(f"  - 語言: 英文 ({params['lang']})")
    print(f"  - 返回數量: {params['max']}")
    print()
    
    try:
        print("正在發送 API 請求...")
        response = requests.get(API_ENDPOINT, params=params, timeout=10)
        
        # 檢查 HTTP 狀態碼
        if response.status_code != 200:
            print(f"❌ API 請求失敗")
            print(f"   狀態碼: {response.status_code}")
            print(f"   回應: {response.text}")
            return False
        
        # 解析 JSON 回應
        data = response.json()
        
        print("✅ API 連接成功！")
        print()
        print("=" * 60)
        print("API 回應摘要")
        print("=" * 60)
        print(f"找到的文章總數: {data.get('totalArticles', 0)}")
        print(f"本次返回的文章數: {len(data.get('articles', []))}")
        print()
        
        # 顯示文章詳情
        articles = data.get('articles', [])
        if articles:
            print("=" * 60)
            print("文章列表")
            print("=" * 60)
            for i, article in enumerate(articles, 1):
                print(f"\n【文章 {i}】")
                print(f"標題: {article.get('title', 'N/A')}")
                print(f"來源: {article.get('source', {}).get('name', 'N/A')}")
                print(f"發布時間: {article.get('publishedAt', 'N/A')}")
                print(f"摘要: {article.get('description', 'N/A')[:100]}...")
                print(f"原始 URL: {article.get('url', 'N/A')}")
        else:
            print("⚠️  未找到任何文章")
        
        print()
        print("=" * 60)
        print("完整 JSON 回應")
        print("=" * 60)
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        return True
        
    except requests.exceptions.Timeout:
        print("❌ 請求超時，請檢查網路連接")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ 連接錯誤，無法連接到 API")
        return False
    except json.JSONDecodeError:
        print("❌ 無法解析 API 回應的 JSON 格式")
        return False
    except Exception as e:
        print(f"❌ 發生未預期的錯誤: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_api()
    exit(0 if success else 1)
