import speedtest
import schedule
import time
import datetime
import os
import threading
import sys
import subprocess


class ProgressBar:
    def __init__(self, interval_seconds=300):  # 5分钟=300秒
        self.interval = interval_seconds
        self.running = False
        self.thread = None
        self.last_test_time = None
        self.lock = threading.Lock()  # 添加锁防止输出冲突

    def start(self):
        """启动进度条"""
        self.running = True
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        """停止进度条"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)

    def _run(self):
        """进度条主循环"""
        dots = 0
        start_time = time.time()

        while self.running:
            with self.lock:  # 加锁确保输出完整性
                elapsed = time.time() - start_time
                remaining = max(0, self.interval - elapsed)

                # 动态显示进度点
                dots = (dots + 1) % 4
                progress_dots = "." * dots + " " * (3 - dots)

                # 格式化剩余时间
                minutes = int(remaining // 60)
                seconds = int(remaining % 60)

                # 清空当前行并打印进度
                sys.stdout.write('\r')
                sys.stdout.write(' ' * 50)  # 先清空区域
                sys.stdout.write('\r')
                sys.stdout.write(f'🔄 等待中{progress_dots} 下次测试: {minutes:02d}:{seconds:02d}后')
                sys.stdout.flush()

            time.sleep(0.5)  # 更新频率

        # 进度条结束时清空行
        with self.lock:
            sys.stdout.write('\r' + ' ' * 50 + '\r')
            sys.stdout.flush()


class TestCounter:
    def __init__(self):
        self.count = 0
        self.lock = threading.Lock()

    def increment(self):
        with self.lock:
            self.count += 1
            return self.count

    def get_current(self):
        with self.lock:
            return self.count


class TestAnimation:
    """简单的测试动画"""

    def __init__(self):
        self.running = False
        self.thread = None
        self.lock = threading.Lock()

    def start(self, test_number):
        """启动测试动画"""
        self.running = True
        self.thread = threading.Thread(target=self._run, args=(test_number,))
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        """停止测试动画"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
        with self.lock:
            sys.stdout.write('\r' + ' ' * 60 + '\r')
            sys.stdout.flush()

    def _run(self, test_number):
        """动画循环"""
        dots = 0
        while self.running:
            with self.lock:
                dots = (dots + 1) % 4
                progress_dots = "." * dots
                sys.stdout.write('\r')
                sys.stdout.write(' ' * 60)  # 先清空区域
                sys.stdout.write('\r')
                sys.stdout.write(f'📡 正在进行第{test_number}次测试{progress_dots}')
                sys.stdout.flush()
            time.sleep(0.5)


def get_wifi_name():
    """获取当前连接的WiFi名称（使用确认可用的命令）"""
    try:
        # 使用确认可用的命令
        cmd = "networksetup -getairportnetwork en0"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            # 解析输出，格式通常是："Current Wi-Fi Network: YourWiFiName"
            output = result.stdout.strip()
            if "Current Wi-Fi Network:" in output:
                wifi_name = output.split("Current Wi-Fi Network:")[1].strip()
                return wifi_name if wifi_name else "未知网络"

        return "未知网络"

    except Exception as e:
        print(f"获取WiFi名称时出错: {e}")
        return "未知网络"


# 创建全局计数器
test_counter = TestCounter()
test_animation = TestAnimation()


def test_wifi_speed(progress_bar):
    """测试WiFi速度并记录结果"""
    try:
        # 停止进度条
        progress_bar.stop()

        # 清空进度行 - 确保完全清空
        sys.stdout.write('\r' + ' ' * 60 + '\r')
        sys.stdout.flush()

        # 获取测试次数
        test_number = test_counter.increment()

        # 获取WiFi名称
        wifi_name = get_wifi_name()

        # 启动测试动画（开始测试中的动画线程）
        test_animation.start(test_number)

        # 创建speedtest对象
        st = speedtest.Speedtest()
        st.get_best_server()

        # 测试下载和上传速度（转换为Mbps）
        download_speed = st.download() / 1_000_000
        upload_speed = st.upload() / 1_000_000

        # 获取ping值
        ping = st.results.ping

        # 停止测试动画（停止测试中的动画线程）
        test_animation.stop()

        # 获取时间戳
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 格式化结果
        result = f"[{current_time}] WiFi: {wifi_name} | 下载: {download_speed:.2f} Mbps, 上传: {upload_speed:.2f} Mbps, 延迟: {ping:.1f} ms"

        # 写入文件
        with open("wifi_speed_log.txt", "a", encoding="utf-8") as f:
            f.write(result + "\n")

        # 单行输出结果 - 确保在新行输出
        print(
            f"✅ 第{test_number}次测试完成! 📶 WiFi: {wifi_name} | 📥 下载: {download_speed:.2f} Mbps  📤 上传: {upload_speed:.2f} Mbps  ⏱️ 延迟: {ping:.1f} ms ")

        # 重新启动进度条（等待中的动画线程）
        progress_bar.start()

    except Exception as e:
        # 停止测试动画
        test_animation.stop()

        # 停止进度条
        progress_bar.stop()
        sys.stdout.write('\r' + ' ' * 60 + '\r')
        sys.stdout.flush()

        test_number = test_counter.get_current()
        wifi_name = get_wifi_name()
        error_msg = f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] WiFi: {wifi_name} | 错误: {str(e)}"
        print(f"❌ 第{test_number}次测试失败! 📶 WiFi: {wifi_name} | 错误: {str(e)}")
        with open("wifi_speed_log.txt", "a", encoding="utf-8") as f:
            f.write(error_msg + "\n")

        # 重新启动进度条
        progress_bar.start()


def main():
    """主函数"""
    # 创建进度条对象
    progress_bar = ProgressBar(interval_seconds=300)  # 5分钟

    print("🚀 WiFi速度监控脚本启动...")
    print("⏰ 每5分钟自动检测一次WiFi速度")
    print("📝 结果将保存到 wifi_speed_log.txt")
    print("⏹️  按 Ctrl+C 停止监控\n")

    # 创建日志文件头（如果文件不存在）
    if not os.path.exists("wifi_speed_log.txt"):
        with open("wifi_speed_log.txt", "w", encoding="utf-8") as f:
            f.write("WiFi速度监控日志\n")
            f.write("=" * 50 + "\n")
            f.write("时间格式: [年-月-日 时:分:秒] WiFi: 网络名称 | 下载: X.XX Mbps, 上传: X.XX Mbps, 延迟: X.X ms\n")
            f.write("=" * 50 + "\n")

    # 包装测试函数以传入进度条参数
    def test_with_progress():
        test_wifi_speed(progress_bar)

    # 立即执行一次测试
    test_with_progress()

    # 设置每5分钟执行一次
    schedule.every(5).minutes.do(test_with_progress)

    # 启动初始进度条
    progress_bar.start()

    try:
        # 保持程序运行
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        progress_bar.stop()
        test_animation.stop()
        total_tests = test_counter.get_current()
        print(f"\n\n🛑 监控已停止")
        print(f"📊 共完成 {total_tests} 次测试")
        print("📋 查看完整日志请打开: wifi_speed_log.txt")


if __name__ == "__main__":
    main()