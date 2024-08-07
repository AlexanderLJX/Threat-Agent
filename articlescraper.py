# import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class ArticleDownloader:
    def __init__(self):
        self.options = Options()
        self.options.add_argument("--disable-search-engine-choice-screen")
        # https://clients2.google.com/service/update2/crx?response=redirect&prodversion=127.0.6533.100&acceptformat=crx2,crx3&x=id%3DGIGHMMPIOBKLFEPJOCNAMGKKBIGLIDOM%26uc
        self.options.add_extension("GIGHMMPIOBKLFEPJOCNAMGKKBIGLIDOM_6_6_0_0_old.crx")
        # self.options.add_extension("CFHDOJBKJHNKLBPKDAIBDCCDDILIFDDB_4_4_0_0.crx")
        self.options.add_argument('--disable-features=PrivacySandboxSettings4')
        self.options.add_argument("--headless")
        # self.driver = uc.Chrome(options=self.options)
        self.driver = webdriver.Chrome(options=self.options)
        # self.driver.set_window_size(1080, 1080)
        # # wait until there are 2 tabs open
        # WebDriverWait(self.driver, 30).until(
        #     EC.number_of_windows_to_be(2)
        # )
        # # close 1 tab
        # self.driver.close()
        # # switch to the first tab
        # self.driver.switch_to.window(self.driver.window_handles[0])
        

    def download_article(self, title, article_href):
        # Open the article
        self.driver.get(article_href)
        
        # Wait for the page to load fully
        WebDriverWait(self.driver, 30).until(
            EC.all_of(
                EC.presence_of_element_located((By.TAG_NAME, "body")),
                EC.title_contains("")  # You can add an expected title here if known
            )
        )
        
        # Sanitize the title
        title = ''.join(e for e in title if e.isalnum() or e.isspace())
        title = title[:40]
        
        # Capture the full page html
        full_page_html = self.driver.page_source
        
        # Write the html to a file
        with open(f'articles/{title}.html', 'w', encoding='utf-8') as f:
            f.write(full_page_html)
        
        # Get page metrics and set window size
        metrics = self.driver.execute_cdp_cmd("Page.getLayoutMetrics", {})
        width = metrics["contentSize"]["width"]
        height = metrics["contentSize"]["height"]
        self.driver.set_window_size(width, height)
        
        # Wait for the page to load fully
        time.sleep(2)
        
        # Take a screenshot
        full_body_element = self.driver.find_element(By.TAG_NAME, "body")
        full_body_element.screenshot(f'articles/{title}.png')
        
        # Close the tab
        self.driver.quit()
        
    def download_articles(self, title_list, href_list):
        # Open all the links in the list in a new tab
        for i, href in enumerate(href_list):
            if i > 0:
                self.driver.switch_to.new_window()
            self.driver.get(href)
        
        
            
        for title, href in zip(title_list, href_list):
            # switch back to the first tab
            self.driver.switch_to.window(self.driver.window_handles[0])
            # wait for the page to load fully
            WebDriverWait(self.driver, 30).until(
                EC.all_of(
                    EC.presence_of_element_located((By.TAG_NAME, "body")),
                    EC.title_contains("")  # You can add an expected title here if known
                )
            )
            # Sanitize the title
            title = ''.join(e for e in title if e.isalnum() or e.isspace())
            title = title[:80]
            
            # Capture the full page html
            full_page_html = self.driver.page_source
            
            # Write the html to a file
            with open(f'articles/{title}.html', 'w', encoding='utf-8') as f:
                f.write(full_page_html)
            
            # Get page metrics and set window size
            metrics = self.driver.execute_cdp_cmd("Page.getLayoutMetrics", {})
            height = metrics["contentSize"]["height"]
            self.driver.set_window_size(1080, height)
            
            # Wait for the page to load fully
            time.sleep(2)
            
            # Take a screenshot
            full_body_element = self.driver.find_element(By.TAG_NAME, "body")
            full_body_element.screenshot(f'articles/{title}.png')
            
            # Close the tab
            self.driver.close()
            
            
        
        

# Usage example:
# downloader = ArticleDownloader()
# downloader.download_article("Article Title", "https://example.com/article")
# downloader.close()