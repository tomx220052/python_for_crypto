"""
共用工具函數
"""

import csv
import sys
from datetime import datetime


def validate_date(date_str, date_name="日期"):
    """
    驗證日期格式和範圍
    :param date_str: 日期字串
    :param date_name: 日期名稱（用於錯誤訊息）
    :return: datetime 物件
    :raises ValueError: 日期格式或範圍錯誤
    """
    # 驗證格式
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"{date_name} 格式錯誤，請使用 YYYY-MM-DD 格式（如：2024-01-01）")

    # 驗證不是未來日期
    today = datetime.now()
    if dt > today:
        raise ValueError(f"{date_name} 不能是未來日期")

    return dt


def validate_date_range(from_date_str, to_date_str):
    """
    驗證日期區間
    :param from_date_str: 開始日期字串
    :param to_date_str: 結束日期字串
    :return: (from_dt, to_dt) datetime 物件元組
    :raises ValueError: 日期範圍錯誤
    """
    from_dt = validate_date(from_date_str, "開始日期")
    to_dt = validate_date(to_date_str, "結束日期")

    # 驗證 from < to
    if from_dt >= to_dt:
        raise ValueError("開始日期必須早於結束日期")

    # 驗證日期區間不超過 365 天
    delta = to_dt - from_dt
    if delta.days >= 365:
        raise ValueError(f"日期區間不能超過 365 天（目前：{delta.days + 1} 天）")

    return from_dt, to_dt


def save_to_csv(prices, coin_id, from_date, to_date, output_file=None):
    """
    將價格資料儲存為 CSV 檔案
    :param prices: 價格資料列表
    :param coin_id: 幣種 ID
    :param from_date: 開始日期
    :param to_date: 結束日期
    :param output_file: 輸出檔案名稱（可選）
    :return: 輸出檔案路徑
    :raises Exception: 儲存失敗
    """
    if not prices:
        raise ValueError("沒有價格資料可以輸出")

    # 計算平均價格（排除 None）
    valid_prices = [p['price'] for p in prices if p['price'] is not None]
    if valid_prices:
        avg_price = round(sum(valid_prices) / len(valid_prices), 8)
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

        return output_file

    except Exception as e:
        raise Exception(f"儲存 CSV 檔案時發生錯誤：{e}")


def calculate_statistics(prices):
    """
    計算價格統計資訊
    :param prices: 價格資料列表
    :return: dict {avg, max, min, valid_count, total_count}
    """
    valid_prices = [p['price'] for p in prices if p['price'] is not None]

    if not valid_prices:
        return {
            'avg': None,
            'max': None,
            'min': None,
            'valid_count': 0,
            'total_count': len(prices)
        }

    return {
        'avg': round(sum(valid_prices) / len(valid_prices), 8),
        'max': max(valid_prices),
        'min': min(valid_prices),
        'valid_count': len(valid_prices),
        'total_count': len(prices)
    }
