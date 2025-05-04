from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd
#import trafilatura

TIME = 5

# 스크롤 제어
def scroll_aladin(driver):
  height = driver.execute_script("return document.body.scrollHeight") # 문서 끝까지 스크롤
  while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(TIME)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if height == new_height:
      break
    height = new_height


# 알라딘 크롤링
def crawl_aladin(num): 
  driver = webdriver.Chrome()
  url = "https://www.aladin.co.kr/shop/common/wbest.aspx?BranchType=1&BestType=Bestseller" # 알라딘 베스트셀러-주간 베스트
  driver.get(url)
  time.sleep(TIME)

  all_title_list = [] # 전체 도서 제목
  all_author_list = [] # 전체 도서 저자
  all_keyword_list = [] # 전체 도서 키워드

  for page in range(1, num + 1): # 1위부터 250위까지 크롤링
    scroll_aladin(driver)

    book_list = driver.find_elements(By.CLASS_NAME, "ss_book_box")
    title_list = []
    author_list = []
    keyword_list = []

    for book in book_list:
      title_element = book.find_element(By.CLASS_NAME, "bo3") # 책 제목
      
      try:
        author_element = book.find_element(By.XPATH, './/div[@class="ss_book_list"]/ul/li[3]/a') # 책 저자
      except:
        author_element = book.find_element(By.XPATH, './/div[@class="ss_book_list"]/ul/li[2]/a') # 책 저자
      
      keyword_element = book.find_elements(By.CLASS_NAME, "ss_f_g2") # 책 간단 소개
      
      title = title_element.text
      author = author_element.text
      keyword = [element.text for element in keyword_element] # 키워드 여러개일 수도 있음

      title_list.append(title)
      author_list.append(author)
      keyword_list.append(keyword)

      #print("책 제목 ", title)
      #print("책 저자 ", author)
      #print("책 간단 소개 ", keyword)

    all_title_list.extend(title_list)
    all_author_list.extend(author_list)
    all_keyword_list.extend(keyword_list)

    if page < num: # 마우스 클릭
      try:
        driver.find_element(By.XPATH, f'//*[@id="newbg_body"]/div[4]/ul/li[{page + 2}]/a').click()
        time.sleep(TIME) # 페이지 로딩
      except:
        print("다음 페이지로 이동 실패 {e}")
    
  driver.quit()

  data = {"title": all_title_list, "author": all_author_list, "keyword": all_keyword_list}
  df = pd.DataFrame(data)
  df.to_csv("aladin_bestseller.csv", encoding="utf-8-sig", index=False) # dataframe을 csv 파일로 변환

if __name__ == "__main__":
  crawl_aladin(5)  

    