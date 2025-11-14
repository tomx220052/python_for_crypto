# API 升級計劃：改用 market_chart/range

## 目標
從使用 CoinGecko `/coins/{id}/history` API 升級至 `/coins/{id}/market_chart/range` API

## API 差異分析

### 舊 API：`/coins/{id}/history`
- **Endpoint**: `GET /api/v3/coins/{id}/history`
- **參數**:
  - `date`: 單一日期 (dd-mm-yyyy)
  - `localization`: false
- **返回結構**:
  ```json
  {
    "market_data": {
      "current_price": {
        "usd": 42261.04
      }
    }
  }
  ```
- **限制**: 每次只能查詢一天，需要多次請求

### 新 API：`/coins/{id}/market_chart/range`
- **Endpoint**: `GET /api/v3/coins/{id}/market_chart/range`
- **參數**:
  - `vs_currency`: 目標貨幣 (usd)
  - `from`: 開始時間 (UNIX timestamp 秒)
  - `to`: 結束時間 (UNIX timestamp 秒)
  - `interval`: 資料粒度 (daily) - 可選
- **返回結構**:
  ```json
  {
    "prices": [
      [1704067241331, 42261.04],
      [1704153641331, 42493.28]
    ],
    "market_caps": [...],
    "total_volumes": [...]
  }
  ```
- **優勢**: 單次請求獲取整個日期範圍

## 改動項目清單

### 1. 修改 `CoinGeckoPriceFetcher` 類別

#### 1.1 修改 `__init__` 方法
- ❌ 移除 `delay` 參數（不再需要）
- ✅ 保留 `api_key` 參數
- ✅ 保留 `session` 物件

**位置**: crypto_price_tool.py:20-33

#### 1.2 重構 `get_price_on_date` → `get_range_prices_api`
- ❌ 移除原本的 `get_price_on_date` 方法（逐日查詢）
- ✅ 新增 `get_range_prices_api` 方法（範圍查詢）
- 功能：
  - 將 YYYY-MM-DD 日期轉換為 UNIX timestamp
  - 調用新 API endpoint
  - 解析 `prices` 陣列
  - 將 timestamp 轉回日期格式
  - 處理每日可能多筆數據的情況

**位置**: crypto_price_tool.py:35-99

#### 1.3 簡化 `get_range_prices` 方法
- ❌ 移除逐日循環邏輯 (for i in range(num_days))
- ❌ 移除 delay 機制 (time.sleep)
- ❌ 移除逐日進度顯示
- ✅ 改為調用 `get_range_prices_api` 一次性獲取數據
- ✅ 保留整體進度提示
- ✅ 數據格式轉換：timestamp → 日期字串
- ✅ 處理缺失日期：補充 None 值

**位置**: crypto_price_tool.py:101-149

### 2. 修改命令列參數

#### 2.1 移除 `--delay` 參數
- ❌ 移除 `parser.add_argument('-d', '--delay', ...)`
- ❌ 移除 help 文件中的 delay 範例

**位置**: crypto_price_tool.py:282-287, 246-247

#### 2.2 更新說明文字
- 移除提及 API 請求間隔的說明
- 更新時間估算（因為速度變快）

**位置**: crypto_price_tool.py:323

### 3. 修改 `main` 函數

#### 3.1 移除 delay 相關代碼
- ❌ 移除 `args.delay` 的顯示
- ❌ 移除傳遞 `delay` 參數給 `CoinGeckoPriceFetcher`

**位置**: crypto_price_tool.py:323-328

### 4. 數據處理邏輯

#### 4.1 日期格式轉換
- 輸入：YYYY-MM-DD 字串
- 中間：UNIX timestamp (秒)
- 輸出：YYYY-MM-DD 字串

#### 4.2 處理多筆同日數據
策略：取該日最後一筆數據（最接近當日結束）
- API 可能返回一天多個時間點
- 需要按日期聚合

#### 4.3 處理缺失日期
- API 可能不返回某些日期的數據
- 需要補充 None 值以保持日期連續性

### 5. 錯誤處理

#### 5.1 保留基本錯誤處理
- ✅ HTTP 錯誤 (404, 429, 500+)
- ✅ 網路超時
- ✅ JSON 解析錯誤
- ✅ 數據缺失處理

#### 5.2 簡化重試機制
- 保留單次重試（max_retries=3）
- 移除複雜的 backoff 邏輯

### 6. 文件更新

#### 6.1 更新 README.md
- 移除 `--delay` 參數說明
- 更新時間估算
- 更新範例命令

#### 6.2 更新 todo.md
- 標記此升級任務完成
- 記錄 API 版本變更

## 實作細節

### 日期轉 UNIX timestamp
```python
from datetime import datetime

def date_to_timestamp(date_str):
    """將 YYYY-MM-DD 轉換為 UNIX timestamp (秒)"""
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return int(dt.timestamp())

def timestamp_to_date(timestamp_ms):
    """將 UNIX timestamp (毫秒) 轉換為 YYYY-MM-DD"""
    dt = datetime.fromtimestamp(timestamp_ms / 1000)
    return dt.strftime("%Y-%m-%d")
```

