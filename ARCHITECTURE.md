# 專案架構說明文檔

## 📚 目錄
1. [專案概述](#專案概述)
2. [目錄結構](#目錄結構)
3. [架構設計](#架構設計)
4. [模組說明](#模組說明)
5. [資料流程](#資料流程)
6. [設計模式](#設計模式)
7. [依賴關係](#依賴關係)

---

## 專案概述

**專案名稱：** 虛擬幣價格查詢工具
**版本：** v2.0 MVP
**架構風格：** 模組化分層架構 (Modular Layered Architecture)
**程式語言：** Python 3.7+
**GUI 框架：** CustomTkinter (基於 Tkinter)

### 核心功能
- 查詢虛擬幣歷史價格（透過 CoinGecko API）
- 計算價格統計資訊（平均、最高、最低）
- 匯出 CSV 報表
- 提供 CLI 和 GUI 兩種使用介面

---

## 目錄結構

```
python_for_crypto2/
│
├── src/                          # 核心業務邏輯層
│   ├── __init__.py              # 模組初始化
│   ├── core.py                  # API 查詢邏輯（CoinGeckoPriceFetcher）
│   ├── utils.py                 # 工具函數（驗證、計算、匯出）
│   └── constants.py             # 常數定義（幣種列表、限制）
│
├── crypto_price_gui.py          # GUI 應用層（CustomTkinter）
├── crypto_price_tool.py         # CLI 應用層（argparse）
├── test_price_precision.py      # 測試工具
│
├── requirements.txt             # Python 依賴清單
├── crypto_price_tool.spec       # PyInstaller 打包配置
│
├── start_gui.bat                # Windows 啟動腳本
├── start_gui.sh                 # macOS/Linux 啟動腳本
│
├── dist/                        # 打包輸出目錄
├── build/                       # 打包暫存目錄
│
└── *.md                         # 文檔
    ├── README.md                # 專案說明
    ├── ARCHITECTURE.md          # 架構文檔（本檔案）
    ├── INSTALLATION.md          # 安裝指南
    ├── GUI_USAGE.md             # GUI 使用說明
    ├── PACKAGING.md             # 打包指南
    └── ...
```

---

## 架構設計

### 分層架構圖

```
┌─────────────────────────────────────────────────────────┐
│                  應用層 (Application Layer)              │
│  ┌──────────────────────┐  ┌──────────────────────┐    │
│  │  crypto_price_gui.py │  │ crypto_price_tool.py │    │
│  │   (GUI Interface)    │  │   (CLI Interface)    │    │
│  └──────────┬───────────┘  └──────────┬───────────┘    │
└─────────────┼───────────────────────────┼───────────────┘
              │                           │
              └───────────┬───────────────┘
                          │
┌─────────────────────────┼───────────────────────────────┐
│               業務邏輯層 (Business Logic Layer)          │
│                         │                                │
│  ┌─────────────────────┴──────────────────┐            │
│  │         src/ (核心模組)                 │            │
│  │                                         │            │
│  │  ┌──────────────────────────────────┐  │            │
│  │  │  core.py                         │  │            │
│  │  │  • CoinGeckoPriceFetcher         │  │            │
│  │  │  • API 請求邏輯                  │  │            │
│  │  │  • 價格數據處理                  │  │            │
│  │  └──────────────────────────────────┘  │            │
│  │                                         │            │
│  │  ┌──────────────────────────────────┐  │            │
│  │  │  utils.py                        │  │            │
│  │  │  • 日期驗證                      │  │            │
│  │  │  • 統計計算                      │  │            │
│  │  │  • CSV 匯出                      │  │            │
│  │  └──────────────────────────────────┘  │            │
│  │                                         │            │
│  │  ┌──────────────────────────────────┐  │            │
│  │  │  constants.py                    │  │            │
│  │  │  • 幣種列表                      │  │            │
│  │  │  • 業務常數                      │  │            │
│  │  └──────────────────────────────────┘  │            │
│  └─────────────────────────────────────┘  │            │
└───────────────────────┬───────────────────────────────┘
                        │
┌───────────────────────┼───────────────────────────────┐
│             外部 API 層 (External API Layer)           │
│                       │                                │
│  ┌────────────────────▼──────────────────────┐        │
│  │       CoinGecko API (REST)                │        │
│  │  • /coins/{id}/market_chart/range         │        │
│  │  • 返回歷史價格數據                       │        │
│  └───────────────────────────────────────────┘        │
└────────────────────────────────────────────────────────┘
```

### 架構特點

1. **分層清晰**
   - 應用層：負責使用者介面（GUI/CLI）
   - 業務邏輯層：負責核心功能（API 查詢、數據處理）
   - 外部 API 層：與第三方服務互動

2. **模組化**
   - 每個模組職責單一
   - 高內聚、低耦合
   - 易於測試和維護

3. **可擴展性**
   - 新增幣種：修改 `constants.py`
   - 新增 UI：實作新的應用層
   - 替換 API：修改 `core.py`

---

## 模組說明

### 1. `src/core.py` - API 查詢核心

**職責：** 封裝 CoinGecko API 的查詢邏輯

#### 主要類別：`CoinGeckoPriceFetcher`

```python
class CoinGeckoPriceFetcher:
    """CoinGecko API 價格查詢類別"""

    BASE_URL = "https://api.coingecko.com/api/v3"

    def __init__(self, api_key=None):
        """初始化，可選 API Key"""

    def get_range_prices_api(self, coin_id, from_date, to_date, ...):
        """呼叫 market_chart/range API 取得價格區間"""

    def get_range_prices(self, coin_id, from_date, to_date,
                         progress_callback=None):
        """完整查詢流程，支援進度回調"""
```

**核心功能：**
- ✅ HTTP 請求管理（使用 `requests.Session`）
- ✅ 日期時間轉換（YYYY-MM-DD ↔ UNIX timestamp）
- ✅ API 數據解析（處理 JSON 響應）
- ✅ 價格數據篩選（選擇 UTC 16:00 的價格）
- ✅ 錯誤處理與重試機制（最多 3 次）
- ✅ 進度回調支援（供 GUI 使用）

**設計亮點：**
```python
# 支援進度回調，解耦 UI 和業務邏輯
if progress_callback:
    progress_callback(current=i+1, total=num_days,
                     date=date_str, price=price, success=True)
```

---

### 2. `src/utils.py` - 工具函數庫

**職責：** 提供通用的工具函數

#### 主要函數

| 函數名稱 | 功能 | 輸入 | 輸出 |
|---------|------|------|------|
| `validate_date()` | 驗證單一日期 | 日期字串 | datetime 物件 |
| `validate_date_range()` | 驗證日期區間 | 開始/結束日期 | (from_dt, to_dt) |
| `save_to_csv()` | 匯出 CSV | 價格列表 | 檔案路徑 |
| `calculate_statistics()` | 計算統計資訊 | 價格列表 | 統計字典 |

**設計特點：**

1. **純函數設計**
   - 無副作用（除了檔案 I/O）
   - 易於測試
   - 可重複使用

2. **完整的錯誤處理**
   ```python
   def validate_date(date_str, date_name="日期"):
       try:
           dt = datetime.strptime(date_str, "%Y-%m-%d")
       except ValueError:
           raise ValueError(f"{date_name} 格式錯誤...")

       # 業務規則驗證
       if dt < min_date:
           raise ValueError(...)
   ```

3. **返回值設計**
   ```python
   def calculate_statistics(prices):
       return {
           'avg': round(..., 4),      # 平均價
           'max': max(...),           # 最高價
           'min': min(...),           # 最低價
           'valid_count': len(...),   # 有效筆數
           'total_count': len(prices) # 總筆數
       }
   ```

---

### 3. `src/constants.py` - 常數定義

**職責：** 集中管理業務常數

#### 主要內容

```python
# 幣種列表（48 種）
COIN_LIST = [
    {"symbol": "BTC", "id": "bitcoin", "name": "Bitcoin"},
    {"symbol": "ETH", "id": "ethereum", "name": "Ethereum"},
    # ... 46 more
]

# 顯示文字 → ID 映射
COIN_MAPPING = {
    "BTC - Bitcoin": "bitcoin",
    "ETH - Ethereum": "ethereum",
    # ...
}

# 業務限制
DATE_MIN = "2025-01-01"
DATE_MAX_DAYS = 100
```

**設計優點：**
- ✅ 單一資料來源（Single Source of Truth）
- ✅ 易於維護（新增幣種只需修改一處）
- ✅ 避免魔術數字（Magic Numbers）

---

### 4. `crypto_price_gui.py` - GUI 應用

**職責：** 提供圖形化使用者介面

#### 主要類別：`CryptoPriceGUI`

```python
class CryptoPriceGUI(ctk.CTk):
    """主 GUI 視窗"""

    def __init__(self):
        """初始化視窗和 UI 元件"""

    def setup_ui(self):
        """建立 UI 佈局"""

    def on_query_clicked(self):
        """查詢按鈕事件處理"""

    def perform_query(self, ...):
        """執行查詢（在背景執行緒）"""

    def display_results(self, prices):
        """顯示查詢結果"""

    def on_export_clicked(self):
        """匯出 CSV 事件處理"""
```

**架構特點：**

1. **MVC 模式變體**
   - Model: `src/core.py`, `src/utils.py`
   - View: CustomTkinter UI 元件
   - Controller: 事件處理方法

2. **多執行緒設計**
   ```python
   def on_query_clicked(self):
       # 在新執行緒執行，避免 UI 凍結
       thread = threading.Thread(
           target=self.perform_query,
           daemon=True
       )
       thread.start()
   ```

3. **執行緒安全的 UI 更新**
   ```python
   def update_progress(self, current, total, ...):
       # 使用 after() 在主執行緒更新 UI
       self.after(0, lambda: self.progress_bar.set(progress))
   ```

4. **UI 元件結構**
   ```
   CryptoPriceGUI
   ├── input_frame (查詢設定)
   │   ├── coin_combobox (幣種下拉選單)
   │   ├── date_entries (日期輸入)
   │   ├── api_key_entry (API Key)
   │   └── query_button (查詢按鈕)
   │
   ├── result_frame (查詢結果)
   │   ├── progress_bar (進度條)
   │   ├── result_text (結果表格)
   │   └── stats_cards (統計卡片)
   │
   └── action_container (操作按鈕)
       ├── export_button (匯出 CSV)
       └── clear_button (清空)
   ```

---

### 5. `crypto_price_tool.py` - CLI 應用

**職責：** 提供命令列介面

#### 架構特點

```python
def parse_arguments():
    """使用 argparse 解析命令列參數"""

def main():
    """主程式入口"""
    args = parse_arguments()

    # 驗證輸入
    validate_date_range(...)

    # 建立 fetcher
    fetcher = CoinGeckoPriceFetcher(api_key=args.api_key)

    # 查詢價格
    prices = fetcher.get_range_prices(...)

    # 匯出 CSV
    save_to_csv(prices, ...)
```

**設計模式：**
- ✅ 命令模式（Command Pattern）
- ✅ 管道過濾器（Pipeline Pattern）

---

## 資料流程

### 查詢流程（GUI 版本）

```
┌─────────────┐
│ 使用者操作  │
│ (點擊查詢)  │
└──────┬──────┘
       │
       ▼
┌──────────────────────────────────┐
│ crypto_price_gui.py              │
│ on_query_clicked()               │
│ • 取得使用者輸入                  │
│ • 驗證輸入                        │
│ • 啟動背景執行緒                  │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ crypto_price_gui.py              │
│ perform_query()                  │
│ • 建立 CoinGeckoPriceFetcher     │
│ • 註冊進度回調                    │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ src/core.py                      │
│ get_range_prices()               │
│ • 計算查詢天數                    │
│ • 呼叫 API                       │
│ • 解析數據                       │
│ • 調用進度回調 ────┐             │
└──────┬──────────────┼─────────────┘
       │              │
       │              ▼
       │      ┌──────────────────┐
       │      │ GUI 進度條更新   │
       │      └──────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ crypto_price_gui.py              │
│ display_results()                │
│ • 格式化顯示價格                  │
│ • 呼叫 calculate_statistics()    │
│ • 更新統計卡片                    │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ 使用者查看結果                    │
│ • 點擊「匯出 CSV」                │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ src/utils.py                     │
│ save_to_csv()                    │
│ • 計算平均價                      │
│ • 寫入 CSV 檔案                  │
└──────────────────────────────────┘
```

### 資料轉換流程

```
CoinGecko API
    │ 原始 JSON
    │ {"prices": [[timestamp, price], ...]}
    ▼
src/core.py
    │ 解析 + 篩選
    │ {date: price_rounded}
    ▼
src/core.py
    │ 轉換為列表
    │ [{"date": "2025-11-10", "price": 0.0098}, ...]
    ▼
crypto_price_gui.py
    │ 格式化顯示
    │ "2025-11-10   $0.0098   ✓"
    ▼
src/utils.py
    │ CSV 匯出
    │ "2025-11-10,0.0098"
```

---

## 設計模式

### 1. **單一職責原則 (Single Responsibility Principle)**

每個模組只負責一件事：
- `core.py` → API 查詢
- `utils.py` → 工具函數
- `constants.py` → 常數定義
- `crypto_price_gui.py` → GUI 介面

### 2. **依賴反轉原則 (Dependency Inversion Principle)**

高層模組（GUI/CLI）依賴抽象（函數介面），不依賴具體實作：

```python
# GUI 不直接操作 API，而是呼叫 core.py 的介面
fetcher = CoinGeckoPriceFetcher(api_key)
prices = fetcher.get_range_prices(...)
```

### 3. **開放封閉原則 (Open-Closed Principle)**

對擴展開放，對修改封閉：

```python
# 新增幣種：只需修改 constants.py，不需改動其他程式碼
COIN_LIST.append({"symbol": "NEW", "id": "new-coin", "name": "New Coin"})
```

### 4. **觀察者模式 (Observer Pattern)**

透過回調函數實現進度通知：

```python
# core.py 提供回調介面
def get_range_prices(self, ..., progress_callback=None):
    if progress_callback:
        progress_callback(current, total, date, price, success)

# GUI 註冊回調
prices = fetcher.get_range_prices(
    ...,
    progress_callback=self.update_progress
)
```

### 5. **工廠模式 (Factory Pattern)**

`COIN_MAPPING` 作為簡單工廠：

```python
# 從顯示文字取得 coin_id
coin_id = COIN_MAPPING.get("BTC - Bitcoin")  # → "bitcoin"
```

---

## 依賴關係

### 模組依賴圖

```
crypto_price_gui.py
    ↓
    ├─→ src.core (CoinGeckoPriceFetcher)
    ├─→ src.utils (validate_date_range, save_to_csv, calculate_statistics)
    ├─→ src.constants (COIN_LIST, COIN_MAPPING)
    └─→ customtkinter (UI 框架)

crypto_price_tool.py
    ↓
    ├─→ src.core (CoinGeckoPriceFetcher)
    ├─→ src.utils (validate_date, save_to_csv)
    └─→ argparse (命令列解析)

src/core.py
    ↓
    ├─→ requests (HTTP 請求)
    └─→ datetime (日期處理)

src/utils.py
    ↓
    ├─→ csv (CSV 檔案處理)
    └─→ datetime (日期驗證)

src/constants.py
    ↓
    └─→ (無外部依賴)
```

### 外部套件依賴

```
requests==2.31.0          # HTTP 請求庫
customtkinter==5.2.0      # GUI 框架
pillow==10.1.0            # CustomTkinter 依賴
pyinstaller==6.3.0        # 打包工具（選用）
darkdetect==0.8.0         # CustomTkinter 自動安裝
packaging==25.0           # CustomTkinter 自動安裝
```

---

## 總結

### 架構優點

✅ **模組化**：每個模組職責清晰，易於維護
✅ **可重用**：核心邏輯（src/）可供 GUI/CLI 共用
✅ **可測試**：純函數設計，易於單元測試
✅ **可擴展**：新增功能無需大幅修改現有程式碼
✅ **易理解**：分層清晰，新手也能快速上手

### 改進空間

🔸 **錯誤處理**：可統一異常處理機制
🔸 **日誌系統**：加入 logging 模組記錄操作
🔸 **配置管理**：使用 config 檔案管理設定
🔸 **快取機制**：減少重複 API 請求
🔸 **單元測試**：增加測試覆蓋率

---

**最後更新：** 2025-11-14
**版本：** v2.0.0 MVP
