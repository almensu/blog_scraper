import requests
from lxml import html
import csv
from datetime import datetime
import time

def scrape_blog(max_pages=None):
    base_url = "https://baoyu.io/blog"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    all_articles = []
    
    urls = {
        "https://baoyu.io/blog": "blog",
        "https://baoyu.io/translations": "translations" 
    }
    
    for base_url, category in urls.items():
        page = 1
        while True:
            url = f"{base_url}?page={page}" if page > 1 else base_url
            
            try:
                time.sleep(1)
                print(f"Scraping {category} page {page}...")
                
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                tree = html.fromstring(response.content)
                
                articles = tree.xpath("//article")
                if not articles or (max_pages and page >= max_pages):
                    print(f"Finished {category} at page {page}")
                    break
                    
                for article in articles:
                    title = article.xpath(".//h2/text()")
                    summary = article.xpath(".//p[1]/text()")
                    date = article.xpath(".//p[2]/text()")
                    href = article.xpath(".//a/@href")[0]
                    url = f"https://baoyu.io/{href}" if href.startswith('blog/') else f"https://baoyu.io/blog/{href}"
                    
                    if title and summary and date:
                        all_articles.append({
                            "title": title[0].strip(),
                            "summary": summary[0].strip(),
                            "date": date[0].strip(),
                            "url": url,
                            "category": category
                        })
                        
                page += 1
                
            except requests.exceptions.RequestException as e:
                print(f"Error fetching {category} page {page}: {e}")
                break
                
    filename = f"blog_posts_{datetime.now().strftime('%Y%m%d')}.csv"
    with open(filename, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "summary", "date", "url", "category"])
        writer.writeheader()
        writer.writerows(all_articles)
        
    print(f"Successfully scraped {len(all_articles)} articles to {filename}")

if __name__ == "__main__":
    scrape_blog()
    # scrape_blog(max_pages=3) 