import os
import random
import string
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# 使用相对路径获取 chromedriver 的路径
def get_driver_path():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, "chromedriver.exe")

# 创建 WebDriver 实例
service = Service(get_driver_path())
driver = webdriver.Chrome(service=service)

# 打开登录页面
login_url = "https://s.zaixiankaoshi.com/student/YOUR-WORK-ID"  # 替换为实际登录页面
driver.get(login_url)

# 等待页面加载
time.sleep(2)

# 定位到用户名和密码输入框
username_input = driver.find_element(By.XPATH, "//div[@class='el-input']/input[@type='text']")
password_input = driver.find_element(By.XPATH, "//div[@class='el-input']/input[@type='password']")

# 输入用户名和密码
username_input.send_keys('YOUR-ACCOUNT')  # 替换为实际账号
password_input.send_keys('YOUR-PASSWORD')  # 替换为实际密码

# 提交登录
password_input.send_keys(Keys.RETURN)

# 等待登录成功
time.sleep(5)

# 跳转到题库页7
driver.get("https://s.zaixiankaoshi.com/online/?paperId=YOUR-PAPERID")  # 替换为试卷 ID
time.sleep(3)

# 使用 JavaScript 强制点击按钮
try:
    # 获取元素
    switch_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//span[contains(text(), '背题模式')]//following-sibling::span//input[@type='checkbox']"))
    )
    
    # 使用 JavaScript 强制点击
    driver.execute_script("arguments[0].click();", switch_button)
    print("背题模式按钮已点击")
except Exception as e:
    print("未能找到背题模式按钮或发生错误:", e)

def enable_back_mode():
    """强制点击背题模式按钮以开启背题模式"""
    try:
        switch_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(text(), '背题模式')]//following-sibling::span//input[@type='checkbox']"))
        )
        driver.execute_script("arguments[0].click();", switch_button)
        print("背题模式按钮已点击")
    except Exception as e:
        print("未能找到背题模式按钮或发生错误:", e)

def check_back_mode():
    """检查背题模式是否已开启"""
    try:
        switch_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(text(), '背题模式')]//following-sibling::span//input[@type='checkbox']"))
        )
        return switch_button.is_selected()
    except Exception as e:
        print("未能找到背题模式按钮或发生错误:", e)
        return False

def random_click_alternative(question_type, question, retry_count=3):
    """当背题模式不可用时随机选择答案并获取答案与解析，支持重试机制"""
    for attempt in range(retry_count):
        try:
            print(f"备用方案: 随机答题中... 尝试次数: {attempt + 1}")
            answer, analysis = None, None
            option_texts = []
            if "单选题" in question_type or "判断题" in question_type:
                options = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".option"))
                )
                chosen_option = random.choice(options)
                option_texts = [o.text for o in options]
                chosen_option.click()  # 随机点击一个选项
            elif "多选题" in question_type:
                options = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".option"))
                )
                chosen_options = random.sample(options, k=random.randint(1, len(options)))
                option_texts = [o.text for o in options]
                for option in chosen_options:
                    option.click()
                submit_button = driver.find_element(By.XPATH, "//button[span[text()='提交答案']]")
                driver.execute_script("arguments[0].click();", submit_button)  # 强制点击提交答案
            elif "填空题" in question_type:
                blanks = driver.find_elements(By.CSS_SELECTOR, ".blank")
                for blank in blanks:
                    blank.send_keys(''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=10)))  # 随机输入
                save_button = driver.find_element(By.XPATH, "//button[span[text()='保存答案']]")
                driver.execute_script("arguments[0].click();", save_button)  # 强制点击保存答案
            elif "简答题" in question_type:
                not_mastered_button = driver.find_element(By.XPATH, "//button[span[text()='未掌握']]")
                driver.execute_script("arguments[0].click();", not_mastered_button)  # 强制点击未掌握按钮

            # 提取答案与解析
            answer = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".right-ans"))
            ).text.split("：")[1].strip()
            analysis = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".answer-analysis"))
            ).text
            print(f"备用方案获取到答案：{answer}")
            print(f"备用方案获取到解析：{analysis}")

            # 文件写入
            with open("questions.txt", "a", encoding="utf-8") as f:
                f.write(f"【{question_type}】{question}\n")
                if option_texts:
                    f.write(f"选项：{' '.join(option_texts)}\n")
                f.write(f"答案：{answer}\n")
                f.write(f"答案解析：{analysis}\n\n")
            break  # 成功后退出循环
        except Exception as e:
            print(f"备用方案中发生错误: {e}")
            if attempt == retry_count - 1:
                print("达到最大重试次数，放弃当前题目...")
            else:
                print("等待后重试...")
                time.sleep(5)  # 等待一段时间后重试

