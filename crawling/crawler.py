from bs4 import BeautifulSoup
import requests
import pandas as pd
from introduction import get_introduction

def crawl_bestseller(page_num: int, year: int, month: int, week: int) -> list:
  """
  현재 날짜를 기준으로 알라딘 주간 베스트를 주차(week)별로 크롤링하는 함수 

  Args:
      page_num (int) : 크롤링할 페이지 수
      year (int) : 크롤링할 연도
      month (int) : 크롤링할 월
      week (int) : 크롤링할 주차

  Returns:
      list : 각 도서의 정보를 담고 있는 딕셔너리들의 리스트   
             각 딕셔너리의 키들은 아래와 같습니다
             "title" (str) : 도서 제목
             "author" (str) : 도서 저자
             "keyword" (str) : 키워드
             "isbn" (str) : ISBN(국제표준도서번호)
             "genre" (str) : 도서 장르
             "image" (str) : 도서 커버 이미지 URL
             "introduction" (str) : 도서 소개 
  """
  all_data = [] # 모든 도서 정보

  for page in range(1, page_num + 1): # 지정된 페이지만큼 접근
    url = f"https://www.aladin.co.kr/shop/common/wbest.aspx?BranchType=1&CID=0&Year={year}&Month={month}&Week={week}&BestType=Bestseller&page={page}"
    response = requests.get(url)

    soup = BeautifulSoup(response.text, "lxml")
    books = soup.find_all("div", {"class": "ss_book_box"})

    for book in books:
      title_element = book.find("a", {"class": "bo3"}) # 도서 제목
      title = title_element.text.strip()
      title = title.replace('★', '').strip() # 특수문자 제거
      print("제목 ", title)

      keyword_elements = book.find_all("span", {"class": "ss_f_g2"}) # 도서 키워드 없을 수도, 여러개일 수도 있음
      keywords = [keyword.text.replace('-', '').strip() for keyword in keyword_elements] # 전처리

      # 상세 페이지 접근(저자, 도서 소개, 장르, 도서 커버 이미지를 얻기 위해서)
      book_url = title_element["href"]    
      response = requests.get(book_url)
      soup = BeautifulSoup(response.text, "lxml")

      try:
        author_element = soup.find("li", {"class": "Ere_sub2_title"}).find_all("a")[0] # 저자
        author = author_element.text.strip()
        print("저자 ", author)
      except AttributeError:
        print("로그인이 필요합니다")
        continue

      isbn, isbn2 = None, None
      try:
        isbn_element = soup.find("meta", {"property": "books:isbn"})["content"]
      except Exception as e:
        li_tags = soup.find("conts_info_list1").find('ul').find_all('li')
        for li in li_tags:
          if "ISBN: " in li.text:
            isbn_element = li.text.replace("ISBN :", "").strip()
            break
      
      isbn = isbn_element
      introduction = get_introduction(book_url, isbn_element) # 도서 소개
      
      if not introduction: # ISBN이 달라져서 책 소개를 가져오지 못하는 경우 
        try:
          a_element = soup.find("a", onclick=lambda x: x and "wrecommend_sms_send" in x)
          click_element = a_element.get("onclick")
          isbn_start_index = click_element.find("ISBN=")
        
          if isbn_start_index != -1:
            start_index = isbn_start_index + len("ISBN=")
            end_index = click_element.find(",", start_index)
            isbn2 = click_element[start_index : end_index]
            isbn2 = isbn2.rstrip("'") #' 붙어있어서 제거
            print("isbn2 ", isbn2)
            isbn = isbn2
            introduction = get_introduction(book_url, isbn2) # 도서 소개

        except Exception as e:
          print(type(e))

      # 책 소개가 없는 경우, 데이터 추가하지 않음
      if not introduction:
        print(f"책 소개가 존재하지 않습니다. 다음 도서로 넘어갑니다")
        continue  

      genre_elements = soup.find("ul", id="ulCategory").find_all("a") # 도서 장르 여러개일 수 있음
      genres = set() # 장르 중복 제거

      for genre in genre_elements:
        genre_text = genre.text if genre else ""
        genre_text = genre_text.replace('..', '').strip()
        split_genres = [content.strip() for content in genre_text.split('/')] # '/'로 나누고 앞뒤 공백 제거
        split_genres = [content for content in split_genres if content.strip() and content.strip() != "접기"] # 빈 문자열이나 필요없는 문자열 제거
        genres.update(split_genres)

      print("장르", genres)

      image_element = soup.find("img", {"id": "CoverMainImage"})
      image = image_element["src"]
      print("도서 이미지 url ", image)

      all_data.append({
        "title": title,
        "author": author,
        "keyword": keywords,
        "isbn": isbn,
        "genre": genres,
        "image": image,
        "introduction": introduction,
      })

  return all_data