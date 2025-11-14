#!/usr/bin/env python3
"""
虛擬幣價格查詢工具
取得指定幣種在指定日期區間內每日的價格，並計算平均價格
"""

import requests
import csv
import argparse
import sys
import time
from datetime import datetime, timedelta


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
        # headers = {
        #     'User-Agent': 'Mozilla/5.0 (Crypto Price Tool)'
        # }
        # if api_key:
        #     headers['x-cg-pro-api-key'] = api_key
        # self.session.headers.update(headers)

    def _date_to_timestamp(self, date_str):
        """
        將 YYYY-MM-DD 轉換為 UNIX timestamp (秒)，使用 UTC 時區
        :param date_str: 日期字串，格式：YYYY-MM-DD
        :return: UNIX timestamp (秒)
        """
        from datetime import timezone
        # 將日期視為 UTC 00:00:00
        dt = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        return int(dt.timestamp())

    def _timestamp_to_date(self, timestamp_ms):
        """
        將 UNIX timestamp (毫秒) 轉換為 YYYY-MM-DD，使用 UTC 時區
        :param timestamp_ms: UNIX timestamp (毫秒)
        :return: 日期字串，格式：YYYY-MM-DD
        """
        from datetime import timezone
        # 使用 UTC 時區轉換，避免受系統時區影響
        dt = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)
        return dt.strftime("%Y-%m-%d")

    def get_range_prices_api(self, coin_id, from_date, to_date, max_retries=3, debug=False):
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
            from datetime import timezone, timedelta
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
            try:
                response = self.session.get(url, params=params, timeout=30)

                if response.status_code == 404:
                    print(f"錯誤：找不到幣種 '{coin_id}'", file=sys.stderr)
                    return None
                elif response.status_code == 429:
                    wait_time = 5
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
                from collections import defaultdict
                from datetime import timedelta
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

                    result[date_str] = round(closest[1])  # 四捨五入到整數

                return result

            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    print(f"錯誤：請求資料時發生錯誤：{e}", file=sys.stderr)
                    return None
                time.sleep(2)  # 錯誤後等待 2 秒再重試
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"錯誤：處理資料時發生錯誤：{e}", file=sys.stderr)
                    return None
                time.sleep(2)

        return None

    def get_range_prices(self, coin_id, from_date, to_date, debug=False):
        """
        取得日期區間內所有日期的價格
        :param coin_id: CoinGecko 的幣種 ID
        :param from_date: 開始日期（YYYY-MM-DD）
        :param to_date: 結束日期（YYYY-MM-DD）
        :param debug: 是否顯示詳細 debug 資訊
        :return: 價格資料列表
        """
        # 轉換為 datetime 物件
        start_dt = datetime.strptime(from_date, "%Y-%m-%d")
        end_dt = datetime.strptime(to_date, "%Y-%m-%d")

        # 計算天數
        delta = end_dt - start_dt
        num_days = delta.days + 1  # 包含結束日期

        print(f"開始取得 {coin_id} 從 {from_date} 到 {to_date} 的價格資料...")
        print(f"共需查詢 {num_days} 天，請稍候...")
        print("-" * 50)

        # 使用新 API 一次取得所有資料
        price_dict = self.get_range_prices_api(coin_id, from_date, to_date, debug=debug)

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
                print(f"{date_str}: ✓ ${price:,}")
            else:
                prices.append({
                    'date': date_str,
                    'price': None
                })
                print(f"{date_str}: ✗ 無資料")

            current_dt += timedelta(days=1)

        print("-" * 50)
        print(f"查詢完成！取得 {len([p for p in prices if p['price'] is not None])} / {num_days} 天的資料")

        return prices


def save_to_csv(prices, coin_id, from_date, to_date, output_file=None):
    """
    將價格資料儲存為 CSV 檔案
    :param prices: 價格資料列表
    :param coin_id: 幣種 ID
    :param from_date: 開始日期
    :param to_date: 結束日期
    :param output_file: 輸出檔案名稱（可選）
    """
    if not prices:
        print("錯誤：沒有價格資料可以輸出", file=sys.stderr)
        return

    # 計算平均價格（排除 None）
    valid_prices = [p['price'] for p in prices if p['price'] is not None]
    if valid_prices:
        avg_price = round(sum(valid_prices) / len(valid_prices))
    else:
        avg_price = None

    # 如果沒有指定輸出檔案名稱，自動產生
    if output_file is None:
        output_file = f"{coin_id}_{from_date}_{to_date}_prices.csv"

    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Date', 'Price (USD)']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()

            # 寫入每日價格
            for price_data in prices:
                writer.writerow({
                    'Date': price_data['date'],
                    'Price (USD)': price_data['price'] if price_data['price'] is not None else 'N/A'
                })

            # 寫入平均價格
            writer.writerow({
                'Date': 'Average',
                'Price (USD)': avg_price if avg_price is not None else 'N/A'
            })

        print("\n" + "=" * 50)
        print(f"成功！資料已儲存至：{output_file}")
        print(f"共 {len(prices)} 天的資料")
        print(f"有效資料：{len(valid_prices)} 天")
        print(f"平均價格：{avg_price if avg_price is not None else 'N/A'}")
        print("=" * 50)

    except Exception as e:
        print(f"錯誤：儲存 CSV 檔案時發生錯誤：{e}", file=sys.stderr)