def extract_data():
    try:
        # 1. 等待并获取题目
        print("等待题目加载...")
        question_element = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".qusetion-box"))
        )
        question = question_element.text  # 获取题目
        print(f"当前题目: {question}")

        # 2. 获取题型
        question_type = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".topic-type"))
        ).text
        print(f"题目类型: {question_type}")

        # 3. 检查背题模式是否开启，并根据结果选择处理方式
        back_mode_enabled = check_back_mode()
        if back_mode_enabled:
            print("背题模式已开启，使用主方案处理...")
            if "单选题" in question_type:
                handle_single_choice(question)
            elif "多选题" in question_type:
                handle_multiple_choice(question)
            elif "判断题" in question_type:
                handle_true_false(question)
            elif "填空题" in question_type:
                handle_fill_in_the_blank(question)
            elif "简答题" in question_type:
                handle_short_answer(question)
        else:
            print("背题模式未开启，使用备用方案处理...")
            random_click_alternative(question_type, question)

        # 4. 点击下一题按钮
        print("等待并点击下一题按钮...")
        next_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//button[span[text()='下一题']]"))
        )
        next_button.click()

        # 5. 等待下一题加载
        print("等待下一题加载...")
        WebDriverWait(driver, 15).until(
            EC.staleness_of(question_element)
        )
        print("下一题加载完成")

    except Exception as e:
        print(f"发生错误：{e}")
        print("当前页面 URL:", driver.current_url)
        print("当前页面 HTML 源码:\n", driver.page_source)


def handle_single_choice(question):
    """处理单选题"""
    print("处理单选题...")
    options = WebDriverWait(driver, 15).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".option"))
    )

    # 提取选项
    option_texts = []
    for option in options:
        spans = option.find_elements(By.TAG_NAME, "span")
        if len(spans) == 2:
            option_letter = spans[0].text  # 获取字母 (A, B, ...)
            option_content = spans[1].text  # 获取选项内容
            option_texts.append(f"{option_letter}. {option_content}")

    # 获取答案
    answer = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".right-ans"))
    ).text.split("：")[1].strip()

    # 获取解析
    analysis = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".answer-analysis"))
    ).text

    # 写入文件
    with open("questions.txt", "a", encoding="utf-8") as f:
        f.write(f"【单选题】{question}\n")
        f.write(" ".join(option_texts) + "\n")
        f.write(f"答案：{answer}\n")
        f.write(f"答案解析：{analysis}\n\n")


def handle_multiple_choice(question):
    """处理多选题"""
    print("处理多选题...")
    options = WebDriverWait(driver, 15).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".option"))
    )

    # 提取选项
    option_texts = []
    for option in options:
        spans = option.find_elements(By.TAG_NAME, "span")
        if len(spans) == 2:
            option_letter = spans[0].text  # 获取字母 (A, B, ...)
            option_content = spans[1].text  # 获取选项内容
            option_texts.append(f"{option_letter}. {option_content}")

    # 获取答案
    answer = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".right-ans"))
    ).text.split("：")[1].strip()

    # 获取解析
    analysis = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".answer-analysis"))
    ).text

    # 写入文件
    with open("questions.txt", "a", encoding="utf-8") as f:
        f.write(f"【多选题】{question}\n")
        f.write(" ".join(option_texts) + "\n")
        f.write(f"答案：{answer}\n")
        f.write(f"答案解析：{analysis}\n\n")


def handle_true_false(question):
    """处理判断题"""
    print("处理判断题...")
    options = WebDriverWait(driver, 15).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".option"))
    )

    # 提取选项
    option_texts = []
    for option in options:
        spans = option.find_elements(By.TAG_NAME, "span")
        if len(spans) == 2:
            option_letter = spans[0].text
            option_content = spans[1].text
            option_texts.append(f"{option_letter}: {option_content}")

    # 获取答案
    answer = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".right-ans"))
    ).text.split("：")[1].strip()

    # 获取解析
    analysis = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".answer-analysis"))
    ).text

    # 写入文件
    with open("questions.txt", "a", encoding="utf-8") as f:
        f.write(f"【判断题】{question}\n")
        f.write(f"选项：{', '.join(option_texts)}\n")
        f.write(f"答案：{answer}\n")
        f.write(f"答案解析：{analysis}\n\n")


def handle_fill_in_the_blank(question):
    """处理填空题"""
    print("处理填空题...")
    answer = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".right-ans"))
    ).text.split("：")[1].strip()

    # 写入文件
    with open("questions.txt", "a", encoding="utf-8") as f:
        f.write(f"【填空题】{question}\n")
        f.write(f"答案：{answer}\n\n")


def handle_short_answer(question):
    """处理简答题"""
    print("处理简答题...")
    answer = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".right-ans"))
    ).text.split("：")[1].strip()

    # 写入文件
    with open("questions.txt", "a", encoding="utf-8") as f:
        f.write(f"【简答题】{question}\n")
        f.write(f"答案：{answer}\n\n")

# 循环提取数据
while True:
    extract_data()
    time.sleep(3)  # 等待页面加载完成