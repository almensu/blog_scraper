import requests
from lxml import html
import csv
from datetime import datetime
import time

def scrape_blog():
    url = "https://baoyu.io/blog"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        # Add delay to be polite
        time.sleep(1)
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        tree = html.fromstring(response.content)
        
        articles = []
        for article in tree.xpath("//article"):
            title = article.xpath("h2/text()")
            summary = article.xpath("p[1]/text()")
            date = article.xpath("p[2]/text()")
            href = article.xpath(".//a/@href")[0]
            url = f"https://baoyu.io/{href}" if href.startswith('blog/') else f"https://baoyu.io/blog/{href}"
            
            if title and summary and date:
                articles.append({
                    "title": title[0].strip(),
                    "summary": summary[0].strip(),
                    "date": date[0].strip(),
                    "url": url
                })
                
        # Write to CSV
        filename = f"blog_posts_{datetime.now().strftime('%Y%m%d')}.csv"
        with open(filename, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["title", "summary", "date", "url"])
            writer.writeheader()
            writer.writerows(articles)
            
        print(f"Successfully scraped {len(articles)} articles to {filename}")
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    scrape_blog() 