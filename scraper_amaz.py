import requests
import pandas as pd
import time
from bs4 import BeautifulSoup
import json
import re

# Function to scrape product details from a given URL
def scrape_product_details(url):
    product_details = {}

    # Define headers for the HTTP request
    headers = {
        "accept-language": "en-US,en;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
    }

    try:
        # Send an HTTP GET request to the URL with custom headers
        response = requests.get(url, headers=headers)

        # Check if the response status code is 200 (OK)
        if response.status_code == 200:
            # Parse the HTML content of the response
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract product details from the HTML
            product_details['Product Title'] = soup.find('h1', {'id': 'title'}).text.strip()
            product_details['Product Image URL'] = soup.select_one('#landingImage').attrs.get('src')
            product_details['Price of the Product'] = soup.find("span", class_="a-offscreen").text
            product_details['Product Description'] = soup.select_one("#productDescription").text.strip()

            return product_details
        else:
            # Handle cases where the URL is not available
            print(f"{url} not available (Error {response.status_code})")
            return None

    except Exception as e:
        # Handle exceptions that may occur during scraping
        print(f"{url}: {e}")

# Path to the CSV file containing ASIN and country data
asin_country_Csv = 'amazon_scraper.csv' # use you file path

# Initialize an empty list to store scraped data
data = []

# Read the CSV file into a DataFrame
df = pd.read_csv(asin_country_Csv)

# Set the batch size for processing URLs
batch_size = 100

# Record the start time for measuring elapsed time
start_time = time.time()

# Loop through the DataFrame in batches
for batch_start in range(0, len(df), batch_size):
    batch_end = batch_start + batch_size
    batch_df = df.iloc[batch_start:batch_end]
    
    # Loop through the rows in the current batch
    for index, row in batch_df.iterrows():
        country = row['country']
        asin = row['Asin']
        url = f"https://www.amazon.{country}/dp/{asin}"
        
        # Scrape product details from the URL
        product_details = scrape_product_details(url)
        
        if product_details:
            data.append(product_details)

    # Calculate and print elapsed time for the current batch
    elapsed_time = time.time() - start_time
    print(f"Batch {batch_start // batch_size + 1} completed. Elapsed time: {elapsed_time:.2f} seconds")

# Output the scraped data to a JSON file
output_file = 'scraped_data.json'
with open(output_file, 'w') as jsonfile:
    json.dump(data, jsonfile, indent=2)

# Print the total number of URLs scraped
print(f"Scraped {len(data)} URLs in total")
