from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from time import sleep
import requests
import pandas as pd

TIME = 2

def get_introduction(isbn):
  url = f'https://www.aladin.co.kr/shop/product/getContents.aspx?ISBN={isbn}&name=Introduce&type=0&date=0'
  headers = {
    "Referer": f"https://www.aladin.co.kr/shop/wproduct.aspx?ItemId={isbn}",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
  }

  try:
    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, "lxml")

    introduce_div = soup.find("div", {"class": "Ere_prod_mconts_LS"}, string="책소개")
    parent_div = introduce_div.find_parent("div", {"class": "Ere_prod_mconts_box"})
    introduce_content_div = parent_div.find("div", {"class": "Ere_prod_mconts_R"})

    introduce_content = None
    content_text = [] # 도서 소개 
  
    for element in introduce_content_div.children:
      if element.name =="div" and "Ere_line2" in element.get("class", []):
        break
      if isinstance(element, str):
        content_text.append(element.strip()) # 앞뒤 공백 제거
      elif element.name == "br":
        content_text.append("\n")  

      introduce_content = "".join(content_text).strip() # 하나의 문자열로 결합 후, 앞뒤 공백 제거
      introduce_content = "\n".join([line.strip() for line in introduce_content.splitlines() if line.strip()])

    if introduce_content:  
      print(introduce_content)
    else:
      print("책 소개 내용을 찾을 수 없습니다")
      return None

    return introduce_content
  
  except requests.exceptions.HTTPError:
    print(f"Http Error")
  except requests.exceptions.Timeout:
    print(f"Timeout Error")  
  except Exception as e:
    print(type(e))


# 알라딘 크롤링
def crawl_aladin(page_num): 
  driver = webdriver.Chrome()
  url = "https://www.aladin.co.kr/shop/common/wbest.aspx?BranchType=1&BestType=Bestseller" # 알라딘 베스트셀러-주간 베스트
  driver.get(url)
  sleep(TIME)
  all_data = [] # 모든 도서 정보

  for page in range(1, page_num + 1): # 지정된 페이지만큼 접근
    for index in range(50): # 현재 페이지에 있는 50개의 도서 목록
      # 뒤로 가기 때문에 매번 도서를 찾아와야 함
      book = driver.find_elements(By.CLASS_NAME, "ss_book_box")[index]
      data = {} # 각 도서 정보

      title_element = book.find_element(By.CLASS_NAME, "bo3") # 도서 제목
      data["title"] = title_element.text
      
      try:
        author_element = book.find_element(By.XPATH, './/div[@class="ss_book_list"]/ul/li[3]/a') # 도서 저자
      except:
        author_element = book.find_element(By.XPATH, './/div[@class="ss_book_list"]/ul/li[2]/a')
      data["author"] = author_element.text  
      
      keyword_elements = book.find_elements(By.CLASS_NAME, "ss_f_g2") # 도서 키워드 없을 수도, 여러개일 수도 있음
      keywords = [keyword.text.replace('-', '').strip() for keyword in keyword_elements] # 전처리
      data["keyword"] = keywords
      
      # 상세 페이지 접근(도서 소개, 장르를 얻기 위해서)
      title_element.click()
      sleep(TIME)

      # 상세 페이지 맨 아래로 스크롤
      driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
      sleep(TIME)

      isbn = None
      isbn2 = None

      isbn_element = driver.find_element(By.XPATH, '//meta[@property="books:isbn"]')
      isbn = isbn_element.get_attribute("content") # ISBN
      
      data["isbn"] = isbn

      if data["isbn"]:
        introduction = get_introduction(isbn) # 도서 소개
        data["introduction"] = introduction
      
      if not data["introduction"]: # ISBN이 달라져서 책 소개를 가져오지 못하는 경우 
        try:
          a_element = driver.find_element(By.CSS_SELECTOR, "a[onclick*='wrecommend_sms_send']") 
          click_element = a_element.get_attribute("onclick")
          print(click_element)
          isbn_start_index = click_element.find("ISBN=")
          print(isbn_element)

          if isbn_start_index != -1:
            start_index = isbn_start_index + len("ISBN=")
            end_index = click_element.find(",", start_index)
            isbn2 = click_element[start_index : end_index]
            isbn2 = isbn2.rstrip("%27") # %27이 뒤에 붙어있어서 제거
            data["isbn"] = isbn2
            print("isbn2 ", isbn2)

            introduction = get_introduction(isbn2) # 도서 소개
            data["introduction"] = introduction

        except Exception as e:
          print(type(e))

      genre_elements = driver.find_elements(By.XPATH, '//*[@id="ulCategory"]/li[*]/a') # 도서 장르 여러개일 수 있음
      genres = [genre.text.strip() for genre in genre_elements]
      processed_genres = []

      for genre in genres:
        split_genres = [content.strip() for content in genre.split('/')] # '/'로 나누고 앞뒤 공백 제거
        split_genres = [content for content in split_genres if content] # 빈 문자열 제거
        processed_genres.extend(split_genres)

      data["genre"] = list(set(processed_genres)) # 중복 제거

      all_data.append(data)
      
      driver.back() # 베스트셀러 목록으로 돌아가기
      sleep(TIME)

    if page < page_num:
      try:
        next_page_xpath = f'//*[@id="newbg_body"]/div[4]/ul/li[{page + 2}]/a'
        driver.find_element(By.XPATH, next_page_xpath).click() # 다음 페이지로 이동
        sleep(TIME) # 페이지 로딩
      except Exception as e:
        print(f"다음 페이지로 이동 실패 : {type(e)}")
    
  driver.quit()

  df = pd.DataFrame(all_data)
  df.to_csv("aladin_bestseller.csv", encoding="utf-8-sig", index=False) # dataframe을 csv 파일로 변환

if __name__ == "__main__":
  crawl_aladin(6)  