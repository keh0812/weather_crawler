# weather_crawler

## 개요

https://nkinfo.unikorea.go.kr/nkp/theme/weather/nkWeather.do
해당 사이트의 북한 날씨 정보를 각 지명들의 고유 코드를 찾아,
code, name, weather_code, weather_name 항목으로 나누어 .json 파일로 만들어 달라는 요청을 받았다. 
(스케줄링 프로그램을 사용하여 매일 오전 11시부터 1시간마다 .json 파일 생성)

## 개발 과정

![image](https://user-images.githubusercontent.com/80734989/149253377-15c22544-4a93-43a1-b221-62cf0f54b671.png)

- #content > div > ul > li > div:nth-child(1) > div.weather-list > ul > li.i13 > span:nth-child(1)의 
- text가 지명으로 이루어져있는 걸 확인할 수 있다.

- #content > div > ul > li > div:nth-child(1) > div.weather-list > ul > li.i13의 class요소가 지명 고유 코드로 이루어져있다.

### 코드
  code = weather_item.get_attribute('class')
  print("code ==>", code)

### 지명
  nametag = "div:nth-child(1) > .weather-list > ul > li." + str(code) + " > span:nth-child(1)"
  name = driver.find_element_by_css_selector(nametag).text
  print("name ==>", name)

### 날씨코드
  weathertag = "div:nth-child(1) > .weather-list > ul > li." + str(code) + " > img"
  weather = driver.find_element_by_css_selector(weathertag).get_attribute('src')
  weather = weather.split('/')[-1]
  weather = weather.replace(".png" , "")

### 날씨
  weather_name = driver.find_element_by_css_selector(weathertag).get_attribute('title')
  
### 기온
  temperaturetag = "div:nth-child(1) > .weather-list > ul > li." + str(code) + " > span:nth-child(3) > strong > span"
  temperature = driver.find_element_by_css_selector(temperaturetag).text
  temperature = temperature.replace("℃" , "")
 
### 스케줄링을 사용할 예정이어서 파일명이 겹칠 위험이 있어, save_path는 오늘 날짜의 시,분,초까지 포함했다.
  
    now = datetime.now()
    today = now.strftime("%Y%m%d%H%M%S")
    
    crawling_path = os.path.join(save_path, data_id)
    os.makedirs(crawling_path, exist_ok=True)


    meta_file_path = os.path.join(crawling_path, data_id + ".json")
    with open(meta_file_path, "w", encoding='UTF-8') as json_file:

        json.dump(weather_list, json_file, ensure_ascii = False, indent = 4)
