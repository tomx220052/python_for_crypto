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

    def __init__(self, api_key=None, delay=10):
        """
        初始化
        :param api_key: CoinGecko API key（可選）
        :param delay: API 調用間隔秒數（避免 rate limit，預設 5 秒）
        """
        self.delay = delay
        self.session = requests.Session()
        # headers = {
        #     'User-Agent': 'Mozilla/5.0 (Crypto Price Tool)'
        # }
        # if api_key:
        #     headers['x-cg-pro-api-key'] = api_key
        # self.session.headers.update(headers)

    def get_price_on_date(self, coin_id, date_str, max_retries=20):
        """
        取得指定日期的價格（含重試機制）
        :param coin_id: CoinGecko 的幣種 ID（如 bitcoin）
        :param date_str: 日期字串，格式：YYYY-MM-DD
        :param max_retries: 最大重試次數
        :return: 價格（整數）或 None
        """
        # 轉換日期格式：YYYY-MM-DD -> dd-mm-yyyy（CoinGecko API 要求格式）
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            api_date = dt.strftime("%Y-%m-%d")  # 轉換為 dd-mm-yyyy
        except ValueError:
            print(f"錯誤：日期格式不正確：{date_str}", file=sys.stderr)
            return None

        url = f"{self.BASE_URL}/coins/{coin_id}/history"
        params = {
            'date': api_date,
            'localization': 'false',
            'x-cg-pro-api-key': 'CG-2wCtiaEmkTfLhz6PUsQDyBiR'
        }

        for attempt in range(max_retries):
            try:
                response = self.session.get(url, params=params, timeout=10)

                if response.status_code == 404:
                    if attempt == 0:  # 只在第一次顯示錯誤
                        print(f"錯誤：找不到幣種 '{coin_id}'", file=sys.stderr)
                    return None
                elif response.status_code == 429:
                    wait_time = 5
                    print(f"警告：API 請求過於頻繁，等待 {wait_time} 秒...", file=sys.stderr)
                    time.sleep(wait_time)
                    continue

                response.raise_for_status()
                data = response.json()

                # 取得市場資料
                if 'market_data' in data and 'current_price' in data['market_data']:
                    price_usd = data['market_data']['current_price'].get('usd', None)
                    if price_usd is not None:
                        # 四捨五入到整數
                        return round(price_usd)
                    else:
                        if attempt == max_retries - 1:
                            return None
                else:
                    if attempt == max_retries - 1:
                        return None

            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    print(f"錯誤：請求 {date_str} 的資料時發生錯誤：{e}", file=sys.stderr)
                    return None
                time.sleep(2)  # 錯誤後等待 2 秒再重試
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"錯誤：處理 {date_str} 的資料時發生錯誤：{e}", file=sys.stderr)
                    return None

        return None

    def get_range_prices(self, coin_id, from_date, to_date):
        """
        取得日期區間內所有日期的價格
        :param coin_id: CoinGecko 的幣種 ID
        :param from_date: 開始日期（YYYY-MM-DD）
        :param to_date: 結束日期（YYYY-MM-DD）
        :return: 價格資料列表
        """
        # 轉換為 datetime 物件
        start_dt = datetime.strptime(from_date, "%Y-%m-%d")
        end_dt = datetime.strptime(to_date, "%Y-%m-%d")

        # 計算天數
        delta = end_dt - start_dt
        num_days = delta.days + 1  # 包含結束日期

        prices = []
        current_dt = start_dt

        print(f"開始取得 {coin_id} 從 {from_date} 到 {to_date} 的價格資料...")
        print(f"共需查詢 {num_days} 天，請稍候...")
        print("-" * 50)

        for i in range(num_days):
            date_str = current_dt.strftime("%Y-%m-%d")
            print(f"查詢 {date_str}...", end=' ')

            price = self.get_price_on_date(coin_id, date_str)

            if price is not None:
                prices.append({
                    'date': date_str,
                    'price': price
                })
                print(f"✓ {price}")
            else:
                prices.append({
                    'date': date_str,
                    'price': None
                })
                print("✗ 無資料")

            # 加入延遲（最後一天不需要延遲）
            if i < num_days - 1:
                time.sleep(self.delay)

            current_dt += timedelta(days=1)

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

  # 自訂 API 請求延遲時間
  python crypto_price_tool.py bitcoin --from 2024-01-01 --to 2024-01-31 --delay 2

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
        '-d', '--delay',
        type=float,
        help='API 請求間隔秒數（預設：10 秒）',
        default=10.0
    )

    parser.add_argument(
        '-k', '--api-key',
        dest='api_key',
        help='CoinGecko API key（Pro 版本）',
        default=None
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
        print(f"API 請求間隔：{args.delay} 秒")
        print("=" * 50)
        print()

        # 建立 fetcher
        fetcher = CoinGeckoPriceFetcher(api_key=args.api_key, delay=args.delay)

        # 取得價格資料
        prices = fetcher.get_range_prices(args.coin_id, args.from_date, args.to_date)

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
