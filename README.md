# Investor_Comments_Scraper
This project aims to scrape and collect comments directed at specific companies from investor interaction platforms.
Web links are as follows：
Shenzhen Stock Exchange: https://irm.cninfo.com.cn
Shanghai Stock Exchange: http://sns.sseinfo.com

This project uses web automation to simulate a human interacting with the website. 
It does so by:
1.Simulating a web browser using Selenium, which automates the Chrome browser to interact with the CNINFO platform. Selenium allows the script to:
  Open the web page.
  Click buttons.
  Enter text into search boxes.
  Navigate through pagination, all mimicking how a user would manually browse the site.
2.Extracting the HTML content of the loaded pages using BeautifulSoup, which is a Python library for parsing HTML and XML documents. Once Selenium loads the page, BeautifulSoup is used to locate and extract specific elements (like comments, stock codes, and release times) from the page's source code.


Based on the launch dates of the two interactive platforms, we scraped the question texts up to June 2024, resulting in over 4,000,000 entries. After further data cleaning, the results are shown as illustrated below, including three columns: company code, comments, and date.

