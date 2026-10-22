
# main.py
# 🎬 어제의 박스오피스 - 무비 스트리밍 스타일
# 초보자도 쉽게 수정할 수 있도록 한국어 주석을 달았습니다.

import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import plotly.express as px
import requests
import streamlit as st


# ==================================================
# 1. 기본 페이지 설정
# ==================================================

st.set_page_config(
    page_title="MOVIE FLOW | 어제의 박스오피스",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ==================================================
# 2. 전체 디자인 CSS
# ==================================================

st.markdown("""
<style>
/* 전체 페이지 배경과 기본 글꼴 */
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

/* 기본 글자 */
html, body, [class*="css"] {
    font-family: "Arial", "Malgun Gothic", sans-serif;
}

h1, h2, h3, p, label {
    color: #f4f3ff;
}

/* 상단 브랜드 */
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
        120deg,
        rgba(100, 65, 210, 0.38),
        rgba(35, 42, 91, 0.72),
        rgba(15, 23, 48, 0.85)
    );
    border: 1px solid rgba(179, 158, 255, 0.24);
    margin: 12px 0 25px 0;
    box-shadow: 0 12px 45px rgba(0, 0, 0, 0.18);
}

.hero-title {
    font-size: clamp(27px, 4vw, 43px);
    font-weight: 900;
    line-height: 1.2;
    letter-spacing: -1.5px;
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
    background: rgba(177, 153, 255, 0.16);
    color: #d8ccff;
    border: 1px solid rgba(177, 153, 255, 0.3);
    border-radius: 30px;
    padding: 7px 13px;
    font-size: 12px;
    font-weight: 700;
    margin-top: 15px;
}

/* 섹션 제목 */
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
    color: #ffffff;
    letter-spacing: -0.6px;
    margin-bottom: 15px;
}

/* 1위 영화 정보 카드 */
.movie-hero {
    background: linear-gradient(
        135deg,
        rgba(54, 46, 105, 0.78),
        rgba(22, 30, 62, 0.92)
    );
    border: 1px solid rgba(172, 151, 255, 0.23);
    border-radius: 22px;
    padding: 23px;
    margin-bottom: 18px;
}

.rank-pill {
    display: inline-block;
    background: linear-gradient(90deg, #9b7bff, #6e5bdb);
    color: white;
    font-size: 12px;
    font-weight: 800;
    border-radius: 8px;
    padding: 7px 12px;
    margin-bottom: 12px;
}

.movie-title {
    color: white;
    font-size: clamp(25px, 3vw, 36px);
    font-weight: 900;
    line-height: 1.25;
    letter-spacing: -1px;
    overflow-wrap: anywhere;
}

.movie-subtitle {
    color: #bfc3e4;
    font-size: 13px;
    margin-top: 10px;
    line-height: 1.8;
}

.movie-note {
    color: #a99be8;
    font-size: 12px;
    font-weight: 700;
    margin-top: 17px;
}

/* Streamlit 지표 카드 */
[data-testid="stMetric"] {
    background: linear-gradient(
        145deg,
        rgba(44, 46, 91, 0.92),
        rgba(23, 31, 61, 0.95)
    );
    border: 1px solid rgba(160, 148, 255, 0.2);
    padding: 20px 20px 17px 20px;
    border-radius: 18px;
    min-height: 115px;
}

[data-testid="stMetricLabel"] {
    color: #c4c3e7 !important;
    font-size: 13px !important;
}

[data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-size: clamp(23px, 3vw, 34px) !important;
    font-weight: 800 !important;
}

/* 표 디자인 */
[data-testid="stDataFrame"] {
    border: 1px solid rgba(155, 145, 235, 0.22);
    border-radius: 14px;
    overflow: hidden;
}

/* 입력 상자 */
[data-testid="stTextInput"] input {
    background: #171d39;
    color: white;
    border: 1px solid #494276;
    border-radius: 12px;
}

/* 버튼 */
.stButton > button {
    background: linear-gradient(100deg, #8b6cff, #6554d9);
    color: white;
    border: 0;
    border-radius: 12px;
    font-weight: 700;
    min-height: 42px;
}

.stButton > button:hover {
    border: 1px solid #c3b6ff;
    color: white;
    filter: brightness(1.12);
}

/* 안내문 */
div[data-testid="stAlert"] {
    border-radius: 14px;
}

/* 하단 */
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
# 3. 한국 시간 기준 어제 날짜 계산
# ==================================================

# 서버의 시간대가 한국과 달라도 한국 날짜를 기준으로 계산한다.
KST = ZoneInfo("Asia/Seoul")

yesterday = (
    datetime.datetime.now(KST).date()
    - datetime.timedelta(days=1)
)

# KOBIS API 날짜 형식: 연도 4자리 + 월 2자리 + 일 2자리
target_dt = yesterday.strftime("%Y%m%d")
display_date = yesterday.strftime("%Y년 %m월 %d일")


# ==================================================
# 4. 상단 브랜드와 메인 배너
# ==================================================

st.markdown(
    '<div class="brand">✦ MOVIE FLOW</div>',
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="hero-banner">
        <div class="hero-title">어제의 영화,<br>오늘의 이야기.</div>
        <div class="hero-description">
            어제 가장 많은 관객을 만난 영화는 무엇일까요?<br>
            일별 박스오피스 순위와 관객 데이터를 한눈에 확인하세요.
        </div>
        <div class="date-chip">📅 {display_date} · KOREA</div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ==================================================
# 5. API 주소
# ==================================================

API_URL = (
    "https://www.kobis.or.kr/kobisopenapi/webservice/rest/"
    "boxoffice/searchDailyBoxOfficeList.json"
)


# ==================================================
# 6. KOBIS API에서 영화 데이터 가져오기
# ==================================================

@st.cache_data(ttl=3600)
def fetch_boxoffice(date_str, api_key):
    """KOBIS API에 요청하고 JSON 데이터를 가져온다."""

    response = requests.get(
        API_URL,
        params={
            "key": api_key,
            "targetDt": date_str,
        },
        timeout=20,
    )

    # HTTP 오류가 있으면 아래에서 안내할 수 있도록 예외를 발생시킨다.
    response.raise_for_status()

    # JSON 형식이 잘못되었으면 ValueError가 발생한다.
    return response.json()


# ==================================================
# 7. 영화 포스터 찾기 (선택 기능)
# ==================================================

@st.cache_data(ttl=86400)
def find_movie_poster(movie_name):
    """
    위키백과의 공개 검색 API에서 영화 관련 이미지를 찾아본다.
    포스터가 없거나 요청이 실패하면 None을 반환한다.
    이 기능은 KOBIS의 공식 포스터 데이터가 아니다.
    """

    # 한국어 문서부터 검색한다.
    search_configs = [
        {
            "language": "ko",
            "query": f"{movie_name} 영화",
        },
        {
            "language": "en",
            "query": f"{movie_name} film",
        },
    ]

    for config in search_configs:
        try:
            url = (
                "https://"
                + config["language"]
                + ".wikipedia.org/w/api.php"
            )

            response = requests.get(
                url,
                params={
                    "action": "query",
                    "generator": "search",
                    "gsrsearch": config["query"],
                    "gsrnamespace": 0,
                    "gsrlimit": 5,
                    "prop": "pageimages",
                    "piprop": "thumbnail",
                    "pithumbsize": 700,
                    "format": "json",
                },
                headers={
                    "User-Agent": "MovieFlowDashboard/1.0"
                },
                timeout=5,
            )

            response.raise_for_status()
            result = response.json()

            pages = result.get("query", {}).get("pages", {})

            # 검색 결과 중 썸네일이 있는 이미지만 선택한다.
            for page in pages.values():
                thumbnail = page.get("thumbnail", {})
                image_url = thumbnail.get("source")

                if image_url:
                    return image_url

        except (requests.exceptions.RequestException, ValueError):
            # 이미지 검색 실패는 전체 앱의 오류로 처리하지 않는다.
            continue

    # 이미지를 찾지 못했을 때도 앱은 계속 실행된다.
    return None


# ==================================================
# 8. Secrets에서 인증키 읽기
# ==================================================

try:
    api_key = str(st.secrets["KOBIS_KEY"]).strip()

    if not api_key:
        st.error("KOBIS_KEY 인증키가 비어 있습니다.")
        st.info(
            "Streamlit Cloud → 앱 Settings → Secrets에서 "
            "KOBIS_KEY를 등록해 주세요."
        )
        st.stop()

except (KeyError, FileNotFoundError):
    st.error("KOBIS_KEY 인증키를 찾을 수 없습니다.")
    st.info(
        'Secrets에 KOBIS_KEY = "발급받은 인증키" 형식으로 '
        "등록했는지 확인해 주세요."
    )
    st.stop()


# ==================================================
# 9. API 요청 및 오류 처리
# ==================================================

try:
    data = fetch_boxoffice(target_dt, api_key)

except requests.exceptions.Timeout:
    st.error("KOBIS 서버의 응답이 너무 늦습니다.")
    st.info("잠시 후 페이지를 새로고침해 주세요.")
    st.stop()

except requests.exceptions.HTTPError as e:
    st.error("KOBIS 서버에서 HTTP 오류가 발생했습니다.")
    st.code(str(e))
    st.info("API 주소와 KOBIS 서버 상태를 확인해 주세요.")
    st.stop()

except requests.exceptions.RequestException as e:
    st.error("KOBIS 서버에 연결할 수 없습니다.")
    st.code(str(e))
    st.info("네트워크 연결이나 KOBIS 서버 상태를 확인해 주세요.")
    st.stop()

except ValueError:
    st.error("KOBIS 응답을 JSON 형식으로 읽을 수 없습니다.")
    st.info("API 응답 형식이나 서버 상태를 확인해 주세요.")
    st.stop()


# HTTP 200이어도 인증키 오류 등의 faultInfo가 올 수 있다.
if not isinstance(data, dict):
    st.error("API 응답의 데이터 형식이 올바르지 않습니다.")
    st.info("KOBIS API 응답을 확인해 주세요.")
    st.stop()

if "faultInfo" in data:
    fault = data.get("faultInfo", {})

    if not isinstance(fault, dict):
        fault = {}

    error_code = fault.get("errorCode", "확인 불가")
    error_message = fault.get("message", "오류 메시지 없음")

    st.error("KOBIS API에서 오류를 반환했습니다.")
    st.write(f"오류 코드: {error_code}")
    st.write(f"오류 메시지: {error_message}")
    st.info(
        "Secrets의 KOBIS_KEY가 정확한지, 인증키가 유효한지, "
        "API 사용 신청에 문제가 없는지 확인해 주세요."
    )
    st.stop()


# ==================================================
# 10. 영화 목록과 숫자 데이터 확인
# ==================================================

box_office = data.get("boxOfficeResult")

if not isinstance(box_office, dict):
    st.error("박스오피스 결과를 찾을 수 없습니다.")
    st.info("KOBIS API의 응답 구조를 확인해 주세요.")
    st.stop()

movies = box_office.get("dailyBoxOfficeList", [])

if not isinstance(movies, list) or len(movies) == 0:
    st.warning("아직 표시할 영화 순위 데이터가 없습니다.")
    st.info(
        "해당 날짜의 집계가 완료되지 않았거나 데이터가 없을 수 있습니다. "
        "조회 날짜와 KOBIS 서비스 상태를 확인해 주세요."
    )
    st.stop()

df = pd.DataFrame(movies)

required_columns = [
    "rank",
    "rankInten",
    "movieNm",
    "openDt",
    "audiCnt",
    "audiAcc",
    "scrnCnt",
]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:
    st.error("응답 데이터에 필요한 항목이 누락되었습니다.")
    st.write("누락된 항목:", ", ".join(missing_columns))
    st.info("KOBIS API 응답 구조를 확인해 주세요.")
    st.stop()


# API 숫자 값은 문자열이므로 숫자 형식으로 변환한다.
numeric_columns = [
    "rank",
    "rankInten",
    "audiCnt",
    "audiAcc",
    "scrnCnt",
]

for column in numeric_columns:
    df[column] = pd.to_numeric(df[column], errors="coerce")

df = df.dropna(
    subset=["rank", "audiCnt", "audiAcc", "scrnCnt"]
).copy()

if df.empty:
    st.warning("화면에 표시할 수 있는 영화 데이터가 없습니다.")
    st.info("API에서 반환된 숫자 데이터를 확인해 주세요.")
    st.stop()

df["rank"] = df["rank"].astype(int)
df["rankInten"] = df["rankInten"].fillna(0).astype(int)

df = df.sort_values("rank").reset_index(drop=True)


# ==================================================
# 11. 1위 영화 메인 영역
# ==================================================

top_movie = df.iloc[0]
movie_name = str(top_movie["movieNm"])
open_date = str(top_movie["openDt"]).strip()

st.markdown(
    '<div class="section-label">TODAY\'S TOP PICK</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-heading">지금 가장 주목받는 영화</div>',
    unsafe_allow_html=True,
)

# 포스터 검색은 선택 기능이다. 검색 실패 시에도 페이지를 유지한다.
poster_url = find_movie_poster(movie_name)

poster_col, info_col = st.columns([0.85, 1.8], gap="large")

with poster_col:
    if poster_url:
        try:
            st.image(
                poster_url,
                caption="영화 이미지 · 외부 공개 이미지 검색",
                use_container_width=True,
            )
        except Exception:
            st.markdown(
                '<div class="movie-hero">🎬<br><br>'
                '이미지를 불러올 수 없습니다.</div>',
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            """
            <div style="
                min-height: 300px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                text-align: center;
                border-radius: 20px;
                border: 1px solid rgba(172,151,255,.25);
                background: linear-gradient(145deg,#39316f,#171e3c);
                padding: 24px;
            ">
                <div style="font-size:58px;">🎞️</div>
                <div style="font-size:17px;font-weight:800;color:white;
                            margin-top:15px;">MOVIE FLOW</div>
                <div style="font-size:12px;color:#c5c4e8;
                            margin-top:8px;">포스터 이미지를 찾지 못했어요</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

with info_col:
    st.markdown(
        f"""
        <div class="movie-hero">
            <div class="rank-pill">🏆 BOX OFFICE NO. 1</div>
            <div class="movie-title">{movie_name}</div>
            <div class="movie-subtitle">
                개봉일: {open_date if open_date else "정보 없음"}<br>
                한국 시간 기준 어제의 일별 박스오피스 1위
            </div>
            <div class="movie-note">
                ✦ 어제의 관객 데이터를 확인해 보세요.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 첫 번째 줄의 지표 3개가 1위 영화의 핵심 데이터다.
    metric1, metric2, metric3 = st.columns(3)

    with metric1:
        st.metric(
            "🎟️ 어제 관객수",
            f"{int(top_movie['audiCnt']):,}명",
        )

    with metric2:
        st.metric(
            "👥 누적 관객수",
            f"{int(top_movie['audiAcc']):,}명",
        )

    with metric3:
        st.metric(
            "🖥️ 스크린수",
            f"{int(top_movie['scrnCnt']):,}개",
        )


# ==================================================
# 12. 전체 영화 순위표
# ==================================================

st.markdown("---")

st.markdown(
    '<div class="section-label">DAILY RANKING</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-heading">오늘 확인하는 영화 순위</div>',
    unsafe_allow_html=True,
)

# 영화 이름을 검색할 수 있는 입력 상자
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
    st.warning("검색한 이름과 일치하는 영화가 없습니다.")
else:
    # 순위 변동 표시를 읽기 쉬운 한국어로 변환한다.
    def make_rank_change(value):
        if value > 0:
            return f"▲ {value}"
        if value < 0:
            return f"▼ {abs(value)}"
        return "-"

    table = filtered_df[
        [
            "rank",
            "rankInten",
            "movieNm",
            "openDt",
            "audiCnt",
            "audiAcc",
            "scrnCnt",
        ]
    ].copy()

    table["rankInten"] = table["rankInten"].map(make_rank_change)

    table.columns = [
        "순위",
        "전일 대비",
        "영화명",
        "개봉일",
        "관객수",
        "누적관객",
        "스크린수",
    ]

    for column in ["관객수", "누적관객", "스크린수"]:
        table[column] = table[column].map(
            lambda value: f"{int(value):,}"
        )

    st.dataframe(
        table,
        hide_index=True,
        use_container_width=True,
        height=min(500, 45 * (len(table) + 1)),
    )


# ==================================================
# 13. 관객수 상위 5편 그래프
# ==================================================

st.markdown("---")

st.markdown(
    '<div class="section-label">AUDIENCE CHART</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-heading">어제 가장 많은 관객을 만난 영화</div>',
    unsafe_allow_html=True,
)

# 순위와 별개로 실제 관객수가 많은 상위 5편을 구한다.
top5 = df.nlargest(5, "audiCnt").copy()
top5 = top5.sort_values("audiCnt", ascending=True)

fig = px.bar(
    top5,
    x="audiCnt",
    y="movieNm",
    orientation="h",
    text="audiCnt",
    labels={
        "audiCnt": "어제 관객수(명)",
        "movieNm": "영화명",
    },
    color="audiCnt",
    color_continuous_scale=["#5144a5", "#9b82ff", "#d2c4ff"],
)

fig.update_traces(
    texttemplate="%{text:,.0f}명",
    textposition="outside",
    cliponaxis=False,
    marker_line_width=0,
)

fig.update_layout(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(
        family="Arial, Malgun Gothic, sans-serif",
        color="#e8e7ff",
        size=13,
    ),
    xaxis=dict(
        title="어제 관객수(명)",
        tickformat=",",
        showgrid=True,
        gridcolor="rgba(170,160,255,0.13)",
        zeroline=False,
    ),
    yaxis=dict(
        title="",
        showgrid=False,
    ),
    coloraxis_showscale=False,
    margin=dict(l=10, r=65, t=20, b=35),
    height=340,
)

st.plotly_chart(fig, use_container_width=True)


# ==================================================
# 14. 하단 출처 및 안내
# ==================================================

st.markdown("---")

st.markdown(
    f"""
    <div class="footer">
        <b>MOVIE FLOW</b><br>
        데이터 출처: 영화진흥위원회 영화관입장권통합전산망(KOBIS)<br>
        조회 날짜: {display_date}<br>
        영화 이미지는 외부 공개 검색 결과를 사용하며,
        이미지가 없을 경우 표시되지 않을 수 있습니다.
    </div>
    """,
    unsafe_allow_html=True,
)
