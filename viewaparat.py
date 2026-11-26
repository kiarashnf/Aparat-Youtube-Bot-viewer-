import requests
import time
import random
import threading
from queue import Queue
from fake_useragent import UserAgent
import logging
from datetime import datetime

# --- CONFIG ---
LIVE_URL = ""  # آدرس لایو خودت رو اینجا بذار یا از ورودی بگیر
NUM_VIEWS = 100  # تعداد ویو مورد نظر
MAX_THREADS = 10  # حداکثر thread همزمان
DELAY_MIN = 1  # حداقل تاخیر بین درخواست‌ها (ثانیه)
DELAY_MAX = 5  # حداکثر تاخیر بین درخواست‌ها (ثانیه)
# -----------------

# تنظیمات لاگ
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(message)s",
    handlers=[
        logging.FileHandler("view_booster.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

class YouTubeViewBooster:
    def __init__(self, live_url, num_views):
        self.live_url = live_url
        self.num_views = num_views
        self.view_count = 0
        self.lock = threading.Lock()
        self.ua = UserAgent()
        self.session = requests.Session()
        self.cookies = self._generate_cookies()
        self.session.cookies.update(self.cookies)
        self.running = True

        # لیست URL‌های تصادفی برای گرم کردن سشن
        self.warmup_urls = [
            "https://www.youtube.com/",
            "https://www.youtube.com/feed/trending",
            "https://www.youtube.com/feed/subscriptions",
            "https://www.youtube.com/feed/history"
        ]

    def _generate_cookies(self):
        """تولید کوکی‌های تصادفی برای شبیه‌سازی کاربر واقعی"""
        return {
            "YSC": f"{random.randint(1000000000, 9999999999)}",
            "VISITOR_INFO1_LIVE": f"{random.randint(100000000, 999999999)}",
            "PREF": f"f1={random.randint(1, 1000)}&f2={random.randint(1, 1000)}&f3={random.randint(1, 1000)}",
            "HL": "en",
            "SOC": random.choice(["en-US", "fa-IR", "ar-SA", "tr-TR"])
        }

    def _get_headers(self):
        """ساخت هدرهای تصادفی"""
        return {
            "User-Agent": self.ua.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://www.google.com/",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }

    def _warmup_session(self):
        """گرم کردن سشن با بازدید از صفحات تصادفی یوتیوب"""
        for url in self.warmup_urls:
            try:
                self.session.get(
                    url,
                    headers=self._get_headers(),
                    timeout=10
                )
                time.sleep(random.uniform(0.5, 1.5))
            except:
                pass

    def _simulate_view(self):
        """شبیه‌سازی یک ویو برای لایو"""
        try:
            # گرم کردن سشن قبل از ارسال درخواست به لایو
            if random.random() < 0.3:  # 30% شانس برای گرم کردن
                self._warmup_session()

            # درخواست به لایو
            response = self.session.get(
                self.live_url,
                headers=self._get_headers(),
                stream=True,  # برای شبیه‌سازی لود ویدیو
                timeout=15
            )

            # شبیه‌سازی لود ویدیو (خواندن قسمتی از محتوا)
            if response.status_code == 200:
                for _ in response.iter_content(chunk_size=1024):
                    if random.random() < 0.1:  # 10% شانس برای توقف زودهنگام
                        break
                    time.sleep(random.uniform(0.1, 0.5))

                with self.lock:
                    self.view_count += 1
                    logging.info(f"✅ View #{self.view_count}/{self.num_views} added!")

                return True
            else:
                logging.warning(f"⚠️ Failed to load live (Status: {response.status_code})")
                return False

        except Exception as e:
            logging.error(f"❌ Error: {str(e)}")
            return False

    def worker(self):
        """کارگر برای هر thread"""
        while self.running and self.view_count < self.num_views:
            success = self._simulate_view()
            if success:
                time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))
            else:
                time.sleep(random.uniform(DELAY_MAX, DELAY_MAX * 2))

    def start(self):
        """شروع عملیات بوست ویو"""
        logging.info("🚀 Starting YouTube View Booster...")
        logging.info(f"🎯 Target: {self.live_url}")
        logging.info(f"📈 Goal: {self.num_views} views")

        threads = []
        for _ in range(min(MAX_THREADS, self.num_views)):
            t = threading.Thread(target=self.worker)
            t.start()
            threads.append(t)

        # منتظر ماندن تا تمام شود
        for t in threads:
            t.join()

        self.running = False
        logging.info("✨ Operation completed!")
        logging.info(f"📊 Total views added: {self.view_count}")

if __name__ == "__main__":
    print("""
██╗  ██╗██╗ █████╗ ██████╗  █████╗ ███████╗██╗  ██╗
██║ ██╔╝██║██╔══██╗██╔══██╗██╔══██╗██╔════╝██║  ██║
█████╔╝ ██║███████║██████╔╝███████║███████╗███████║
██╔═██╗ ██║██╔══██║██╔══██╗██╔══██║╚════██║██╔══██║
██║  ██╗██║██║  ██║██║  ██║██║  ██║███████║██║  ██║
╚═╝  ╚═╝╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
    """)

    live_url = input("🔗 آدرس لایو یوتیوب رو وارد کن (مثال: https://www.youtube.com/live/ABC123): ").strip()
    num_views = int(input("📊 چندتا ویو میخوای؟ (مثال: 100): "))

    booster = YouTubeViewBooster(live_url, num_views)
    booster.start()