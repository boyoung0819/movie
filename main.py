
import datetime
import html
import random
from zoneinfo import ZoneInfo

import pandas as pd
import plotly.express as px
import requests
import streamlit as st


# ==========================================
# 1. 기본 설정
# ==========================================
st.set_page_config(
    page_title="Pastel Movie | 영화 놀이터",
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
        --ink: #403653;
        --purple: #8471D9;
        --muted: #8F87A5;
    }

    html, body, [class*="css"] {
        font-family: 'Gowun Dodum', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(ellipse at 0% 0%, #EEE8FF 0%, transparent 38%),
            radial-gradient(ellipse at 100% 5%, #FFE8F1 0%, transparent 35%),
            linear-gradient(150deg, #FBFAFF 0%, #FFF8FC 52%, #F1FAFF 100%);
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
    }

    .brand {
        display: flex;
        align-items: center;
        gap: 13px;
        margin-bottom: 8px;
    }

    .brand-icon {
        width: 56px;
        height: 56px;
        border-radius: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 29px;
        background: linear-gradient(145deg, #E5DCFF, #FBE0ED);
        box-shadow: 6px 6px 14px #ded8eb, -5px -5px 12px #ffffff;
    }

    .brand-name {
        font-family: 'Jua', sans-serif;
        font-size: 32px;
        color: #5B4A9C;
        line-height: 1.2;
    }

    .brand-sub {
        font-size: 11px;
        color: #958AAE;
        letter-spacing: 1.7px;
        margin-top: 5px;
    }

    .pill {
        display: inline-block;
        border-radius: 30px;
        padding: 7px 12px;
        font-size: 12px;
        background: #F0EBFF;
        color: #7664C5;
        margin: 3px 4px 3px 0;
    }

    .section-title {
        font-family: 'Jua', sans-serif;
        color: #51466F;
        font-size: 24px;
        margin: 26px 0 5px 0;
    }

    .section-subtitle {
        color: #928BA4;
        font-size: 13px;
        margin-bottom: 15px;
    }

    .soft-card {
        background: rgba(255,255,255,0.88);
        border: 1px solid rgba(255,255,255,0.98);
        border-radius: 24px;
        padding: 22px;
        box-shadow: 8px 8px 22px rgba(111,99,157,0.08),
                    -5px -5px 18px rgba(255,255,255,0.9);
    }

    .hero-card {
        background: linear-gradient(125deg, #E9E2FF, #FBE5F0 58%, #E2F3FF);
        border-radius: 27px;
        padding: 27px;
        box-shadow: 9px 10px 25px rgba(118,102,170,0.12),
                    -5px -5px 18px rgba(255,255,255,0.9);
        margin: 5px 0 17px 0;
    }

    .hero-label {
        display: inline-block;
        background: rgba(255,255,255,0.8);
        color: #7563B6;
        padding: 7px 13px;
        border-radius: 30px;
        font-size: 12px;
        font-weight: bold;
        margin-bottom: 14px;
    }

    .hero-title {
        font-family: 'Jua', sans-serif;
        font-size: clamp(25px, 3vw, 38px);
        line-height: 1.4;
        color: #38304F;
        overflow-wrap: anywhere;
    }

    .hero-meta {
        color: #786F91;
        font-size: 14px;
        line-height: 2;
    }

    .ticket {
        background: linear-gradient(135deg, #FFFFFF, #F5F0FF);
        border: 2px dashed #D5C8F6;
        border-radius: 23px;
        padding: 23px;
        box-shadow: 7px 7px 18px rgba(111,99,157,0.08);
        position: relative;
    }

    .ticket-kicker {
        color: #8A76D8;
        font-size: 11px;
        letter-spacing: 2px;
        font-weight: bold;
    }

    .ticket-title {
        font-family: 'Jua', sans-serif;
        font-size: 25px;
        color: #493C77;
        margin: 10px 0;
        overflow-wrap: anywhere;
    }

    .ticket-line {
        border-top: 1px dashed #D8CDED;
        margin: 14px 0;
    }

    .ticket-detail {
        color: #817794;
        font-size: 13px;
        line-height: 1.9;
    }

    .sticker-card {
        border-radius: 22px;
        padding: 18px 12px;
        text-align: center;
        min-height: 150px;
        border: 1px solid rgba(255,255,255,0.95);
        box-shadow: 5px 6px 14px rgba(111,99,157,0.07);
    }

    .sticker-emoji {
        font-size: 34px;
        margin-bottom: 8px;
    }

    .sticker-name {
        font-family: 'Jua', sans-serif;
        color: #51466F;
        font-size: 17px;
        margin-bottom: 6px;
    }

    .sticker-desc {
        color: #857B9A;
        font-size: 12px;
        line-height: 1.6;
    }

    div[data-testid="stMetric"] {
        background: rgba(255,255,255,0.88);
        border: 1px solid rgba(255,255,255,0.98);
        padding: 17px 19px;
        border-radius: 21px;
        box-shadow: 7px 7px 17px rgba(111,99,157,0.07),
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

    div[data-baseweb="select"] > div,
    div[data-testid="stDateInput"] > div > div {
        border-radius: 14px !important;
        border-color: #E6DFFC !important;
        background: rgba(255,255,255,0.93) !important;
    }

    .stTextInput input {
        border-radius: 14px !important;
        background: rgba(255,255,255,0.95) !important;
    }

    .stButton button {
        border-radius: 15px;
        border: 1px solid #E2D9FF;
        background: linear-gradient(135deg, #F0EBFF, #FDEBF3);
        color: #5B4E9B;
        font-weight: bold;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        box-shadow: 3px 4px 10px rgba(111,99,157,0.07);
    }

    .stButton button:hover {
        border-color: #B9A9F5;
        color: #493B8C;
        transform: translateY(-2px);
        box-shadow: 4px 6px 13px rgba(111,99,157,0.12);
    }

    .stButton button:active {
        transform: scale(0.98);
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid #EEE9FA;
        border-radius: 17px;
        overflow: hidden;
    }

    .footer {
        text-align: center;
        color: #A19AB4;
        font-size: 12px;
        line-height: 2;
        padding-top: 30px;
    }

    @media (max-width: 700px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .hero-card {
            padding: 20px;
        }

        .brand-name {
            font-size: 27px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==========================================
# 3. 상단 로고
# ==========================================
st.markdown(
    """
    <div class="brand">
        <div class="brand-icon">🎬</div>
        <div>
            <div class="brand-name">Pastel Movie</div>
            <div class="brand-sub">YOUR LITTLE MOVIE PLAYGROUND</div>
        </div>
    </div>
    <p style="color:#9289AD; margin:10px 0 18px 2px;">
        영화도 구경하고, 티켓도 뽑고, 스티커도 모아 봐요! 🍿
    </p>
    <span class="pill">🎟️ MOVIE TICKET</span>
    <span class="pill">🎲 RANDOM PICK</span>
    <span class="pill">🌟 STICKER BOOK</span>
    <span class="pill">🧩 MOVIE QUIZ</span>
    """,
    unsafe_allow_html=True,
)


# ==========================================
# 4. 날짜 선택
# ==========================================
st.markdown(
    '<div class="section-title">🗓️ 영화 기록 날짜</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="section-subtitle">달력에서 날짜를 골라 그날의 영화 놀이터를 열어 보세요.</div>',
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
        <div class="soft-card">
            <div style="color:#8272C9;font-weight:bold;">✨ 선택한 영화 기록</div>
            <div style="font-family:'Jua',sans-serif;font-size:23px;color:#51466F;margin-top:6px;">
                {selected_date.strftime("%Y년 %m월 %d일")}
            </div>
            <div style="color:#9188A6;font-size:12px;margin-top:5px;">
                어제까지의 일별 박스오피스를 확인할 수 있어요.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==========================================
# 5. KOBIS API 데이터 불러오기
# ==========================================
@st.cache_data(ttl=3600, show_spinner=False)
def get_box_office(target_date, api_key):
    params = {
        "key": api_key,
        "targetDt": target_date,
        "itemPerPage": 10,
    }

    response = requests.get(API_URL, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()

    if "faultInfo" in data:
        fault = data["faultInfo"]
        raise ValueError(
            fault.get("message", "KOBIS API 오류가 발생했습니다.")
        )

    result = data.get("boxOfficeResult")
    if not result:
        raise ValueError("박스오피스 응답 데이터를 찾을 수 없습니다.")

    return result.get("dailyBoxOfficeList", [])


# ==========================================
# 6. 포스터 검색
# ==========================================
@st.cache_data(ttl=86400, show_spinner=False)
def get_movie_poster(movie_name):
    api_url = "https://ko.wikipedia.org/w/api.php"
    headers = {"User-Agent": "PastelMovieDashboard/1.0"}

    for query in [f"{movie_name} 영화", movie_name]:
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

            pages = response.json().get("query", {}).get("pages", {})
            for page in pages.values():
                image_url = page.get("thumbnail", {}).get("source")
                if image_url:
                    return image_url

        except Exception:
            continue

    return None


# ==========================================
# 7. API 키 확인
# ==========================================
try:
    api_key = st.secrets["KOBIS_KEY"]
except Exception:
    st.error(
        "🔑 KOBIS API 키가 없어요. "
        "Streamlit Cloud의 Settings → Secrets에 등록해 주세요."
    )
    st.code('KOBIS_KEY = "발급받은_API_키"', language="toml")
    st.stop()


# ==========================================
# 8. 데이터 불러오기 및 오류 처리
# ==========================================
target_date = selected_date.strftime("%Y%m%d")

try:
    with st.spinner("🍿 영화 상자를 여는 중..."):
        movies = get_box_office(target_date, api_key)

except requests.exceptions.Timeout:
    st.error("⏳ 서버 응답 시간이 초과되었어요. 잠시 후 다시 시도해 주세요.")
    st.stop()

except requests.exceptions.RequestException:
    st.error("🌐 인터넷 연결 또는 KOBIS 서버에 문제가 있어요.")
    st.stop()

except ValueError as error:
    st.error(f"⚠️ 데이터를 가져오지 못했어요: {error}")
    st.stop()

except Exception as error:
    st.error(f"⚠️ 예상하지 못한 오류가 발생했어요: {error}")
    st.stop()

if not movies:
    st.warning("📅 그날은 아직 집계 전입니다")
    st.caption("달력에서 다른 날짜를 골라 다시 확인해 주세요.")
    st.stop()


# ==========================================
# 9. 데이터 정리
# ==========================================
df = pd.DataFrame(movies)

numeric_columns = [
    "rank", "rankInten", "audiCnt",
    "audiAcc", "scrnCnt", "showCnt",
]

for column in numeric_columns:
    if column in df.columns:
        df[column] = (
            pd.to_numeric(df[column], errors="coerce")
            .fillna(0)
            .astype(int)
        )

df["movieNm"] = df["movieNm"].fillna("영화 제목 없음")
df["openDt"] = df["openDt"].fillna("-")


def number_format(value):
    return f"{int(value):,}"


def rank_change(value):
    value = int(value)
    if value > 0:
        return f"🔺 {value}"
    if value < 0:
        return f"🔻 {abs(value)}"
    return "➖ 0"


def display_movie_name(row):
    if int(row["audiAcc"]) > 1_000_000:
        return f"🏆 {row['movieNm']}"
    return str(row["movieNm"])


df["표시 영화명"] = df.apply(display_movie_name, axis=1)

first_movie = df.iloc[0]
first_title = str(first_movie["movieNm"])
first_total = int(first_movie["audiAcc"])


# ==========================================
# 10. 영화 티켓
# ==========================================
st.markdown(
    '<div class="section-title">🎟️ 오늘의 스페셜 영화 티켓</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="section-subtitle">그날의 1위 영화가 특별 티켓으로 등장해요.</div>',
    unsafe_allow_html=True,
)

ticket_left, ticket_right = st.columns([1, 1.6], gap="large")

with ticket_left:
    poster_url = get_movie_poster(first_title)

    if poster_url:
        try:
            st.image(poster_url, use_container_width=True)
        except Exception:
            st.markdown("## 🎬")
    else:
        st.markdown(
            """
            <div style="
                min-height:250px;
                border-radius:25px;
                background:linear-gradient(145deg,#E4DCFF,#FBE0ED,#DFF3FF);
                display:flex;
                align-items:center;
                justify-content:center;
                font-size:75px;
                box-shadow:8px 8px 20px rgba(111,99,157,0.09);
            ">🍿</div>
            """,
            unsafe_allow_html=True,
        )

with ticket_right:
    safe_title = html.escape(first_title)
    safe_open_date = html.escape(str(first_movie["openDt"]))
    trophy = " 🏆" if first_total > 1_000_000 else ""

    st.markdown(
        f"""
        <div class="ticket">
            <div class="ticket-kicker">PASTEL MOVIE · SPECIAL TICKET</div>
            <div style="font-size:32px;margin-top:12px;">🎟️ ✨ 🍿</div>
            <div class="ticket-title">{safe_title}{trophy}</div>
            <div class="ticket-detail">
                🏅 일별 박스오피스 {int(first_movie['rank'])}위<br>
                📅 개봉일: {safe_open_date}<br>
                👀 선택일 관객 수: {number_format(first_movie['audiCnt'])}명<br>
                💗 누적 관객 수: {number_format(first_total)}명
            </div>
            <div class="ticket-line"></div>
            <div class="ticket-detail">
                DATE · {selected_date.strftime("%Y.%m.%d")}<br>
                HAVE A LOVELY MOVIE DAY!
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("")
    m1, m2 = st.columns(2)
    m1.metric("🎥 상영 스크린", f"{number_format(first_movie['scrnCnt'])}개")
    m2.metric("✨ 상영 횟수", f"{number_format(first_movie['showCnt'])}회")


# ==========================================
# 11. 랜덤 영화 뽑기
# ==========================================
st.markdown(
    '<div class="section-title">🎲 두근두근 랜덤 영화 뽑기</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="section-subtitle">오늘의 영화 순위에서 한 편을 무작위로 골라 봐요.</div>',
    unsafe_allow_html=True,
)

if "random_movie_key" not in st.session_state:
    st.session_state.random_movie_key = None

if "random_date_key" not in st.session_state:
    st.session_state.random_date_key = None

current_date_key = selected_date.strftime("%Y%m%d")

# 날짜를 바꾸면 이전 날짜에서 뽑은 영화는 초기화합니다.
if st.session_state.random_date_key != current_date_key:
    st.session_state.random_movie_key = None
    st.session_state.random_date_key = current_date_key

random_col, result_col = st.columns([1, 2], gap="large")

with random_col:
    st.markdown(
        """
        <div class="soft-card" style="text-align:center;">
            <div style="font-size:53px;">🎁</div>
            <div style="font-family:'Jua',sans-serif;font-size:20px;color:#65539D;">
                오늘의 랜덤 박스
            </div>
            <div style="font-size:12px;color:#9187A5;margin-top:7px;">
                버튼을 눌러 영화 한 편을 뽑아 보세요!
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("🎲 영화 한 편 뽑기!", use_container_width=True):
        choices = df.to_dict("records")
        st.session_state.random_movie_key = random.choice(choices)["movieCd"]
        st.toast("✨ 두근두근! 영화가 뽑혔어요!")

with result_col:
    chosen_movie = None

    if st.session_state.random_movie_key is not None:
        matches = df[df["movieCd"] == st.session_state.random_movie_key]
        if not matches.empty:
            chosen_movie = matches.iloc[0]

    if chosen_movie is not None:
        safe_random_title = html.escape(str(chosen_movie["movieNm"]))
        st.markdown(
            f"""
            <div class="hero-card">
                <div class="hero-label">🎉 YOUR RANDOM MOVIE</div>
                <div class="hero-title">🎬 {safe_random_title}</div>
                <div class="hero-meta">
                    오늘의 순위: {int(chosen_movie['rank'])}위<br>
                    관객 수: {number_format(chosen_movie['audiCnt'])}명<br>
                    누적 관객 수: {number_format(chosen_movie['audiAcc'])}명
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div class="soft-card" style="
                text-align:center;
                min-height:160px;
                display:flex;
                align-items:center;
                justify-content:center;
                flex-direction:column;
            ">
                <div style="font-size:34px;">💌</div>
                <div style="color:#8B80A3;margin-top:8px;">
                    아직 뽑힌 영화가 없어요.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ==========================================
# 12. 영화 스티커 도감
# ==========================================
st.markdown(
    '<div class="section-title">🌟 나의 영화 스티커 도감</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="section-subtitle">그날의 영화 기록을 바탕으로 스티커를 모아 봐요.</div>',
    unsafe_allow_html=True,
)

# 스티커는 선택한 날짜의 실제 데이터 조건에 따라 열립니다.
stickers = [
    {
        "emoji": "👑",
        "name": "오늘의 왕관",
        "desc": "그날의 박스오피스 1위 영화가 있으면 획득!",
        "earned": len(df) > 0,
        "bg": "#F0E9FF",
    },
    {
        "emoji": "🏆",
        "name": "백만 관객 클럽",
        "desc": "누적 관객 수 100만 명 초과 영화가 있으면 획득!",
        "earned": bool((df["audiAcc"] > 1_000_000).any()),
        "bg": "#FFF0D9",
    },
    {
        "emoji": "🚀",
        "name": "순위 점프!",
        "desc": "전날보다 순위가 오른 영화가 있으면 획득!",
        "earned": bool((df["rankInten"] > 0).any()),
        "bg": "#E4F5FF",
    },
    {
        "emoji": "💎",
        "name": "꾸준한 인기",
        "desc": "누적 관객 수 10만 명 이상인 영화가 있으면 획득!",
        "earned": bool((df["audiAcc"] >= 100_000).any()),
        "bg": "#FCE8F2",
    },
    {
        "emoji": "🍿",
        "name": "영화 탐험가",
        "desc": "조회된 영화 목록이 있으면 획득!",
        "earned": len(df) > 0,
        "bg": "#E6F6E9",
    },
    {
        "emoji": "🎬",
        "name": "열 편의 이야기",
        "desc": "박스오피스 영화 10편이 조회되면 획득!",
        "earned": len(df) >= 10,
        "bg": "#E6F0FF",
    },
]

earned_count = sum(1 for sticker in stickers if sticker["earned"])
st.progress(earned_count / len(stickers))
st.caption(f"스티커 {earned_count} / {len(stickers)}개 획득")

sticker_cols = st.columns(3)

for i, sticker in enumerate(stickers):
    with sticker_cols[i % 3]:
        if sticker["earned"]:
            emoji = sticker["emoji"]
            name = sticker["name"]
            desc = sticker["desc"]
            bg = sticker["bg"]
            status = "✨ 획득 완료"
            opacity = "1"
        else:
            emoji = "🔒"
            name = "비밀 스티커"
            desc = "조건을 달성하면 공개돼요!"
            bg = "#F2F0F7"
            status = "아직 잠겨 있어요"
            opacity = "0.72"

        st.markdown(
            f"""
            <div class="sticker-card" style="background:{bg};opacity:{opacity};">
                <div class="sticker-emoji">{emoji}</div>
                <div class="sticker-name">{html.escape(name)}</div>
                <div class="sticker-desc">{html.escape(desc)}</div>
                <div style="font-size:11px;color:#8B7BC5;margin-top:8px;">
                    {status}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)


# ==========================================
# 13. 영화 순위 맞히기 퀴즈
# ==========================================
st.markdown(
    '<div class="section-title">🧩 두뇌 풀가동! 영화 순위 퀴즈</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="section-subtitle">영화 제목을 보고 그날의 순위를 맞혀 보세요.</div>',
    unsafe_allow_html=True,
)

if "quiz_movie_code" not in st.session_state:
    st.session_state.quiz_movie_code = None

if "quiz_revealed" not in st.session_state:
    st.session_state.quiz_revealed = False

if "quiz_date_key" not in st.session_state:
    st.session_state.quiz_date_key = None

if st.session_state.quiz_date_key != current_date_key:
    st.session_state.quiz_movie_code = None
    st.session_state.quiz_revealed = False
    st.session_state.quiz_date_key = current_date_key

quiz_left, quiz_right = st.columns([1, 1.4], gap="large")

with quiz_left:
    st.markdown(
        """
        <div class="soft-card" style="text-align:center;">
            <div style="font-size:48px;">🕵️</div>
            <div style="font-family:'Jua',sans-serif;font-size:21px;color:#66539D;">
                순위 탐정단
            </div>
            <div style="font-size:12px;color:#9187A5;margin-top:7px;">
                영화의 순위를 추리해 보세요!
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("🧩 새 퀴즈 시작하기", use_container_width=True):
        quiz_choices = df.to_dict("records")
        quiz_movie = random.choice(quiz_choices)
        st.session_state.quiz_movie_code = quiz_movie["movieCd"]
        st.session_state.quiz_revealed = False
        st.toast("🔍 새로운 퀴즈가 준비됐어요!")

with quiz_right:
    quiz_movie = None

    if st.session_state.quiz_movie_code is not None:
        quiz_matches = df[df["movieCd"] == st.session_state.quiz_movie_code]
        if not quiz_matches.empty:
            quiz_movie = quiz_matches.iloc[0]

    if quiz_movie is None:
        st.markdown(
            """
            <div class="soft-card" style="min-height:160px;text-align:center;">
                <div style="font-size:30px;">❔</div>
                <div style="color:#817794;margin-top:10px;">
                    새 퀴즈 시작하기를 눌러 주세요.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="hero-card">
                <div class="hero-label">🔎 MYSTERY RANK</div>
                <div class="hero-title">{html.escape(str(quiz_movie['movieNm']))}</div>
                <div class="hero-meta">
                    이 영화는 {selected_date.strftime("%Y년 %m월 %d일")}에 몇 위였을까요?
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        selected_rank = st.selectbox(
            "내가 생각하는 순위",
            options=list(range(1, len(df) + 1)),
            format_func=lambda value: f"{value}위",
            key=f"guess_rank_{current_date_key}_{st.session_state.quiz_movie_code}",
        )

        if st.button("정답 확인하기 ✨", use_container_width=True):
            st.session_state.quiz_revealed = True

        if st.session_state.quiz_revealed:
            correct_rank = int(quiz_movie["rank"])

            # 버튼을 눌렀을 때 선택한 답과 정답을 비교합니다.
            if selected_rank == correct_rank:
                st.success(f"🎉 정답이에요! {correct_rank}위가 맞아요!")
                st.balloons()
            else:
                st.info(
                    f"아쉽지만 정답은 {correct_rank}위예요! "
                    "다음 퀴즈에 다시 도전해 봐요."
                )


# ==========================================
# 14. TOP 5 관객 수 그래프
# ==========================================
st.markdown(
    '<div class="section-title">📊 관객들이 사랑한 TOP 5</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="section-subtitle">그날의 관객 수를 비교해 보세요.</div>',
    unsafe_allow_html=True,
)

top5 = df.head(5).copy()
top5["관객 수"] = top5["audiCnt"]
top5["영화"] = top5["표시 영화명"]
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
    font=dict(
        family="Gowun Dodum, sans-serif",
        color="#625977",
        size=12,
    ),
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

st.plotly_chart(fig, use_container_width=True)


# ==========================================
# 15. 전체 순위표와 검색
# ==========================================
st.markdown(
    '<div class="section-title">🎞️ 오늘의 영화 순위</div>',
    unsafe_allow_html=True,
)
st.markdown(
    """
    <div class="section-subtitle">
        🔺 순위 상승 &nbsp; 🔻 순위 하락 &nbsp;
        ➖ 변동 없음 &nbsp; 🏆 누적 관객 100만 명 초과
    </div>
    """,
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
        "순위 변동": display_df["rankInten"].map(rank_change),
        "영화 제목": display_df["표시 영화명"],
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
# 16. 하단 안내
# ==========================================
st.markdown(
    f"""
    <div class="footer">
        💜 PASTEL MOVIE · YOUR LITTLE MOVIE PLAYGROUND 🍿<br>
        데이터 출처: 영화진흥위원회(KOBIS) 일별 박스오피스 API<br>
        조회 기준일: {selected_date.strftime("%Y-%m-%d")}<br>
        스티커는 선택한 날짜의 조회 데이터에 따라 표시돼요.
    </div>
    """,
    unsafe_allow_html=True,
)
