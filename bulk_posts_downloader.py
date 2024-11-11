import asyncio
from playwright.async_api import async_playwright
import random
from typing import Optional

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
        
        self.browser = None
        self.context = None
        self.page = None
    
    async def init_browser(self):
        """初始化浏览器"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=True)
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent=self.headers["User-Agent"]
        )
        self.page = await self.context.new_page()
        
        # 模拟人类行为
        await self.page.set_default_timeout(30000)
        await self.page.set_default_navigation_timeout(30000)
    
    async def close_browser(self):
        """关闭浏览器"""
        if self.browser:
            await self.browser.close()
    
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
            # 随机延迟
            await asyncio.sleep(random.uniform(2, 5))
            
            # 访问页面
            await self.page.goto(url)
            await self.human_scroll()

            # 提取文章信息
            title = await self.page.locator("h1").text_content()
            date = await self.page.locator("time").text_content()
            
            # 提取段落内容
            paragraphs = await self.page.locator("article p").all_text_contents()
            content = "\n\n".join(p.strip() for p in paragraphs if p.strip())

            # 生成 Markdown 格式内容 / Generate Markdown content
            markdown = f"""# {title}

发布日期: {date}

{content}
"""
            # 生成安全的文件名 / Generate safe filename
            safe_title = "".join(c for c in title[:20] if c.isalnum() or c in ('-', '_', '.'))
            filename = f"{safe_title}.md"
            filepath = self.articles_dir / filename
            
            # 保存文件 / Save file
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(markdown)
                
            print(f"Saved: {filename}")
            
        except Exception as e:
            print(f"Playwright error: {e}")
            raise
    
    async def download_from_csv(self, csv_file):
        """
        异步版本的批量下载
        """
        try:
            await self.init_browser()
            # 获取已下载的文章列表 / Get list of existing articles
            existing_files = {f.stem for f in self.articles_dir.glob("*.md")}
            
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                total = len(rows)
                
                print(f"Found {total} articles to process")
                
                for i, row in enumerate(rows, 1):
                    # 随机延迟 2-5 秒
                    delay = random.uniform(2, 5)
                    time.sleep(delay)
                    
                    # 生成安全的文件名用于检查 / Generate safe filename for checking
                    safe_title = "".join(c for c in row['title'][:20] if c.isalnum() or c in ('-', '_', '.'))
                    
                    # 如果文章已存在则跳过 / Skip if article already exists
                    if safe_title in existing_files:
                        print(f"Skipping {i}/{total}: {row['title']} (already exists)")
                        skipped += 1
                        continue
                        
                    try:
                        print(f"\nProcessing {i}/{total}: {row['title']}")
                        await self.scrape_article(row['url'])
                        success += 1
                        time.sleep(1)
                    except Exception as e:
                        failed += 1
                        print(f"Error downloading {row['url']}: {e}")
                        
                print(f"\nDownload completed:")
                print(f"Total: {total}")
                print(f"Success: {success}")
                print(f"Failed: {failed}")
                print(f"Skipped: {skipped}")
        finally:
            await self.close_browser()

if __name__ == "__main__":
    # 创建下载器实例并开始下载 / Create downloader instance and start downloading
    downloader = BulkPostsDownloader()
    asyncio.run(downloader.download_from_csv("blog_posts_20241108.csv"))