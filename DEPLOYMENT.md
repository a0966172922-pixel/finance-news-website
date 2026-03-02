# 部署到 Render 的步驟

本文件說明如何將財經新聞網站部署到 Render 作為永久網站。

## 前置條件

1. **GitHub 帳號** - 如果您還沒有，請在 [github.com](https://github.com) 註冊
2. **Render 帳號** - 在 [render.com](https://render.com) 註冊（可使用 GitHub 帳號登入）
3. **GNews API 金鑰** - 從 [gnews.io](https://gnews.io) 獲取

## 部署步驟

### 第 1 步：創建 GitHub 倉庫

1. 登入 GitHub
2. 點擊右上角的 `+` 圖標，選擇 `New repository`
3. 填寫倉庫信息：
   - **Repository name**: `finance-news-website`
   - **Description**: `財經新聞網站 - 印度與東南亞新聞聚合`
   - **Visibility**: 選擇 `Public`（Render 需要公開倉庫）
4. 點擊 `Create repository`

### 第 2 步：推送代碼到 GitHub

在您的本地電腦上執行以下命令（或使用 GitHub Desktop）：

```bash
cd /home/ubuntu/finance_news_website

# 初始化 Git 倉庫
git init

# 添加所有文件
git add .

# 提交更改
git commit -m "Initial commit: Finance news website"

# 添加遠程倉庫（替換 YOUR_USERNAME 和 YOUR_REPO_NAME）
git remote add origin https://github.com/YOUR_USERNAME/finance-news-website.git

# 推送到 GitHub
git branch -M main
git push -u origin main
```

### 第 3 步：在 Render 上創建新服務

1. 登入 [render.com](https://render.com)
2. 點擊 `New +` 按鈕，選擇 `Web Service`
3. 選擇 `Connect a repository`
4. 授權 GitHub 並選擇您剛才創建的 `finance-news-website` 倉庫
5. 填寫服務信息：
   - **Name**: `finance-news-website`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: 選擇 `Free`（免費方案）

### 第 4 步：配置環境變數

1. 在 Render 服務頁面，找到 `Environment` 部分
2. 點擊 `Add Environment Variable`
3. 添加以下環境變數：
   - **Key**: `GNEWS_API_KEY`
   - **Value**: 您的 GNews API 金鑰
4. 點擊 `Save`

### 第 5 步：部署

1. Render 會自動開始部署
2. 在 `Logs` 標籤中查看部署進度
3. 部署完成後，您會看到一個公開網址，格式如：`https://finance-news-website.onrender.com`

## 常見問題

### Q: 網站在 15 分鐘無活動後進入休眠，如何解決？

**A**: 有幾個選項：

1. **升級到付費方案** - 點擊 `Instance Type` 改為 `Paid`（最低 $7/月）
2. **定期訪問網站** - 保持網站活動以避免休眠
3. **使用監控工具** - 使用免費的監控服務（如 UptimeRobot）定期 ping 網站

### Q: 如何更新網站代碼？

**A**: 只需在本地修改代碼後推送到 GitHub：

```bash
git add .
git commit -m "Your commit message"
git push origin main
```

Render 會自動檢測更改並重新部署。

### Q: API 金鑰洩露了怎麼辦？

**A**: 立即：

1. 在 GNews 控制面板重新生成 API 金鑰
2. 在 Render 環境變數中更新新金鑰
3. 確保 `.env` 文件在 `.gitignore` 中（已包含）

### Q: 如何查看網站日誌？

**A**: 在 Render 服務頁面點擊 `Logs` 標籤查看實時日誌。

## 支援的功能

- ✅ 從 GNews API 抓取財經新聞
- ✅ 支援 7 個國家（印度、新加坡、馬來西亞、泰國、越南、印尼、菲律賓）
- ✅ 支援 3 個主題（財經、商業、經濟）
- ✅ 自動中文翻譯（使用 OpenAI）
- ✅ 響應式設計（支援手機、平板、桌面）

## 獲得幫助

如有問題，請：

1. 查看 Render 的 [文檔](https://render.com/docs)
2. 檢查 Flask 應用的日誌
3. 確認 GNews API 金鑰有效

---

**部署完成！** 🎉

您的財經新聞網站現在已經在互聯網上永久運行。祝您使用愉快！
