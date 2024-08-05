from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

# Define the path to your cookie file
cookie_file_path = 'feedly.com_cookies.txt'

# Function to parse the cookie file and return a list of cookies
def parse_cookies(file_path):
    cookies = []
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if not line.startswith("#") and line.strip():
                parts = line.strip().split("\t")
                cookie = {
                    'domain': parts[0],
                    'secure': parts[1].lower() == 'true',
                    'path': parts[2],
                    'httpOnly': parts[3].lower() == 'true',
                    'expiry': int(parts[4]),
                    'name': parts[5],
                    'value': parts[6]
                }
                cookies.append(cookie)
    return cookies

# Set up WebDriver options
options = Options()

driver = webdriver.Chrome(options=options)

# Open the website
driver.get("https://feedly.com")

# Add cookies to the session
cookies = parse_cookies(cookie_file_path)
for cookie in cookies:
    driver.add_cookie(cookie)

# Refresh the page to apply cookies
driver.refresh()

# Pause to allow time for page load (adjust as needed)
time.sleep(30)

# Perform any additional actions as needed
# For example, you might want to verify that you're logged in

# Close the browser
driver.quit()
