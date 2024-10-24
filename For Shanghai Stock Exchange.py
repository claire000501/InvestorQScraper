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

# 设置 Chrome 浏览器选项
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)  # 确保浏览器在脚本执行完后保持打开状态

# 初始化 Chrome 浏览器
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# 读取Excel文件中的公司代码
df_codes = pd.read_excel("/Users/clairewang/Desktop/上证.xlsx", usecols=["代码"])
company_codes = df_codes["代码"].astype(str).tolist()

# 定义提取日期的函数
def extract_date(date_str):
    # 使用正则表达式匹配日期
    match = re.search(r'(\d{4})年(\d{2})月(\d{2})日', date_str)
    if match:
        year, month, day = match.groups()
        return f"{year}/{month}/{day}"
    return ""

# 定义抓取问题和日期的函数
def scrape_questions_and_dates():
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    questions = soup.select(".m_feed_detail.m_qa_detail .m_feed_txt")
    dates = soup.select(".m_feed_from span")

    questions_and_dates = []
    for question, date in zip(questions, dates):
        question_text = question.text.strip(":")  # 去掉问题文本前面的冒号
        date_text = extract_date(date.text)
        questions_and_dates.append((question_text, date_text))
    
    return questions_and_dates

# 定义获取最后一页页码的函数
def get_last_page_number():
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    pagination = soup.find('div', {'id': 'pagination'})
    if pagination:
        last_page = pagination.find_all('a')[-2].text  # 倒数第二个 <a> 标签通常是最后一页的页码
        return int(last_page)
    return 1

# 循环处理每个公司代码
for company_code in company_codes:
    # 打开目标网页
    driver.get("https://sns.sseinfo.com/qa.do")

    # 输入公司代码
    company_input = driver.find_element(By.ID, "company_txt")
    company_input.send_keys(company_code)

    # 使用 JavaScript 直接设置日期值
    start_date = "2010-01-01"
    end_date = "2024-06-30"
    driver.execute_script(f"document.getElementById('sdate').value = '{start_date}'")
    driver.execute_script(f"document.getElementById('edate').value = '{end_date}'")

    # 点击搜索按钮
    search_button = driver.find_element(By.CSS_SELECTOR, ".sBut")
    search_button.click()

    # 等待页面加载完成并显示结果
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "feedall"))
        )
    except Exception as e:
        print(f"Error: {e}")
        continue

    time.sleep(2)  # 等待加载更多问题

    # 初始化一个列表用于保存所有页的问题和日期
    all_questions_and_dates = []

    # 抓取第一页的问题和日期
    all_questions_and_dates.extend(scrape_questions_and_dates())

    # 获取最后一页的页码
    last_page_number = get_last_page_number()

    # 循环点击每个页码
    for i in range(2, last_page_number + 1):
        try:
            # 找到并点击页码链接
            page = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.LINK_TEXT, str(i)))
            )
            driver.execute_script("arguments[0].click();", page)

            # 抓取当前页面的问题和日期并保存到列表
            all_questions_and_dates.extend(scrape_questions_and_dates())
        except Exception as e:
            print(f"Error on page {i} for company {company_code}: {e}")
            break

    # 将所有问题和日期保存到以公司代码命名的Excel文件中
    df = pd.DataFrame(all_questions_and_dates, columns=["Question", "Date"])
    df.insert(0, "Company Code", company_code)  # 在第一列插入公司代码
    df.to_excel(f"/Users/clairewang/Desktop/{company_code}.xlsx", index=False)

    print(f"公司代码 {company_code} 的所有问题和日期已保存到 /Users/clairewang/Desktop/{company_code}.xlsx 文件中。")

# 关闭浏览器
driver.quit()
