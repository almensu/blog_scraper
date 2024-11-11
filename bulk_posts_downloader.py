from pathlib import Path
import asyncio
from playwright.async_api import async_playwright
import random
from typing import Optional
import csv
import time

class BulkPostsDownloader:
    """
    批量文章下载器
    Bulk article downloader for blog posts
    """
    
    def __init__(self):
        # 初始化基础 URL 和请求头 / Initialize base URL and request headers
        self.base_url = "https://baoyu.io"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
        }
        
        # 创建文章保存目录 / Create directory for saving articles
        self.articles_dir = Path("articles")
        self.articles_dir.mkdir(exist_ok=True)
        
        # 初始化 playwright 相关属性
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        
        self.loop = asyncio.get_event_loop()
        # Set up global exception handler
        self.loop.set_exception_handler(self.handle_exception)
    
    async def init_browser(self):
        """初始化浏览器"""
        try:
            print("Starting browser...")
            self.playwright = await async_playwright().start()
            print("Browser started")
            
            print("Launching chromium...")
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=[
                    '--disable-gpu',
                    '--disable-dev-shm-usage',
                    '--disable-setuid-sandbox',
                    '--no-sandbox',
                ]
            )
            print("Chromium launched")
            
            print("Creating context...")
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent=self.headers["User-Agent"]
            )
            print("Context created")
            
            print("Creating new page...")
            self.page = await self.context.new_page()
            print(f"Page created: {self.page}")
            
            if self.page is None:
                raise Exception("Failed to create page")
                
            print("Setting timeouts...")
            self.page.set_default_timeout(30000)
            self.page.set_default_navigation_timeout(30000)
            print("Browser initialization complete")
            
        except Exception as e:
            print(f"Browser initialization error: {e}")
            print(f"Current state: playwright={self.playwright}, browser={self.browser}, context={self.context}, page={self.page}")
            await self.close_browser()
            raise
    
    async def close_browser(self):
        """关闭浏览器"""
        if self.browser:
            await self.browser.close()
            await self.playwright.stop()
    
    async def human_scroll(self):
        """模拟人类滚动行为"""
        for _ in range(random.randint(3, 6)):
            await self.page.mouse.wheel(0, random.randint(300, 800))
            await asyncio.sleep(random.uniform(0.5, 2))
    
    async def scrape_article(self, url):
        """
        使用 playwright 抓取文章
        """
        if not self.page:
            await self.init_browser()

        try:
            print(f"Accessing URL: {url}")
            # 随机延迟
            await asyncio.sleep(random.uniform(2, 5))
            
            # 访问页面
            print("Loading page...")
            await self.page.goto(url)
            print("Page loaded")
            
            print("Simulating scroll...")
            await self.human_scroll()
            print("Scroll complete")

            # 提取文章信息
            print("Extracting content...")
            title = await self.page.locator("h1").text_content()
            print(f"Title: {title}")
            
            date = await self.page.locator("time").text_content()
            print(f"Date: {date}")
            
            # 提取段落内容
            paragraphs = await self.page.locator("article p").all_text_contents()
            content = "\n\n".join(p.strip() for p in paragraphs if p.strip())
            print(f"Content length: {len(content)} chars")

            # 生成 Markdown 格式内容
            markdown = f"""# {title}

发布日期: {date}

{content}
"""
            # 生成安全的文件名
            safe_title = "".join(c for c in title[:20] if c.isalnum() or c in ('-', '_', '.'))
            filename = f"{safe_title}.md"
            filepath = self.articles_dir / filename
            
            # 保存文件
            print(f"Saving to: {filepath}")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(markdown)
                
            print(f"Successfully saved: {filename}")
            
        except Exception as e:
            print(f"Error details:")
            print(f"- URL: {url}")
            print(f"- Error type: {type(e).__name__}")
            print(f"- Error message: {str(e)}")
            print(f"- Current page URL: {self.page.url}")
            print(f"- Page content length: {len(await self.page.content())}")
            raise
    
    async def download_from_csv(self, csv_file):
        """
        异步版本的批量下载
        """
        try:
            await self.init_browser()
            
            # 读取 CSV 并保存到临时列表
            rows = []
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames
                if 'status' not in fieldnames:
                    fieldnames = fieldnames + ['status']
                rows = list(reader)
                
            total = len(rows)
            success = failed = skipped = 0
            
            # 处理文章
            for i, row in enumerate(rows, 1):
                if row.get('status') == 'completed':
                    print(f"Skipping {i}/{total}: {row['title']} (already completed)")
                    skipped += 1
                    continue
                    
                try:
                    print(f"\nProcessing {i}/{total}: {row['title']}")
                    await self.scrape_article(row['url'])
                    row['status'] = 'completed'  # 更新态
                    success += 1
                    time.sleep(1)
                except Exception as e:
                    failed += 1
                    row['status'] = 'failed'  # 标记失败
                    print(f"Error downloading {row['url']}: {e}")
                
                # 实时更新 CSV
                with open(csv_file, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(rows)
                    
            print(f"\nDownload completed:")
            print(f"Total: {total}")
            print(f"Success: {success}")
            print(f"Failed: {failed}")
            print(f"Skipped: {skipped}")
        finally:
            await self.close_browser()
    
    def handle_exception(self, loop, context):
        """Handle exceptions from tasks"""
        # Extract exception details from context
        exception = context.get('exception', context['message'])
        print(f'Caught exception: {exception}')
        
        # Create task to handle cleanup and shutdown
        asyncio.create_task(self.cleanup_and_shutdown(exception))

    async def cleanup_and_shutdown(self, exception):
        """Cleanup resources and shutdown"""
        print(f"Cleaning up after error: {exception}")
        await self.close_browser()
        self.loop.stop()

if __name__ == "__main__":
    # 创建下载器实例并开始下载 / Create downloader instance and start downloading
    downloader = BulkPostsDownloader()
    asyncio.run(downloader.download_from_csv("blog_posts_20241108.csv"))