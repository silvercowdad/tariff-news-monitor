# Tariff News Monitor (Reuters) — Streamlit Cloud

미국 관세 관련 로이터 뉴스를 자동으로 모아 요약/정리하여 보여주는 간단한 대시보드입니다.

## 배포(Streamlit Cloud)

1. GitHub에 이 폴더를 업로드 (파일: `app.py`, `requirements.txt`, `README.md`)
2. https://streamlit.io/cloud -> Sign in -> New app
3. Repo 선택, Branch: main, App file: `app.py` -> Deploy
4. 앱 설정 -> Secrets -> 아래처럼 추가 후 저장
   ```toml
   OPENAI_API_KEY = "sk-..."
   ```
5. 배포된 URL에서 바로 사용

## 환경변수 / 시크릿
- `OPENAI_API_KEY`: OpenAI API 키 (Streamlit Secrets 권장)

## 커스터마이징
- `FEED_URLS`에 다른 Reuters RSS 추가 가능
- 사이드바에서 키워드 정규식, 미국 관련 제한 체크, 최대 기사 수 조절
