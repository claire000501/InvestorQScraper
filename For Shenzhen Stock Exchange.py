import os
import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd

# Read the codes from the Excel file
code = pd.read_excel('shenzhen_stock_exchange.xlsx', header=0, dtype=str)
code['Code'] = code['Code'].str.replace('.SZ', '')
code_list = code['Code'].tolist()

# Ensure the result folder exists
if not os.path.exists('Results'):
    os.makedirs('Results')

# Initialize Chrome browser
opt = ChromeOptions()
opt.headless = True
driver = webdriver.Chrome(options=opt)

total_comments = 0

def process_code(code, start_date, end_date):
    global total_comments
    print(f'Processing code: {code}...')
    driver.get("https://irm.cninfo.com.cn/views/interactiveAnswer")

    # Wait for the "Quick Search" button to appear and click
    query_button = WebDriverWait(driver, 100).until(
        EC.element_to_be_clickable((By.CLASS_NAME, 'kscx_dig'))  # Change to actual button selector
    )
    query_button.click()

    # Wait for the search box to appear
    search_box = WebDriverWait(driver, 100).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input.el-input__inner[placeholder="Code Abbreviation"]'))  # Change to actual search box selector
    )

    # Input the search query
    search_query = code
    search_box.send_keys(search_query)

    # Wait for the date input boxes to appear and set dates
    start_date_box = WebDriverWait(driver, 100).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder="Start Date"]'))  # Change to actual start date input box selector
    )
    end_date_box = WebDriverWait(driver, 100).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder="End Date"]'))  # Change to actual end date input box selector
    )
    start_date_box.send_keys(start_date)
    end_date_box.send_keys(end_date)

    # Submit the query
    submit_button = WebDriverWait(driver, 100).until(
        EC.element_to_be_clickable((By.XPATH, '//button[span="Confirm"]'))  # Change to actual submit button selector
    )
    submit_button.click()

    # Wait a few seconds for the page to load (adjust as needed)
    time.sleep(2)

    # Get total number of pages
    pagination = WebDriverWait(driver, 100).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'el-pagination'))
    )
    total_pages = int(pagination.find_elements(By.CLASS_NAME, 'number')[-1].text)

    # Create a CSV file and write the data
    output_file_path = os.path.join('Results', f'{code}.csv')
    with open(output_file_path, mode='w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        writer.writerow(['Code', 'comment', 'release Time'])

        # To store already processed comments
        processed_comments = set()

        for page in range(1, total_pages + 1):
            # Wait for the current page to fully load
            time.sleep(0.5)

            # Get the current page source
            page_source = driver.page_source

            # Parse the page content using BeautifulSoup
            soup = BeautifulSoup(page_source, 'html.parser')

            # Find all comment blocks
            comment_blocks = soup.find_all('div', class_='f14 overhide mt_20')

            for block in comment_blocks:
                # Get the comment content
                comment_element = block.find('div', class_='comment-content')
                comment = comment_element.text.strip() if comment_element else 'N/A'

                # Skip if the comment has already been processed
                if comment in processed_comments:
                    continue

                # Get the stock code
                stock_code_element = block.find('span', class_='company-code')
                stock_code = stock_code_element.text.strip() if stock_code_element else 'N/A'

                # Get the release time
                comment_time_element = block.find('span', class_='comment-time')
                release_time = comment_time_element.text.strip() if comment_time_element else 'N/A'

                # Write to the CSV file
                writer.writerow([stock_code, comment, release_time])
                total_comments += 1

                # Add the comment to the set
                processed_comments.add(comment)

            print(f'Processed page {page}, total pages: {total_pages}')
            # Click the "Next Page" button if it exists
            next_button = driver.find_element(By.CLASS_NAME, 'btn-next')
            if next_button.is_enabled():
                next_button.click()
            else:
                break

    print(f'Data saved to {output_file_path}')

# Call the function to process data for each year
for idx, code in enumerate(code_list):
    for year in range(xxxx, xxxx):
        start_date = f'{year}-xx-xx'
        end_date = f'{year}-xx-xx'
        process_code(code, start_date, end_date)
        
# Close the browser
driver.quit()

print(f'Total comments collected: {total_comments}')
