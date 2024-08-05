from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# open up passwords.txt and get the username which is the first line and the password which is the second line
with open('password.txt') as f:
    lines = f.readlines()
    username = lines[0].strip()
    password = lines[1].strip()

# Set up WebDriver options
options = Options()
options.add_argument("--disable-search-engine-choice-screen")

# Add headless option if you want to run it without opening a browser window
# options.add_argument("--headless")

driver = webdriver.Chrome(options=options)

# Open the website
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
    header_title_element = WebDriverWait(driver, 10).until(
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
        print(f'Found article title: {title}')
        article_href = title_element.get_attribute("href")
        print(f'Found article href: {article_href}')
        
        # open the href in a new tab
        driver.execute_script(f"window.open('{article_href}');")
        
    break                                                                                                                                                                                                                                                                                                        
    
    # Wait before moving to the next item (if necessary)
    time.sleep(2)

# Switch to one of the newly opened tabs
driver.switch_to.window(driver.window_handles[1])
# wait for the page to load fully
WebDriverWait(driver, 30).until(
    EC.all_of(
        EC.presence_of_element_located((By.TAG_NAME, "body")),
        EC.title_contains("")  # You can add an expected title here if known
    )
)
    

# Wait for a bit
time.sleep(60)

# Close the browser
driver.quit()