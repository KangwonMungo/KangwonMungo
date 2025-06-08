## 실행 방법

```bash
# 패키지 설치
npm install
pip install axios fastapi pydantic

# 로컬 서버 실행
cd KANGWONMUNGO/Frontend
npm run dev

# 백엔드 서버 실행
uvicorn backend.app.main:app --reload

# chroma db 설명
- chroma db 폴더에 chroma.sqlite3만 있을 경우, chroma db 폴더를 삭제한 뒤 main.py를 실행하여 다시 생성
- chroma db 폴더에 .bin 폴더들이 있어야, 도서 검색 가능합니다

# 서버 중단
ctrl + c
```
