from playwright.sync_api import sync_playwright
from pathlib import Path

def take_screenshot(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_context(
            viewport={'width': 750, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
        ).new_page()
        
        page.goto(url, wait_until="networkidle")
        
        # 创建screenshots目录
        screenshots_dir = Path("screenshots")
        screenshots_dir.mkdir(exist_ok=True)
        
        # 从URL提取文件名
        filename = url.split('/')[-1][:30] + '.png'
        filepath = screenshots_dir / filename
        
        # 截取全页面
        page.screenshot(path=str(filepath), full_page=True)
        print(f"Screenshot saved: {filepath}")

if __name__ == "__main__":
    url = "https://baoyu.io/translations/how-to-reach-5m-arr-profitably"
    take_screenshot(url)