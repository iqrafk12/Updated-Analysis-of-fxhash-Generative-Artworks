from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Set up Chrome options (Remove headless mode to see Chrome window)
chrome_options = Options()
chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration
chrome_options.add_argument("--no-sandbox")  # Disable sandbox
chrome_options.add_argument("--remote-debugging-port=9222")  # For remote debugging if needed

# Initialize WebDriver with ChromeDriverManager
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# List of URLs to check for the "Run" button
urls = [
     "https://www.fxhash.xyz/generative/30661",
    "https://www.fxhash.xyz/generative/30662",
    "https://www.fxhash.xyz/generative/30663",
    "https://www.fxhash.xyz/generative/30664",
    "https://www.fxhash.xyz/generative/30665",
    "https://www.fxhash.xyz/generative/30666",
    "https://www.fxhash.xyz/generative/30667",
    "https://www.fxhash.xyz/generative/30668",
    "https://www.fxhash.xyz/generative/30669",
    "https://www.fxhash.xyz/generative/30670",
    "https://www.fxhash.xyz/generative/30671",
    "https://www.fxhash.xyz/generative/30672"

]

# Function to find and click the "Run" button
def click_run_button(url):
    try:
        # Open the URL
        driver.get(url)
        time.sleep(10)  # Allow the page to load
        
        # Locate the "Run" button using XPath or CSS selectors
        run_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'Button_btn_content__REfX5') and contains(., 'run')]"))
        )

        if run_button:
            print(f"'Run' button found on: {url}, clicking on it...")
            run_button.click()  # Click the "Run" button

            # Wait for the "Stop" button to appear after clicking "Run"
            stop_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'Button_btn_content__REfX5') and contains(., 'Stop')]"))
            )
            print(f"'Stop' button found on: {url}, artwork is running.")
            stop_button.click()  # Click "Stop" button
            
            # Wait for the "Replay" button to appear after stopping
            replay_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'Button_btn_content__REfX5') and contains(., 'Replay')]"))
            )
            print(f"'Replay' button found on: {url}, clicking on it to replay.")
            replay_button.click()  # Click "Replay" button
            time.sleep(5)  # Wait for the replay action
        else:
            print(f"No 'Run' button found on: {url}")
    
    except Exception as e:
        print(f"Error processing {url}: {e}")

# Loop through the list of URLs and click the "Run" button if found
for url in urls:
    click_run_button(url)

# Close the browser after the task is complete
driver.quit()
