/**
 * 財經新聞網站前端 JavaScript
 * 負責與後端 API 通訊和動態更新頁面
 * 支持異步翻譯和漸進式加載
 */

// ========== 全域變數 ========== 

// 使用相對路徑以支持跨域
const API_BASE_URL = window.location.origin;
let currentNews = [];
let translationPollingIntervals = {}; // 存儲輪詢計時器

// ========== 初始化 ========== 

document.addEventListener('DOMContentLoaded', function() {
    console.log('頁面載入完成，初始化應用...');
    
    // 載入國家列表
    loadCountries();
    
    // 綁定事件監聽器
    document.getElementById('search-btn').addEventListener('click', searchNews);
    document.getElementById('country-select').addEventListener('change', function() {
        // 當選擇國家時，可以自動搜尋（可選）
    });
});

// ========== 載入國家列表 ========== 

async function loadCountries() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/countries`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success && data.countries) {
            const countrySelect = document.getElementById('country-select');
            
            // 清空現有選項（保留第一個提示選項）
            while (countrySelect.options.length > 1) {
                countrySelect.remove(1);
            }
            
            // 添加國家選項
            data.countries.forEach(country => {
                const option = document.createElement('option');
                option.value = country.code;
                option.textContent = `${country.name} (${country.code})`;
                countrySelect.appendChild(option);
            });
            
            console.log('國家列表載入成功');
        }
    } catch (error) {
        console.error('載入國家列表失敗:', error);
        showError('無法載入國家列表，請重新整理頁面');
    }
}

// ========== 搜尋新聞 ========== 

async function searchNews() {
    const country = document.getElementById('country-select').value;
    const topic = document.getElementById('topic-select').value;
    const maxArticles = document.getElementById('max-articles').value;
    
    // 驗證選擇
    if (!country) {
        showError('請選擇一個國家');
        return;
    }
    
    // 停止之前的輪詢
    stopAllPolling();
    
    // 顯示載入狀態
    showLoading(true);
    hideError();
    
    try {
        // 構建 API 請求 URL
        const url = new URL(`${API_BASE_URL}/api/news`);
        url.searchParams.append('country', country);
        url.searchParams.append('topic', topic);
        url.searchParams.append('max', maxArticles);
        
        console.log(`正在搜尋新聞: ${url.toString()}`);
        
        const response = await fetch(url.toString());
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            currentNews = data.articles || [];
            displayNews(data);
            
            // 開始輪詢翻譯結果
            startTranslationPolling(data.articles);
            
            console.log(`成功載入 ${currentNews.length} 篇新聞`);
        } else {
            throw new Error(data.error || '無法載入新聞');
        }
        
    } catch (error) {
        console.error('搜尋新聞失敗:', error);
        showError(`搜尋失敗: ${error.message}`);
        displayNews(null);
    } finally {
        showLoading(false);
    }
}

// ========== 輪詢翻譯結果 ========== 

function startTranslationPolling(articles) {
    /**
     * 開始輪詢翻譯結果
     * 每 2 秒檢查一次是否有新的翻譯完成
     */
    
    // 收集所有需要翻譯的文章 ID
    const articleIds = articles
        .filter(article => !article.chinese_description)
        .map(article => article.article_id);
    
    if (articleIds.length === 0) {
        console.log('所有文章都已翻譯');
        return;
    }
    
    console.log(`開始輪詢 ${articleIds.length} 篇文章的翻譯結果`);
    
    // 設置輪詢計時器
    const pollingKey = `poll_${Date.now()}`;
    let pollCount = 0;
    const maxPolls = 60; // 最多輪詢 60 次（2 秒 × 60 = 120 秒 = 2 分鐘）
    
    translationPollingIntervals[pollingKey] = setInterval(async () => {
        pollCount++;
        
        try {
            // 獲取翻譯結果
            const url = new URL(`${API_BASE_URL}/api/translations`);
            url.searchParams.append('article_ids', articleIds.join(','));
            
            const response = await fetch(url.toString());
            
            if (!response.ok) {
                console.warn('獲取翻譯結果失敗');
                return;
            }
            
            const data = await response.json();
            
            if (data.success && data.translations) {
                console.log(`收到 ${data.total_translated} 篇翻譯結果`);
                
                // 更新頁面上的翻譯
                updateTranslations(data.translations);
                
                // 如果所有翻譯都完成，停止輪詢
                if (data.total_translated === articleIds.length) {
                    console.log('所有翻譯已完成');
                    clearInterval(translationPollingIntervals[pollingKey]);
                    delete translationPollingIntervals[pollingKey];
                }
            }
            
        } catch (error) {
            console.error('輪詢翻譯結果失敗:', error);
        }
        
        // 如果達到最大輪詢次數，停止
        if (pollCount >= maxPolls) {
            console.log('輪詢已達最大次數，停止');
            clearInterval(translationPollingIntervals[pollingKey]);
            delete translationPollingIntervals[pollingKey];
        }
        
    }, 2000); // 每 2 秒輪詢一次
}

function stopAllPolling() {
    /**
     * 停止所有正在進行的輪詢
     */
    Object.keys(translationPollingIntervals).forEach(key => {
        clearInterval(translationPollingIntervals[key]);
        delete translationPollingIntervals[key];
    });
    console.log('已停止所有輪詢');
}

function updateTranslations(translations) {
    /**
     * 更新頁面上的翻譯結果
     * 
     * 參數:
     *     translations (object): 翻譯結果，格式為 { article_id: chinese_text }
     */
    
    Object.entries(translations).forEach(([articleId, chineseText]) => {
        // 查找對應的卡片
        const card = document.querySelector(`[data-article-id="${articleId}"]`);
        
        if (card) {
            // 查找中文摘要容器
            const chineseDescriptionElement = card.querySelector('.news-card-description-chinese');
            
            if (chineseDescriptionElement) {
                // 更新文本
                chineseDescriptionElement.textContent = chineseText;
                
                // 移除載入狀態樣式
                chineseDescriptionElement.classList.remove('news-card-description-loading');
                
                console.log(`已更新翻譯: ${articleId.substring(0, 20)}...`);
            }
        }
    });
}

// ========== 顯示新聞 ========== 

function displayNews(data) {
    const newsContainer = document.getElementById('news-container');
    
    // 清空容器
    newsContainer.innerHTML = '';
    
    if (!data || !data.articles || data.articles.length === 0) {
        newsContainer.innerHTML = '<p class="placeholder">未找到相關新聞</p>';
        return;
    }
    
    // 更新頁面標題
    const countryName = data.country_name || data.country;
    const topicName = data.topic_name || data.topic;
    document.querySelector('.news-section h2').textContent = 
        `${countryName} - ${topicName}新聞 (共 ${data.articles.length} 篇)`;
    
    // 更新時間
    const now = new Date();
    document.getElementById('update-time').textContent = 
        now.toLocaleString('zh-TW', { 
            year: 'numeric', 
            month: '2-digit', 
            day: '2-digit', 
            hour: '2-digit', 
            minute: '2-digit', 
            second: '2-digit' 
        });
    
    // 建立新聞卡片
    data.articles.forEach((article, index) => {
        const card = createNewsCard(article);
        newsContainer.appendChild(card);
    });
}

// ========== 建立新聞卡片 ========== 

function createNewsCard(article) {
    const card = document.createElement('div');
    card.className = 'news-card';
    card.setAttribute('data-article-id', article.article_id);
    
    // 格式化發布時間
    const publishedDate = new Date(article.publishedAt);
    const formattedDate = publishedDate.toLocaleString('zh-TW', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
    
    // 準備描述文本
    let descriptionHTML = '';
    
    if (article.description) {
        // 添加英文摘要
        descriptionHTML += `
            <div class="news-card-description-wrapper">
                <div class="news-card-description-label">English Summary</div>
                <p class="news-card-description">${escapeHtml(article.description)}</p>
            </div>
        `;
        
        // 添加中文摘要
        if (article.chinese_description) {
            // 如果已經有翻譯，直接顯示
            descriptionHTML += `
                <div class="news-card-description-wrapper">
                    <div class="news-card-description-label-chinese">Chinese Summary (中文摘要)</div>
                    <p class="news-card-description-chinese">${escapeHtml(article.chinese_description)}</p>
                </div>
            `;
        } else {
            // 如果還沒有翻譯，顯示「正在翻譯中...」
            descriptionHTML += `
                <div class="news-card-description-wrapper">
                    <div class="news-card-description-label-chinese">Chinese Summary (中文摘要)</div>
                    <p class="news-card-description-chinese news-card-description-loading">正在翻譯中...</p>
                </div>
            `;
        }
    }
    
    // 建立卡片 HTML
    card.innerHTML = `
        <div class="news-card-content">
            <h3 class="news-card-title">${escapeHtml(article.title)}</h3>
            <div class="news-card-meta">
                <span class="news-card-source">${escapeHtml(article.source)}</span>
                <span class="news-card-date">${formattedDate}</span>
            </div>
            ${descriptionHTML}
            <div class="news-card-footer">
                <a href="${article.url}" target="_blank" rel="noopener noreferrer" class="news-card-link">
                    閱讀全文 →
                </a>
            </div>
        </div>
    `;
    
    return card;
}

// ========== 工具函數 ========== 

/**
 * 顯示/隱藏載入狀態
 */
function showLoading(show) {
    const loading = document.getElementById('loading');
    if (show) {
        loading.style.display = 'flex';
    } else {
        loading.style.display = 'none';
    }
}

/**
 * 顯示錯誤訊息
 */
function showError(message) {
    const errorDiv = document.getElementById('error-message');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
}

/**
 * 隱藏錯誤訊息
 */
function hideError() {
    const errorDiv = document.getElementById('error-message');
    errorDiv.style.display = 'none';
}

/**
 * 轉義 HTML 特殊字元，防止 XSS 攻擊
 */
function escapeHtml(text) {
    if (!text) return '';
    
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    
    return text.replace(/[&<>"']/g, m => map[m]);
}

/**
 * 格式化日期
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('zh-TW');
}

console.log('JavaScript 載入完成');
