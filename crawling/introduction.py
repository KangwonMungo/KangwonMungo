from bs4 import BeautifulSoup
import requests
import re

def get_introduction(referer: str, isbn: str):
  """
  알라딘 상세 페이지의 getContents를 호출하여 도서 내용을 추출

  Args:
      referer (str) : Referer 헤더값, 상세 페이지 URL
      isbn (str) : 도서의 isbn

  Returns:
        str 또는 None : 도서의 소개 내용 
  """
  url = f'https://www.aladin.co.kr/shop/product/getContents.aspx?ISBN={isbn}&name=Introduce&type=0&date=0' # 동적 로딩 
  headers = {
    "Referer": referer,
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
  }

  try:
    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, "lxml")
    
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
    return None
  except requests.exceptions.Timeout:
    print(f"Timeout Error")  
    return None
  except Exception as e:
    print(f"오류 발생 type(e)")
    return None