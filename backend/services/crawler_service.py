"""
crawler_service.py
------------------
Web crawler for automated product scanning from e-commerce platforms.
"""

import re
import logging
import random
import threading
import time
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

try:
    import requests
    from bs4 import BeautifulSoup
    CRAWLER_DEPS = True
except ImportError:
    CRAWLER_DEPS = False


class CrawlerService:
    """Automated web crawler for product compliance scanning."""

    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept-Language': 'en-IN,en;q=0.9',
    }

    SEED_URLS = {
        "amazon": "https://www.amazon.in/s?k=packaged+food",
        "flipkart": "https://www.flipkart.com/search?q=packaged+food",
        "ondc_mystore": "https://www.mystore.in/en/search?q=food",
        "ondc_magicpin": "https://magicpin.in/india/products/food",
    }

    def __init__(self, analyzer=None):
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._interval = 3600
        self._callback = None
        self.analyzer = analyzer
        self.stats = {
            "total_scans": 0,
            "last_scan_time": None,
            "errors": 0
        }

    def extract_product_data(self, url: str) -> dict:
        if not CRAWLER_DEPS:
            raise RuntimeError("requests/bs4 required")
        try:
            resp = requests.get(url, headers=self.HEADERS, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.content, 'html.parser')
            
            # Check if this is a search result page (discovery phase)
            if "search" in url or "/s?" in url:
                links = self._discover_product_links(soup, url)
                if links:
                    random_link = random.choice(links)
                    # Resolve relative URLs
                    if random_link.startswith('/'):
                        from urllib.parse import urljoin
                        random_link = urljoin(url, random_link)
                    logger.info("Discovery: Found %d links, picked %s", len(links), random_link)
                    # Recurse into the specific product page
                    return self.extract_product_data(random_link)

            # Extract structured text and meta tags from a specific product page
            text = soup.get_text(separator='\n', strip=True)
            fields = self._extract_fields(text)
            
            # Try to get more from meta tags
            og_title = soup.find('meta', property='og:title')
            if og_title and not fields.get('product_name'):
                fields['product_name'] = og_title.get('content')
            
            fields['source_url'] = url
            fields['crawled_at'] = datetime.now().isoformat()
            return fields
        except Exception as e:
            logger.error("Crawl failed for %s: %s", url, e)
            self.stats["errors"] += 1
            return {'source_url': url, 'error': str(e)}

    def _discover_product_links(self, soup: BeautifulSoup, base_url: str) -> list[str]:
        """Find product detail links on a search results page."""
        links = []
        if "amazon" in base_url:
            # Amazon product links usually follow this pattern
            for a in soup.select('h2 a.a-link-normal'):
                href = a.get('href', '')
                if "/dp/" in href:
                    links.append(href)
        elif "mystore" in base_url:
            for a in soup.select('a.product-link, .product-item-info a'):
                href = a.get('href', '')
                if href:
                    links.append(href)
        elif "magicpin" in base_url:
            for a in soup.find_all('a', href=True):
                if "/product/" in a['href']:
                    links.append(a['href'])
        
        # Generic fallback
        if not links:
            for a in soup.find_all('a', href=True):
                if "/product/" in a['href'] or "/p/" in a['href'] or "/item/" in a['href']:
                    links.append(a['href'])
        
        return list(set(links)) # Unique links only

    def _extract_fields(self, text: str) -> dict:
        fields = {}
        # Clean text for better matching
        text_clean = re.sub(r'\s+', ' ', text)
        
        patterns = {
            'product_name': r'(?:Title|Name)[:\s]*([^\n]{3,150})',
            'mrp': r'(?:MRP|Price|M\.R\.P)[:\s]*[₹Rs.]*\s*([\d,]+\.?\d*)',
            'net_quantity': r'(?:Net\s*(?:Qty|Quantity|Wt|Weight))[:\s]*([\d.]+\s*(?:kg|g|l|ml|pcs|units?))',
            'manufacturer_name': r'(?:Manufactured\s*By|Mfg\.?\s*By|Brand)[:\s]*([^\n]{3,100})',
            'manufacturer_address': r'(?:Address|Regd\.\s*Office)[:\s]*([^\n]{10,200})',
            'country_of_origin': r'(?:Country\s*of\s*Origin|Made\s*[iI]n)[:\s]*([A-Za-z\s]{3,30})',
            'expiry_date': r'(?:Exp(?:iry)?\.?\s*(?:Date)?|Best\s*Before)[:\s]*([\d/\-.\s\w]{4,30})',
            'license_number': r'(?:FSSAI|Lic\.?\s*No\.?)[:\s]*(\d{14})',
        }
        
        for key, pat in patterns.items():
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                fields[key] = m.group(1).strip()
        
        # Fallback for product name if not found by pattern
        if not fields.get('product_name'):
            lines = [l.strip() for l in text.split('\n') if l.strip() and len(l.strip()) > 10]
            if lines:
                fields['product_name'] = lines[0][:150]
                
        return fields

    def start_scheduled_scanning(self, interval=3600, callback=None):
        if self._running:
            return
        self._interval = interval
        self._callback = callback
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        logger.info("Crawler Service started with interval: %d s", interval)

    def stop_scheduled_scanning(self):
        self._running = False
        logger.info("Crawler Service stopping...")

    def _loop(self):
        while self._running:
            try:
                # 1. Select random platform/seed
                platform = random.choice(list(self.SEED_URLS.keys()))
                url = self.SEED_URLS[platform]
                logger.info("Scheduled Scan: Crawling %s", platform)
                
                # 2. Extract Data
                data = self.extract_product_data(url)
                
                if 'error' not in data:
                    # 3. AI Validation (if analyzer provided)
                    if self.analyzer:
                        # Convert crawled data to pseudo-OCR text for analyzer
                        ocr_input = "\n".join([f"{k}: {v}" for k, v in data.items() if v])
                        report = self.analyzer.analyze(ocr_input)
                        
                        # Add crawler metadata
                        report['data_source'] = 'WEB_CRAWLER'
                        report['source_url'] = url
                        report['platform'] = platform
                        
                        # Save to Firestore is handled inside ComplianceService/FirestoreService
                        # which is usually called by ComplianceAnalyzer if integrated, 
                        # but here we might need to call it explicitly if ComplianceAnalyzer just returns the dict.
                        from services.firestore_service import FirestoreService
                        fs = FirestoreService()
                        fs.save_report(report)
                        
                        logger.info("Scheduled Scan: Report generated for %s (Score: %d)", 
                                    data.get('product_name', 'Unknown'), report.get('complianceScore', 0))
                    
                    if self._callback:
                        self._callback(data)
                        
                self.stats["total_scans"] += 1
                self.stats["last_scan_time"] = datetime.now().isoformat()
                
            except Exception as e:
                logger.error("Scheduled crawl error: %s", e)
                self.stats["errors"] += 1
                
            time.sleep(self._interval)
