import requests
from bs4 import BeautifulSoup
import logging
import re
from config import Config

logger = logging.getLogger(__name__)

class EcommerceService:
    """Service for scraping e-commerce platforms"""
    
    def __init__(self):
        """Initialize e-commerce service"""
        self.headers = {
            'User-Agent': Config.USER_AGENT
        }
    
    def scrape_product(self, url, platform='auto'):
        """
        Scrape product information from e-commerce URL
        
        Args:
            url: Product URL
            platform: Platform identifier (auto, amazon, flipkart, etc.)
            
        Returns:
            dict: Product information
        """
        try:
            # Detect platform if auto
            if platform == 'auto':
                platform = self.detect_platform(url)
            
            logger.info(f"Scraping product from {platform}: {url}")
            
            # Route to appropriate scraper
            if platform == 'amazon':
                return self.scrape_amazon(url)
            elif platform == 'flipkart':
                return self.scrape_flipkart(url)
            else:
                return self.scrape_generic(url)
                
        except Exception as e:
            logger.error(f"E-commerce scraping failed: {str(e)}")
            raise Exception(f"Failed to scrape product: {str(e)}")
    
    def detect_platform(self, url):
        """
        Detect e-commerce platform from URL
        
        Args:
            url: Product URL
            
        Returns:
            str: Platform identifier
        """
        url_lower = url.lower()
        
        if 'amazon' in url_lower:
            return 'amazon'
        elif 'flipkart' in url_lower:
            return 'flipkart'
        elif 'myntra' in url_lower:
            return 'myntra'
        elif 'snapdeal' in url_lower:
            return 'snapdeal'
        else:
            return 'generic'
    
    def scrape_amazon(self, url):
        """Scrape product from Amazon"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            product = {
                'id': self.generate_product_id(),
                'name': '',
                'manufacturerName': '',
                'manufacturerAddress': '',
                'netQuantity': '',
                'mrp': '',
                'manufacturingDate': '',
                'expiryDate': '',
                'customerCareDetails': '',
                'countryOfOrigin': '',
                'source': 'ECOMMERCE',
                'scannedText': ''
            }
            
            # Extract product name
            title_elem = soup.find('span', {'id': 'productTitle'})
            if title_elem:
                product['name'] = title_elem.get_text().strip()
            
            # Extract price
            price_elem = soup.find('span', {'class': 'a-price-whole'})
            if price_elem:
                product['mrp'] = f"Rs. {price_elem.get_text().strip()}"
            
            # Extract product information from table
            details_table = soup.find('table', {'id': 'productDetails_techSpec_section_1'})
            if details_table:
                rows = details_table.find_all('tr')
                for row in rows:
                    th = row.find('th')
                    td = row.find('td')
                    if th and td:
                        key = th.get_text().strip().lower()
                        value = td.get_text().strip()
                        
                        if 'manufacturer' in key:
                            product['manufacturerName'] = value
                        elif 'country' in key and 'origin' in key:
                            product['countryOfOrigin'] = value
                        elif 'net quantity' in key or 'item weight' in key:
                            product['netQuantity'] = value
            
            # Extract from product details
            details_section = soup.find('div', {'id': 'detailBullets_feature_div'})
            if details_section:
                text = details_section.get_text()
                product['scannedText'] = text
                
                # Extract manufacturer
                manufacturer_match = re.search(r'Manufacturer\s*[:\-]\s*([^,\n]+)', text, re.IGNORECASE)
                if manufacturer_match and not product['manufacturerName']:
                    product['manufacturerName'] = manufacturer_match.group(1).strip()
                
                # Extract country
                country_match = re.search(r'Country of Origin\s*[:\-]\s*([^,\n]+)', text, re.IGNORECASE)
                if country_match:
                    product['countryOfOrigin'] = country_match.group(1).strip()
            
            logger.info(f"Successfully scraped Amazon product: {product['name']}")
            return product
            
        except Exception as e:
            logger.error(f"Amazon scraping failed: {str(e)}")
            raise
    
    def scrape_flipkart(self, url):
        """Scrape product from Flipkart"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            product = {
                'id': self.generate_product_id(),
                'name': '',
                'manufacturerName': '',
                'manufacturerAddress': '',
                'netQuantity': '',
                'mrp': '',
                'manufacturingDate': '',
                'expiryDate': '',
                'customerCareDetails': '',
                'countryOfOrigin': '',
                'source': 'ECOMMERCE',
                'scannedText': ''
            }
            
            # Extract product name
            title_elem = soup.find('span', {'class': 'B_NuCI'})
            if title_elem:
                product['name'] = title_elem.get_text().strip()
            
            # Extract price
            price_elem = soup.find('div', {'class': '_30jeq3'})
            if price_elem:
                product['mrp'] = price_elem.get_text().strip()
            
            # Extract specifications
            specs_tables = soup.find_all('table', {'class': '_14cfVK'})
            for table in specs_tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        key = cells[0].get_text().strip().lower()
                        value = cells[1].get_text().strip()
                        
                        if 'manufacturer' in key:
                            product['manufacturerName'] = value
                        elif 'country' in key:
                            product['countryOfOrigin'] = value
                        elif 'net quantity' in key or 'quantity' in key:
                            product['netQuantity'] = value
            
            logger.info(f"Successfully scraped Flipkart product: {product['name']}")
            return product
            
        except Exception as e:
            logger.error(f"Flipkart scraping failed: {str(e)}")
            raise
    
    def scrape_generic(self, url):
        """Generic scraper for unknown platforms"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            product = {
                'id': self.generate_product_id(),
                'name': '',
                'manufacturerName': '',
                'manufacturerAddress': '',
                'netQuantity': '',
                'mrp': '',
                'manufacturingDate': '',
                'expiryDate': '',
                'customerCareDetails': '',
                'countryOfOrigin': '',
                'source': 'ECOMMERCE',
                'scannedText': soup.get_text()
            }
            
            # Try to extract product name from common locations
            title_candidates = [
                soup.find('h1'),
                soup.find('meta', {'property': 'og:title'}),
                soup.find('title')
            ]
            
            for candidate in title_candidates:
                if candidate:
                    if candidate.name == 'meta':
                        product['name'] = candidate.get('content', '').strip()
                    else:
                        product['name'] = candidate.get_text().strip()
                    if product['name']:
                        break
            
            # Try to extract price from common patterns
            price_pattern = r'(?:Rs\.?|₹)\s*(\d+)'
            price_match = re.search(price_pattern, soup.get_text())
            if price_match:
                product['mrp'] = f"Rs. {price_match.group(1)}"
            
            logger.info(f"Successfully scraped generic product: {product['name']}")
            return product
            
        except Exception as e:
            logger.error(f"Generic scraping failed: {str(e)}")
            raise
    
    def generate_product_id(self):
        """Generate unique product ID"""
        import uuid
        return str(uuid.uuid4())
