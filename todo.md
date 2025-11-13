# 虛擬幣價格查詢工具 - 開發計畫

## 專案概述

**目標：** 建立一個 Python 工具，取得指定虛擬幣在指定日期區間內每日的價格，並計算平均價格，輸出為 CSV 檔案

**輸入參數：**
- 幣種 ID（如：bitcoin, ethereum, tether）- 直接使用 CoinGecko coin ID
- from 日期（格式：YYYY-MM-DD）
- to 日期（格式：YYYY-MM-DD）

**輸出：**
- CSV 檔案，包含每日價格和平均價格
- 檔名格式：`{coin}_{from}_{to}_prices.csv`
- 例如：`bitcoin_2024-01-01_2024-01-31_prices.csv`

**技術選型：**
- 語言：Python 3
- API：CoinGecko API (https://api.coingecko.com)
- 打包：PyInstaller（產生可執行檔，免安裝 Python）

---

## 技術架構設計

### API 選擇
- **使用 API：** `https://api.coingecko.com/api/v3/coins/{coin_id}/history?date={dd-mm-yyyy}`
- **優點：**
  - 免費額度充足
  - 穩定可靠
  - 有歷史資料
- **限制：**
  - 每次請求只能取得一天的資料
  - 查詢 N 天需要 N 次 API 調用
  - 免費版有 rate limit（約 10-50 次/分鐘）
  - 需要加入延遲機制：**1 秒/次**

### 程式架構

```
crypto_price_tool.py         # 主程式
├── CoinGeckoPriceFetcher   # API 查詢類別
│   ├── get_price_on_date() # 取得單日價格（含重試機制）
│   └── get_range_prices()  # 取得日期區間價格
├── save_to_csv()           # CSV 輸出功能
├── parse_arguments()       # 命令列參數解析
└── main()                  # 主流程
```

---

## 功能規格

### 日期限制與驗證
- **最早日期：** 2009-01-01（比特幣誕生日）
- **最晚日期：** 今天（不能查詢未來）
- **日期關係：** from < to（必須至少 2 天，不允許 from = to）
- **最大區間：** 90 天

### 價格格式
- **處理方式：** 四捨五入到整數
- **顯示格式：** 純數字，不加貨幣符號
- **範例：** 43500 (不是 $43,500.00)

### 缺失資料處理
- **重試機制：** 如果 API 沒有回傳資料，重試 2 次（共調用 3 次）
- **失敗處理：** 3 次都失敗後，CSV 中該日顯示 "N/A"
- **平均值計算：** N/A 的日期不計入平均值計算

### 進度顯示
在終端機顯示查詢進度，範例：
```
查詢 2024-01-01... ✓ 43500
查詢 2024-01-02... ✓ 44200
查詢 2024-01-03... ✗ 無資料
```

---

## 開發任務清單

### Phase 1: 環境設置
- [ ] 建立專案資料夾結構
- [ ] 建立 `requirements.txt`
  - requests
  - pyinstaller
- [ ] 建立 `.gitignore`（如果需要版本控制）

### Phase 2: 核心功能開發
- [ ] **API 整合模組**
  - [ ] 實作 CoinGeckoPriceFetcher 類別
  - [ ] 實作單日價格查詢功能 get_price_on_date()
    - 發送 HTTP 請求
    - 解析 JSON response
    - 取得 USD 價格
    - 重試機制（3 次）
  - [ ] 加入 rate limit 延遲機制（1 秒）
  - [ ] 加入錯誤處理（404, 429, timeout 等）
  - [ ] 實作日期區間價格查詢功能 get_range_prices()
    - 計算日期區間內所有日期
    - 迴圈調用 get_price_on_date()
    - 處理缺失資料（顯示 N/A）

- [ ] **資料處理模組**
  - [ ] 計算兩個日期之間的天數
  - [ ] 計算平均價格（排除 N/A）
  - [ ] 價格四捨五入到整數

- [ ] **CSV 輸出模組**
  - [ ] 實作 CSV 寫入功能
  - [ ] 欄位設計：Date, Price (USD)
  - [ ] 最後一行加入平均價格
  - [ ] 自動產生檔名：`{coin}_{from}_{to}_prices.csv`

- [ ] **命令列介面**
  - [ ] 使用 argparse 解析參數
  - [ ] 參數設計：
    - 必填：coin_id, --from, --to
    - 選填：--output（輸出檔案名稱）, --delay（延遲時間）
  - [ ] 加入 help 說明和使用範例

### Phase 3: 錯誤處理與驗證
- [ ] **輸入驗證**
  - [ ] 驗證 from 日期格式（YYYY-MM-DD）
  - [ ] 驗證 to 日期格式（YYYY-MM-DD）
  - [ ] 驗證 from < to（不允許相等）
  - [ ] 驗證日期不早於 2009-01-01
  - [ ] 驗證日期不晚於今天
  - [ ] 驗證日期區間不超過 90 天
  - [ ] 驗證幣種是否存在（透過 API 回應）

- [ ] **錯誤處理**
  - [ ] 網路錯誤處理
  - [ ] API 錯誤處理（404, 429, 500）
  - [ ] 檔案寫入錯誤處理
  - [ ] 使用者中斷處理（Ctrl+C）

- [ ] **進度顯示**
  - [ ] 顯示查詢進度（日期 + 結果）
  - [ ] 顯示成功/失敗狀態（✓ / ✗）
  - [ ] 顯示最終統計資料

### Phase 4: 測試
- [ ] **功能測試**
  - [ ] 測試查詢最近的日期區間（如 2024-10-01 ~ 2024-10-10）
  - [ ] 測試不同幣種（bitcoin, ethereum, tether）
  - [ ] 測試不同天數區間（2 天、30 天、90 天）
  - [ ] 測試 CSV 輸出格式
  - [ ] 測試平均價格計算正確性
  - [ ] 測試價格四捨五入

- [ ] **錯誤測試**
  - [ ] 測試錯誤的幣種名稱
  - [ ] 測試錯誤的日期格式
  - [ ] 測試 from >= to 的情況
  - [ ] 測試未來日期
  - [ ] 測試超過 90 天的區間
  - [ ] 測試網路中斷情況

- [ ] **邊界測試**
  - [ ] 測試最早日期（2009-01-01）
  - [ ] 測試今天的日期
  - [ ] 測試剛好 90 天的區間
  - [ ] 測試 rate limit 機制
  - [ ] 測試缺失資料處理（N/A）

### Phase 5: 文件與打包
- [ ] **使用文件**
  - [ ] 建立 README.md
    - 功能說明
    - 安裝方式
    - 使用方式
    - 參數說明
    - 使用範例
    - 常見問題
  - [ ] 建立使用範例

- [ ] **PyInstaller 打包**
  - [ ] 建立打包說明文件
  - [ ] 測試打包指令：`pyinstaller --onefile crypto_price_tool.py`
  - [ ] 測試可執行檔在乾淨環境執行
  - [ ] 確認檔案大小合理
  - [ ] 建立不同平台版本（Windows/macOS/Linux，視需求）

- [ ] **交付準備**
  - [ ] 整理專案結構
  - [ ] 準備使用說明文件
  - [ ] 測試客戶端環境執行

---

## 技術細節說明

### CoinGecko API 使用

**Endpoint:** `/coins/{id}/history`

**參數：**
- `id`: 幣種 ID（如 bitcoin, ethereum, tether）
- `date`: 日期格式 **dd-mm-yyyy**（注意：是 dd-mm-yyyy，不是 YYYY-MM-DD）
  - 例如：01-01-2024（表示 2024 年 1 月 1 日）
- `localization`: false（不需要多語言）

**Request 範例：**
```
GET https://api.coingecko.com/api/v3/coins/bitcoin/history?date=01-01-2024&localization=false
```

**Response 範例：**
```json
{
  "id": "bitcoin",
  "symbol": "btc",
  "name": "Bitcoin",
  "market_data": {
    "current_price": {
      "usd": 43500.25,
      "eur": 38200.10,
      ...
    }
  }
}
```

**取得價格：** `response['market_data']['current_price']['usd']`

### 日期格式轉換

**輸入格式：** YYYY-MM-DD（如 2024-01-01）
**API 需要格式：** dd-mm-yyyy（如 01-01-2024）

Python 轉換範例：
```python
from datetime import datetime

input_date = "2024-01-01"
dt = datetime.strptime(input_date, "%Y-%m-%d")
api_date = dt.strftime("%d-%m-%Y")  # "01-01-2024"
```

### CSV 輸出格式範例

```csv
Date,Price (USD)
2024-01-01,43500
2024-01-02,44120
2024-01-03,N/A
2024-01-04,45678
Average,44433
```

**注意：**
- 價格為整數（四捨五入）
- 無資料顯示 N/A
- 平均價格排除 N/A 後計算

### 命令列參數範例

```bash
# 基本使用
python crypto_price_tool.py bitcoin --from 2024-01-01 --to 2024-01-31

# 指定輸出檔名
python crypto_price_tool.py ethereum --from 2024-01-01 --to 2024-01-10 --output eth_jan.csv

# 自訂延遲時間
python crypto_price_tool.py bitcoin --from 2024-01-01 --to 2024-01-31 --delay 2
```

---

## 風險與注意事項

### API 限制
- **Rate Limit:** 免費版約 10-50 次/分鐘
- **解決方案:** 每次請求間隔 1 秒（可調整）
- **估計時間:**
  - 查詢 30 天約需 30 秒（不含重試）
  - 查詢 90 天約需 90 秒（1.5 分鐘）

### 資料完整性
- 部分舊日期可能沒有資料（特別是 2009-2010 年）
- 新上市的幣種可能沒有完整歷史資料
- 需要重試機制和 N/A 處理

### PyInstaller 打包
- 打包後的檔案較大（約 10-20 MB）
- 不同作業系統需要分別打包
- 防毒軟體可能誤報（需要白名單設定）

### 日期區間限制
- 最大 90 天的限制是為了：
  1. 避免過長的 API 調用時間
  2. 避免觸發 rate limit
  3. 提供更好的使用體驗
- 如需更長區間，建議分批查詢

---

## 預估時程

- Phase 1: 0.5 小時
- Phase 2: 2-3 小時
- Phase 3: 1 小時
- Phase 4: 1-2 小時
- Phase 5: 1 小時

**總計：5.5-7.5 小時**

---

## 後續優化建議（V2.0）

- [ ] 支援多幣種同時查詢
- [ ] 移除 90 天限制，改用進度條顯示
- [ ] 加入資料視覺化（圖表）
- [ ] 支援更多輸出格式（Excel, JSON）
- [ ] 加入快取機制（避免重複查詢）
- [ ] 支援其他交易所 API
- [ ] 支援多幣別（不只 USD，加入 EUR, TWD 等）
- [ ] 提供 GUI 介面
- [ ] 加入統計資訊（最高價、最低價、中位數等）
