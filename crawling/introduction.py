from bs4 import BeautifulSoup
import requests
import re

"""
  getContents 부분은 동적으로 처리되어 이를 비동기적인 요청을 통해 구현

  Ere_prod_mconts_box의 이름을 가진 여러 개의 div 중
  책 소개 내용이 담긴 특정 Ere_prod_mconts_box로부터 도서 내용을 얻어냄 
  내부 구조는 아래와 같음
  Ere_prod_mconts_box
    > Ere_prod_mconts_LS
    > Ere_prod_mconts_LL
    > Ere_prod_mconts_R : 책 소개 내용
      > Ere_line2
    > Ere_clear 
"""
def get_introduction(referer, isbn):
  url = f'https://www.aladin.co.kr/shop/product/getContents.aspx?ISBN={isbn}&name=Introduce&type=0&date=0' # 동적 로딩 
  headers = {
    "Referer": referer,
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
  }

  try:
    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, "lxml")
    
    #introduce_div = soup.find("div", {"class": "Ere_prod_mconts_LS"}, string="책소개")
    introduce_div = None
    div_tags = soup.find_all("div", {"class": "Ere_prod_mconts_LS"})
    for div in div_tags :
      if "소개" in div.text.strip():
        introduce_div = div
        break
    
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
    introduce_content = re.sub(r'[★〈〉《》≪≫「」『』]', '', introduce_content) # 특수문자 제거
    introduce_content = re.sub(r'[\u4e00-\u9fff]', '', introduce_content) # 한자 제거
    introduce_content = re.sub(r'\n?\s*\d+\.\s*', ' ', introduce_content) # (1. 2. 3. 등) 제거
    introduce_content = re.sub(r'\n?\s*[•●]\s*', ' ', introduce_content) # (•, ●) 제거
    introduce_content = re.sub(r'\s*[\n\r]+\s*', '. ', introduce_content) # 줄바꿈을 마침표로 자연스럽게 이어줌
    introduce_content = re.sub(r'\.\s*\.+', '.', introduce_content) # 마침표 중복 제거

    if introduce_content:  
      print("책 소개 ", introduce_content)
   
    return introduce_content
  
  except requests.exceptions.HTTPError:
    print(f"Http Error")
  except requests.exceptions.Timeout:
    print(f"Timeout Error")  
  except Exception as e:
    print(type(e))