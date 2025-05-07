from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd

TIME = 3


# 알라딘 크롤링
def crawl_aladin(page_num): 
  driver = webdriver.Chrome()
  url = "https://www.aladin.co.kr/shop/common/wbest.aspx?BranchType=1&BestType=Bestseller" # 알라딘 베스트셀러-주간 베스트
  driver.get(url)
  time.sleep(TIME)
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
      
      keyword_element = book.find_elements(By.CLASS_NAME, "ss_f_g2") # 도서 키워드 없을 수도, 여러개일 수도 있음
      data["keyword"] = [keyword.text for keyword in keyword_element] 
      
      # 상세 페이지 접근(도서 소개, 장르를 얻기 위해서서)
      title_element.click()
      time.sleep(TIME)

      genre_element = driver.find_elements(By.XPATH, '//*[@id="ulCategory"]/li[*]/a') # 도서 장르 여러개일 수 있음
      data["genre"] = [genre.text for genre in genre_element] 
      
      all_data.append(data)
      
      driver.back()
      time.sleep(TIME)

    if page < page_num:
      try:
        next_page_xpath = f'//*[@id="newbg_body"]/div[4]/ul/li[{page + 2}]/a'
        driver.find_element(By.XPATH, next_page_xpath).click() # 다음 페이지로 이동
        time.sleep(TIME) # 페이지 로딩
      except Exception as e:
        print(f"다음 페이지로 이동 실패 {e}")
    
  driver.quit()

  df = pd.DataFrame(all_data)
  df.to_csv("aladin_bestseller.csv", encoding="utf-8-sig", index=False) # dataframe을 csv 파일로 변환

if __name__ == "__main__":
  crawl_aladin(2)  
