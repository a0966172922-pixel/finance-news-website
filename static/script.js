/**
 * 財經新聞網站前端 JavaScript
 * 負責與後端 API 通訊和動態更新頁面
 */

// ========== 全域變數 ========== 

// 使用相對路徑以支持跨域
const API_BASE_URL = window.location.origin;
let currentNews = [];

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
        descriptionHTML += `<p class="news-card-description">${escapeHtml(article.description)}</p>`;
        
        // 如果有中文翻譯，添加到下方
        if (article.chinese_description) {
            descriptionHTML += `<p class="news-card-description-chinese">${escapeHtml(article.chinese_description)}</p>`;
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
