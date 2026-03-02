#!/usr/bin/env python3
"""
財經新聞網站後端
使用 Flask 框架和 GNews API 來抓取印度與東南亞的財經新聞
"""

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import requests
import json
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from openai import OpenAI
import re

# 載入環境變數
load_dotenv()

# 初始化 Flask 應用
app = Flask(__name__)
CORS(app)  # 啟用 CORS 以支援前端跨域請求

# 配置
API_KEY = os.getenv('GNEWS_API_KEY', '6dd86b625d672e20b4e70730c39f51aa')
API_ENDPOINT = "https://gnews.io/api/v4/search"

# 支援的國家
SUPPORTED_COUNTRIES = {
    'in': '印度',
    'sg': '新加坡',
    'my': '馬來西亞',
    'th': '泰國',
    'vn': '越南',
    'id': '印尼',
    'ph': '菲律賓'
}

# 支援的主題（搜尋關鍵字）
SUPPORTED_TOPICS = {
    'finance': '財經',
    'business': '商業',
    'economy': '經濟'
}

# 初始化 OpenAI 客戶端用於翻譯
try:
    openai_client = OpenAI()
except:
    openai_client = None

def is_english(text):
    """檢查文本是否主要是英文"""
    if not text:
        return False
    
    # 計算英文字符的比例
    english_chars = sum(1 for c in text if ord(c) < 128 and c.isalpha())
    chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    
    # 如果中文字符較多，則認為已經是中文
    if chinese_chars > english_chars:
        return False
    
    return english_chars > 0

def translate_to_chinese(text):
    """
    使用 OpenAI API 將英文文本翻譯成繁體中文
    
    參數:
        text (str): 要翻譯的英文文本
    
    返回:
        str: 翻譯後的中文文本，或 None（如果翻譯失敗或不需要翻譯）
    """
    
    if not text or not openai_client:
        return None
    
    # 檢查是否是英文
    if not is_english(text):
        print(f"文本已是中文或不需要翻譯")
        return None
    
    try:
        print(f"正在翻譯文本: {text[:50]}...")
        
        response = openai_client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": "你是一個專業的財經翻譯助手。請將提供的英文文本翻譯成繁體中文，保持原意、專業性和簡潔性。只返回翻譯後的文本，不要添加任何額外說明。"
                },
                {
                    "role": "user",
                    "content": text[:500]  # 限制長度以節省 token
                }
            ],
            temperature=0.3,
            max_tokens=500,
            timeout=10  # 增加超時時間
        )
        
        translated = response.choices[0].message.content.strip()
        print(f"翻譯成功: {translated[:50]}...")
        return translated
    
    except Exception as e:
        print(f"翻譯錯誤: {str(e)}")
        return None

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
    
    # 構建查詢參數
    params = {
        'q': topic,
        'country': country,
        'lang': 'en',
        'max': min(max_articles, 100),  # GNews API 最多返回 100 篇
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
        
        # 處理文章資料
        articles = []
        for article in data.get('articles', []):
            description = article.get('description', '')
            
            # 如果是英文，進行翻譯
            chinese_description = None
            if is_english(description):
                chinese_description = translate_to_chinese(description)
            
            articles.append({
                'title': article.get('title', ''),
                'description': description,
                'chinese_description': chinese_description,
                'content': article.get('content', ''),
                'url': article.get('url', ''),
                'source': article.get('source', {}).get('name', 'Unknown'),
                'publishedAt': article.get('publishedAt', ''),
                'country': country,
                'topic': topic
            })
        
        return {
            'success': True,
            'country': country,
            'country_name': SUPPORTED_COUNTRIES.get(country),
            'topic': topic,
            'topic_name': SUPPORTED_TOPICS.get(topic),
            'total_articles': data.get('totalArticles', 0),
            'returned_articles': len(articles),
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
                'name': name
            }
            for code, name in SUPPORTED_COUNTRIES.items()
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
