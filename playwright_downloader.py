from playwright.sync_api import sync_playwright
import time
from datetime import datetime
from pathlib import Path
import csv
import random

class PlaywrightDownloader:
    """
    使用 Playwright 的批量文章下载器
    Bulk article downloader using Playwright
    """
    
    def __init__(self):
        # 初始化 Playwright / Initialize Playwright
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=True,  # 无头模式 / Headless mode
        )
        # 创建上下文 / Create context
        self.context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
        )
        
        # 创建文章保存目录 / Create directory for saving articles
        self.articles_dir = Path("articles")
        self.articles_dir.mkdir(exist_ok=True)
    
    def download_from_csv(self, csv_file):
        """从 CSV 文件读取 URL 并下载文章 / Download articles from CSV file"""
        total = success = failed = skipped = 0
        existing_files = {f.stem for f in self.articles_dir.glob("*.md")}
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            total = len(rows)
            
            print(f"Found {total} articles to process")
            
            for i, row in enumerate(rows, 1):
                # 随机延迟 / Random delay
                time.sleep(random.uniform(2, 5))
                
                safe_title = "".join(c for c in row['title'][:20] if c.isalnum() or c in ('-', '_', '.'))
                
                if safe_title in existing_files:
                    print(f"Skipping {i}/{total}: {row['title']} (already exists)")
                    skipped += 1
                    continue
                
                try:
                    print(f"\nProcessing {i}/{total}: {row['title']}")
                    if self.scrape_article(row['url'], safe_title):
                        success += 1
                    else:
                        failed += 1
                except Exception as e:
                    failed += 1
                    print(f"Error downloading {row['url']}: {e}")
            
            print(f"\nDownload completed:")
            print(f"Total: {total}")
            print(f"Success: {success}")
            print(f"Failed: {failed}")
            print(f"Skipped: {skipped}")
    
    def scrape_article(self, url, safe_title):
        """使用 Playwright 抓取文章 / Scrape article using Playwright"""
        page = self.context.new_page()
        try:
            # 访问页面并等待加载 / Visit page and wait for load
            page.goto(url, wait_until="networkidle")
            time.sleep(random.uniform(1, 2))  # 短暂等待
            
            # 提取内容 / Extract content
            title = page.locator("h1").text_content().strip()
            date = page.locator("time").text_content().strip()
            
            # 使用 evaluate 执行 JavaScript 获取所有段落
            paragraphs = page.locator("article p").all_text_contents()
            content = "\n\n".join(p.strip() for p in paragraphs if p.strip())
            
            # 生成 Markdown / Generate Markdown
            markdown = f"""# {title}

发布日期: {date}

{content}
"""
            # 保存文件 / Save file
            filename = f"{safe_title}.md"
            filepath = self.articles_dir / filename
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(markdown)
            
            print(f"Saved: {filename}")
            return True
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return False
            
        finally:
            page.close()
    
    def __del__(self):
        """清理资源 / Cleanup resources"""
        try:
            self.browser.close()
            self.playwright.stop()
        except:
            pass

if __name__ == "__main__":
    # 创建下载器实例并开始下载 / Create downloader instance and start downloading
    downloader = PlaywrightDownloader()
    downloader.download_from_csv("blog_posts_20241108.csv")
