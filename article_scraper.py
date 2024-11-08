import requests
from lxml import html
import time
from datetime import datetime
import os
from pathlib import Path

class ArticleScraper:
    def __init__(self):
        self.base_url = "https://baoyu.io"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        self.articles_dir = Path("articles")
        self.articles_dir.mkdir(exist_ok=True)
    
    def scrape_article(self, url):
        try:
            time.sleep(1)
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            tree = html.fromstring(response.content)
            
            # 提取文章信息
            title = tree.xpath("//h1/text()")[0].strip()
            date = tree.xpath("//text()[contains(., 'Published on')]")[0]
            date = date.replace("Published on ", "").strip()
            
            # 提取文章内容
            paragraphs = tree.xpath("//article//p/text()")
            content = "\n\n".join(p.strip() for p in paragraphs if p.strip())
            
            # 生成 markdown
            markdown = f"""# {title}

发布日期: {date}

{content}
"""
            # 保存文件
            filename = f"{date}-{title[:30]}.md"
            filepath = self.articles_dir / filename
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(markdown)
                
            print(f"Successfully saved: {filename}")
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")

if __name__ == "__main__":
    scraper = ArticleScraper()
    url = "https://baoyu.io/blog/from-rubber-duck-to-ai-assistant-programmer-debugging-secrets"
    scraper.scrape_article(url)
