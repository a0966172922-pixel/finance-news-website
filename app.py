#!/usr/bin/env python3
"""
財經新聞網站後端
使用 Flask 框架和 GNews API 來抓取印度與東南亞的財經新聞
支持異步翻譯以提升性能
改進的搜尋策略確保新聞與所選國家相關
"""

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import requests
import json
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import re

# 載入環境變數
load_dotenv()

# 初始化 Flask 應用
app = Flask(__name__)
CORS(app)  # 啟用 CORS 以支援前端跨域請求

# 配置
API_KEY = os.getenv('GNEWS_API_KEY', '6dd86b625d672e20b4e70730c39f51aa')
API_ENDPOINT = "https://gnews.io/api/v4/search"

# 支援的國家 - 包含英文名稱和搜尋關鍵字
SUPPORTED_COUNTRIES = {
    'in': {
        'name': '印度',
        'english_name': 'India',
        'keywords': ['India', 'Indian', 'New Delhi', 'Mumbai']
    },
    'sg': {
        'name': '新加坡',
        'english_name': 'Singapore',
        'keywords': ['Singapore', 'Singaporean', 'Singapore Stock Exchange']
    },
    'my': {
        'name': '馬來西亞',
        'english_name': 'Malaysia',
        'keywords': ['Malaysia', 'Malaysian', 'Kuala Lumpur', 'Bursa Malaysia']
    },
    'th': {
        'name': '泰國',
        'english_name': 'Thailand',
        'keywords': ['Thailand', 'Thai', 'Bangkok', 'SET Thailand']
    },
    'vn': {
        'name': '越南',
        'english_name': 'Vietnam',
        'keywords': ['Vietnam', 'Vietnamese', 'Hanoi', 'Ho Chi Minh']
    },
    'id': {
        'name': '印尼',
        'english_name': 'Indonesia',
        'keywords': ['Indonesia', 'Indonesian', 'Jakarta', 'IDX Indonesia']
    },
    'ph': {
        'name': '菲律賓',
        'english_name': 'Philippines',
        'keywords': ['Philippines', 'Philippine', 'Manila', 'PSE Philippines']
    }
}

# 支援的主題（搜尋關鍵字）
SUPPORTED_TOPICS = {
    'finance': '財經',
    'business': '商業',
    'economy': '經濟'
}





def is_article_relevant_to_country(article, country_code):
    """
    檢查文章是否與所選國家相關
    
    參數:
        article (dict): 文章資料
        country_code (str): 國家代碼
    
    返回:
        bool: 如果文章與國家相關則返回 True
    """
    
    if country_code not in SUPPORTED_COUNTRIES:
        return True
    
    country_info = SUPPORTED_COUNTRIES[country_code]
    keywords = country_info['keywords']
    
    # 檢查標題和描述中是否包含國家關鍵字
    title = article.get('title', '').lower()
    description = article.get('description', '').lower()
    source = article.get('source', {}).get('name', '').lower()
    
    combined_text = f"{title} {description} {source}"
    
    # 檢查是否包含任何國家關鍵字
    for keyword in keywords:
        if keyword.lower() in combined_text:
            return True
    
    # 如果沒有找到關鍵字，返回 False（不相關）
    return False

