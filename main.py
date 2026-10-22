
import datetime
import html
from zoneinfo import ZoneInfo

import pandas as pd
import plotly.express as px
import requests
import streamlit as st


# ==========================================
# 1. 기본 설정
# ==========================================
st.set_page_config(
    page_title="Pastel Movie | 박스오피스",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

API_URL = (
    "https://www.kobis.or.kr/kobisopenapi/webservice/rest/"
    "boxoffice/searchDailyBoxOfficeList.json"
)

KST = ZoneInfo("Asia/Seoul")
TODAY = datetime.datetime.now(KST).date()
YESTERDAY = TODAY - datetime.timedelta(days=1)


# ==========================================
# 2. 파스텔 무비 디자인
# ==========================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Gowun+Dodum&family=Jua&display=swap');

    :root {
        --lavender: #8B7BE8;
        --lavender-light: #F0ECFF;
        --pink: #F6B9D0;
        --blue: #B9E2F8;
        --mint: #C7EBD9;
        --ink: #39334F;
        --muted: #89849F;
        --surface: #FFFFFF;
    }

    html, body, [class*="css"] {
        font-family: 'Gowun Dodum', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(ellipse at 0% 0%, #F0EAFE 0%, transparent 38%),
            radial-gradient(ellipse at 100% 10%, #FDEBF3 0%, transparent 32%),
            linear-gradient(150deg, #FAF9FF 0%, #FFF9FC 55%, #F4FAFF 100%);
        color: var(--ink);
    }

    .block-container {
        max-width: 1280px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3 {
        color: var(--ink) !important;
        font-family: 'Jua', sans-serif !important;
        letter-spacing: -0.4px;
    }

    p, label, span {
        color: inherit;
    }

    /* 상단 로고 */
    .brand {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 8px;
    }

    .brand-icon {
        width: 52px;
        height: 52px;
        border-radius: 18px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 27px;
        background: linear-gradient(145deg, #E6DEFF, #FCE4F0);
        box-shadow: 6px 6px 14px #ded9eb, -5px -5px 12px #ffffff;
    }

    .brand-name {
        font-family: 'Jua', sans-serif;
        font-size: 30px;
        color: #5B4E9B;
        line-height: 1.2;
    }

    .brand-sub {
        font-size: 12px;
        color: #9289AD;
        letter-spacing: 1.5px;
        margin-top: 4px;
    }

    /* 둥근 카드 */
    .soft-card {
        background: rgba(255, 255, 255, 0.83);
        border: 1px solid rgba(255,255,255,0.95);
        border-radius: 24px;
        padding: 23px;
        box-shadow:
            8px 8px 22px rgba(111, 99, 157, 0.09),
            -5px -5px 18px rgba(255,255,255,0.9);
    }

    /* 대표 영화 */
    .hero-card {
        background: linear-gradient(125deg, #E9E2FF 0%, #FBE5F0 55%, #E2F3FF 100%);
        border-radius: 28px;
        padding: 28px;
        box-shadow:
            9px 10px 25px rgba(118, 102, 170, 0.13),
            -5px -5px 18px rgba(255,255,255,0.9);
        margin: 8px 0 20px 0;
    }

    .hero-label {
        display: inline-block;
        background: rgba(255,255,255,0.78);
        color: #7563B6;
        padding: 7px 13px;
        border-radius: 30px;
        font-size: 12px;
        font-weight: bold;
        letter-spacing: 1px;
        margin-bottom: 15px;
    }

    .hero-title {
        font-family: 'Jua', sans-serif;
        font-size: clamp(25px, 3vw, 38px);
        line-height: 1.35;
        color: #38304F;
        overflow-wrap: anywhere;
        margin-bottom: 9px;
    }

    .hero-meta {
        color: #786F91;
        font-size: 14px;
        line-height: 1.9;
    }

    .hero-caption {
        color: #766D8C;
        font-size: 13px;
        margin-top: 12px;
    }

    /* 작은 안내 태그 */
    .pill {
        display: inline-block;
        border-radius: 30px;
        padding: 6px 11px;
        font-size: 12px;
        background: #F0ECFF;
        color: #7664C5;
        margin: 3px 4px 3px 0;
    }

    /* 섹션 제목 */
    .section-title {
        font-family: 'Jua', sans-serif;
        color: #51466F;
        font-size: 23px;
        margin: 24px 0 5px 0;
    }

    .section-subtitle {
        color: #928BA4;
        font-size: 13px;
        margin-bottom: 14px;
    }

    /* 메트릭 카드 */
    div[data-testid="stMetric"] {
        background: rgba(255,255,255,0.86);
        border: 1px solid rgba(255,255,255,0.98);
        padding: 18px 20px;
        border-radius: 22px;
        box-shadow: 7px 7px 17px rgba(111,99,157,0.08),
                    -4px -4px 12px rgba(255,255,255,0.9);
    }

    div[data-testid="stMetricLabel"] {
        color: #817994 !important;
        font-size: 13px !important;
    }

    div[data-testid="stMetricValue"] {
        color: #5B4E9B !important;
        font-family: 'Jua', sans-serif !important;
    }

    /* 입력창 */
    div[data-baseweb="select"] > div,
    div[data-testid="stDateInput"] > div > div {
        border-radius: 14px !important;
        border-color: #E6DFFC !important;
        background: rgba(255,255,255,0.9) !important;
    }

    .stTextInput input {
        border-radius: 14px !important;
        background: rgba(255,255,255,0.9) !important;
    }

    /* 표 */
    div[data-testid="stDataFrame"] {
        border: 1px solid #EEE9FA;
        border-radius: 17px;
        overflow: hidden;
    }

    /* 버튼 */
    .stButton button {
        border-radius: 14px;
        border: 1px solid #E2D9FF;
        background: linear-gradient(135deg, #F0EBFF, #FDEBF3);
        color: #5B4E9B;
        font-weight: bold;
    }

    .stButton button:hover {
        border-color: #B9A9F5;
        color: #493B8C;
    }

    /* 하단 */
    .footer {
        text-align: center;
        color: #A19AB4;
        font-size: 12px;
        line-height: 2;
        padding-top: 28px;
    }

    /* 모바일 화면 */
    @media (max-width: 700px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .hero-card {
            padding: 20px;
        }

        .brand-name {
            font-size: 25px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==========================================
# 3. 상단 제목
# ==========================================
st.markdown(
    """
    <div class="brand">
        <div class="brand-icon">🎬</div>
        <div>
            <div class="brand-name">Pastel Movie</div>
            <div class="brand-sub">YOUR DAILY BOX OFFICE DIARY</div>
        </div>
    </div>
    <p style="color:#9289AD; margin: 10px 0 20px 2px;">
        오늘은 어떤 영화가 가장 많은 사랑을 받았을까요? 🍿
    </p>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div>
        <span class="pill">🎞️ DAILY RANKING</span>
        <span class="pill">💜 MOVIE DIARY</span>
        <span class="pill">☁️ PASTEL EDITION</span>
    </div>
    """,
    unsafe_allow_html=True,
)


# ==========================================
# 4. 날짜 선택
# ==========================================
st.markdown('<div class="section-title">🗓️ 영화 기록 날짜</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-subtitle">조회하고 싶은 날짜의 박스오피스를 선택해 보세요.</div>',
    unsafe_allow_html=True,
)

date_col, info_col = st.columns([1, 2], vertical_alignment="center")

with date_col:
    selected_date = st.date_input(
        "조회 날짜",
        value=YESTERDAY,
        min_value=datetime.date(2004, 1, 1),
        max_value=YESTERDAY,
        format="YYYY-MM-DD",
    )

with info_col:
    st.markdown(
        f"""
        <div style="
            background:rgba(255,255,255,0.72);
            border:1px solid #EEE7FF;
            border-radius:18px;
            padding:16px 20px;
            color:#817994;
            line-height:1.8;
        ">
            <span style="color:#7764C5;font-weight:bold;">✨ 선택한 날짜</span><br>
            <span style="font-size:21px;color:#4D426E;font-weight:bold;">
                {selected_date.strftime("%Y년 %m월 %d일")}
            </span><br>
            <span style="font-size:12px;">한국 영화진흥위원회(KOBIS) 일별 박스오피스 기준</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==========================================
# 5. API에서 박스오피스 데이터 가져오기
# ==========================================
@st.cache_data(ttl=3600, show_spinner=False)
def get_box_office(target_date, api_key):
    """선택한 날짜의 일별 박스오피스 데이터를 가져옵니다."""
    params = {
        "key": api_key,
        "targetDt": target_date,
        "itemPerPage": 10,
    }

    response = requests.get(API_URL, params=params, timeout=15)
    response.raise_for_status()

    data = response.json()

    # KOBIS는 오류가 발생해도 JSON으로 응답할 수 있습니다.
    if "faultInfo" in data:
        fault = data["faultInfo"]
        message = fault.get("message", "KOBIS API에서 오류가 발생했습니다.")
        raise ValueError(message)

    result = data.get("boxOfficeResult")
    if not result:
        raise ValueError("박스오피스 응답 데이터를 찾을 수 없습니다.")

    movies = result.get("dailyBoxOfficeList", [])
    return movies


# ==========================================
# 6. 영화 포스터 찾기
#    위키백과에서 이미지를 찾습니다.
#    이미지를 못 찾더라도 앱은 계속 작동합니다.
# ==========================================
@st.cache_data(ttl=86400, show_spinner=False)
def get_movie_poster(movie_name):
    """위키백과 검색 결과에서 영화 관련 썸네일을 찾습니다."""
    api_url = "https://ko.wikipedia.org/w/api.php"

    headers = {
        "User-Agent": "PastelMovieDashboard/1.0 (movie information viewer)"
    }

    # 먼저 한국어 위키백과에서 검색합니다.
    search_queries = [
        f"{movie_name} 영화",
        movie_name,
    ]

    for query in search_queries:
        try:
            params = {
                "action": "query",
                "format": "json",
                "generator": "search",
                "gsrsearch": query,
                "gsrnamespace": 0,
                "gsrlimit": 5,
                "prop": "pageimages",
                "piprop": "thumbnail",
                "pithumbsize": 600,
            }

            response = requests.get(
                api_url,
                params=params,
                headers=headers,
                timeout=5,
            )
            response.raise_for_status()
            data = response.json()

            pages = data.get("query", {}).get("pages", {})
            for page in pages.values():
                thumbnail = page.get("thumbnail", {}).get("source")
                if thumbnail:
                    return thumbnail

        except Exception:
            # 포스터 검색 실패는 전체 앱 오류로 이어지지 않습니다.
            continue

    return None


# ==========================================
# 7. API 키 확인 및 데이터 불러오기
# ==========================================
try:
    api_key = st.secrets["KOBIS_KEY"]
except Exception:
    st.error(
        "🔑 KOBIS API 키를 찾을 수 없어요. "
        "Streamlit Cloud의 Settings → Secrets에 "
        "KOBIS_KEY를 등록해 주세요."
    )
    st.code('KOBIS_KEY = "발급받은_API_키"', language="toml")
    st.stop()


target_date = selected_date.strftime("%Y%m%d")

try:
    with st.spinner("🍿 영화 기록장을 펼치는 중..."):
        movies = get_box_office(target_date, api_key)

except requests.exceptions.Timeout:
    st.error("⏳ 서버 응답 시간이 초과되었어요. 잠시 후 다시 시도해 주세요.")
    st.stop()

except requests.exceptions.RequestException:
    st.error("🌐 인터넷 연결 또는 KOBIS 서버에 문제가 있어요.")
    st.stop()

except ValueError as error:
    st.error(f"⚠️ 박스오피스 데이터를 가져오지 못했어요: {error}")
    st.stop()

except Exception as error:
    st.error(f"⚠️ 예상하지 못한 오류가 발생했어요: {error}")
    st.stop()


if not movies:
    st.warning(
        "🌷 선택한 날짜의 박스오피스 자료가 없어요. "
        "다른 날짜를 선택해 주세요."
    )
    st.stop()


# ==========================================
# 8. 데이터 정리
# ==========================================
df = pd.DataFrame(movies)

numeric_columns = [
    "rank",
    "rankInten",
    "audiCnt",
    "audiAcc",
    "scrnCnt",
    "showCnt",
]

for column in numeric_columns:
    if column in df.columns:
        df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0).astype(int)

df["movieNm"] = df["movieNm"].fillna("영화 제목 없음")
df["openDt"] = df["openDt"].fillna("-")

first_movie = df.iloc[0]
first_title = str(first_movie["movieNm"])
first_rank = int(first_movie["rank"])
first_audience = int(first_movie["audiCnt"])
first_total = int(first_movie["audiAcc"])
first_screens = int(first_movie["scrnCnt"])
first_shows = int(first_movie["showCnt"])


def number_format(value):
    """숫자에 천 단위 쉼표를 붙입니다."""
    return f"{int(value):,}"


def rank_change(value):
    """순위 변동을 읽기 쉬운 기호로 바꿉니다."""
    value = int(value)

    if value > 0:
        return f"▲ {value}"
    if value < 0:
        return f"▼ {abs(value)}"
    return "—"


# ==========================================
# 9. 대표 영화 카드
# ==========================================
poster_url = get_movie_poster(first_title)

st.markdown(
    '<div class="section-title">🌟 오늘의 주인공</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="section-subtitle">선택한 날짜에 가장 높은 순위를 기록한 영화예요.</div>',
    unsafe_allow_html=True,
)

poster_col, hero_col = st.columns([0.85, 2.15], gap="large")

with poster_col:
    if poster_url:
        try:
            st.image(poster_url, use_container_width=True)
        except Exception:
            st.markdown(
                """
                <div style="
                    background:linear-gradient(145deg,#E6DEFF,#FCE4F0);
                    border-radius:22px;
                    min-height:300px;
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    font-size:72px;
                ">🎬</div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            """
            <div style="
                background:linear-gradient(145deg,#E6DEFF,#FCE4F0,#DDF1FF);
                border-radius:22px;
                min-height:300px;
                display:flex;
                align-items:center;
                justify-content:center;
                box-shadow:8px 8px 20px rgba(111,99,157,0.10);
                font-size:72px;
            ">🍿</div>
            """,
            unsafe_allow_html=True,
        )

    st.caption("포스터 이미지는 검색 결과에 따라 표시되지 않을 수 있어요.")

with hero_col:
    safe_title = html.escape(first_title)
    safe_open_date = html.escape(str(first_movie["openDt"]))

    st.markdown(
        f"""
        <div class="hero-card">
            <div class="hero-label">🏆 NO. {first_rank} · DAILY BEST</div>
            <div class="hero-title">{safe_title}</div>
            <div class="hero-meta">
                🎬 개봉일 &nbsp; {safe_open_date}<br>
                🗓️ 조회일 &nbsp; {selected_date.strftime("%Y년 %m월 %d일")}
            </div>
            <div style="margin-top:18px;">
                <span class="pill">💜 오늘의 1위</span>
                <span class="pill">🍿 관객이 선택한 영화</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    metric1, metric2 = st.columns(2)

    with metric1:
        st.metric(
            label="🎟️ 선택일 관객 수",
            value=f"{number_format(first_audience)}명",
        )

    with metric2:
        st.metric(
            label="💗 누적 관객 수",
            value=f"{number_format(first_total)}명",
        )

    small1, small2 = st.columns(2)

    with small1:
        st.metric(
            label="🎥 상영 스크린",
            value=f"{number_format(first_screens)}개",
        )

    with small2:
        st.metric(
            label="✨ 상영 횟수",
            value=f"{number_format(first_shows)}회",
        )


# ==========================================
# 10. TOP 5 관객 수 그래프
# ==========================================
st.markdown(
    '<div class="section-title">📊 관객들이 사랑한 TOP 5</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="section-subtitle">선택한 날짜의 영화별 관객 수를 비교해 보세요.</div>',
    unsafe_allow_html=True,
)

top5 = df.head(5).copy()
top5["관객 수"] = top5["audiCnt"]
top5["영화"] = top5["movieNm"]

# 순위 1위가 위에 오도록 순서를 뒤집습니다.
top5 = top5.iloc[::-1]

fig = px.bar(
    top5,
    x="관객 수",
    y="영화",
    orientation="h",
    text="관객 수",
    color="rank",
    color_continuous_scale=[
        "#C9E9FA",
        "#D9D0FF",
        "#F7CDE0",
        "#B8A8F0",
        "#8C7BE8",
    ],
    custom_data=["rank"],
)

fig.update_traces(
    texttemplate="%{text:,.0f}명",
    textposition="outside",
    cliponaxis=False,
    marker_line_width=0,
    hovertemplate="<b>%{y}</b><br>관객 수: %{x:,.0f}명<extra></extra>",
)

fig.update_layout(
    height=360,
    margin=dict(l=10, r=70, t=15, b=10),
    paper_bgcolor="rgba(255,255,255,0)",
    plot_bgcolor="rgba(255,255,255,0)",
    font=dict(family="Gowun Dodum, sans-serif", color="#625977", size=12),
    showlegend=False,
    coloraxis_showscale=False,
    xaxis=dict(
        title="관객 수",
        showgrid=True,
        gridcolor="rgba(170,157,206,0.18)",
        zeroline=False,
        tickformat=",",
    ),
    yaxis=dict(
        title="",
        showgrid=False,
        automargin=True,
    ),
)

st.markdown(
    '<div class="soft-card">',
    unsafe_allow_html=True,
)
st.plotly_chart(fig, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)


# ==========================================
# 11. 전체 박스오피스 순위표
# ==========================================
st.markdown(
    '<div class="section-title">🎞️ 오늘의 영화 순위</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="section-subtitle">영화 제목을 검색하고 순위와 관객 수를 확인해 보세요.</div>',
    unsafe_allow_html=True,
)

search_text = st.text_input(
    "🔎 영화 검색",
    placeholder="궁금한 영화 제목을 입력해 보세요.",
)

display_df = df.copy()

if search_text.strip():
    display_df = display_df[
        display_df["movieNm"].str.contains(
            search_text.strip(),
            case=False,
            na=False,
        )
    ]

if display_df.empty:
    st.info("검색 결과가 없어요. 다른 영화 제목을 입력해 주세요.")
else:
    table_df = pd.DataFrame({
        "순위": display_df["rank"].map(lambda x: f"{x}위"),
        "변동": display_df["rankInten"].map(rank_change),
        "영화 제목": display_df["movieNm"],
        "개봉일": display_df["openDt"],
        "관객 수": display_df["audiCnt"].map(lambda x: f"{x:,}명"),
        "누적 관객 수": display_df["audiAcc"].map(lambda x: f"{x:,}명"),
    })

    st.dataframe(
        table_df,
        use_container_width=True,
        hide_index=True,
        height=min(440, 38 * (len(table_df) + 1)),
    )


# ==========================================
# 12. 하단 안내
# ==========================================
st.markdown(
    f"""
    <div class="footer">
        💜 PASTEL MOVIE · YOUR DAILY BOX OFFICE DIARY 🍿<br>
        데이터 출처: 영화진흥위원회(KOBIS) 일별 박스오피스 API<br>
        조회 기준일: {selected_date.strftime("%Y-%m-%d")}<br>
        <span style="font-size:11px;">
            포스터는 위키백과 검색 결과를 활용하며, 일부 영화는 이미지가 표시되지 않을 수 있습니다.
        </span>
    </div>
    """,
    unsafe_allow_html=True,
)
