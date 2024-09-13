# import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import google.generativeai as genai
import os
import PIL.Image

class ArticleDownloader:
    def __init__(self):
        self.options = Options()
        self.options.add_argument("--disable-search-engine-choice-screen")
        # https://clients2.google.com/service/update2/crx?response=redirect&prodversion=127.0.6533.100&acceptformat=crx2,crx3&x=id%3DGIGHMMPIOBKLFEPJOCNAMGKKBIGLIDOM%26uc
        # self.options.add_extension("GIGHMMPIOBKLFEPJOCNAMGKKBIGLIDOM_6_6_0_0_old.crx")
        # self.options.add_extension("CFHDOJBKJHNKLBPKDAIBDCCDDILIFDDB_4_4_0_0.crx")
        self.options.add_argument('--disable-features=PrivacySandboxSettings4')
        # self.options.add_argument("--headless")
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
        
        genai.configure(api_key=os.environ["API_KEY"])
        

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
        
        sample_image = PIL.Image.open('articles/{title}.png')
        
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = """based on the information can you transcribe the whole article making sure to add in any hyperlinks if there are

Based on the article can you answer the following questions and put the answers (Yes or No) in the delimiters {{{}}}. Provide a deep explanation before giving the answer.

1. Is this relevant to any security incidents or security vulnerabilities?

2. Has this security incient or vulnerability been exploited to affect any country's CIIs? The CII sectors are energy, water, banking and finance, healthcare, transport (which includes land, maritime, and aviation), infocomm, media, security and emergency services, and government.

3. If the answer to 2. is yes, are there any IOCs present in the article? 

4. Did this article mention that this security incident or vulnerabilty affected Singapore CIIs?"""
        response = model.generate_content([sample_image, prompt])
        print(response)
        
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
            
            sample_image = PIL.Image.open(f'articles/{title}.png')
        
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = """based on the information can you transcribe the whole article making sure to add in any hyperlinks if there are

    Based on the article can you answer the following questions and put the answers (Yes or No) in the delimiters {{{}}}. Provide a deep explanation before giving the answer.

    1. Does this article discuss general security concepts, rather than a specific security incident or security vulnerabilities? for example, summary articles, security tools, previous cyber attacks, advertisements or articles where there is little to no information

    2. Has this security incient or vulnerability been exploited to affect any country's CIIs? The CII sectors are energy, water, banking and finance, healthcare, transport (which includes land, maritime, and aviation), infocomm, media, security and emergency services, and government.

    3. Are there any IOCs present in the article? For example IPs or Hashes or Domain names. 

    4. Did this article mention that this security incident or vulnerabilty affected Singapore CIIs?"""
    #         prompt = """based on the information can you transcribe the whole article making sure to add in any hyperlinks if there are
    # CII sectors are energy, water, banking and finance, healthcare, transport (which includes land, maritime, and aviation), infocomm, media, security and emergency services, and government.
    
    # Based on the article can you answer the following questions and return the final answer in the delimiters {{{}}}. Provide a deep explanation before giving the answer.

    # 1. If this is not a current cyber attack related article eg monthly reports, security tools, previous cyber attack return Irrelevant
    # 2. If this is cyber attack related article, eg cyber attack on gaming platform, return Relevant
    # 3. If this article contains Singapore related IOCs, eg cyber attack on Singapore's with Indicators Of Compromise such as IP Addresses or domains, return C
    # 4. If this is a security incident affecting other countries CII, eg cyber attacks on USA Government, return B
    # 5. If this is a security incident affecting Singapore's CII, eg cyber attacks on Singapore Bank, return A"""
    
            response = model.generate_content([sample_image, prompt])
            print(response)
            # put it in a txt file
            # get todays date in the format of YYYYMMDD
            date = time.strftime("%Y%m%d")
            # append to text file {date}/toc.txt
            # with open(f'articles/{date}/toc.txt', 'a', encoding='utf-8') as f:
            #     f.write(f'{title}\n')
            
            
            # Close the tab
            self.driver.close()
            
            
        
        

# Usage example:
# downloader = ArticleDownloader()
# downloader.download_article("Article Title", "https://example.com/article")
# downloader.close()