def get_news_from_gnews(country, topic='finance', max_articles=10):
    """
    從 GNews API 抓取新聞
    
    參數:
        country (str): 國家代碼 (e.g., 'in', 'sg')
        topic (str): 主題關鍵字 (e.g., 'finance', 'business')
        max_articles (int): 返回的最大文章數
    
    返回:
        dict: 包含文章列表的字典，或錯誤信息
    """
    
    # 驗證國家代碼
    if country not in SUPPORTED_COUNTRIES:
        return {
            'success': False,
            'error': f'不支援的國家代碼: {country}',
            'supported_countries': list(SUPPORTED_COUNTRIES.keys())
        }
    
    # 驗證主題
    if topic not in SUPPORTED_TOPICS:
        topic = 'finance'  # 預設為財經
    
    country_info = SUPPORTED_COUNTRIES[country]
    country_english = country_info['english_name']
    
    # 構建改進的搜尋查詢 - 包含國家名稱
    search_query = f"{country_english} {topic}"
    
    print(f"搜尋查詢: {search_query}, 國家: {country}")
    
    # 構建查詢參數
    params = {
        'q': search_query,
        'country': country,
        'lang': 'en',
        'max': min(max_articles * 2, 100),  # 獲取更多結果以進行過濾
        'sortby': 'publishedAt',
        'apikey': API_KEY
    }
    
    try:
        # 發送 API 請求
        response = requests.get(API_ENDPOINT, params=params, timeout=10)
        
        # 檢查 HTTP 狀態碼
        if response.status_code != 200:
            return {
                'success': False,
                'error': f'GNews API 錯誤: {response.status_code}',
                'details': response.text
            }
        
        # 解析 JSON 回應
        data = response.json()
        
        # 處理文章資料 - 添加相關性過濾
        articles = []
        filtered_count = 0
        
        for idx, article in enumerate(data.get('articles', [])):
            # 檢查文章是否與國家相關
            if not is_article_relevant_to_country(article, country):
                filtered_count += 1
                print(f"過濾掉不相關的文章: {article.get('title', '')[:50]}")
                continue
            
            description = article.get('description', '')
            
            articles.append({
                'title': article.get('title', ''),
                'description': description,
                'content': article.get('content', ''),
                'url': article.get('url', ''),
                'source': article.get('source', {}).get('name', 'Unknown'),
                'publishedAt': article.get('publishedAt', ''),
                'country': country,
                'topic': topic
            })
            
            # 達到所需的文章數量後停止
            if len(articles) >= max_articles:
                break
        
        print(f"過濾結果: 原始 {len(data.get('articles', []))} 篇, 過濾掉 {filtered_count} 篇, 返回 {len(articles)} 篇")
        
        return {
            'success': True,
            'country': country,
            'country_name': country_info['name'],
            'topic': topic,
            'topic_name': SUPPORTED_TOPICS.get(topic),
            'total_articles': data.get('totalArticles', 0),
            'returned_articles': len(articles),
            'filtered_articles': filtered_count,
            'articles': articles
        }
        
    except requests.exceptions.Timeout:
        return {
            'success': False,
            'error': 'API 請求超時'
        }
    except requests.exceptions.ConnectionError:
        return {
            'success': False,
            'error': '無法連接到 GNews API'
        }
    except json.JSONDecodeError:
        return {
            'success': False,
            'error': '無法解析 API 回應'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'發生錯誤: {str(e)}'
        }

# ============ API 端點 ============

@app.route('/', methods=['GET'])
def index():
    """首頁 - 返回主頁面"""
    return render_template('index.html')

@app.route('/api/news', methods=['GET'])
def get_news():
    """
    獲取新聞的 API 端點
    
    查詢參數:
        - country (必填): 國家代碼 (e.g., 'in', 'sg')
        - topic (可選): 主題 (e.g., 'finance', 'business', 'economy')，預設為 'finance'
        - max (可選): 返回的最大文章數，預設為 10
    
    返回:
        JSON 格式的新聞資料
    """
    
    # 獲取查詢參數
    country = request.args.get('country', '').lower()
    topic = request.args.get('topic', 'finance').lower()
    max_articles = request.args.get('max', 10, type=int)
    
    # 驗證必填參數
    if not country:
        return jsonify({
            'success': False,
            'error': '缺少必填參數: country',
            'supported_countries': list(SUPPORTED_COUNTRIES.keys())
        }), 400
    
    # 從 GNews API 抓取新聞
    result = get_news_from_gnews(country, topic, max_articles)
    
    # 根據結果返回適當的 HTTP 狀態碼
    status_code = 200 if result.get('success') else 400
    
    return jsonify(result), status_code



@app.route('/api/countries', methods=['GET'])
def get_countries():
    """返回支援的國家列表"""
    return jsonify({
        'success': True,
        'countries': [
            {
                'code': code,
                'name': info['name']
            }
            for code, info in SUPPORTED_COUNTRIES.items()
        ]
    })

@app.route('/api/topics', methods=['GET'])
def get_topics():
    """返回支援的主題列表"""
    return jsonify({
        'success': True,
        'topics': [
            {
                'code': code,
                'name': name
            }
            for code, name in SUPPORTED_TOPICS.items()
        ]
    })

@app.route('/health', methods=['GET'])
def health_check():
    """健康檢查端點"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

# ============ 錯誤處理 ============

@app.errorhandler(404)
def not_found(error):
    """處理 404 錯誤"""
    return jsonify({
        'success': False,
        'error': '端點不存在',
        'message': '請訪問 / 查看可用的 API 端點'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """處理 500 錯誤"""
    return jsonify({
        'success': False,
        'error': '伺服器內部錯誤'
    }), 500

# ============ 主程式 ============

if __name__ == '__main__':
    # 在開發環境中執行
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
