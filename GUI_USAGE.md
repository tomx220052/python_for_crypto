# GUI 版本使用說明

## 🚀 快速開始

### 1. 安裝依賴

```bash
pip3 install -r requirements.txt
```

### 2. 啟動 GUI 版本

```bash
python3 crypto_price_gui.py
```

或直接雙擊執行（如果已賦予執行權限）：

```bash
./crypto_price_gui.py
```

---

## 📖 使用步驟

### 步驟 1：輸入幣種 ID

在「幣種 ID」欄位輸入您要查詢的幣種，例如：
- `bitcoin` - 比特幣
- `ethereum` - 以太坊
- `tether` - 泰達幣
- `binancecoin` - BNB

💡 **提示：** 更多幣種 ID 請參考 [CoinGecko 官網](https://www.coingecko.com/)

### 步驟 2：選擇日期區間

- **開始日期：** 輸入格式 `YYYY-MM-DD`，例如 `2025-11-10`
- **結束日期：** 輸入格式 `YYYY-MM-DD`，例如 `2025-11-13`

⚠️ **限制：**
- 日期不能早於 2025-01-01
- 日期不能是未來日期
- 日期區間不能超過 100 天

### 步驟 3：輸入 API Key（可選）

如果您有 CoinGecko Pro API Key，可以輸入以獲得更穩定的服務。

🔒 **安全提示：** 您的 API Key 不會被儲存到任何地方。

### 步驟 4：開始查詢

點擊「🔍 開始查詢」按鈕，等待查詢完成。

查詢過程中您會看到：
- 進度條顯示查詢進度
- 每日價格即時顯示
- 統計資訊（平均價、最高價、最低價）

### 步驟 5：匯出結果

查詢完成後，點擊「📥 匯出 CSV」按鈕，選擇儲存位置即可。

---

## 🎨 介面說明

### 查詢設定區
- **幣種 ID：** 輸入 CoinGecko 幣種 ID（文字輸入框）
- **日期區間：** 輸入開始和結束日期
- **API Key：** 可選，輸入後顯示為星號保護

### 查詢結果區
- **進度條：** 顯示查詢進度百分比
- **價格表格：** 顯示每日日期、價格和狀態
- **統計卡片：** 顯示平均價、最高價、最低價

### 操作按鈕
- **📥 匯出 CSV：** 將結果匯出為 CSV 檔案
- **🗑️ 清空：** 清空當前查詢結果

### 狀態列
顯示當前操作狀態和最後查詢時間。

---

## ❗ 常見問題

### Q1: 為什麼查詢失敗？

**可能原因：**
1. 幣種 ID 輸入錯誤 → 檢查拼寫是否正確
2. 日期格式不正確 → 使用 YYYY-MM-DD 格式
3. 日期超過限制 → 確保在 2025-01-01 之後且不超過 100 天
4. 網路連線問題 → 檢查網路連線

### Q2: 為什麼某些日期顯示「無資料」？

**可能原因：**
1. 該日期幣種尚未上市
2. CoinGecko 該日期無交易資料
3. 查詢過於頻繁被限制 → 使用 API Key 可緩解

### Q3: 如何找到幣種 ID？

訪問 [CoinGecko](https://www.coingecko.com/)，搜尋您要的幣種，網址中的最後一段就是 ID。

例如：
- `https://www.coingecko.com/en/coins/bitcoin` → ID 是 `bitcoin`
- `https://www.coingecko.com/en/coins/ethereum` → ID 是 `ethereum`

### Q4: GUI 視窗無法開啟？

**解決方法：**
1. 確認已安裝 `customtkinter`：`pip3 install customtkinter`
2. 確認 Python 版本 >= 3.7
3. 嘗試在終端機執行：`python3 crypto_price_gui.py`，查看錯誤訊息

### Q5: 可以同時查詢多個幣種嗎？

目前 MVP 版本僅支援單一幣種查詢，多幣種查詢功能計劃在 v2.1 版本實作。

---

## 💡 進階技巧

### 快速重複查詢

如果您需要多次查詢：
1. 查詢完成後先匯出 CSV
2. 點擊「清空」按鈕
3. 修改參數後再次查詢

### 獲取 API Key

1. 註冊 [CoinGecko Pro](https://www.coingecko.com/en/api/pricing)
2. 選擇合適的方案（有免費方案）
3. 在儀表板取得 API Key
4. 將 Key 貼到 GUI 的「API Key」欄位

---

## 🐛 問題回報

如果遇到任何問題，請提供以下資訊：

1. 作業系統版本
2. Python 版本（`python3 --version`）
3. 錯誤訊息截圖
4. 操作步驟

---

## 🎯 下一步

想了解更多功能？查看 `gui-upgrade-todo.md` 了解未來計劃！
