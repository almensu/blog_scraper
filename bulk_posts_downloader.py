import requests
from lxml import html
import time
from datetime import datetime
import os
from pathlib import Path
import csv

class BulkPostsDownloader:
    """
    批量文章下载器
    Bulk article downloader for blog posts
    """
    
    def __init__(self):
        # 初始化基础 URL 和请求头 / Initialize base URL and request headers
        self.base_url = "https://baoyu.io"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        # 创建文章保存目录 / Create directory for saving articles
        self.articles_dir = Path("articles")
        self.articles_dir.mkdir(exist_ok=True)
    
    def download_from_csv(self, csv_file):
        """
        从 CSV 文件读取 URL 并下载文章
        Read URLs from CSV file and download articles
        
        Args:
            csv_file (str): CSV 文件路径 / Path to CSV file
        """
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    print(f"Downloading: {row['title']}")
                    self.scrape_article(row['url'])
                    # 添加延迟避免请求过快 / Add delay to avoid too frequent requests
                    time.sleep(1)
                except Exception as e:
                    print(f"Error downloading {row['url']}: {e}")
    
    def scrape_article(self, url):
        """
        抓取单篇文章内容并保存为 Markdown
        Scrape single article and save as Markdown
        
        Args:
            url (str): 文章 URL / Article URL
        """
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

if __name__ == "__main__":
    # 创建下载器实例并开始下载 / Create downloader instance and start downloading
    downloader = BulkPostsDownloader()
    downloader.download_from_csv("blog_posts_20241107.csv")