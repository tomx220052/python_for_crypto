# 虛擬幣價格查詢工具

一個簡單的命令列工具，用於查詢虛擬幣在指定日期區間內的每日價格，並計算平均價格。

## 功能特色

- 查詢指定日期區間內的每日虛擬幣價格
- 自動計算平均價格（排除無資料的日期）
- 輸出為 CSV 格式，方便匯入 Excel 或其他工具
- 支援 CoinGecko Pro API key
- 自動重試機制（處理臨時性錯誤）
- 友善的進度顯示
- 完整的錯誤處理

## 系統需求

- Python 3.6 或以上版本
- 網路連線

## 安裝方式

### 方式一：使用 Python 執行

1. 確保已安裝 Python 3.6+
2. 安裝相依套件：
   ```bash
   pip3 install -r requirements.txt
   ```

### 方式二：使用可執行檔（免安裝 Python）

請參考「打包為可執行檔」章節。

## 使用方式

### 基本語法

```bash
python3 crypto_price_tool.py <幣種ID> --from <開始日期> --to <結束日期> --api-key <API金鑰>
```

### 參數說明

- `幣種ID`: CoinGecko 的幣種 ID（必填）
  - 例如：bitcoin, ethereum, tether, binancecoin
- `--from`: 開始日期，格式 YYYY-MM-DD（必填）
- `--to`: 結束日期，格式 YYYY-MM-DD（必填）
- `--api-key` 或 `-k`: CoinGecko Pro API key（必填）
- `--output` 或 `-o`: 輸出檔案名稱（選填，預設自動產生）
- `--delay` 或 `-d`: API 請求間隔秒數（選填，預設 5 秒）

### 使用範例

#### 1. 查詢 Bitcoin 最近一週的價格

```bash
python3 crypto_price_tool.py bitcoin \
  --from 2025-11-05 \
  --to 2025-11-12 \
  --api-key "你的API金鑰"
```

#### 2. 查詢 Ethereum 並指定輸出檔名

```bash
python3 crypto_price_tool.py ethereum \
  --from 2025-11-01 \
  --to 2025-11-10 \
  --api-key "你的API金鑰" \
  --output eth_november.csv
```

#### 3. 自訂 API 請求延遲（加快查詢速度，但可能觸發 rate limit）

```bash
python3 crypto_price_tool.py bitcoin \
  --from 2025-11-10 \
  --to 2025-11-12 \
  --api-key "你的API金鑰" \
  --delay 3
```

## 輸出格式

程式會產生 CSV 檔案，格式如下：

```csv
Date,Price (USD)
2025-11-10,N/A
2025-11-11,105909
2025-11-12,102961
Average,104435
```

- **Date**: 日期（YYYY-MM-DD 格式）
- **Price (USD)**: 該日的 USD 價格（四捨五入到整數）
- 如果某日無資料，顯示 `N/A`
- 最後一行顯示平均價格（排除 N/A 的日期）

## 限制與注意事項

### 日期限制

- **最早日期**: 2025-01-01
- **最晚日期**: 今天
- **日期關係**: 開始日期必須早於結束日期（至少 2 天）
- **最大區間**: 90 天

### API 限制

- CoinGecko Pro API 有 rate limit 限制
- 預設每次請求間隔 5 秒（可透過 `--delay` 調整）
- 查詢時間估算：
  - 10 天約需 50 秒
  - 30 天約需 2.5 分鐘
  - 90 天約需 7.5 分鐘

### 資料完整性

- 部分日期可能沒有資料（顯示為 N/A）
- 新上市的幣種可能沒有完整歷史資料
- 程式會自動重試 3 次，失敗後標記為 N/A

## 常見幣種 ID

| 幣種名稱 | CoinGecko ID |
|---------|--------------|
| Bitcoin | bitcoin |
| Ethereum | ethereum |
| Tether | tether |
| BNB | binancecoin |
| USDC | usd-coin |
| XRP | ripple |
| Cardano | cardano |
| Dogecoin | dogecoin |
| Solana | solana |
| TRON | tron |
| Polkadot | polkadot |
| Polygon | matic-network |
| Litecoin | litecoin |
| Shiba Inu | shiba-inu |
| Avalanche | avalanche-2 |

完整列表請參考：https://www.coingecko.com/

## 取得 CoinGecko API Key

1. 前往 CoinGecko 官網：https://www.coingecko.com/
2. 註冊帳號並登入
3. 前往 API 設定頁面
4. 申請 Pro API key
5. 複製 API key 並在使用工具時透過 `--api-key` 參數傳入

## 常見問題

### Q: 為什麼顯示「開始日期不能早於 2025-01-01」？

A: CoinGecko Pro API 的歷史資料有時間限制，目前僅支援 2025 年之後的資料。

### Q: 為什麼某些日期顯示 N/A？

A: 可能原因：
1. 該日期沒有交易資料
2. CoinGecko API 該日資料缺失
3. 網路暫時性錯誤

程式會自動重試 3 次，如果都失敗則標記為 N/A。

### Q: 可以一次查詢超過 90 天的資料嗎？

A: 目前限制最多 90 天，是為了：
- 避免過長的查詢時間
- 降低觸發 API rate limit 的風險
- 提供更好的使用體驗

如需更長時間的資料，建議分批查詢。

### Q: 為什麼查詢速度這麼慢？

A: CoinGecko API 的 history endpoint 每次只能查詢一天的資料，且有 rate limit 限制。為避免觸發 rate limit，程式預設每次請求間隔 5 秒。

如果您確定不會觸發 rate limit，可以透過 `--delay` 參數調整：

```bash
--delay 3  # 3 秒間隔（較快但可能觸發 rate limit）
--delay 2  # 2 秒間隔（更快但風險更高）
```

### Q: 執行時出現 401 Unauthorized 錯誤？

A: 請檢查：
1. API key 是否正確
2. API key 是否有效（未過期）
3. 是否正確使用 `--api-key` 參數

### Q: 執行時出現 429 Too Many Requests 錯誤？

A: 表示觸發了 API rate limit。程式會自動等待 5 秒後重試。如果頻繁出現，建議：
1. 增加 `--delay` 參數值
2. 減少查詢天數
3. 稍後再試

## 打包為可執行檔

請參考 `PACKAGING.md` 檔案。

## 授權

本專案為內部使用工具。

## 技術支援

如有問題，請聯繫開發團隊。