### 新 API 請求範例
```python
url = f"{self.BASE_URL}/coins/{coin_id}/market_chart/range"
params = {
    'vs_currency': 'usd',
    'from': date_to_timestamp(from_date),  # UNIX timestamp (秒)
    'to': date_to_timestamp(to_date),      # UNIX timestamp (秒)
    'interval': 'daily',                    # 每日一筆
    'x-cg-pro-api-key': 'CG-2wCtiaEmkTfLhz6PUsQDyBiR'
}
response = self.session.get(url, params=params, timeout=30)
data = response.json()

# 解析 prices
prices_array = data['prices']  # [[timestamp_ms, price], ...]
```

### 數據聚合邏輯
```python
# 將 timestamp 按日期分組
from collections import defaultdict

daily_prices = defaultdict(list)
for timestamp_ms, price in data['prices']:
    date_str = timestamp_to_date(timestamp_ms)
    daily_prices[date_str].append(price)

# 每日取最後一筆（或平均值）
result = []
for date_str in sorted(daily_prices.keys()):
    price = daily_prices[date_str][-1]  # 取最後一筆
    # price = sum(prices) / len(prices)  # 或取平均
    result.append({'date': date_str, 'price': round(price)})
```

## 測試計劃

### 測試案例

#### TC1: 基本功能測試
```bash
python crypto_price_tool.py bitcoin --from 2025-11-01 --to 2025-11-10
```
預期：
- 成功返回 10 天數據
- CSV 格式正確
- 平均價格計算正確

#### TC2: 長日期範圍測試
```bash
python crypto_price_tool.py ethereum --from 2025-09-01 --to 2025-11-13
```
預期：
- 73 天數據（接近 90 天限制）
- 速度明顯提升（從 ~6 分鐘降至 ~2 秒）

#### TC3: 錯誤處理測試
```bash
# 錯誤的幣種 ID
python crypto_price_tool.py invalid_coin --from 2025-11-01 --to 2025-11-10

# 未來日期
python crypto_price_tool.py bitcoin --from 2025-12-01 --to 2025-12-31
```
預期：
- 顯示友善錯誤訊息
- 不會崩潰

#### TC4: 缺失數據測試
```bash
# 某些新幣種可能沒有早期數據
python crypto_price_tool.py new-coin --from 2025-01-01 --to 2025-01-31
```
預期：
- 缺失日期標記為 N/A
- 平均價格僅計算有效數據

#### TC5: API Key 測試
```bash
python crypto_price_tool.py bitcoin --from 2025-11-01 --to 2025-11-10 --api-key INVALID_KEY
```
預期：
- 顯示認證錯誤

### 性能對比

| 查詢天數 | 舊 API 時間 | 新 API 時間 | 提升比例 |
|---------|-----------|-----------|---------|
| 10 天   | ~50 秒    | ~2 秒     | 25x     |
| 30 天   | ~2.5 分鐘 | ~2 秒     | 75x     |
| 90 天   | ~7.5 分鐘 | ~2 秒     | 225x    |

## 潛在風險與注意事項

### 風險 1: API 返回數據格式變化
- **描述**: timestamp 可能是毫秒或秒
- **緩解**: 檢測數值大小自動判斷
- **程式碼**:
  ```python
  if timestamp > 1e12:  # 毫秒
      timestamp = timestamp / 1000
  ```

### 風險 2: 一天多筆數據
- **描述**: 即使設定 `interval=daily`，API 可能返回多筆
- **緩解**: 實作聚合邏輯（取最後一筆或平均）
- **已規劃**: 見上方數據聚合邏輯

### 風險 3: Rate Limit 變化
- **描述**: 雖然請求次數減少，但新 API 可能有不同限制
- **緩解**: 保留基本重試機制
- **監控**: 觀察 429 錯誤

### 風險 4: 向後兼容性
- **描述**: 輸出格式需保持一致
- **緩解**: 確保 CSV 格式不變
- **測試**: 對比升級前後的輸出

### 風險 5: 缺失日期處理
- **描述**: 新 API 可能跳過無交易的日期
- **緩解**: 實作日期補全邏輯
- **測試**: 使用已知有缺失的日期範圍測試

## 回滾計劃

若升級後發現嚴重問題，可回滾至舊版本：

```bash
git checkout HEAD~1 crypto_price_tool.py
```

或手動恢復關鍵方法：
- 恢復 `get_price_on_date` 方法
- 恢復 `get_range_prices` 的循環邏輯
- 恢復 `--delay` 參數

## 時間估算

- 代碼修改：1-2 小時
- 測試驗證：1 小時
- 文件更新：30 分鐘
- **總計：2.5-3.5 小時**

## 完成標準

- [ ] 所有代碼修改完成
- [ ] 通過所有測試案例
- [ ] 性能提升符合預期
- [ ] 輸出格式保持一致
- [ ] 文件更新完成
- [ ] 無明顯錯誤或警告

## 後續優化建議（v2.0）

1. **API Key 管理**
   - 從環境變數讀取 API key
   - 支援 `.env` 文件
   - 移除 hardcoded key

2. **多幣種查詢**
   - 支援一次查詢多個幣種
   - 並行請求提升速度

3. **輸出格式擴充**
   - 支援 JSON 輸出
   - 支援 Excel 格式
   - 包含 market cap 和 volume

4. **圖表功能**
   - 使用 matplotlib 產生價格走勢圖
   - 支援技術指標（MA, RSI 等）

5. **快取機制**
   - 快取已查詢的數據
   - 避免重複請求

---

**建立日期**: 2025-11-13
**版本**: 1.0
**負責人**: Howard Chang
