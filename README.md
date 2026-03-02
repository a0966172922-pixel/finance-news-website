# 財經新聞網站

一個透過 GNews API 自動抓取並展示印度與東南亞地區最新財經新聞的網站。

## 功能特性

- 🌍 **多國家支援**：涵蓋印度、新加坡、馬來西亞、泰國、越南、印尼、菲律賓
- 📊 **多主題支援**：財經、商業、經濟
- 🔍 **即時搜尋**：透過 GNews API 即時抓取最新新聞
- 📱 **響應式設計**：完全適配桌面、平板和手機設備
- 🎨 **現代化介面**：美觀的卡片式新聞展示
- ⚡ **快速載入**：非同步 JavaScript 實現流暢的使用者體驗

## 技術棧

### 後端
- **框架**：Flask 2.3.3
- **語言**：Python 3.11
- **API**：GNews API v4

### 前端
- **標記**：HTML5
- **樣式**：CSS3（Grid、Flexbox、漸層）
- **互動**：Vanilla JavaScript（Fetch API）

### 其他
- **跨域支援**：Flask-CORS
- **環境管理**：python-dotenv

## 安裝指南

### 系統需求
- Python 3.8 或更高版本
- pip（Python 套件管理器）
- 網路連接（用於 API 呼叫）

### 安裝步驟

1. **複製或下載專案**
   ```bash
   cd finance_news_website
   ```

2. **建立虛擬環境（推薦）**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或
   venv\Scripts\activate  # Windows
   ```

3. **安裝相依套件**
   ```bash
   pip install -r requirements.txt
   ```

4. **設定 API 金鑰**
   
   編輯 `.env` 檔案，將您的 GNews API 金鑰填入：
   ```
   GNEWS_API_KEY=your_api_key_here
   ```

   如果沒有 API 金鑰，請訪問 [GNews 官方網站](https://gnews.io/) 免費申請。

## 使用方法

### 啟動應用

```bash
python app.py
```

應用將在 `http://localhost:5000` 啟動。

### 訪問網站

1. 打開瀏覽器
2. 訪問 `http://localhost:5000`
3. 在頁面上選擇國家和主題
4. 點擊「搜尋新聞」按鈕
5. 查看結果並點擊「閱讀全文」連結查看完整文章

## API 端點

### 1. 獲取新聞
**端點**：`GET /api/news`

**查詢參數**：
- `country` (必填)：國家代碼 (in, sg, my, th, vn, id, ph)
- `topic` (可選)：主題 (finance, business, economy)，預設為 finance
- `max` (可選)：返回的最大文章數 (1-100)，預設為 10

**範例**：
```
GET http://localhost:5000/api/news?country=in&topic=finance&max=10
```

**回應**：
```json
{
  "success": true,
  "country": "in",
  "country_name": "印度",
  "topic": "finance",
  "topic_name": "財經",
  "total_articles": 100,
  "returned_articles": 10,
  "articles": [
    {
      "title": "文章標題",
      "description": "文章摘要",
      "content": "完整內容",
      "url": "原始文章 URL",
      "image": "圖片 URL",
      "source": "新聞來源",
      "publishedAt": "2026-02-25T20:03:42Z"
    }
  ]
}
```

### 2. 獲取支援的國家
**端點**：`GET /api/countries`

**範例**：
```
GET http://localhost:5000/api/countries
```

### 3. 獲取支援的主題
**端點**：`GET /api/topics`

**範例**：
```
GET http://localhost:5000/api/topics
```

### 4. 健康檢查
**端點**：`GET /health`

**範例**：
```
GET http://localhost:5000/health
```

## 支援的國家

| 國家 | 代碼 |
|------|------|
| 印度 | in |
| 新加坡 | sg |
| 馬來西亞 | my |
| 泰國 | th |
| 越南 | vn |
| 印尼 | id |
| 菲律賓 | ph |

## 支援的主題

| 主題 | 代碼 |
|------|------|
| 財經 | finance |
| 商業 | business |
| 經濟 | economy |

## 專案結構

```
finance_news_website/
├── app.py                 # Flask 應用主程式
├── test_api.py            # API 測試腳本
├── requirements.txt       # Python 相依套件
├── .env                   # 環境變數配置
├── API_INFO.md            # API 資訊文件
├── README.md              # 本檔案
├── templates/
│   └── index.html         # 前端主頁面
└── static/
    ├── style.css          # CSS 樣式表
    └── script.js          # JavaScript 邏輯
```

## 故障排除

### 問題：無法連接到 API
**解決方案**：
- 檢查網路連接
- 確認 API 金鑰正確
- 檢查 `.env` 檔案中的 API 金鑰設定

### 問題：頁面無法載入
**解決方案**：
- 確保 Flask 應用正在運行
- 檢查瀏覽器控制台是否有錯誤訊息
- 嘗試清除瀏覽器快取並重新整理

### 問題：新聞未顯示
**解決方案**：
- 確認已選擇國家
- 檢查網路連接
- 查看瀏覽器開發者工具中的 Network 標籤

## 開發指南

### 修改 API 金鑰
編輯 `.env` 檔案：
```
GNEWS_API_KEY=your_new_api_key
```

### 添加新國家
1. 編輯 `app.py` 中的 `SUPPORTED_COUNTRIES` 字典
2. 添加國家代碼和名稱

### 添加新主題
1. 編輯 `app.py` 中的 `SUPPORTED_TOPICS` 字典
2. 添加主題代碼和名稱

### 自訂樣式
編輯 `static/style.css` 檔案以修改網站外觀。

## 限制

- GNews API 免費方案每月限制 100 次呼叫
- 每次最多返回 100 篇文章
- 分頁最多支援 1000 篇文章

## 許可證

本專案為開源專案，可自由使用和修改。

## 支援

如遇到問題，請檢查：
1. [GNews API 文件](https://docs.gnews.io/)
2. [Flask 官方文件](https://flask.palletsprojects.com/)
3. 本專案的 `API_INFO.md` 檔案

## 更新日誌

### v1.0 (2026-02-26)
- 初始版本發布
- 實現基本的新聞抓取和展示功能
- 支援 7 個國家和 3 個主題

---

**最後更新**：2026-02-26

**開發者**：財經新聞網站團隊
