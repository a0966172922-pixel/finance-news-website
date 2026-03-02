# GNews API 資訊

## API 基本資訊

**API 端點：** `https://gnews.io/api/v4/search`

**認證方式：** API 金鑰作為查詢參數 `apikey=YOUR_API_KEY`

## 支援的國家代碼

本專案目標地區的代碼：
- 印度 (India): `in`
- 新加坡 (Singapore): `sg`
- 馬來西亞 (Malaysia): `my`
- 泰國 (Thailand): `th`
- 越南 (Vietnam): `vn`
- 印尼 (Indonesia): `id`
- 菲律賓 (Philippines): `ph`

## 支援的語言代碼

- 英文 (English): `en`
- 中文 (Chinese): `zh`
- 印地文 (Hindi): `hi`
- 印尼文 (Indonesian): `id`

## API 查詢參數

| 參數名稱 | 預設值 | 說明 |
|---------|--------|------|
| `q` | 無 | **必填**。搜尋關鍵字，最多 200 字元 |
| `lang` | Any | 語言代碼 (2 字母) |
| `country` | Any | 國家代碼 (2 字母) |
| `max` | 10 | 返回的文章數量 (1-100) |
| `sortby` | publishedAt | 排序方式：`publishedAt` 或 `relevance` |
| `page` | 1 | 分頁頁碼 |

## API 回應格式

```json
{
  "totalArticles": 100,
  "articles": [
    {
      "title": "文章標題",
      "description": "文章摘要",
      "content": "完整文章內容",
      "image": "圖片 URL",
      "url": "原始文章 URL",
      "source": {
        "name": "新聞來源名稱",
        "url": "來源網站"
      },
      "publishedAt": "2025-07-18T21:32:58.500Z"
    }
  ]
}
```

## 搜尋範例

### 搜尋印度的財經新聞
```
GET https://gnews.io/api/v4/search?q=finance&country=in&lang=en&max=10&apikey=YOUR_API_KEY
```

### 搜尋東南亞的商業新聞
```
GET https://gnews.io/api/v4/search?q=business&country=sg&lang=en&max=10&apikey=YOUR_API_KEY
```

## 查詢語法

支援邏輯運算符：
- **AND**: `Apple AND Microsoft` (預設行為，空格即為 AND)
- **OR**: `Apple OR Microsoft`
- **NOT**: `Apple NOT iPhone`
- **引號**: `"Apple iPhone"` (精確搜尋)
- **括號**: `(Apple AND iPhone) OR Microsoft` (優先級控制)

## 費用說明

- 免費方案：每月 100 次 API 呼叫
- 需要更高額度時可升級付費方案
