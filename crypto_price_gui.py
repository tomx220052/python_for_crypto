#!/usr/bin/env python3
"""
虛擬幣價格查詢工具 - GUI 版本
使用 CustomTkinter 製作現代化介面
"""

import customtkinter as ctk
import threading
import sys
import os
import time
from datetime import datetime
from tkinter import messagebox, filedialog
from src.core import CoinGeckoPriceFetcher
from src.utils import validate_date_range, save_to_csv, calculate_statistics
from src.constants import COIN_LIST, COIN_MAPPING


class CryptoPriceGUI(ctk.CTk):
    """主 GUI 視窗"""

    def __init__(self):
        super().__init__()

        # 視窗設定
        self.title("虛擬幣價格查詢工具 v2.0 MVP")
        self.geometry("700x950")

        # 設定主題
        ctk.set_appearance_mode("dark")  # 深色模式
        ctk.set_default_color_theme("blue")

        # 資料儲存
        self.prices_data = []
        self.is_querying = False
        self.is_batch_query_cancelled = False

        # 建立 UI
        self.setup_ui()

    def setup_ui(self):
        """建立 UI 元件"""

        # 主容器（使用可滾動容器）
        main_container = ctk.CTkScrollableFrame(self)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # ==================== 標題 ====================
        title_label = ctk.CTkLabel(
            main_container,
            text="💰 虛擬幣價格查詢工具",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(0, 20))

        # ==================== 查詢設定區域 ====================
        input_frame = ctk.CTkFrame(main_container)
        input_frame.pack(fill="x", pady=(0, 20))

        # 標題
        input_title = ctk.CTkLabel(
            input_frame,
            text="查詢設定",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        input_title.pack(pady=(10, 15), padx=20, anchor="w")

        # 幣種選擇（下拉選單）
        coin_label = ctk.CTkLabel(input_frame, text="選擇幣種：", font=ctk.CTkFont(size=14))
        coin_label.pack(pady=(5, 5), padx=20, anchor="w")

        # 建立幣種選項列表（最前面加入「全部」選項）
        coin_options = ["全部 - All Coins"] + [f"{coin['symbol']} - {coin['name']}" for coin in COIN_LIST]

        self.coin_combobox = ctk.CTkComboBox(
            input_frame,
            values=coin_options,
            width=400,
            height=35,
            state="readonly"  # 只能選擇，不能手動輸入
        )
        self.coin_combobox.pack(pady=(0, 10), padx=20, anchor="w")
        self.coin_combobox.set("BTC - Bitcoin")  # 預設值

        # 日期區間
        date_label = ctk.CTkLabel(input_frame, text="日期區間：", font=ctk.CTkFont(size=14))
        date_label.pack(pady=(10, 5), padx=20, anchor="w")

        # 日期輸入容器
        date_container = ctk.CTkFrame(input_frame, fg_color="transparent")
        date_container.pack(pady=(0, 10), padx=20, anchor="w")

        # 開始日期
        self.from_date_entry = ctk.CTkEntry(
            date_container,
            placeholder_text="YYYY-MM-DD",
            width=150,
            height=35
        )
        self.from_date_entry.pack(side="left", padx=(0, 10))

        # 預設開始日期為 3 天前
        default_from = (datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) -
                       __import__('datetime').timedelta(days=3)).strftime("%Y-%m-%d")
        self.from_date_entry.insert(0, default_from)

        # "至" 標籤
        to_label = ctk.CTkLabel(date_container, text="至", font=ctk.CTkFont(size=14))
        to_label.pack(side="left", padx=(0, 10))

        # 結束日期
        self.to_date_entry = ctk.CTkEntry(
            date_container,
            placeholder_text="YYYY-MM-DD",
            width=150,
            height=35
        )
        self.to_date_entry.pack(side="left")

        # 預設結束日期為昨天
        default_to = (datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) -
                     __import__('datetime').timedelta(days=1)).strftime("%Y-%m-%d")
        self.to_date_entry.insert(0, default_to)

        # 提示
        date_hint = ctk.CTkLabel(
            input_frame,
            text="ℹ️  最多 365 天",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        date_hint.pack(pady=(0, 10), padx=20, anchor="w")

        # API Key 輸入
        api_label = ctk.CTkLabel(input_frame, text="API Key（選填）：", font=ctk.CTkFont(size=14))
        api_label.pack(pady=(10, 5), padx=20, anchor="w")

        self.api_key_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="CoinGecko Pro API Key",
            width=400,
            height=35,
            show="*"
        )
        self.api_key_entry.pack(pady=(0, 5), padx=20, anchor="w")

        api_hint = ctk.CTkLabel(
            input_frame,
            text="🔒 您的 API Key 不會被儲存",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        api_hint.pack(pady=(0, 15), padx=20, anchor="w")

        # 查詢按鈕
        self.query_button = ctk.CTkButton(
            input_frame,
            text="🔍 開始查詢",
            command=self.on_query_clicked,
            height=40,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.query_button.pack(pady=(0, 15), padx=20)

        # ==================== 查詢結果區域 ====================
        result_frame = ctk.CTkFrame(main_container)
        result_frame.pack(fill="x", pady=(0, 20))

        # 標題
        result_title = ctk.CTkLabel(
            result_frame,
            text="查詢結果",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        result_title.pack(pady=(10, 10), padx=20, anchor="w")

        # 進度條
        self.progress_bar = ctk.CTkProgressBar(result_frame, width=400)
        self.progress_bar.pack(pady=(0, 5), padx=20)
        self.progress_bar.set(0)

        # 進度文字
        self.progress_label = ctk.CTkLabel(
            result_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.progress_label.pack(pady=(0, 15), padx=20)

        # 結果顯示區（使用 Textbox）
        self.result_text = ctk.CTkTextbox(
            result_frame,
            width=640,
            height=200,
            font=ctk.CTkFont(family="Monaco", size=12)
        )
        self.result_text.pack(pady=(0, 15), padx=20)

        # 統計資訊容器
        stats_container = ctk.CTkFrame(result_frame, fg_color="transparent")
        stats_container.pack(pady=(0, 15), padx=20)

        # 統計卡片
        self.avg_label = self.create_stat_card(stats_container, "📊 平均價格", "---")
        self.avg_label.pack(side="left", padx=5)

        self.max_label = self.create_stat_card(stats_container, "📈 最高價", "---")
        self.max_label.pack(side="left", padx=5)

        self.min_label = self.create_stat_card(stats_container, "📉 最低價", "---")
        self.min_label.pack(side="left", padx=5)

        # ==================== 操作按鈕區域 ====================
        action_container = ctk.CTkFrame(main_container, fg_color="transparent")
        action_container.pack(pady=(0, 10))

        self.export_button = ctk.CTkButton(
            action_container,
            text="📥 匯出 CSV",
            command=self.on_export_clicked,
            width=140,
            height=35,
            state="disabled"
        )
        self.export_button.pack(side="left", padx=5)

        self.clear_button = ctk.CTkButton(
            action_container,
            text="🗑️ 清空",
            command=self.on_clear_clicked,
            width=140,
            height=35
        )
        self.clear_button.pack(side="left", padx=5)

        # ==================== 狀態列 ====================
        self.status_label = ctk.CTkLabel(
            main_container,
            text="📡 就緒",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.status_label.pack(pady=(10, 0))

    def create_stat_card(self, parent, title, value):
        """建立統計卡片"""
        card = ctk.CTkFrame(parent, width=180, height=70)
        card.pack_propagate(False)

        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        title_label.pack(pady=(10, 0))

        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=18, weight="bold")
        )
        value_label.pack(pady=(0, 10))

        # 儲存 value_label 供更新使用
        card.value_label = value_label

        return card

    def on_query_clicked(self):
        """查詢按鈕點擊事件"""
        if self.is_querying:
            messagebox.showwarning("警告", "查詢進行中，請稍候...")
            return

        # 取得輸入值
        selected_coin = self.coin_combobox.get()
        from_date = self.from_date_entry.get().strip()
        to_date = self.to_date_entry.get().strip()
        api_key = self.api_key_entry.get().strip() or None

        # 基本驗證
        if not from_date or not to_date:
            messagebox.showerror("錯誤", "請輸入日期區間")
            return

        # 驗證日期範圍
        try:
            validate_date_range(from_date, to_date)
        except ValueError as e:
            messagebox.showerror("錯誤", str(e))
            return

        # 檢查是否選擇批量查詢
        if selected_coin == "全部 - All Coins":
            # 批量查詢所有幣種
            thread = threading.Thread(
                target=self.perform_batch_query,
                args=(from_date, to_date, api_key),
                daemon=True
            )
            thread.start()
        else:
            # 單一幣種查詢
            coin_id = COIN_MAPPING.get(selected_coin, None)
            if not coin_id:
                messagebox.showerror("錯誤", "請選擇幣種")
                return

            thread = threading.Thread(
                target=self.perform_query,
                args=(coin_id, from_date, to_date, api_key),
                daemon=True
            )
            thread.start()

    def perform_query(self, coin_id, from_date, to_date, api_key):
        """執行查詢（在背景執行緒）"""
        self.is_querying = True

        # 更新 UI（在主執行緒）
        self.after(0, lambda: self.query_button.configure(state="disabled", text="查詢中..."))
        self.after(0, lambda: self.export_button.configure(state="disabled"))
        self.after(0, lambda: self.result_text.delete("1.0", "end"))
        self.after(0, lambda: self.progress_bar.set(0))
        self.after(0, lambda: self.update_status(f"正在查詢 {coin_id}..."))

        try:
            # 建立 fetcher
            fetcher = CoinGeckoPriceFetcher(api_key=api_key)

            # 查詢價格
            prices = fetcher.get_range_prices(
                coin_id,
                from_date,
                to_date,
                debug=False,
                progress_callback=self.update_progress
            )

            if not prices:
                self.after(0, lambda: messagebox.showerror("錯誤", "無法取得價格資料"))
                self.after(0, lambda: self.update_status("查詢失敗"))
                return

            # 儲存資料
            self.prices_data = prices

            # 顯示結果
            self.after(0, lambda: self.display_results(prices, coin_id, from_date, to_date))
            self.after(0, lambda: self.export_button.configure(state="normal"))
            self.after(0, lambda: self.update_status(f"查詢完成！取得 {len(prices)} 天的資料"))

        except Exception as e:
            self.after(0, lambda: messagebox.showerror("錯誤", f"查詢時發生錯誤：{e}"))
            self.after(0, lambda: self.update_status("查詢失敗"))

        finally:
            self.is_querying = False
            self.after(0, lambda: self.query_button.configure(state="normal", text="🔍 開始查詢"))

    def on_cancel_batch_query(self):
        """終止批量查詢"""
        self.is_batch_query_cancelled = True
        self.after(0, lambda: self.query_button.configure(text="正在終止...", state="disabled"))
        self.after(0, lambda: self.update_status("正在終止批量查詢..."))

    def perform_batch_query(self, from_date, to_date, api_key):
        """批量查詢所有幣種（在背景執行緒）"""
        self.is_querying = True
        self.is_batch_query_cancelled = False  # 重置終止標誌

        # 更新 UI
        self.after(0, lambda: self.query_button.configure(state="normal", text="🛑 終止查詢", command=self.on_cancel_batch_query))
        self.after(0, lambda: self.export_button.configure(state="disabled"))
        self.after(0, lambda: self.result_text.delete("1.0", "end"))
        self.after(0, lambda: self.progress_bar.set(0))

        # 創建輸出目錄
        output_dir = "./csv_file"
        try:
            os.makedirs(output_dir, exist_ok=True)
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("錯誤", f"無法創建目錄 {output_dir}：{e}"))
            self.is_querying = False
            self.after(0, lambda: self.query_button.configure(state="normal", text="🔍 開始查詢"))
            return

        # 初始化統計
        total_coins = len(COIN_LIST)
        success_count = 0
        failed_coins = []

        self.after(0, lambda: self.update_status(f"開始批量查詢 {total_coins} 個幣種..."))

        try:
            # 建立 fetcher
            fetcher = CoinGeckoPriceFetcher(api_key=api_key)

            # 遍歷所有幣種
            for index, coin in enumerate(COIN_LIST, start=1):
                # 檢查是否被取消
                if self.is_batch_query_cancelled:
                    self.after(0, lambda: self.result_text.insert("end", f"\n⚠️  批量查詢已被使用者終止\n"))
                    break

                coin_id = coin['id']
                coin_symbol = coin['symbol']

                # 更新進度
                progress = index / total_coins
                self.after(0, lambda p=progress: self.progress_bar.set(p))
                self.after(0, lambda i=index, t=total_coins, s=coin_symbol:
                          self.progress_label.configure(text=f"正在查詢 {s} ({i}/{t})..."))
                self.after(0, lambda i=index, t=total_coins, s=coin_symbol:
                          self.update_status(f"查詢 {s} ({i}/{t})..."))

                try:
                    # 查詢價格（傳遞取消檢查函數）
                    prices = fetcher.get_range_prices(
                        coin_id,
                        from_date,
                        to_date,
                        debug=False,
                        progress_callback=None,  # 批量查詢時不顯示單個幣種的進度
                        cancellation_check=lambda: self.is_batch_query_cancelled
                    )

                    # 檢查查詢後是否被取消
                    if self.is_batch_query_cancelled:
                        self.after(0, lambda: self.result_text.insert("end", f"\n⚠️  批量查詢已被使用者終止\n"))
                        break

                    if prices:
                        # 保存 CSV
                        output_file = os.path.join(output_dir, f"{coin_id}_{from_date}_{to_date}.csv")
                        save_to_csv(prices, coin_id, from_date, to_date, output_file=output_file)
                        success_count += 1

                        # 計算平均價格
                        stats = calculate_statistics(prices)
                        if stats['avg'] is not None:
                            # 在結果區域顯示平均價格
                            self.after(0, lambda s=coin_symbol, cid=coin_id, avg=stats['avg']:
                                      self.result_text.insert("end", f"✓ {s} ({cid}) - 平均價格: ${avg:.8f}\n"))
                        else:
                            # 無有效價格數據
                            self.after(0, lambda s=coin_symbol, cid=coin_id:
                                      self.result_text.insert("end", f"✗ {s} ({cid}) - NaN\n"))
                    else:
                        failed_coins.append(f"{coin_symbol} ({coin_id})")
                        self.after(0, lambda s=coin_symbol, cid=coin_id:
                                  self.result_text.insert("end", f"✗ {s} ({cid}) - NaN\n"))

                except Exception as e:
                    failed_coins.append(f"{coin_symbol} ({coin_id}): {str(e)}")
                    self.after(0, lambda s=coin_symbol, cid=coin_id:
                              self.result_text.insert("end", f"✗ {s} ({cid}) - NaN\n"))

                # 每次查詢後延遲 0.5 秒，避免 API 限制
                if index < total_coins:  # 最後一個不需要延遲
                    time.sleep(0.5)

            # 顯示統計摘要
            failed_count = len(failed_coins)
            summary = f"\n{'='*60}\n"

            if self.is_batch_query_cancelled:
                summary += f"批量查詢已終止\n"
            else:
                summary += f"批量查詢完成\n"

            summary += f"{'='*60}\n"
            summary += f"成功：{success_count} 個幣種\n"
            summary += f"失敗：{failed_count} 個幣種\n"
            summary += f"輸出目錄：{output_dir}\n"

            if failed_coins:
                summary += f"\n失敗清單：\n"
                for failed in failed_coins:
                    summary += f"  - {failed}\n"

            self.after(0, lambda s=summary: self.result_text.insert("end", s))

            if self.is_batch_query_cancelled:
                self.after(0, lambda sc=success_count, tc=total_coins:
                          self.update_status(f"批量查詢已終止！已完成 {sc}/{tc} 個幣種"))
                # 顯示終止提示
                self.after(0, lambda sc=success_count, tc=total_coins, od=output_dir:
                          messagebox.showwarning("已終止", f"批量查詢已終止！\n已完成：{sc}/{tc}\n檔案已保存至：{od}"))
            else:
                self.after(0, lambda sc=success_count, tc=total_coins:
                          self.update_status(f"批量查詢完成！成功 {sc}/{tc} 個幣種"))
                # 顯示完成提示
                self.after(0, lambda sc=success_count, tc=total_coins, od=output_dir:
                          messagebox.showinfo("完成", f"批量查詢完成！\n成功：{sc}/{tc}\n檔案已保存至：{od}"))

        except Exception as e:
            self.after(0, lambda err=str(e): messagebox.showerror("錯誤", f"批量查詢時發生錯誤：{err}"))
            self.after(0, lambda: self.update_status("批量查詢失敗"))

        finally:
            self.is_querying = False
            self.after(0, lambda: self.query_button.configure(state="normal", text="🔍 開始查詢", command=self.on_query_clicked))
            self.after(0, lambda: self.progress_bar.set(1.0))

    def update_progress(self, current, total, date, price, success):
        """更新進度（回調函數）"""
        progress = current / total
        self.after(0, lambda: self.progress_bar.set(progress))

        if success:
            status = f"✓ ${price:,.8f}"
        else:
            status = "✗ 無資料"

        progress_text = f"{date}: {status} ({current}/{total})"
        self.after(0, lambda: self.progress_label.configure(text=progress_text))

    def display_results(self, prices, coin_id, from_date, to_date):
        """顯示查詢結果"""
        # 清空結果
        self.result_text.delete("1.0", "end")

        # 顯示標題
        self.result_text.insert("end", "=" * 60 + "\n")
        self.result_text.insert("end", f"幣種：{coin_id}\n")
        self.result_text.insert("end", f"日期：{from_date} ~ {to_date}\n")
        self.result_text.insert("end", "=" * 60 + "\n\n")

        # 顯示每日價格
        self.result_text.insert("end", f"{'日期':<15} {'價格 (USD)':<20} {'狀態':<10}\n")
        self.result_text.insert("end", "-" * 60 + "\n")

        for price_data in prices:
            date = price_data['date']
            price = price_data['price']
            if price is not None:
                self.result_text.insert("end", f"{date:<15} ${price:>18,.8f}       ✓\n")
            else:
                self.result_text.insert("end", f"{date:<15} {'N/A':>18}       ✗\n")

        self.result_text.insert("end", "-" * 60 + "\n")

        # 計算並顯示統計資訊
        stats = calculate_statistics(prices)

        if stats['avg'] is not None:
            self.avg_label.value_label.configure(text=f"${stats['avg']:,.8f}")
            self.max_label.value_label.configure(text=f"${stats['max']:,.8f}")
            self.min_label.value_label.configure(text=f"${stats['min']:,.8f}")

            self.result_text.insert("end", f"\n平均價格：${stats['avg']:,.8f}\n")
            self.result_text.insert("end", f"最高價格：${stats['max']:,.8f}\n")
            self.result_text.insert("end", f"最低價格：${stats['min']:,.8f}\n")
            self.result_text.insert("end", f"有效資料：{stats['valid_count']} / {stats['total_count']} 天\n")
        else:
            self.avg_label.value_label.configure(text="N/A")
            self.max_label.value_label.configure(text="N/A")
            self.min_label.value_label.configure(text="N/A")
            self.result_text.insert("end", "\n無有效資料\n")

    def on_export_clicked(self):
        """匯出 CSV 按鈕點擊事件"""
        if not self.prices_data:
            messagebox.showwarning("警告", "沒有資料可匯出")
            return

        # 取得參數
        selected_coin = self.coin_combobox.get()
        coin_id = COIN_MAPPING.get(selected_coin, "unknown")
        from_date = self.from_date_entry.get().strip()
        to_date = self.to_date_entry.get().strip()

        # 預設檔名
        default_filename = f"{coin_id}_{from_date}_{to_date}_prices.csv"

        # 開啟儲存對話框
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile=default_filename,
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if filename:
            try:
                output_file = save_to_csv(
                    self.prices_data,
                    coin_id,
                    from_date,
                    to_date,
                    output_file=filename
                )
                messagebox.showinfo("成功", f"資料已匯出至：\n{output_file}")
                self.update_status(f"已匯出：{output_file}")
            except Exception as e:
                messagebox.showerror("錯誤", f"匯出失敗：{e}")

    def on_clear_clicked(self):
        """清空按鈕點擊事件"""
        self.result_text.delete("1.0", "end")
        self.prices_data = []
        self.progress_bar.set(0)
        self.progress_label.configure(text="")
        self.avg_label.value_label.configure(text="---")
        self.max_label.value_label.configure(text="---")
        self.min_label.value_label.configure(text="---")
        self.export_button.configure(state="disabled")
        self.update_status("已清空")

    def update_status(self, message):
        """更新狀態列"""
        self.status_label.configure(text=f"📡 {message}")


def main():
    """主程式"""
    app = CryptoPriceGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
