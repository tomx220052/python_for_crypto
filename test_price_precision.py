#!/usr/bin/env python3
"""
測試價格精度 - 查看原始 API 數據
使用方式：python3 test_price_precision.py <coin_id> <date>
範例：python3 test_price_precision.py shiba-inu 2025-11-10
"""

import sys
sys.path.insert(0, '.')
from src.core import CoinGeckoPriceFetcher

def test_price_precision(coin_id, date):
    """測試指定幣種和日期的價格精度"""
    print(f"正在查詢 {coin_id} 在 {date} 的價格...")
    print("=" * 60)

    fetcher = CoinGeckoPriceFetcher()

    # 查詢單日價格
    result = fetcher.get_range_prices_api(coin_id, date, date, debug=True)

    if result:
        price = result.get(date)
        if price is not None:
            print("\n" + "=" * 60)
            print("價格精度分析：")
            print("-" * 60)
            print(f"原始值（程式內部）: {price}")
            print(f"round(price, 2):   {round(price, 2)}")
            print(f"round(price, 3):   {round(price, 3)}")
            print(f"round(price, 4):   {round(price, 4)}")
            print(f"格式化 .2f:        ${price:.2f}")
            print(f"格式化 .3f:        ${price:.3f}")
            print(f"格式化 .4f:        ${price:.4f}")
            print("=" * 60)
            print()
            print("結論：")
            if price < 0.01:
                print(f"  這是一個低價幣種（< $0.01）")
                print(f"  原始值: {price:.6f}")
                print(f"  四捨五入到 2 位: ${round(price, 2):.2f}")
                if round(price, 2) == 0.01 and price < 0.01:
                    print(f"  ⚠️  因為四捨五入，{price:.4f} 被進位到 $0.01")
            else:
                print(f"  正常價格範圍")
        else:
            print(f"錯誤：{date} 沒有價格數據")
    else:
        print(f"錯誤：無法取得價格數據")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("使用方式：python3 test_price_precision.py <coin_id> <date>")
        print("範例：")
        print("  python3 test_price_precision.py shiba-inu 2025-11-10")
        print("  python3 test_price_precision.py gala 2025-11-12")
        sys.exit(1)

    coin_id = sys.argv[1]
    date = sys.argv[2]
    test_price_precision(coin_id, date)
