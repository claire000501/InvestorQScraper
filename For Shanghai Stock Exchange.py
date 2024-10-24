import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re

# Set Chrome browser options
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)  # Keep the browser open after the script finishes execution

# Initialize the Chrome browser
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Read company codes from the Excel file
df_codes = pd.read_excel("shanghai_stock_exchange.xlsx", usecols=["Code"])
company_codes = df_codes["Code"].astype(str).tolist()

# Define a function to extract dates
def extract_date(date_str):
    # Use regex to match dates
    match = re.search(r'(\d{4})年(\d{2})月(\d{2})日', date_str)
    if match:
        year, month, day = match.groups()
        return f"{year}/{month}/{day}"
    return ""

# Define a function to scrape comments and dates
def scrape_comments_and_dates():
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    comments = soup.select(".m_feed_detail.m_qa_detail .m_feed_txt")
    dates = soup.select(".m_feed_from span")

    comments_and_dates = []
    for comment, date in zip(comments, dates):
        comment_text = comment.text.strip(":")  # Remove colon from the beginning of comment text
        date_text = extract_date(date.text)
        comments_and_dates.append((comment_text, date_text))
    
    return comments_and_dates

# Define a function to get the last page number
def get_last_page_number():
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    pagination = soup.find('div', {'id': 'pagination'})
    if pagination:
        last_page = pagination.find_all('a')[-2].text  # The second to last <a> tag is usually the last page number
        return int(last_page)
    return 1

# Loop through each company code
for company_code in company_codes:
    # Open the target webpage
    driver.get("https://sns.sseinfo.com/qa.do")

    # Enter the company code
    company_input = driver.find_element(By.ID, "company_txt")
    company_input.send_keys(company_code)

    # Use JavaScript to directly set the date values
    start_date = "xxxx-xx-xx"
    end_date = "xxxx-xx-xx"
    driver.execute_script(f"document.getElementById('sdate').value = '{start_date}'")
    driver.execute_script(f"document.getElementById('edate').value = '{end_date}'")

    # Click the search button
    search_button = driver.find_element(By.CSS_SELECTOR, ".sBut")
    search_button.click()

    # Wait for the page to load and display results
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "feedall"))
        )
    except Exception as e:
        print(f"Error: {e}")
        continue

    time.sleep(2)  # Wait for more comments to load

    # Initialize a list to store all comments and dates
    all_comments_and_dates = []

    # Scrape comments and dates from the first page
    all_comments_and_dates.extend(scrape_comments_and_dates())

    # Get the last page number
    last_page_number = get_last_page_number()

    # Loop through and click each page number
    for i in range(2, last_page_number + 1):
        try:
            # Find and click the page number link
            page = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.LINK_TEXT, str(i)))
            )
            driver.execute_script("arguments[0].click();", page)

            # Scrape comments and dates from the current page and add them to the list
            all_comments_and_dates.extend(scrape_comments_and_dates())
        except Exception as e:
            print(f"Error on page {i} for company {company_code}: {e}")
            break

    # Save all comments and dates into an Excel file named after the company code
    df = pd.DataFrame(all_comments_and_dates, columns=["comment", "Date"])
    df.insert(0, "Company Code", company_code)  # Insert company code as the first column
    df.to_excel(f"/Desktop/shanghai_stock_exchange/{company_code}.xlsx", index=False)

    print(f"All comments and dates for company code {company_code} have been saved to /Desktop/shanghai_stock_exchange/{company_code}.xlsx.")

# Close the browser
driver.quit()
