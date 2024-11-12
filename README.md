# 🤖 Blog Post Scraper

A comprehensive tool for scraping blog posts using multiple methods (Requests/BeautifulSoup and Playwright). Built for efficiency and ease of use! ✨

## ✨ Features

- 📝 Single post scraping with metadata extraction
- 📚 Bulk posts downloading
- 📸 Screenshot capture capability
- ⚡ Support for both sync and async operations
- 📊 CSV export for post metadata
- 📄 Markdown file generation for each article

## 🗂️ Project Structure

```
.
├── blog_scraper.py           # Main scraper implementation
├── single_post_scraper.py    # Single post scraping logic
├── bulk_posts_downloader.py  # Batch download functionality
├── playwright_downloader.py  # Playwright-based scraper
├── single_playwright_screenshot.py  # Screenshot capture utility
└── articles/                 # Scraped articles storage
```

## 🚀 Prerequisites

- Python 3.8+
- pip

## 💻 Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd blog-post-scraper
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## 🎮 Usage

### 📝 Single Post Scraping
```bash
python single_post_scraper.py --url <blog-post-url>
```

### 📚 Bulk Download
```bash
python bulk_posts_downloader.py --input blog_posts_20241108.csv
```

### 📸 Capture Screenshots
```bash
python single_playwright_screenshot.py --url <blog-post-url>
```

## ⚙️ Configuration

- 📁 Output articles are stored in the `articles/` directory
- 📊 Post metadata is saved in CSV format
- 🖼️ Screenshots are saved in PNG format

## 📦 Dependencies

- 🌐 requests: HTTP requests
- 🔍 beautifulsoup4: HTML parsing
- 🎭 playwright: Browser automation and screenshots

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

MIT License - see LICENSE file for details

---
⭐ Star us on GitHub if this project helps you!