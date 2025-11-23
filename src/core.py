"""
CoinGecko API 價格查詢核心模組
支援 CLI 和 GUI 共用
"""

import requests
import sys
import time
from datetime import datetime, timedelta, timezone
from collections import defaultdict


class CoinGeckoPriceFetcher:
    """CoinGecko API 價格查詢類別"""

    BASE_URL = "https://api.coingecko.com/api/v3"

    def __init__(self, api_key=None):
        """
        初始化
        :param api_key: CoinGecko API key（可選）
        """
        self.api_key = api_key
        self.session = requests.Session()

    def _date_to_timestamp(self, date_str):
        """
        將 YYYY-MM-DD 轉換為 UNIX timestamp (秒)，使用 UTC 時區
        :param date_str: 日期字串，格式：YYYY-MM-DD
        :return: UNIX timestamp (秒)
        """
        # 將日期視為 UTC 00:00:00
        dt = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        return int(dt.timestamp())

    def _timestamp_to_date(self, timestamp_ms):
        """
        將 UNIX timestamp (毫秒) 轉換為 YYYY-MM-DD，使用 UTC 時區
        :param timestamp_ms: UNIX timestamp (毫秒)
        :return: 日期字串，格式：YYYY-MM-DD
        """
        # 使用 UTC 時區轉換，避免受系統時區影響
        dt = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)
        return dt.strftime("%Y-%m-%d")

    def get_range_prices_api(self, coin_id, from_date, to_date, max_retries=20, debug=False, cancellation_check=None):
        """
        使用 market_chart/range API 取得日期區間內的價格
        :param coin_id: CoinGecko 的幣種 ID（如 bitcoin）
        :param from_date: 開始日期，格式：YYYY-MM-DD
        :param to_date: 結束日期，格式：YYYY-MM-DD
        :param max_retries: 最大重試次數
        :param debug: 是否顯示詳細 debug 資訊
        :return: 價格資料字典 {date: price} 或 None
        """
        try:
            # from_date 需要往前推一天，因為該日數據來自前一天的 16:00 UTC
            from_dt = datetime.strptime(from_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            from_dt = from_dt - timedelta(days=1)  # 往前推一天
            from_ts = int(from_dt.timestamp())

            # to_date 要延伸到當天的 23:59:59，確保包含當天 16:00 的數據
            to_dt = datetime.strptime(to_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            to_dt = to_dt.replace(hour=23, minute=59, second=59)
            to_ts = int(to_dt.timestamp())
        except ValueError as e:
            print(f"錯誤：日期格式不正確：{e}", file=sys.stderr)
            return None

        url = f"{self.BASE_URL}/coins/{coin_id}/market_chart/range"
        params = {
            'vs_currency': 'usd',
            'from': from_ts,
            'to': to_ts
        }

        # 如果有 API key，添加到參數中（並啟用 daily interval）
        if self.api_key:
            params['x_cg_pro_api_key'] = self.api_key
            params['interval'] = 'daily'  # daily interval 是付費功能

        for attempt in range(max_retries):
            # 檢查是否被取消
            if cancellation_check and cancellation_check():
                return None  # 立即返回，放棄查詢

            try:
                response = self.session.get(url, params=params, timeout=30)

                if response.status_code == 404:
                    print(f"錯誤：找不到幣種 '{coin_id}'", file=sys.stderr)
                    return None
                elif response.status_code == 429:
                    # 在等待前檢查是否被取消
                    if cancellation_check and cancellation_check():
                        return None
                    wait_time = 15
                    print(f"警告：API 請求過於頻繁 (429)，等待 {wait_time} 秒...", file=sys.stderr)
                    print(f"響應內容：{response.text}", file=sys.stderr)
                    time.sleep(wait_time)
                    continue
                elif response.status_code == 401:
                    print(f"錯誤：API 認證失敗 (401)", file=sys.stderr)
                    print(f"響應內容：{response.text}", file=sys.stderr)
                    return None

                response.raise_for_status()
                data = response.json()

                # 解析 prices 陣列
                if 'prices' not in data:
                    print("錯誤：API 返回資料格式不正確", file=sys.stderr)
                    return None

                prices_array = data['prices']
                if not prices_array:
                    print("警告：API 返回空資料", file=sys.stderr)
                    return {}

                # 將 timestamp 按日期分組（處理同日多筆數據）
                # 注意：CoinGecko 的邏輯是 UTC 16:00 的價格算作次日
                daily_prices = defaultdict(list)

                for timestamp_ms, price in prices_array:
                    dt = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)

                    # 如果時間 >= 16:00，算作次日的數據
                    if dt.hour >= 16:
                        dt = dt + timedelta(days=1)

                    date_str = dt.strftime("%Y-%m-%d")
                    daily_prices[date_str].append((timestamp_ms, price))  # 保存 timestamp 和 price

                # 每日取最接近 UTC 16:00 的價格（CoinGecko 標準每日結算時間）
                # 注意：歸類到某日的數據實際上來自前一天的 16:xx
                result = {}
                for date_str in sorted(daily_prices.keys()):
                    price_data = daily_prices[date_str]  # [(timestamp_ms, price), ...]

                    # 計算前一天 UTC 16:00 的時間戳（毫秒）
                    # 因為歸類到 date_str 的數據實際上是前一天 >= 16:00 的數據
                    target_dt = datetime.strptime(date_str, "%Y-%m-%d").replace(
                        hour=16, minute=0, second=0, microsecond=0, tzinfo=timezone.utc
                    )
                    target_dt = target_dt - timedelta(days=1)  # 前一天的 16:00
                    target_ts_ms = int(target_dt.timestamp() * 1000)

                    # 找到最接近前一天 UTC 16:00 的數據點
                    closest = min(price_data, key=lambda x: abs(x[0] - target_ts_ms))

                    if debug:
                        # 顯示詳細的時間資訊
                        closest_dt = datetime.fromtimestamp(closest[0] / 1000, tz=timezone.utc)
                        time_diff = abs(closest[0] - target_ts_ms) / 1000 / 60  # 分鐘
                        print(f"  {date_str}: 目標前日 UTC 16:00, 實際選擇 {closest_dt.strftime('%Y-%m-%d %H:%M:%S')} UTC (差距 {time_diff:.1f} 分鐘)", file=sys.stderr)
                        print(f"            原始價格: ${closest[1]:.10f}, round 後: ${round(closest[1], 8):.8f}", file=sys.stderr)

                    result[date_str] = round(closest[1], 8)  # 四捨五入到小數點後八位

                return result

            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    print(f"錯誤：請求資料時發生錯誤：{e}", file=sys.stderr)
                    return None
                # 在等待前檢查是否被取消
                if cancellation_check and cancellation_check():
                    return None
                time.sleep(2)  # 錯誤後等待 2 秒再重試
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"錯誤：處理資料時發生錯誤：{e}", file=sys.stderr)
                    return None
                # 在等待前檢查是否被取消
                if cancellation_check and cancellation_check():
                    return None
                time.sleep(2)

        return None

    def get_range_prices(self, coin_id, from_date, to_date, debug=False, progress_callback=None, cancellation_check=None):
        """
        取得日期區間內所有日期的價格
        :param coin_id: CoinGecko 的幣種 ID
        :param from_date: 開始日期（YYYY-MM-DD）
        :param to_date: 結束日期（YYYY-MM-DD）
        :param debug: 是否顯示詳細 debug 資訊
        :param progress_callback: 進度回調函數 callback(current, total, date, price, success)
        :return: 價格資料列表
        """
        # 轉換為 datetime 物件
        start_dt = datetime.strptime(from_date, "%Y-%m-%d")
        end_dt = datetime.strptime(to_date, "%Y-%m-%d")

        # 計算天數
        delta = end_dt - start_dt
        num_days = delta.days + 1  # 包含結束日期

        # 使用新 API 一次取得所有資料
        price_dict = self.get_range_prices_api(coin_id, from_date, to_date, debug=debug, cancellation_check=cancellation_check)

        if price_dict is None:
            return []

        # 建立完整的日期列表，補充缺失的日期
        prices = []
        current_dt = start_dt

        for i in range(num_days):
            date_str = current_dt.strftime("%Y-%m-%d")
            price = price_dict.get(date_str, None)

            if price is not None:
                prices.append({
                    'date': date_str,
                    'price': price
                })
                # 回調進度（成功）
                if progress_callback:
                    progress_callback(current=i+1, total=num_days, date=date_str, price=price, success=True)
            else:
                prices.append({
                    'date': date_str,
                    'price': None
                })
                # 回調進度（失敗）
                if progress_callback:
                    progress_callback(current=i+1, total=num_days, date=date_str, price=None, success=False)

            current_dt += timedelta(days=1)

        return prices
