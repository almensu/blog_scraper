import requests
from lxml import html
import time
from datetime import datetime
import os
from pathlib import Path
import csv
import random

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
    
    def download_from_csv(self, csv_file):
        """
        从 CSV 文件读取 URL 并下载文章，跳过已下载的文章
        Read URLs from CSV file and download articles, skip existing ones
        
        Args:
            csv_file (str): CSV 文件路径 / Path to CSV file
        """
        total = 0
        success = 0
        failed = 0
        skipped = 0
        
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
                    self.scrape_article(row['url'])
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
    
    def scrape_article(self, url):
        """
        抓取单篇文章内容并保存为 Markdown
        Scrape single article and save as Markdown
        
        Args:
            url (str): 文章 URL / Article URL
        """
        try:
            # 添加重试机制
            for attempt in range(3):
                response = requests.get(url, headers=self.headers, timeout=10)
                
                if response.status_code == 200:
                    break
                    
                time.sleep(5 * (attempt + 1))  # 递增等待时间
            
            response.raise_for_status()
            
            # 发送请求获取页面内容 / Send request to get page content
            response = requests.get(url, headers=self.headers)
            tree = html.fromstring(response.content)
            
            # 提取文章信息 / Extract article information
            title = tree.xpath("//h1/text()")[0].strip()
            date = tree.xpath("//time")[0].text_content().strip()
            
            # 提取文章正文 / Extract article content
            paragraphs = tree.xpath("//article//p/text()")
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
            
        except requests.exceptions.RequestException as e:
            print(f"Network error: {e}")
            raise

if __name__ == "__main__":
    # 创建下载器实例并开始下载 / Create downloader instance and start downloading
    downloader = BulkPostsDownloader()
    downloader.download_from_csv("blog_posts_20241108.csv")