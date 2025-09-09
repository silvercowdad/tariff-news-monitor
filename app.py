import os
import re
import feedparser
import trafilatura
import streamlit as st
from openai import OpenAI

# --- Secrets / API Key ---
API_KEY = st.secrets.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    st.error("OPENAI_API_KEY가 설정되지 않았습니다. Streamlit Cloud Secrets에 키를 추가하세요.")
    st.stop()

client = OpenAI(api_key=API_KEY)

# --- Settings ---
FEED_URLS = [
    "https://feeds.reuters.com/reuters/businessNews",
    # 필요시 추가: "https://feeds.reuters.com/reuters/worldNews",
]
DEFAULT_KEYWORDS = "tariff|tariffs|duty|duties|section 301|section 232|anti-dumping|countervailing|retaliatory tariff"

st.set_page_config(page_title="US Tariff News (Reuters)", layout="wide")
st.title("🇺🇸 미국 관세 관련 로이터 뉴스 모니터")

with st.sidebar:
    st.header("필터")
    kw_pattern = st.text_input("키워드(정규식 | 로 구분)", DEFAULT_KEYWORDS)
    must_contain_us = st.checkbox("미국 관련(US/United States/U.S.) 포함만 보기", value=True)
    max_articles = st.slider("요약할 최대 기사 수", 1, 20, 6, 1)
    st.caption("※ 요약은 OpenAI API 호출 비용이 발생합니다.")

@st.cache_data(ttl=600)
def load_feed_entries(feed_urls):
    entries = []
    for url in feed_urls:
        feed = feedparser.parse(url)
        for e in feed.entries:
            entries.append({
                "title": e.get("title", ""),
                "link": e.get("link", ""),
                "summary": e.get("summary", ""),
            })
    return entries

def match_article(entry, pattern, require_us):
    title = (entry["title"] or "").lower()
    summary = (entry["summary"] or "").lower()
    text = title + " " + summary
    if not re.search(pattern, text, flags=re.IGNORECASE):
        return False
    if require_us and not re.search(r"\b(united states|u\.s\.|u\.s|us)\b", text, flags=re.IGNORECASE):
        # 본문까지 확인 위해 간단 fetch
        html = trafilatura.fetch_url(entry["link"])
        body = (trafilatura.extract(html) or "").lower() if html else ""
        if not re.search(r"\b(united states|u\.s\.|u\.s|us)\b", body, flags=re.IGNORECASE):
            return False
    return True

def fetch_body(url):
    html = trafilatura.fetch_url(url)
    return trafilatura.extract(html) if html else ""

def summarize_with_gpt(title, body):
    # 본문이 짧거나 비어 있어도 제목 기반으로 처리
    prompt = f"""
다음 기사를 한국어로 '전문 보도기사 요약' 스타일로 정리하세요.
- 3줄 요약(사실 위주, 과장 금지)
- 핵심 포인트 3~5개
- 관세/무역 관련 키워드가 있다면 반드시 반영(예: 301/232, anti-dumping 등)

[제목]
{title}

[본문]
{body[:3500]}
"""
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.2,
        messages=[
            {"role":"system","content":"당신은 한국어 뉴스 에디터입니다. 정확·간결·객관적으로 요약합니다."},
            {"role":"user","content": prompt}
        ],
    )
    return resp.choices[0].message.content

entries = load_feed_entries(FEED_URLS)

# 필터링
pattern = kw_pattern if kw_pattern.strip() else DEFAULT_KEYWORDS
filtered = []
for e in entries:
    try:
        if match_article(e, pattern, must_contain_us):
            filtered.append(e)
    except Exception:
        pass

st.caption(f"필터링 결과: {len(filtered)}건")

# 상위 N건 요약
for idx, e in enumerate(filtered[:max_articles], start=1):
    st.subheader(f"{idx}. {e['title']}")
    st.caption(e["link"])
    body = fetch_body(e["link"]) or ""
    summary = summarize_with_gpt(e["title"], body)
    st.write(summary)
    st.markdown("---")