def validate_date(date_str, date_name):
    """
    驗證日期格式和範圍
    :param date_str: 日期字串
    :param date_name: 日期名稱（用於錯誤訊息）
    :return: datetime 物件
    """
    # 驗證格式
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"{date_name} 格式錯誤，請使用 YYYY-MM-DD 格式（如：2024-01-01）")

    # 驗證不早於 2025-01-01
    min_date = datetime(2025, 1, 1)
    if dt < min_date:
        raise ValueError(f"{date_name} 不能早於 2025-01-01")

    # 驗證不是未來日期
    today = datetime.now()
    if dt > today:
        raise ValueError(f"{date_name} 不能是未來日期")

    return dt


def parse_arguments():
    """解析命令列參數"""
    parser = argparse.ArgumentParser(
        description='虛擬幣價格查詢工具 - 取得指定幣種在指定日期區間內每日的價格',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例：
  # 取得 Bitcoin 在 2024-01-01 到 2024-01-31 的價格
  python crypto_price_tool.py bitcoin --from 2024-01-01 --to 2024-01-31

  # 取得 Ethereum 在特定區間的價格並指定輸出檔案
  python crypto_price_tool.py ethereum --from 2024-01-01 --to 2024-01-10 --output eth_jan.csv

  # 使用自訂 API key
  python crypto_price_tool.py bitcoin --from 2024-01-01 --to 2024-01-31 --api-key YOUR_API_KEY

常見幣種 ID：
  bitcoin, ethereum, tether, binancecoin, ripple, cardano, dogecoin, solana,
  polkadot, litecoin, shiba-inu, avalanche-2

更多幣種 ID 請參考：https://www.coingecko.com/
        """
    )

    parser.add_argument(
        'coin_id',
        help='CoinGecko 幣種 ID（如：bitcoin, ethereum, tether）'
    )

    parser.add_argument(
        '--from',
        dest='from_date',
        required=True,
        help='開始日期，格式：YYYY-MM-DD（如：2024-01-01）'
    )

    parser.add_argument(
        '--to',
        dest='to_date',
        required=True,
        help='結束日期，格式：YYYY-MM-DD（如：2024-01-31）'
    )

    parser.add_argument(
        '-o', '--output',
        help='輸出檔案名稱（預設：{coin_id}_{from}_{to}_prices.csv）',
        default=None
    )

    parser.add_argument(
        '-k', '--api-key',
        dest='api_key',
        help='CoinGecko API key（Pro 版本）',
        default=None
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='顯示詳細的時間篩選資訊（用於驗證 UTC 16:00 邏輯）',
        default=False
    )

    return parser.parse_args()


def main():
    """主程式"""
    args = parse_arguments()

    try:
        # 驗證日期
        from_dt = validate_date(args.from_date, "開始日期")
        to_dt = validate_date(args.to_date, "結束日期")

        # 驗證 from < to
        if from_dt >= to_dt:
            raise ValueError("開始日期必須早於結束日期（至少要有 2 天的區間）")

        # 驗證日期區間不超過 90 天
        delta = to_dt - from_dt
        if delta.days >= 90:
            raise ValueError(f"日期區間不能超過 90 天（目前：{delta.days + 1} 天）")

        print("=" * 50)
        print("虛擬幣價格查詢工具")
        print("=" * 50)
        print(f"幣種 ID：{args.coin_id}")
        print(f"日期區間：{args.from_date} ~ {args.to_date}")
        print(f"查詢天數：{delta.days + 1} 天")
        print("=" * 50)
        print()

        # 建立 fetcher
        fetcher = CoinGeckoPriceFetcher(api_key=args.api_key)

        # 取得價格資料
        prices = fetcher.get_range_prices(args.coin_id, args.from_date, args.to_date, debug=args.debug)

        if not prices:
            print("\n錯誤：無法取得任何價格資料", file=sys.stderr)
            sys.exit(1)

        # 儲存為 CSV
        save_to_csv(prices, args.coin_id, args.from_date, args.to_date, args.output)

    except ValueError as e:
        print(f"錯誤：{e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n程式已被使用者中斷", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"錯誤：{e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
