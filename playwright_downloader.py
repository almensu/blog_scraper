from playwright.sync_api import sync_playwright
from pathlib import Path
import random
import time

def take_screenshot(url):
    with sync_playwright() as p:
        # 使用有头模式
        browser = p.chromium.launch(headless=False)
        
        context = browser.new_context(
            viewport={'width': 750, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        page = context.new_page()
        
        # 模拟人类行为
        page.set_default_timeout(30000)
        page.goto(url)
        
        # 随机滚动
        for _ in range(3):
            page.mouse.wheel(0, random.randint(300, 700))
            time.sleep(random.uniform(0.5, 2))
        
        # 等待页面完全加载
        page.wait_for_load_state('networkidle')
        time.sleep(random.uniform(2, 4))
        
        screenshots_dir = Path("screenshots")
        screenshots_dir.mkdir(exist_ok=True)
        
        filename = url.split('/')[-1][:30] + '.png'
        filepath = screenshots_dir / filename
        
        page.screenshot(path=str(filepath), full_page=True)
        print(f"Screenshot saved: {filepath}")
        
        # 随机延迟后关闭
        time.sleep(random.uniform(1, 3))
        browser.close()

if __name__ == "__main__":
    url = "https://baoyu.io/blog/ai/why-do-someone-think-chatgpt-doesnot-really-work-for-them"
    take_screenshot(url)
