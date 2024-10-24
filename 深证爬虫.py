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

# 读取Excel文件中的代码
code = pd.read_excel('深证.xlsx', header=0, dtype=str)
code['代码'] = code['代码'].str.replace('.SZ', '')
code_list = code['代码'].tolist()

# 确保结果文件夹存在
if not os.path.exists('结果'):
    os.makedirs('结果')

# 初始化Chrome浏览器
opt = ChromeOptions()
opt.headless = True
driver = webdriver.Chrome(options=opt)

total_questions = 0

def process_code(code, start_date, end_date):
    global total_questions
    print(f'处理代码: {code}...')
    driver.get("https://irm.cninfo.com.cn/views/interactiveAnswer")

    # 等待“快速查询”按钮出现并点击
    query_button = WebDriverWait(driver, 100).until(
        EC.element_to_be_clickable((By.CLASS_NAME, 'kscx_dig'))  # 更改为实际的按钮选择器
    )
    query_button.click()

    # 等待查询框出现
    search_box = WebDriverWait(driver, 100).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input.el-input__inner[placeholder="代码简称"]'))  # 更改为实际的查询框选择器
    )

    # 在查询框中输入内容
    search_query = code
    search_box.send_keys(search_query)

    # 等待日期输入框出现并设置日期
    start_date_box = WebDriverWait(driver, 100).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder="开始日期"]'))  # 更改为实际的开始日期输入框选择器
    )
    end_date_box = WebDriverWait(driver, 100).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder="结束日期"]'))  # 更改为实际的结束日期输入框选择器
    )
    start_date_box.send_keys(start_date)
    end_date_box.send_keys(end_date)

    # 提交查询
    submit_button = WebDriverWait(driver, 100).until(
        EC.element_to_be_clickable((By.XPATH, '//button[span="确定"]'))  # 更改为实际的提交按钮选择器
    )
    submit_button.click()

    # 等待几秒钟让页面加载（视情况而定）
    time.sleep(2)

    # 获取总页数
    pagination = WebDriverWait(driver, 100).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'el-pagination'))
    )
    total_pages = int(pagination.find_elements(By.CLASS_NAME, 'number')[-1].text)

    # 创建CSV文件并写入数据
    output_file_path = os.path.join('结果', f'{code}.csv')
    with open(output_file_path, mode='w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        writer.writerow(['代码', '提问', '回复时间'])

        # 用于存储已经处理过的提问组合
        processed_questions = set()

        for page in range(1, total_pages + 1):
            # 等待当前页面加载完成
            time.sleep(0.5)

            # 获取当前页的网页源代码
            page_source = driver.page_source

            # 使用BeautifulSoup解析网页内容
            soup = BeautifulSoup(page_source, 'html.parser')

            # 找到所有问答块
            question_blocks = soup.find_all('div', class_='f14 overhide mt_20')

            for block in question_blocks:
                # 获取提问内容
                question_element = block.find('div', class_='question-content')
                question = question_element.text.strip() if question_element else 'N/A'

                # 如果提问已经存在，则跳过
                if question in processed_questions:
                    continue

                # 获取深市代码
                stock_code_element = block.find('span', class_='company-code')
                stock_code = stock_code_element.text.strip() if stock_code_element else 'N/A'

                # 获取提问时间
                question_time_element = block.find('span', class_='question-time')
                reply_time = question_time_element.text.strip() if question_time_element else 'N/A'

                # 写入CSV文件
                writer.writerow([stock_code, question, reply_time])
                total_questions += 1

                # 将提问加入集合
                processed_questions.add(question)

            print(f'已处理第 {page} 页，总页数: {total_pages}')
            # 如果有下一页按钮，则点击下一页
            next_button = driver.find_element(By.CLASS_NAME, 'btn-next')
            if next_button.is_enabled():
                next_button.click()
            else:
                break

    print(f'数据已保存到 {output_file_path} 文件中')

# 调用函数处理每年数据
for idx, code in enumerate(code_list):
    for year in range(2010, 2024):
        start_date = f'{year}-01-01'
        end_date = f'{year}-06-30'
        process_code(code, start_date, end_date)
        
# 关闭浏览器
driver.quit()

print(f'一共收集到了 {total_questions} 条问答')
