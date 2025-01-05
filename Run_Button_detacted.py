import time
import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.common.exceptions import NoSuchElementException

# Ensure the directory exists for the CSV file
output_directory = "results"
os.makedirs(output_directory, exist_ok=True)

# Path to save the CSV output
csv_file_path = os.path.join(output_directory, "artwork_results.csv")

# Chrome and Firefox browser options (without headless mode)
chrome_options = ChromeOptions()  # No headless argument means the browser window will open
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

firefox_options = FirefoxOptions()  # No headless argument means the browser window will open

# Function to initialize WebDriver (Chrome or Firefox)
def get_driver(browser="chrome"):
    if browser == "chrome":
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
        print("Chrome WebDriver initialized successfully!")
    elif browser == "firefox":
        driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=firefox_options)
        print("Firefox WebDriver initialized successfully!")
    return driver

# Function to search for 'Run' button
def check_run_button(driver, url):
    driver.get(url)
    time.sleep(2)  # Wait for the page to load

    # Scroll to ensure dynamic content loads
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)  # Wait for content to load after scroll

    try:
        # Wait for the "Run" button to be visible based on its class and text
        run_button = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'Button_btn_content__REfX5')]//span[text()='run']"))
        )
        return True  # Found the button
    except NoSuchElementException:
        return False  # Button not found

# Function to process multiple URLs and check for 'Run' button
def process_artworks(artwork_urls, browser="chrome"):
    # Initialize the WebDriver
    driver = get_driver(browser)

    with open(csv_file_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["URL", "Run Button Found", "Status"])

        # Process each URL
        for url in artwork_urls:
            print(f"Processing: {url}")
            try:
                run_button_found = check_run_button(driver, url)
                if run_button_found:
                    writer.writerow([url, "Yes", "Success"])
                    print(f"Run button found on: {url}")
                else:
                    writer.writerow([url, "No", "Not Found"])
                    print(f"No run button found on: {url}")
            except Exception as e:
                writer.writerow([url, "Error", str(e)])
                print(f"Error processing {url}: {e}")

    driver.quit()

# List of artwork URLs to process
artwork_urls = [
    "https://www.fxhash.xyz/generative/30661",
    "https://www.fxhash.xyz/generative/30662",
    "https://www.fxhash.xyz/generative/30663"
]

# Process artworks using Chrome (will show the browser window)
process_artworks(artwork_urls, browser="chrome")

# Process artworks using Firefox (will show the browser window) (Uncomment if you want to use Firefox as well)
# process_artworks(artwork_urls, browser="firefox")
