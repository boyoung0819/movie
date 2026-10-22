
# main.py
# 🎬 MOVIE FLOW - 날짜를 선택할 수 있는 박스오피스 앱

import datetime
from zoneinfo import ZoneInfo
from html import escape

import pandas as pd
import plotly.express as px
import requests
import streamlit as st


# ==================================================
# 1. 기본 설정
# ==================================================

st.set_page_config(
    page_title="MOVIE FLOW | 박스오피스",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 한국 시간 기준 오늘과 어제를 계산한다.
KST = ZoneInfo("Asia/Seoul")
today = datetime.datetime.now(KST).date()
yesterday = today - datetime.timedelta(days=1)

# KOBIS 공식 일별 박스오피스 API 주소
API_URL = (
    "https://www.kobis.or.kr/kobisopenapi/webservice/rest/"
    "boxoffice/searchDailyBoxOfficeList.json"
)


# ==================================================
# 2. 디자인
# ==================================================

st.markdown("""
<style>
.stApp {
    background:
        radial-gradient(ellipse at 5% 0%, #29205b 0%, transparent 34%),
        radial-gradient(ellipse at 95% 15%, #25205a 0%, transparent 30%),
        linear-gradient(180deg, #0b1023 0%, #10152d 55%, #0b1020 100%);
    color: #f4f3ff;
}
.block-container {
    max-width: 1250px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}
h1, h2, h3, p, label {
    color: #f4f3ff;
}
.brand {
    color: #b9a5ff;
    font-size: 13px;
    font-weight: 800;
    letter-spacing: 4px;
    margin-bottom: 10px;
}
.hero-banner {
    padding: 28px 30px;
    border-radius: 24px;
    background: linear-gradient(
        120deg, rgba(100,65,210,.38),
        rgba(35,42,91,.72), rgba(15,23,48,.85)
    );
    border: 1px solid rgba(179,158,255,.24);
    margin: 12px 0 22px 0;
}
.hero-title {
    font-size: clamp(27px,4vw,43px);
    font-weight: 900;
    line-height: 1.2;
    color: white;
}
.hero-description {
    color: #c7c9e8;
    font-size: 14px;
    line-height: 1.8;
    margin-top: 12px;
}
.date-chip {
    display: inline-block;
    background: rgba(177,153,255,.16);
    color: #d8ccff;
    border: 1px solid rgba(177,153,255,.3);
    border-radius: 30px;
    padding: 7px 13px;
    font-size: 12px;
    font-weight: 700;
    margin-top: 15px;
}
.section-label {
    color: #b6a4ff;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 2px;
    margin-bottom: 7px;
}
.section-heading {
    font-size: 23px;
    font-weight: 800;
    color: white;
    margin-bottom: 15px;
}
.movie-hero {
    background: linear-gradient(135deg,rgba(54,46,105,.78),
        rgba(22,30,62,.92));
    border: 1px solid rgba(172,151,255,.23);
    border-radius: 22px;
    padding: 23px;
    margin-bottom: 18px;
}
.rank-pill {
    display: inline-block;
    background: linear-gradient(90deg,#9b7bff,#6e5bdb);
    color: white;
    font-size: 12px;
    font-weight: 800;
    border-radius: 8px;
    padding: 7px 12px;
    margin-bottom: 12px;
}
.movie-title {
    color: white;
    font-size: clamp(25px,3vw,36px);
    font-weight: 900;
    line-height: 1.25;
    overflow-wrap: anywhere;
}
.movie-subtitle {
    color: #bfc3e4;
    font-size: 13px;
    margin-top: 10px;
    line-height: 1.8;
}
.movie-note {
    color: #c0adff;
    font-size: 12px;
    font-weight: 700;
    margin-top: 17px;
}
[data-testid="stMetric"] {
    background: linear-gradient(145deg,rgba(44,46,91,.92),
        rgba(23,31,61,.95));
    border: 1px solid rgba(160,148,255,.2);
    padding: 18px;
    border-radius: 18px;
    min-height: 110px;
}
[data-testid="stMetricLabel"] {
    color: #c4c3e7 !important;
}
[data-testid="stMetricValue"] {
    color: white !important;
    font-size: clamp(22px,3vw,32px) !important;
    font-weight: 800 !important;
}
[data-testid="stDataFrame"] {
    border: 1px solid rgba(155,145,235,.22);
    border-radius: 14px;
    overflow: hidden;
}
[data-testid="stDateInput"] input {
    background: #171d39;
    color: white;
    border: 1px solid #6554a8;
    border-radius: 12px;
}
.stButton > button {
    background: linear-gradient(100deg,#8b6cff,#6554d9);
    color: white;
    border: 0;
    border-radius: 12px;
    font-weight: 700;
    min-height: 42px;
}
.stButton > button:hover {
    border: 1px solid #c3b6ff;
    color: white;
}
.footer {
    color: #8d94bb;
    font-size: 12px;
    text-align: center;
    line-height: 1.9;
    padding-top: 18px;
}
</style>
""", unsafe_allow_html=True)


# ==================================================
# 3. 상단 제목
# ==================================================

st.markdown(
    '<div class="brand">✦ MOVIE FLOW</div>',
    unsafe_allow_html=True,
)

st.markdown("""
<div class="hero-banner">
    <div class="hero-title">어제의 영화,<br>오늘의 이야기.</div>
    <div class="hero-description">
        날짜를 선택하고 그날의 박스오피스 순위를 확인하세요.<br>
        관객수부터 누적 관객수까지 한눈에 살펴볼 수 있습니다.
    </div>
</div>
""", unsafe_allow_html=True)


# ==================================================
# 4. 날짜 선택
# ==================================================

st.markdown(
    '<div class="section-label">SELECT A DATE</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="section-heading">📅 조회할 날짜를 선택하세요</div>',
    unsafe_allow_html=True,
)

# 처음 접속하면 어제가 기본으로 선택된다.
# 오늘 이후는 아직 일별 집계가 끝나지 않았으므로 선택할 수 없다.
selected_date = st.date_input(
    "박스오피스 날짜",
    value=yesterday,
    min_value=datetime.date(2004, 1, 1),
    max_value=yesterday,
    format="YYYY-MM-DD",
)

# 선택한 날짜를 KOBIS API용 YYYYMMDD 문자열로 변환한다.
target_dt = selected_date.strftime("%Y%m%d")
display_date = selected_date.strftime("%Y년 %m월 %d일")

st.markdown(
    f'<div class="date-chip">📅 선택한 날짜: {display_date}</div>',
    unsafe_allow_html=True,
)

st.caption(
    "날짜를 변경하면 해당 날짜의 박스오피스 데이터로 자동 갱신됩니다. "
    "오늘 날짜는 집계 전이므로 선택할 수 없습니다."
)


# ==================================================
# 5. KOBIS API 요청
# ==================================================

@st.cache_data(ttl=3600)
def fetch_boxoffice(date_str, api_key):
    """선택한 날짜의 일별 박스오피스 데이터를 가져온다."""
    response = requests.get(
        API_URL,
        params={"key": api_key, "targetDt": date_str},
        timeout=20,
    )
    response.raise_for_status()
    return response.json()


# ==================================================
# 6. 포스터 이미지 검색 (선택 기능)
# ==================================================

@st.cache_data(ttl=86400)
def find_movie_poster(movie_name):
    """공개 위키백과 검색에서 썸네일을 찾는다. 없으면 None을 반환한다."""
    search_configs = [
        ("ko", f"{movie_name} 영화"),
        ("en", f"{movie_name} film"),
    ]

    for language, query in search_configs:
        try:
            response = requests.get(
                f"https://{language}.wikipedia.org/w/api.php",
                params={
                    "action": "query",
                    "generator": "search",
                    "gsrsearch": query,
                    "gsrnamespace": 0,
                    "gsrlimit": 5,
                    "prop": "pageimages",
                    "piprop": "thumbnail",
                    "pithumbsize": 700,
                    "format": "json",
                },
                headers={"User-Agent": "MovieFlowDashboard/1.0"},
                timeout=5,
            )
            response.raise_for_status()
            result = response.json()
            pages = result.get("query", {}).get("pages", {})

            for page in pages.values():
                image_url = page.get("thumbnail", {}).get("source")
                if image_url:
                    return image_url

        except (requests.exceptions.RequestException, ValueError):
            # 이미지 검색 실패는 전체 앱을 중단시키지 않는다.
            continue

    return None


# ==================================================
# 7. Secrets에서 인증키 읽기
# ==================================================

try:
    api_key = str(st.secrets["KOBIS_KEY"]).strip()

    if not api_key:
        st.error("KOBIS_KEY 인증키가 비어 있습니다.")
        st.info("앱 설정 → Secrets에서 인증키를 입력해 주세요.")
        st.stop()

except (KeyError, FileNotFoundError):
    st.error("KOBIS_KEY 인증키를 찾을 수 없습니다.")
    st.info(
        'Secrets에 KOBIS_KEY = "발급받은 인증키" 형식으로 '
        "등록했는지 확인해 주세요."
    )
    st.stop()


# ==================================================
# 8. API 오류 처리
# ==================================================

try:
    data = fetch_boxoffice(target_dt, api_key)

except requests.exceptions.Timeout:
    st.error("KOBIS 서버의 응답 시간이 초과되었습니다.")
    st.info("잠시 기다린 뒤 다시 시도해 주세요.")
    st.stop()

except requests.exceptions.HTTPError as e:
    st.error("KOBIS 서버에서 HTTP 오류가 발생했습니다.")
    st.code(str(e))
    st.info("API 주소와 KOBIS 서버 상태를 확인해 주세요.")
    st.stop()

except requests.exceptions.RequestException as e:
    st.error("KOBIS 서버에 연결하지 못했습니다.")
    st.code(str(e))
    st.info("네트워크 연결과 KOBIS 서버 상태를 확인해 주세요.")
    st.stop()

except ValueError:
    st.error("API 응답을 JSON으로 읽을 수 없습니다.")
    st.info("KOBIS API 응답 형식을 확인해 주세요.")
    st.stop()

if not isinstance(data, dict):
    st.error("API 응답 형식이 올바르지 않습니다.")
    st.stop()

# HTTP 상태가 200이어도 API 오류 상자가 올 수 있다.
if "faultInfo" in data:
    fault = data.get("faultInfo", {})
    if not isinstance(fault, dict):
        fault = {}

    st.error("KOBIS API에서 오류를 반환했습니다.")
    st.write("오류 코드:", fault.get("errorCode", "확인 불가"))
    st.write("오류 메시지:", fault.get("message", "상세 메시지 없음"))
    st.info(
        "KOBIS_KEY 인증키가 정확한지, 유효한 키인지, "
        "API 사용 신청에 문제가 없는지 확인해 주세요."
    )
    st.stop()


# ==================================================
# 9. 영화 목록 확인 및 데이터 정리
# ==================================================

box_office = data.get("boxOfficeResult")

if not isinstance(box_office, dict):
    st.error("박스오피스 결과를 찾을 수 없습니다.")
    st.info("KOBIS API의 응답 구조를 확인해 주세요.")
    st.stop()

movies = box_office.get("dailyBoxOfficeList", [])

if not isinstance(movies, list) or not movies:
    st.warning(f"{display_date}의 영화 목록이 비어 있습니다.")
    st.info(
        "해당 날짜의 집계가 완료되지 않았거나 데이터가 없을 수 있습니다. "
        "다른 날짜를 선택하거나 KOBIS 서비스 상태를 확인해 주세요."
    )
    st.stop()

df = pd.DataFrame(movies)

required_columns = [
    "rank", "rankInten", "movieNm", "openDt",
    "audiCnt", "audiAcc", "scrnCnt",
]

missing = [col for col in required_columns if col not in df.columns]

if missing:
    st.error("API 응답에 필요한 항목이 누락되었습니다.")
    st.write("누락된 항목:", ", ".join(missing))
    st.stop()

# API의 숫자는 문자열이므로 숫자 형식으로 바꾼다.
numeric_columns = ["rank", "rankInten", "audiCnt", "audiAcc", "scrnCnt"]

for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(
    subset=["rank", "audiCnt", "audiAcc", "scrnCnt"]
).copy()

if df.empty:
    st.warning("표시할 수 있는 영화 데이터가 없습니다.")
    st.info("API에서 반환된 숫자 데이터를 확인해 주세요.")
    st.stop()

df["rank"] = df["rank"].astype(int)
df["rankInten"] = df["rankInten"].fillna(0).astype(int)
df = df.sort_values("rank").reset_index(drop=True)


# ==================================================
# 10. 선택한 날짜의 1위 영화
# ==================================================

top_movie = df.iloc[0]
movie_name = str(top_movie["movieNm"])
open_date = str(top_movie["openDt"]).strip()

st.markdown("---")
st.markdown(
    '<div class="section-label">BOX OFFICE NO. 1</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="section-heading">🏆 선택한 날짜의 1위 영화</div>',
    unsafe_allow_html=True,
)

poster_col, info_col = st.columns([0.85, 1.8], gap="large")

with poster_col:
    poster_url = find_movie_poster(movie_name)

    if poster_url:
        try:
            st.image(
                poster_url,
                caption="외부 공개 이미지 검색 결과",
                use_container_width=True,
            )
        except Exception:
            st.info("포스터 이미지를 표시할 수 없습니다.")
    else:
        st.markdown("""
        <div style="
            min-height:300px; display:flex; flex-direction:column;
            justify-content:center; align-items:center; text-align:center;
            border-radius:20px; border:1px solid rgba(172,151,255,.25);
            background:linear-gradient(145deg,#39316f,#171e3c);
            padding:24px;">
            <div style="font-size:58px;">🎞️</div>
            <div style="font-size:17px;font-weight:800;color:white;
                        margin-top:15px;">MOVIE FLOW</div>
            <div style="font-size:12px;color:#c5c4e8;margin-top:8px;">
                포스터 이미지가 없습니다
            </div>
        </div>
        """, unsafe_allow_html=True)

with info_col:
    # 영화 제목은 HTML에 안전하게 표시하도록 처리한다.
    safe_movie_name = escape(movie_name)
    safe_open_date = escape(open_date) if open_date else "정보 없음"

    st.markdown(
        f"""
        <div class="movie-hero">
            <div class="rank-pill">🏆 BOX OFFICE NO. 1</div>
            <div class="movie-title">{safe_movie_name}</div>
            <div class="movie-subtitle">
                개봉일: {safe_open_date}<br>
                조회 날짜: {display_date}
            </div>
            <div class="movie-note">✦ 선택한 날짜의 관객 데이터</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    card1, card2, card3 = st.columns(3)

    with card1:
        st.metric("🎟️ 어제 관객수", f"{int(top_movie['audiCnt']):,}명")

    with card2:
        st.metric("👥 누적 관객수", f"{int(top_movie['audiAcc']):,}명")

    with card3:
        st.metric("🖥️ 스크린수", f"{int(top_movie['scrnCnt']):,}개")


# ==================================================
# 11. 전체 영화 순위표
# ==================================================

st.markdown("---")
st.markdown(
    '<div class="section-label">DAILY RANKING</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="section-heading">📋 영화 순위</div>',
    unsafe_allow_html=True,
)

search_text = st.text_input(
    "🔎 영화 검색",
    placeholder="영화 제목을 입력하세요",
)

filtered_df = df.copy()

if search_text.strip():
    filtered_df = filtered_df[
        filtered_df["movieNm"].astype(str).str.contains(
            search_text.strip(),
            case=False,
            na=False,
        )
    ]

if filtered_df.empty:
    st.warning("검색한 영화가 없습니다.")
else:
    def rank_change(value):
        if value > 0:
            return f"▲ {value}"
        if value < 0:
            return f"▼ {abs(value)}"
        return "-"

    table = filtered_df[
        [
            "rank", "rankInten", "movieNm",
            "openDt", "audiCnt", "audiAcc", "scrnCnt",
        ]
    ].copy()

    table["rankInten"] = table["rankInten"].map(rank_change)

    table.columns = [
        "순위", "전일 대비", "영화명",
        "개봉일", "관객수", "누적관객", "스크린수",
    ]

    for col in ["관객수", "누적관객", "스크린수"]:
        table[col] = table[col].map(lambda value: f"{int(value):,}")

    st.dataframe(
        table,
        hide_index=True,
        use_container_width=True,
        height=min(500, 45 * (len(table) + 1)),
    )


# ==================================================
# 12. 관객수 상위 5편 그래프
# ==================================================

st.markdown("---")
st.markdown(
    '<div class="section-label">AUDIENCE CHART</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="section-heading">📊 관객수 상위 5편</div>',
    unsafe_allow_html=True,
)

top5 = df.nlargest(5, "audiCnt").sort_values("audiCnt")

fig = px.bar(
    top5,
    x="audiCnt",
    y="movieNm",
    orientation="h",
    text="audiCnt",
    labels={
        "audiCnt": "관객수(명)",
        "movieNm": "영화명",
    },
    color="audiCnt",
    color_continuous_scale=["#5144a5", "#9b82ff", "#d2c4ff"],
)

fig.update_traces(
    texttemplate="%{text:,.0f}명",
    textposition="outside",
    cliponaxis=False,
)

fig.update_layout(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#e8e7ff", size=13),
    xaxis=dict(
        title="관객수(명)",
        tickformat=",",
        gridcolor="rgba(170,160,255,.13)",
        zeroline=False,
    ),
    yaxis_title="",
    coloraxis_showscale=False,
    margin=dict(l=10, r=65, t=20, b=35),
    height=340,
)

st.plotly_chart(fig, use_container_width=True)


# ==================================================
# 13. 하단 안내
# ==================================================

st.markdown("---")
st.markdown(
    f"""
    <div class="footer">
        <b>MOVIE FLOW</b><br>
        데이터 출처: 영화진흥위원회 영화관입장권통합전산망(KOBIS)<br>
        조회 날짜: {display_date}<br>
        포스터 이미지는 외부 검색 결과이며 제공되지 않을 수 있습니다.
    </div>
    """,
    unsafe_allow_html=True,
)
