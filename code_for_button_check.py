from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import csv
import time

# Set up Chrome WebDriver options
options = webdriver.ChromeOptions()
# Comment out the headless mode for debugging
# options.add_argument("--headless")  
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Initialize WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Function to check for the "Run" button on the page
def check_run_button(artwork_url, retries=3):
    for attempt in range(retries):
        try:
            driver.get(artwork_url)
            print(f"Checking Artwork URL: {artwork_url} (Attempt {attempt + 1}/{retries})")
            
            # Wait up to 60 seconds for the "Run" button to be visible
            run_button = WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Run')]"))
            )
            
            # If found, return success
            if run_button:
                print(f"'run ▶︎' button found for {artwork_url}")
                return "Run button works"
        except TimeoutException:
            print(f"Timeout while checking {artwork_url} on attempt {attempt + 1}")
        except NoSuchElementException:
            print(f"No 'Run' button found on {artwork_url}, attempt {attempt + 1}")
        
        # Retry mechanism if failure
        if attempt < retries - 1:
            time.sleep(5)  # Increased delay before retrying
            print(f"Retrying {artwork_url} (Attempt {attempt + 2}/{retries})")
        else:
            print(f"Failed after {retries} attempts for {artwork_url}")
            return "Failed after multiple retries"
    
    return "Failed after multiple retries"

# Main function to process multiple artworks
def process_artworks(artwork_urls):
    results = []
    for url in artwork_urls:
        result = check_run_button(url)
        results.append((url, result))
    
    # Write results to a CSV file
    with open('artwork_button_check_results.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Artwork URL", "Status"])
        writer.writerows(results)

# List of artwork URLs to check (add more URLs as needed)
artwork_urls = [
    "https://www.fxhash.xyz/generative/30661",
    "https://www.fxhash.xyz/generative/30662",
    "https://www.fxhash.xyz/generative/30663",
    # Add more URLs here...
]

# Start processing the artworks
process_artworks(artwork_urls)

# Close the WebDriver when done
driver.quit()
