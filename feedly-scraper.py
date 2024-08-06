# from selenium import webdriver
import undetected_chromedriver as uc
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException


def download_article(title, article_href):
    # Create a new driver and open the article
    new_options = Options()
    new_options.add_argument("--disable-search-engine-choice-screen")
    new_options.add_argument("--headless")
    # https://clients2.google.com/service/update2/crx?response=redirect&prodversion=127.0.6533.89&acceptformat=crx2,crx3&x=id%3Dgighmmpiobklfepjocnamgkkbiglidom%26uc
    new_options.add_extension("GIGHMMPIOBKLFEPJOCNAMGKKBIGLIDOM_6_6_0_0.crx")
    prefs = {
    "profile.default_content_setting_values.notifications": 2,
    "profile.default_content_setting_values.popups": 0,
    "profile.block_third_party_cookies": True,
    "profile.default_content_setting_values.automatic_downloads": 1,
    "extensions.newtabpage.enabled": False,
    "extensions.startup": False,
    }
    new_options.add_experimental_option("prefs", prefs)
    new_driver = uc.Chrome(options=new_options)
    new_driver.get(article_href)
    
    
    # Wait for the page to load fully
    WebDriverWait(new_driver, 30).until(
        EC.all_of(
            EC.presence_of_element_located((By.TAG_NAME, "body")),
            EC.title_contains("")  # You can add an expected title here if known
        )
    )
    # sanitize the title to only allow alphanumeric characters and spaces
    title = ''.join(e for e in title if e.isalnum() or e.isspace())
    # make sure title is not too long
    title = title[:40]
    # Capture the full page html
    full_page_html = new_driver.page_source
    # Write the html to a file
    with open(f'articles/{title}.html', 'w', encoding='utf-8') as f:
        f.write(full_page_html)
        
    
    metrics = new_driver.execute_cdp_cmd("Page.getLayoutMetrics", {})
    width = metrics["contentSize"]["width"]
    height = metrics["contentSize"]["height"]
    new_driver.set_window_size(width, height)
    # wait for the page to load fully
    time.sleep(3)
    full_body_element = new_driver.find_element(By.TAG_NAME, "body")
    full_body_element.screenshot(f'articles/{title}.png')
    
    # screenshot = new_driver.get_screenshot_as_file("articles/" + title + ".png")
    
    # Close the driver
    new_driver.quit()

# open up passwords.txt and get the username which is the first line and the password which is the second line
with open('password.txt') as f:
    lines = f.readlines()
    username = lines[0].strip()
    password = lines[1].strip()

# Set up WebDriver options
options = Options()
options.add_argument("--disable-search-engine-choice-screen")
# options.add_argument("--headless")

driver = uc.Chrome(options=options)

# Open the website
driver.get("https://feedly.com")

# wait for page to load
WebDriverWait(driver, 30).until(
    EC.all_of(
        EC.presence_of_element_located((By.TAG_NAME, "body")),
        EC.title_contains("")  # You can add an expected title here if known
    )
)

driver.get("https://feedly.com/i/back")


# Wait for the login button and click it
login_button = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "auth.primary.feedly"))
)
login_button.click()

# Enter username
# username_field = driver.find_element(By.NAME, "email")
# username_field.send_keys(username)

# wait for the username field and enter the username
username_field = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.NAME, "login"))
)
username_field.send_keys(username)


# Click the next button
next_button = driver.find_element(By.CSS_SELECTOR, 'input[type="submit"]')
next_button.click()

# Wait for password field and enter password
password_field = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.NAME, "password"))
)
password_field.send_keys(password)

# Click the next button again
next_button = driver.find_element(By.CSS_SELECTOR, 'input[type="submit"]')
next_button.click()

# Wait for the dashboard page to load
WebDriverWait(driver, 30).until(
    EC.url_contains("https://feedly.com/i/dashboard/")
)

# Wait for the page to fully load
time.sleep(5)

# Find the element <div title="Vulnerabilities" class="LeftnavListRow">
feed1 = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, 'div[title="Vulnerabilities"]'))
)

# Find the "Show/Hide" button and get its aria-label <div title="Vulnerabilities" class="LeftnavListRow"><button type="button" aria-label="Show Feeds for Vulnerabilities"
show_or_hide_button = feed1.find_element(By.TAG_NAME, "button")
show_or_hide = show_or_hide_button.get_attribute('aria-label')

# Click the button if it contains "Show"
if "Show" in show_or_hide:
    show_or_hide_button.click()
    
# Get the parent element of the feed1 element
feed1_parent = feed1.find_element(By.XPATH, "..")

# Get all direct children of the parent element which class is LeftnavListRow--child, <span title="Adobe" class="MockLink LeftnavListRow LeftnavListRow--child LeftnavListRow--selected
children = feed1_parent.find_elements(By.CLASS_NAME, "LeftnavListRow--child")

# Loop through the children
for child in children:
    # Click on the child element
    child.click()
    
    # Wait for the element to load
    time.sleep(3)  # Adjust this if necessary based on the load time
    
    # find the element, it is a child of the element with the class="header row kickered"
    # find the element <span id="header-title">Adobe</span>, the key word is Adobe it is the title attribute of the child
    keyword = child.get_attribute("title")
    header_title_element = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, f'//span[@id="header-title" and text()="{keyword}"]'))
    )
    
    # Perform any other actions needed on the header_title_element
    print(f'Found header title: {header_title_element.text}')
    
    # Find the articles in the feed with the class="entry magazine" also make sure it doesn't have the class="entry--read"
    articles = driver.find_elements(By.CLASS_NAME, "entry.magazine:not(.entry--read)")
    # articles = driver.find_elements(By.CLASS_NAME, "entry.magazine.entry--read")
    

    # Loop through the articles
    for article in articles:
        # Find the title of the article
        # class="M_plfet2nk5hSEutAwZA EntryTitleLink Ntv7CpeLiwiGZ5mI9GBp T0e4YLvAR7VVePrfkQDl"
        title_element = article.find_element(By.CLASS_NAME, "M_plfet2nk5hSEutAwZA.EntryTitleLink.Ntv7CpeLiwiGZ5mI9GBp.T0e4YLvAR7VVePrfkQDl")
        # title is the text enclosed in the title_element
        title = title_element.text
        article_href = title_element.get_attribute("href")
        
        print(f'Found article title: {title}')
        print(f'Found article href: {article_href}')
        
        download_article(title, article_href)

        
    
    # Wait before moving to the next item (if necessary)
    time.sleep(2)
    


# Wait for a bit
time.sleep(60)

# Close the browser
driver.quit()