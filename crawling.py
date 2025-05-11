from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from time import sleep
import requests
import pandas as pd
import re


def get_introduction(referer, isbn):
  url = f'https://www.aladin.co.kr/shop/product/getContents.aspx?ISBN={isbn}&name=Introduce&type=0&date=0'
  headers = {
    "Referer": referer,
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
  }

  try:
    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, "lxml")

    introduce_div = soup.find("div", {"class": "Ere_prod_mconts_LS"}, string="책소개")
    if not introduce_div:
      print("책 소개하는 내용이 없습니다")
      return None

    parent_div = introduce_div.find_parent("div", {"class": "Ere_prod_mconts_box"})
    introduce_content_div = parent_div.find("div", {"class": "Ere_prod_mconts_R"})

    content_text = [] # 도서 소개 
  
    for element in introduce_content_div.children:
      if element.name =="div" and "Ere_line2" in element.get("class", []):
        break
      if isinstance(element, str):
        content_text.append(element.strip()) # 앞뒤 공백 제거
      elif element.name == "br":
        content_text.append("\n")  
      else:
        content_text.append(element.get_text(separator="\n", strip=True))  

    introduce_content = "".join(content_text).strip() # 하나의 문자열로 결합 후, 앞뒤 공백 제거
    introduce_content = "\n".join([line.strip() for line in introduce_content.splitlines() if line.strip()])

    # 전처리
    introduce_content = re.sub(r'[〈〉《》「」『』]', '', introduce_content) # 특수문자 제거
    introduce_content = re.sub(r'[\u4e00-\u9fff]', '', introduce_content) # 한자 제거
    introduce_content = re.sub(r'\n?\s*\d+\.\s*', ' ', introduce_content) # (1. 2. 3. 등) 제거
    introduce_content = re.sub(r'\n?\s*•\s*', ' ', introduce_content) # (•) 제거
    introduce_content = re.sub(r'\n?\s*[●]\s*', ' ', introduce_content) # (●) 제거거
    introduce_content = re.sub(r'\s*[\n\r]+\s*', '. ', introduce_content) # 줄바꿈을 마침표로 자연스럽게 이어줌
    introduce_content = re.sub(r'\.\s*\.+', '.', introduce_content) # 마침표 중복 제거
    introduce_content = introduce_content.strip()

    if not introduce_content.endswith('.'):
      introduce_content += '.'

    if introduce_content:  
      print("책 소개 ", introduce_content)
   
    return introduce_content
  
  except requests.exceptions.HTTPError:
    print(f"Http Error")
  except requests.exceptions.Timeout:
    print(f"Timeout Error")  
  except Exception as e:
    print(type(e))


# 알라딘 크롤링
def crawl_aladin(page_num): 
  all_data = [] # 모든 도서 정보

  for page in range(1, page_num + 1): # 지정된 페이지만큼 접근
    url = f"https://www.aladin.co.kr/shop/common/wbest.aspx?BranchType=1&BestType=Bestseller&page={page}"
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
      
      # 상세 페이지 접근(저자, 도서 소개, 장르를 얻기 위해서)
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
      isbn_meta = soup.find("meta", {"property": "books:isbn"})["content"]
      isbn = isbn_meta

      introduction = get_introduction(book_url, isbn_meta) # 도서 소개
      
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

      genre_elements = soup.find("ul", id="ulCategory").find_all("a") # 도서 장르 여러개일 수 있음
      genres = set() # 장르 중복 제거

      for genre in genre_elements:
        genre_text = genre.text if genre else ""
        genre_text = genre_text.replace('..', '').strip()
        split_genres = [content.strip() for content in genre_text.split('/')] # '/'로 나누고 앞뒤 공백 제거
        split_genres = [content for content in split_genres if content.strip() and content.strip() != "접기"] # 필요없거나 빈 문자열 제거
        genres.update(split_genres)

      print("장르", genres)

      all_data.append({
        "title": title,
        "author": author,
        "keyword": keywords,
        "isbn": isbn,
        "genre": genres,
        "introduction": introduction
      })

  df = pd.DataFrame(all_data)
  df.to_csv("aladin_bestseller.csv", encoding="utf-8-sig", index=False) # dataframe을 csv 파일로 변환

if __name__ == "__main__":
  crawl_aladin(page_num=8)  