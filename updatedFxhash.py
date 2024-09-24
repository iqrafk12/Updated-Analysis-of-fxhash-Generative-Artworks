from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
import time

# Function to convert IPFS links to HTTP format
def ipfs_to_http(ipfs_link):
    if ipfs_link.startswith("ipfs://"):
        # Convert to HTTP gateway format
        return (
            f"https://gateway.ipfs.io/ipfs/{ipfs_link[7:]}",
            f"https://gateway.fxhash2.xyz/ipfs/{ipfs_link[7:]}"
        )
    return ipfs_link, ipfs_link

# Function to fetch data from the fxhash public API
def fetch_artwork_from_api(artwork_id):
    api_url = f"https://api.fxhash.xyz/v1/tokens/{artwork_id}"
    try:
        response = requests.get(api_url, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"API Error: {str(e)}"

# Function to fetch code from the IPFS link
def fetch_ipfs_code(ipfs_link):
    try:
        code_response = requests.get(ipfs_link, timeout=5)
        code_response.raise_for_status()
        return code_response.text
    except requests.exceptions.RequestException as e:
        return f"IPFS Error: {str(e)}"

# Function to extract JavaScript libraries from code content
def extract_libraries(code_content):
    if not code_content or "Error" in code_content:
        return "No p5.js found", "No other libraries found"

    p5_versions = re.findall(r'(p5(\.min)?\.js)[^\s]*', code_content)
    version_numbers = re.findall(r'(v?\d+\.\d+\.\d+|p5@\d+\.\d+\.\d+)', code_content)
    js_libraries = re.findall(r'(https?://[^"\'\s]+\.js)', code_content)

    p5_version_summary = " / ".join(set(version_numbers)) if version_numbers else "No p5.js found"
    other_libraries_summary = " / ".join(set(js_libraries)) if js_libraries else "No other libraries found"

    return p5_version_summary, other_libraries_summary

# Function to extract specific URI data from the soup
def extract_uri_data(soup, uri_type):
    script_tag = soup.find('script', string=lambda x: x and uri_type in x)
    if script_tag:
        match = re.search(rf'"{uri_type}":"(ipfs://[^"]+)"', script_tag.string)
        return match.group(1) if match else "-"
    return "-"

# Main analysis function for an artwork
def analyze_artwork(url, artwork_id):
    # Try fetching from the API
    api_data = fetch_artwork_from_api(artwork_id)
    
    if isinstance(api_data, dict) and 'token' in api_data:
        token = api_data['token']
        description_text = token.get('description', '-')
        ipfs_link = token.get('ipfs', '-')

        # Fetch code from IPFS
        code_content = fetch_ipfs_code(ipfs_link)

        # Extract libraries
        p5_version_summary, other_libraries = extract_libraries(code_content)

        # Extract additional URIs
        artifact_uri = token.get('artifactUri', '-')
        display_uri = token.get('displayUri', '-')
        thumbnail_uri = token.get('thumbnailUri', '-')
        generative_uri = token.get('generativeUri', '-')

        # Convert IPFS URIs to HTTP format
        artifact_uri_http, artifact_uri_fxhash = ipfs_to_http(artifact_uri)
        display_uri_http, display_uri_fxhash = ipfs_to_http(display_uri)
        thumbnail_uri_http, thumbnail_uri_fxhash = ipfs_to_http(thumbnail_uri)
        generative_uri_http, generative_uri_fxhash = ipfs_to_http(generative_uri)

        return ("working", description_text, ipfs_link, p5_version_summary, other_libraries,
                artifact_uri_http, artifact_uri_fxhash,
                display_uri_http, display_uri_fxhash,
                thumbnail_uri_http, thumbnail_uri_fxhash,
                generative_uri_http, generative_uri_fxhash)

    # If API data not available, fallback to web scraping
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract description and IPFS link
        library_description = soup.find('div', class_="Clamp_container__xOFme GenerativeDisplay_description__NweHb")
        description_text = library_description.get_text(separator=" ").strip() if library_description else "-"
        
        ipfs_link_tag = soup.find('a', href=lambda x: x and 'ipfs' in x)
        ipfs_link = ipfs_link_tag['href'].split(',')[0].strip() if ipfs_link_tag else "-"

        # Fetch code from IPFS
        code_content = fetch_ipfs_code(ipfs_link)

        # Extract libraries
        p5_version_summary, other_libraries = extract_libraries(code_content)

        # Extract additional URIs
        artifact_uri = extract_uri_data(soup, 'artifactUri')
        display_uri = extract_uri_data(soup, 'displayUri')
        thumbnail_uri = extract_uri_data(soup, 'thumbnailUri')
        generative_uri = extract_uri_data(soup, 'generativeUri')

        # Convert IPFS URIs to HTTP format
        artifact_uri_http, artifact_uri_fxhash = ipfs_to_http(artifact_uri)
        display_uri_http, display_uri_fxhash = ipfs_to_http(display_uri)
        thumbnail_uri_http, thumbnail_uri_fxhash = ipfs_to_http(thumbnail_uri)
        generative_uri_http, generative_uri_fxhash = ipfs_to_http(generative_uri)

        return ("working", description_text, ipfs_link, p5_version_summary, other_libraries,
                artifact_uri_http, artifact_uri_fxhash,
                display_uri_http, display_uri_fxhash,
                thumbnail_uri_http, thumbnail_uri_fxhash,
                generative_uri_http, generative_uri_fxhash)

    except requests.exceptions.RequestException as e:
        return (f"Request Error: {str(e)}", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-")

# Main function
def main():
    start_id = 30661
    end_id = 31600
    artwork_links = [f"https://www.fxhash.xyz/generative/{artwork_id}" for artwork_id in range(start_id, end_id + 1)]
    
    # Set up the Chrome driver
    options = Options()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # Data containers
    results = []

    # Analyze each artwork
    for artwork_id, artwork_url in enumerate(artwork_links, start=start_id):
        print(f"Analyzing Artwork ID: {artwork_id} URL: {artwork_url}")
        result = analyze_artwork(artwork_url, artwork_id)
        results.append(result)

    # Create a DataFrame for the results
    df = pd.DataFrame(results, columns=[
        "Link Status", "Description", "IPFS Link", "p5.js Versions", "Other JS Libraries",
        "Artifact URI HTTP", "Artifact URI fxhash", "Display URI HTTP",
        "Display URI fxhash", "Thumbnail URI HTTP", "Thumbnail URI fxhash",
        "Generative URI HTTP", "Generative URI fxhash"
    ])

    # Save to CSV
    df.to_csv('fxhash_artwork_analysis.csv', index=False)

    # Close the browser
    driver.quit()

if __name__ == "__main__":
    main()
