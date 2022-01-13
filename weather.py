import os
import time
import shutil
import json
import configparser

from datetime import datetime
from dateutil.relativedelta import relativedelta
from selenium import webdriver

from crawling_main import log_setting
from crawling_main import create_log
from crawling_utils import CrawlingUtils


crawling_utils = CrawlingUtils()

# 설정파일 읽기
config = configparser.ConfigParser()    
config.read('../config.ini', encoding='utf-8') 

env = config['system']['env']

logger = log_setting()

l_cd = "C002"
l_cd_name = "국내"
m_cd = "201"
m_cd_name = "통일부"
s_cd = "2106"
s_cd_name = "북한정보포털"
menu_cd = "weather"
menu_name = "북한의 날씨"

crawling_type = "nk_weather"
template_code = "nk_weather"

info_data = {
    "l_cd" : l_cd,
    "l_cd_name" : l_cd_name,
    "m_cd" : m_cd,
    "m_cd_name" : m_cd_name,
    "s_cd" : s_cd,
    "s_cd_name" : s_cd_name,
    "menu_cd" : menu_cd,
    "menu_name" : menu_name,
}

print(info_data)

try:

    # 오늘 날짜
    now = datetime.now()
    today = now.strftime("%Y%m%d%H%M%S")

    # chromedriver 경로
    driver_path = '../chromedriver/chromedriver.exe'

    # Chrome WebDriver를 이용해 Chrome을 실행
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    options.add_argument('--disable-gpu')

    default_directory = os.path.join(config['chromedriver']['download_path'], crawling_type)
    prefs = {"download.default_directory" : default_directory}
    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(driver_path, chrome_options=options)

    # 페이지 로딩 최대 30초 대기
    driver.implicitly_wait(30)

    # 결과 저장 날짜 정보
    now_yyyy = datetime.now().strftime('%Y')
    now_mm = datetime.now().strftime('%m')
    now_dd = datetime.now().strftime('%d')
    save_path = os.path.join(config['crawling']['save_path'], l_cd, m_cd, s_cd, menu_cd, now_yyyy, now_mm, now_dd)

    # 북한기상관측 화면 이동
    data_id = "nk_weather_" + today
    url = "https://nkinfo.unikorea.go.kr/nkp/theme/weather/nkWeather.do"
    driver.get(url)

    # 브라우저창 최대 사이즈
    driver.maximize_window()
    time.sleep(2)

    weather_list = []

    weather_tag = driver.find_elements_by_css_selector("div:nth-child(1) > .weather-list > ul > li")
    weather_items_cnt = len(weather_tag)


    for i in range (weather_items_cnt):

        weather_items = driver.find_elements_by_css_selector("div:nth-child(1) > .weather-list > ul > li")
        weather_item = weather_tag[i]

        # 코드
        code = weather_item.get_attribute('class')
        print("code ==>", code)

        # 지명
        nametag = "div:nth-child(1) > .weather-list > ul > li." + str(code) + " > span:nth-child(1)"
        name = driver.find_element_by_css_selector(nametag).text
        print("name ==>", name)

        # 날씨코드
        weathertag = "div:nth-child(1) > .weather-list > ul > li." + str(code) + " > img"
        weather = driver.find_element_by_css_selector(weathertag).get_attribute('src')
        weather = weather.split('/')[-1]
        weather = weather.replace(".png" , "")

        # 날씨
        weather_name = driver.find_element_by_css_selector(weathertag).get_attribute('title')

        # 기온
        temperaturetag = "div:nth-child(1) > .weather-list > ul > li." + str(code) + " > span:nth-child(3) > strong > span"
        temperature = driver.find_element_by_css_selector(temperaturetag).text
        temperature = temperature.replace("℃" , "")

        weather_data = {}
        
        # 추출 결과 파일 weather.json 세팅
        # 코드
        weather_data['code'] =  code
        # 지명
        weather_data['name'] =  name
        # 날씨코드
        weather_data['weather'] =  weather
        # 날씨
        weather_data['weather_name'] =  weather_name
        # 기온
        weather_data['temperature'] =  temperature

        print("weather_data ==", weather_data)

        weather_list.append(weather_data)

    print(weather_list)

    # 추출 결과 저장 경로
    crawling_path = os.path.join(save_path, data_id)
    os.makedirs(crawling_path, exist_ok=True)

    # 추출 결과(json) 저장
    meta_file_path = os.path.join(crawling_path, data_id + ".json")
    with open(meta_file_path, "w", encoding='UTF-8') as json_file:

        json.dump(weather_list, json_file, ensure_ascii = False, indent = 4)

    # driver 닫기
    driver.close()
    driver.quit()

    logger.info(f'crawling | {template_code} | {crawling_type} | {l_cd}/{m_cd}/{s_cd}/{menu_cd} | 크롤링 종료')
    create_log(crawling_type, "INFO", "SYSTEM", l_cd + "/" + m_cd + "/" + s_cd + "/" + menu_cd, l_cd, m_cd, s_cd, url, "크롤링 성공")


except Exception as e:

    e_str = str(e)

    split_str = e_str.splitlines()
    join_str = "".join(split_str)

    logger.error(f'crawling | {template_code} | {crawling_type} | {l_cd}/{m_cd}/{s_cd}/{menu_cd} | Exception {join_str}')
    create_log(crawling_type, "ERROR", "SYSTEM", l_cd + "/" + m_cd + "/" + s_cd + "/" + menu_cd, l_cd, m_cd, s_cd, url, "크롤링 실패 " + join_str)