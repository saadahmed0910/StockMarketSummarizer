import pandas as pd
import asyncio
import random
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Optional
import logging
from json_cleaned import json_to_dataframe

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WebScraper:
    def __init__(self, delay_range=(2, 5), timeout=30000):
        """
        Initialize the web scraper
        
        Args:
            delay_range: Tuple of (min, max) seconds to wait between requests
            timeout: Playwright timeout in milliseconds
        """
        self.delay_range = delay_range
        self.timeout = timeout
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0'
        ]
    
    def clean_text(self, html_content: str) -> str:
        """
        Clean HTML content and extract readable text
        
        Args:
            html_content: Raw HTML content
            
        Returns:
            Cleaned text content
        """
        if not html_content:
            return ""
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script, style, and other non-content tags
        for script in soup(["script", "style", "nav", "header", "footer", "aside", "menu"]):
            script.decompose()
        
        # Get text and clean it
        text = soup.get_text()
        
        # Clean whitespace and normalize
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    async def scrape_url(self, browser, url: str) -> Dict[str, any]:
        """
        Scrape a single URL
        
        Args:
            browser: Playwright browser instance
            url: URL to scrape
            
        Returns:
            Dictionary with url, content, status, and error information
        """
        result = {
            'url': url,
            'content': '',
            'status': 'failed',
            'error': None,
            'title': ''
        }
        
        try:
            # Create a new page with random user agent
            page = await browser.new_page(
                user_agent=random.choice(self.user_agents)
            )
            
            # Set viewport to mimic real browser
            await page.set_viewport_size({"width": 1920, "height": 1080})
            
            # Navigate to the page
            logger.info(f"Scraping: {url}")
            response = await page.goto(url, timeout=self.timeout, wait_until='domcontentloaded')
            
            if response and response.status == 200:
                # Wait a bit for dynamic content to load
                await asyncio.sleep(random.uniform(1, 3))
                
                # Get page content
                html_content = await page.content()
                
                # Extract title
                title = await page.title()
                
                # Clean the content
                cleaned_content = self.clean_text(html_content)
                
                result.update({
                    'content': cleaned_content,
                    'status': 'success',
                    'title': title
                })
                
                logger.info(f"Successfully scraped: {url} ({len(cleaned_content)} characters)")
                
            else:
                result['error'] = f"HTTP {response.status if response else 'No response'}"
                logger.warning(f"Failed to load {url}: {result['error']}")
                
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Error scraping {url}: {e}")
            
        finally:
            try:
                await page.close()
            except:
                pass
                
        return result
    
    async def scrape_urls(self, urls: List[str]) -> List[Dict[str, any]]:
        """
        Scrape multiple URLs with browser automation
        
        Args:
            urls: List of URLs to scrape
            
        Returns:
            List of dictionaries with scraping results
        """
        results = []
        
        async with async_playwright() as p:
            # Launch browser - FIXED: removed parentheses from executable_path
            browser = await p.chromium.launch(
                headless=True,
            )
            
            try:
                for i, url in enumerate(urls):
                    # Scrape the URL
                    result = await self.scrape_url(browser, url)
                    results.append(result)
                    
                    # Add delay between requests (except for last one)
                    if i < len(urls) - 1:
                        delay = random.uniform(*self.delay_range)
                        logger.info(f"Waiting {delay:.1f} seconds before next request...")
                        await asyncio.sleep(delay)
                        
            finally:
                await browser.close()
        
        return results

def scrape_dataframe_urls(df: pd.DataFrame, url_column: str, delay_range=(3, 7)) -> Dict[str, any]:
    """
    Main function to scrape URLs from a dataframe column
    
    Args:
        df: Pandas dataframe containing URLs
        url_column: Name of the column containing URLs
        delay_range: Tuple of (min, max) seconds to wait between requests
        
    Returns:
        Dictionary containing organized scraped data
    """
    # Extract URLs from dataframe
    urls = df[url_column].dropna().tolist()
    logger.info(f"Found {len(urls)} URLs to scrape")
    
    # Initialize scraper
    scraper = WebScraper(delay_range=delay_range)
    
    # Run the scraping
    results = asyncio.run(scraper.scrape_urls(urls))
    
    # Organize the results
    successful_scrapes = [r for r in results if r['status'] == 'success']
    failed_scrapes = [r for r in results if r['status'] == 'failed']
    
    # Create organized output
    scraped_data = {
        'all_content_combined': '\n\n--- ARTICLE SEPARATOR ---\n\n'.join([
            f"Title: {r['title']}\nURL: {r['url']}\nContent: {r['content']}" 
            for r in successful_scrapes
        ]),
        'individual_articles': [
            {
                'title': r['title'],
                'url': r['url'], 
                'content': r['content']
            } for r in successful_scrapes
        ],
        'summary_stats': {
            'total_urls': len(urls),
            'successful': len(successful_scrapes),
            'failed': len(failed_scrapes),
            'total_characters': sum(len(r['content']) for r in successful_scrapes)
        },
        'failed_urls': [{'url': r['url'], 'error': r['error']} for r in failed_scrapes]
    }
    
    logger.info(f"Scraping complete! {len(successful_scrapes)}/{len(urls)} URLs successful")
    
    return scraped_data


def get_llm_ready_content(json_file='news_raw.json', delay_range=(5, 12)):
    """
    Get scraped content ready for LLM processing.
    Only runs when explicitly called (not on import).
    
    Args:
        json_file: Path to JSON file containing URLs
        delay_range: Tuple of (min, max) seconds to wait between requests
        
    Returns:
        String containing all scraped content ready for LLM
    """
    sample_urls = []
    for df_urls in json_to_dataframe(json_file)['url']:
        sample_urls.append(df_urls)
    
    df = pd.DataFrame(sample_urls, columns=['urls'])
    scraped_data = scrape_dataframe_urls(df, 'urls', delay_range=delay_range)
    
    return scraped_data['all_content_combined']
