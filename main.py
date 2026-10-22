
import random
import datetime as dt
from zoneinfo import ZoneInfo
from html import escape

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

st.set_page_config(
    page_title="Pastel Movie | Cinema, Curated",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

KST = ZoneInfo("Asia/Seoul")
MAX_DATE = dt.datetime.now(KST).date() - dt.timedelta(days=1)
MIN_DATE = dt.date(2004, 1, 1)
API_URL = (
    "https://www.kobis.or.kr/kobisopenapi/webservice/rest/"
    "boxoffice/searchDailyBoxOfficeList.json"
)

STICKERS = [
    {"id": "first", "emoji": "🎞️", "name": "첫 번째 크레딧", "mission": "영화 1편 발견"},
    {"id": "three", "emoji": "🍿", "name": "팝콘 클럽", "mission": "서로 다른 영화 3편 발견"},
    {"id": "five", "emoji": "🎟️", "name": "티켓 컬렉터", "mission": "서로 다른 영화 5편 발견"},
    {"id": "ten", "emoji": "💎", "name": "시네마 젬", "mission": "서로 다른 영화 10편 발견"},
    {"id": "quiz1", "emoji": "🔎", "name": "순위 탐정", "mission": "퀴즈 첫 정답"},
    {"id": "quiz5", "emoji": "🏆", "name": "퀴즈 마스터", "mission": "퀴즈 정답 5회"},
    {"id": "streak3", "emoji": "🔥", "name": "연속 정답왕", "mission": "3문제 연속 정답"},
    {"id": "explore5", "emoji": "🧭", "name": "필름 탐험가", "mission": "랜덤 영화 5회 뽑기"},
]

DEFAULT_PROFILE = {
    "found_movies": [],
    "stickers": [],
    "quiz_score": 0,
    "quiz_total": 0,
    "quiz_streak": 0,
    "best_streak": 0,
    "explore_count": 0,
}

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Noto+Sans+KR:wght@400;500;600;700;800&display=swap');
:root {--ink:#252037;--muted:#81798f;--line:#ebe5f2;}
html,body,[class*="css"] {font-family:'DM Sans','Noto Sans KR',sans-serif;color:var(--ink);}
.stApp {
 background:
 radial-gradient(ellipse at 5% 0%,#eee7ff 0,transparent 30%),
 radial-gradient(ellipse at 95% 5%,#fff0f7 0,transparent 27%),
 #f8f7fb;
}
#MainMenu,footer {visibility:hidden;}
header[data-testid="stHeader"] {background:transparent;}
.block-container {max-width:1320px;padding-top:1.3rem;padding-bottom:3rem;}
h1,h2,h3 {letter-spacing:-.035em;color:var(--ink);}
.brand {font-weight:800;letter-spacing:.13em;color:#6e5a9a;font-size:.88rem;}
.brand-icon {display:inline-block;background:linear-gradient(135deg,#c9b8ff,#f6c8df);padding:9px;border-radius:12px;margin-right:9px;}
.hero {
 border:1px solid white;border-radius:28px;padding:clamp(24px,4vw,48px);
 background:linear-gradient(115deg,#e8e0ff,#fbe8f2 55%,#e2f3fb);
 box-shadow:0 18px 45px #51406c0d;margin:18px 0 25px;overflow:hidden;
}
.hero h1 {font-size:clamp(2rem,4vw,3.2rem);line-height:1.12;margin:.7rem 0;}
.hero p {color:#756b87;line-height:1.8;max-width:720px;}
.eyebrow {font-size:.68rem;letter-spacing:.16em;font-weight:800;color:#8170a5;}
.feature {
 border:1px solid white;border-radius:25px;padding:25px;
 background:linear-gradient(130deg,#e8e0ff,#fae9f2 60%,#e4f5fc);
 box-shadow:0 12px 35px #51406c0a;
}
.surface {background:#ffffffdf;border:1px solid #eee8f5;border-radius:21px;padding:20px;box-shadow:0 8px 25px #51406c08;}
.section {margin:28px 0 13px;}
.section h2 {font-size:1.45rem;margin:0;}
.muted {color:var(--muted);font-size:.84rem;}
.tag {display:inline-block;background:#ffffffc9;border:1px solid white;border-radius:99px;padding:6px 11px;font-size:.68rem;font-weight:800;letter-spacing:.08em;color:#6d5b93;}
.poster-fallback {aspect-ratio:2/3;border-radius:16px;background:linear-gradient(145deg,#ded4fc,#f8d9e9,#d8effa);display:flex;align-items:center;justify-content:center;text-align:center;padding:12px;color:#6e5d94;overflow:hidden;}
.poster-fallback img {width:100%;height:100%;object-fit:cover;}
.stButton>button {border-radius:13px;border:1px solid #e5dcef;background:linear-gradient(105deg,#eee8ff,#fff0f7);color:#51436f;font-weight:700;min-height:43px;transition:transform .15s ease,box-shadow .15s ease;}
.stButton>button:hover {transform:translateY(-1px);border-color:#c9b7ed;box-shadow:0 7px 18px #75608e12;color:#40325e;}
.stTextInput input,.stSelectbox div[data-baseweb="select"]>div,.stDateInput input {border-radius:12px!important;border-color:#e8e1f0!important;background:white;}
div[data-testid="stMetric"] {background:#ffffffcf;border:1px solid #eee8f4;border-radius:17px;padding:14px 16px;}
.stProgress>div>div>div>div {background:linear-gradient(90deg,#b6a1f4,#f0bcd6,#a9def3);}
.stPlotlyChart {background:#ffffffb8;border:1px solid #eee8f4;border-radius:20px;padding:8px;}
div[data-testid="stDataFrame"] {border:1px solid #eee8f4;border-radius:16px;overflow:hidden;}
hr {border-color:#eae4f1!important;}
</style>
""", unsafe_allow_html=True)


# ---------- 세션 상태 ----------
def init_state():
    defaults = {
        "page": "home",
        "selected_date": MAX_DATE,
        "loaded_date": None,
        "df": None,
        "load_error": None,
        "profile": DEFAULT_PROFILE.copy(),
        "profile_loaded": False,
        "quiz_movie": None,
        "quiz_answered": False,
        "quiz_feedback": None,
        "quiz_balloons_shown": False,
        "random_movie": None,
        "new_sticker": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_state()


# ---------- Supabase 선택적 영구 저장 ----------
def supabase_ready():
    try:
        return all(
            str(st.secrets.get(key, "")).strip()
            for key in ("SUPABASE_URL", "SUPABASE_KEY", "PROFILE_ID")
        )
    except Exception:
        return False


def load_profile():
    if not supabase_ready():
        return DEFAULT_PROFILE.copy()

    try:
        base = str(st.secrets["SUPABASE_URL"]).rstrip("/")
        key = str(st.secrets["SUPABASE_KEY"])
        table = str(st.secrets.get("SUPABASE_TABLE", "movie_profiles"))
        profile_id = str(st.secrets["PROFILE_ID"])

        response = requests.get(
            f"{base}/rest/v1/{table}",
            params={
                "profile_id": f"eq.{profile_id}",
                "select": "profile_id,data",
            },
            headers={
                "apikey": key,
                "Authorization": f"Bearer {key}",
            },
            timeout=10,
        )
        response.raise_for_status()
        rows = response.json()

        if rows:
            profile = DEFAULT_PROFILE.copy()
            profile.update(rows[0].get("data") or {})
            return profile

    except (requests.RequestException, ValueError, TypeError, KeyError):
        st.warning("저장된 기록을 불러오지 못했어요. Supabase 설정을 확인해 주세요.")

    return DEFAULT_PROFILE.copy()


def save_profile():
    if not supabase_ready():
        return

    try:
        base = str(st.secrets["SUPABASE_URL"]).rstrip("/")
        key = str(st.secrets["SUPABASE_KEY"])
        table = str(st.secrets.get("SUPABASE_TABLE", "movie_profiles"))

        response = requests.post(
            f"{base}/rest/v1/{table}",
            params={"on_conflict": "profile_id"},
            headers={
                "apikey": key,
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
                "Prefer": "resolution=merge-duplicates,return=minimal",
            },
            json={
                "profile_id": str(st.secrets["PROFILE_ID"]),
                "data": st.session_state.profile,
            },
            timeout=10,
        )
        response.raise_for_status()

    except (requests.RequestException, KeyError):
        st.warning("기록 저장에 실패했어요. Supabase 테이블 설정을 확인해 주세요.")


def persist():
    save_profile()


if not st.session_state.profile_loaded:
    st.session_state.profile = load_profile()
    st.session_state.profile_loaded = True


# ---------- 데이터 ----------
def fmt(value):
    try:
        return f"{int(float(value)):,}"
    except (ValueError, TypeError):
        return "0"


def safe(value):
    return escape(str(value if value is not None else ""))


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_boxoffice(date_string):
    try:
        api_key = st.secrets["KOBIS_KEY"]
    except Exception:
        return None, "KOBIS_KEY가 Streamlit Secrets에 등록되어 있지 않습니다."

    try:
        response = requests.get(
            API_URL,
            params={"key": api_key, "targetDt": date_string},
            timeout=15,
        )
        response.raise_for_status()
        payload = response.json()

        if "faultInfo" in payload:
            return None, payload["faultInfo"].get("message", "KOBIS API 오류")

        rows = payload.get("boxOfficeResult", {}).get("dailyBoxOfficeList", [])
        if not rows:
            return pd.DataFrame(), None

        df = pd.DataFrame(rows)

        for col in ["rank", "rankInten", "audiCnt", "audiAcc", "scrnCnt", "showCnt"]:
            if col not in df.columns:
                df[col] = 0
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

        for col in ["movieNm", "movieCd", "openDt"]:
            if col not in df.columns:
                df[col] = ""

        return df, None

    except requests.Timeout:
        return None, "KOBIS 서버 응답 시간이 초과됐어요. 잠시 후 다시 시도해 주세요."
    except requests.RequestException:
        return None, "네트워크 연결을 확인해 주세요."
    except (ValueError, TypeError):
        return None, "KOBIS에서 읽을 수 없는 응답을 받았어요."


def load_date_data(date, force=False):
    date_string = date.strftime("%Y%m%d")

    if force or st.session_state.loaded_date != date_string:
        df, error = fetch_boxoffice(date_string)
        st.session_state.loaded_date = date_string
        st.session_state.df = df
        st.session_state.load_error = error

        # 날짜가 바뀌면 진행 중인 퀴즈를 초기화
        st.session_state.quiz_movie = None
        st.session_state.quiz_answered = False
        st.session_state.quiz_feedback = None

    return st.session_state.df, st.session_state.load_error


@st.cache_data(ttl=86400, show_spinner=False)
def get_poster(movie_name):
    """위키미디어/위키백과에서 포스터 이미지를 찾아요. 없으면 기본 디자인을 보여 줍니다."""
    try:
        response = requests.get(
            "https://ko.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "generator": "search",
                "gsrsearch": f"{movie_name} 영화 포스터",
                "gsrnamespace": 6,
                "gsrlimit": 5,
                "prop": "imageinfo",
                "iiprop": "url",
                "iiurlwidth": 360,
                "format": "json",
            },
            headers={"User-Agent": "PastelMovie/1.0"},
            timeout=6,
        )
        response.raise_for_status()
        pages = response.json().get("query", {}).get("pages", {})

        for page in pages.values():
            info = page.get("imageinfo", [])
            if info:
                url = info[0].get("thumburl") or info[0].get("url")
                if url and url.lower().split("?")[0].endswith(
                    (".jpg", ".jpeg", ".png", ".webp")
                ):
                    return url

    except (requests.RequestException, ValueError, TypeError):
        pass

    return ""


def show_poster(movie_name):
    url = get_poster(str(movie_name))
    if url:
        st.image(url, use_container_width=True)
    else:
        st.markdown(
            f'<div class="poster-fallback"><div>'
            f'<div style="font-size:38px;">🎞️</div>'
            f'<div style="font-size:.65rem;letter-spacing:.15em;">PASTEL MOVIE</div>'
            f'<div style="font-weight:800;margin-top:9px;">{safe(movie_name)}</div>'
            f'<div style="font-size:.7rem;margin-top:8px;">POSTER UNAVAILABLE</div>'
            f'</div></div>',
            unsafe_allow_html=True,
        )


# ---------- 업적과 스티커 ----------
def unlock(sticker_id):
    profile = st.session_state.profile
    if sticker_id not in profile["stickers"]:
        profile["stickers"].append(sticker_id)
        st.session_state.new_sticker = sticker_id
        persist()


def check_achievements():
    p = st.session_state.profile
    rules = [
        (len(p["found_movies"]) >= 1, "first"),
        (len(p["found_movies"]) >= 3, "three"),
        (len(p["found_movies"]) >= 5, "five"),
        (len(p["found_movies"]) >= 10, "ten"),
        (p["quiz_score"] >= 1, "quiz1"),
        (p["quiz_score"] >= 5, "quiz5"),
        (p["best_streak"] >= 3, "streak3"),
        (p["explore_count"] >= 5, "explore5"),
    ]
    for achieved, sticker_id in rules:
        if achieved:
            unlock(sticker_id)


def add_movie(movie):
    code = str(movie.get("movieCd", "")).strip()
    if not code or code.lower() == "nan":
        code = str(movie.get("movieNm", "")).strip()

    p = st.session_state.profile
    if code and code not in p["found_movies"]:
        p["found_movies"].append(code)
        persist()

    check_achievements()


def show_toast():
    sticker_id = st.session_state.get("new_sticker")
    if sticker_id:
        item = next((s for s in STICKERS if s["id"] == sticker_id), None)
        if item:
            st.toast(f"새 스티커 획득! {item['emoji']} {item['name']}", icon="✨")
        st.session_state.new_sticker = None


# ---------- 공통 네비게이션 ----------
def nav_header(active):
    st.markdown(
        '<div class="brand"><span class="brand-icon">🎬</span>'
        'PASTEL MOVIE <span style="color:#aaa0bd;font-weight:500;"> / CINEMA, CURATED</span></div>',
        unsafe_allow_html=True,
    )
    st.write("")
    cols = st.columns([1, 1, 1, 4])

    items = [
        ("home", "⌂  Discover"),
        ("quiz", "✦  Rank Quiz"),
        ("stickers", "✧  My Collection"),
    ]

    for col, (page, label) in zip(cols[:3], items):
        with col:
            if st.button(
                label,
                key=f"nav_{active}_{page}",
                use_container_width=True,
                type="primary" if active == page else "secondary",
            ):
                st.session_state.page = page
                if page == "quiz":
                    st.session_state.quiz_movie = None
                    st.session_state.quiz_answered = False
                    st.session_state.quiz_feedback = None
                st.rerun()

    with cols[3]:
        p = st.session_state.profile
        st.markdown(
            f'<div style="text-align:right;padding:10px;color:#898198;font-size:.78rem;">'
            f'MY COLLECTION ✦ {len(p["stickers"])} / {len(STICKERS)} STICKERS</div>',
            unsafe_allow_html=True,
        )
    st.markdown("<hr>", unsafe_allow_html=True)


def footer():
    st.markdown(
        "<hr><div style='text-align:center;color:#a39ab1;font-size:.73rem;padding:10px;'>"
        "PASTEL MOVIE · CINEMA, CURATED<br>"
        "Daily box office data powered by KOBIS · 영화진흥위원회</div>",
        unsafe_allow_html=True,
    )


# ---------- 홈 ----------
def show_home():
    nav_header("home")

    st.markdown(
        '<div class="hero"><div class="eyebrow">YOUR DAILY CINEMA GUIDE</div>'
        '<h1>Every day is a<br>movie discovery.</h1>'
        '<p>오늘의 박스오피스를 발견하고, 순위를 추리하고, 나만의 시네마 컬렉션을 완성해 보세요.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    date_col, refresh_col, _ = st.columns([1.5, 1, 4])
    with date_col:
        selected_date = st.date_input(
            "BOX OFFICE DATE",
            value=st.session_state.selected_date,
            min_value=MIN_DATE,
            max_value=MAX_DATE,
            key="home_date",
        )
        st.session_state.selected_date = selected_date

    with refresh_col:
        st.write("")
        st.write("")
        refresh = st.button("↻ Refresh data", use_container_width=True)

    df, error = load_date_data(selected_date, force=refresh)

    if error:
        st.error(error)
        st.info("Streamlit Cloud → Settings → Secrets에서 KOBIS_KEY를 확인해 주세요.")
        return

    if df is None or df.empty:
        st.warning("📅 그날은 아직 집계 전입니다. 다른 날짜를 선택해 주세요.")
        return

    for movie in df.to_dict("records"):
        add_movie(movie)

    p = st.session_state.profile
    first = df.iloc[0].to_dict()

    st.markdown(
        '<div class="section"><h2>Today’s spotlight</h2>'
        '<span class="muted">DAILY BOX OFFICE · KOBIS</span></div>',
        unsafe_allow_html=True,
    )

    poster_col, feature_col = st.columns([1, 2.1], gap="large")

    with poster_col:
        show_poster(first.get("movieNm", ""))

    with feature_col:
        st.markdown(
            f'<div class="feature"><span class="tag">✦ NO. 01 · TODAY’S LEADER</span>'
            f'<h1 style="font-size:clamp(1.8rem,3.3vw,2.8rem);margin-top:20px;">'
            f'{safe(first.get("movieNm", ""))}</h1>'
            f'<p style="color:#756b87;">개봉일 {safe(first.get("openDt") or "정보 없음")}'
            f' · 누적 관객 {fmt(first.get("audiAcc"))}명</p><hr>'
            f'<div class="eyebrow">A LITTLE MOVIE MAGIC</div>'
            f'<p style="line-height:1.8;color:#756b87;">오늘의 극장가를 이끄는 영화예요. '
            f'순위를 살펴보고 퀴즈에도 도전해 보세요.</p></div>',
            unsafe_allow_html=True,
        )

        m1, m2, m3 = st.columns(3)
        m1.metric("당일 관객", f"{fmt(first.get('audiCnt'))}명")
        m2.metric("스크린 수", f"{fmt(first.get('scrnCnt'))}개")
        m3.metric("상영 횟수", f"{fmt(first.get('showCnt'))}회")

    st.markdown(
        '<div class="section"><h2>Explore the cinema</h2>'
        '<span class="muted">PLAY · COLLECT · DISCOVER</span></div>',
        unsafe_allow_html=True,
    )

    a, b, c = st.columns(3, gap="medium")
    with a:
        st.markdown(
            '<div class="surface"><div class="eyebrow">01 / CHALLENGE</div>'
            '<h3>Rank Quiz</h3><p class="muted">영화 제목만 보고 오늘의 순위를 추리해요.</p></div>',
            unsafe_allow_html=True,
        )
        if st.button("퀴즈 시작하기 →", key="home_quiz", use_container_width=True):
            st.session_state.page = "quiz"
            st.session_state.quiz_movie = None
            st.session_state.quiz_answered = False
            st.session_state.quiz_feedback = None
            st.rerun()

    with b:
        st.markdown(
            '<div class="surface"><div class="eyebrow">02 / COLLECTION</div>'
            '<h3>Sticker Archive</h3><p class="muted">미션을 달성하고 나만의 스티커를 모아요.</p></div>',
            unsafe_allow_html=True,
        )
        if st.button("도감 열기 →", key="home_stickers", use_container_width=True):
            st.session_state.page = "stickers"
            st.rerun()

    with c:
        st.markdown(
            '<div class="surface"><div class="eyebrow">03 / SURPRISE</div>'
            '<h3>Lucky Pick</h3><p class="muted">오늘의 박스오피스에서 랜덤 영화를 발견해요.</p></div>',
            unsafe_allow_html=True,
        )
        if st.button("랜덤 영화 뽑기 ✦", key="home_random", use_container_width=True):
            st.session_state.random_movie = random.choice(df.to_dict("records"))
            p["explore_count"] += 1
            persist()
            check_achievements()
            st.rerun()

    if st.session_state.random_movie:
        movie = st.session_state.random_movie
        st.markdown(
            '<div class="section"><h2>Your lucky pick</h2>'
            '<span class="muted">A RANDOM DISCOVERY</span></div>',
            unsafe_allow_html=True,
        )
        pc, info = st.columns([1, 3])
        with pc:
            show_poster(movie.get("movieNm", ""))
        with info:
            st.markdown(
                f'<div class="feature"><span class="tag">RANK {safe(movie.get("rank", "?"))}</span>'
                f'<h2 style="margin-top:18px;">{safe(movie.get("movieNm", ""))}</h2>'
                f'<p style="color:#756b87;">당일 관객 {fmt(movie.get("audiCnt"))}명'
                f' · 누적 관객 {fmt(movie.get("audiAcc"))}명</p></div>',
                unsafe_allow_html=True,
            )
            if st.button("다른 영화 발견하기 ↻", key="reroll"):
                st.session_state.random_movie = random.choice(df.to_dict("records"))
                p["explore_count"] += 1
                persist()
                check_achievements()
                st.rerun()

    st.markdown(
        '<div class="section"><h2>Top 5 at the box office</h2>'
        '<span class="muted">AUDIENCE · DAILY</span></div>',
        unsafe_allow_html=True,
    )

    top5 = df.head(5).copy()
    chart = px.bar(
        top5,
        x="audiCnt",
        y="movieNm",
        orientation="h",
        text="audiCnt",
        labels={"audiCnt": "당일 관객 수(명)", "movieNm": "영화"},
        color="rank",
        color_continuous_scale=["#b9a5f5", "#f2bfd7", "#b9e3f5"],
    )
    chart.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside",
        cliponaxis=False,
        marker_line_width=0,
    )
    chart.update_layout(
        yaxis={"categoryorder": "total ascending"},
        xaxis={"tickformat": ",", "gridcolor": "#eee8f4"},
        plot_bgcolor="rgba(255,255,255,0)",
        paper_bgcolor="rgba(255,255,255,0)",
        coloraxis_showscale=False,
        margin=dict(l=10, r=45, t=10, b=10),
        font=dict(color="#6f687d"),
        height=320,
    )
    st.plotly_chart(chart, use_container_width=True)

    st.markdown(
        '<div class="section"><h2>Find a film</h2>'
        '<span class="muted">SEARCH TODAY’S LINEUP</span></div>',
        unsafe_allow_html=True,
    )
    query = st.text_input("영화 제목 검색", placeholder="검색할 영화 제목을 입력하세요")

    if query.strip():
        results = df[df["movieNm"].astype(str).str.contains(query.strip(), case=False, na=False)]
        if results.empty:
            st.info("검색 결과가 없어요. 다른 제목으로 검색해 보세요.")
        else:
            for movie in results.to_dict("records"):
                left, right = st.columns([1, 4])
                with left:
                    show_poster(movie.get("movieNm", ""))
                with right:
                    st.markdown(
                        f'<div class="surface"><span class="tag">RANK {safe(movie.get("rank"))}</span>'
                        f'<h3>{safe(movie.get("movieNm", ""))}</h3>'
                        f'<p class="muted">당일 관객 {fmt(movie.get("audiCnt"))}명'
                        f' · 누적 관객 {fmt(movie.get("audiAcc"))}명'
                        f' · 개봉일 {safe(movie.get("openDt") or "정보 없음")}</p></div>',
                        unsafe_allow_html=True,
                    )
                    add_movie(movie)

    st.markdown(
        '<div class="section"><h2>Daily ranking</h2>'
        '<span class="muted">OFFICIAL DAILY DATA</span></div>',
        unsafe_allow_html=True,
    )

    table = df.copy()
    table["변동"] = table["rankInten"].apply(
        lambda x: f"🔺 +{x}" if x > 0 else (f"🔻 {x}" if x < 0 else "—")
    )
    table["영화"] = table.apply(
        lambda r: ("🏆 " if int(r.get("audiAcc", 0)) >= 1_000_000 else "")
        + str(r.get("movieNm", "")),
        axis=1,
    )
    table["당일 관객"] = table["audiCnt"].map(lambda x: f"{x:,}명")
    table["누적 관객"] = table["audiAcc"].map(lambda x: f"{x:,}명")
    table = table[["rank", "변동", "영화", "당일 관객", "누적 관객", "openDt"]]
    table = table.rename(columns={"rank": "순위", "openDt": "개봉일"})
    st.dataframe(table, use_container_width=True, hide_index=True, height=420)

    st.markdown(
        '<div class="surface"><div class="eyebrow">YOUR COLLECTION STATUS</div>'
        '<h3>나의 시네마 여정</h3>',
        unsafe_allow_html=True,
    )
    st.progress(len(p["stickers"]) / len(STICKERS))
    st.caption(
        f"스티커 {len(p['stickers'])}/{len(STICKERS)}개 · "
        f"발견한 영화 {len(p['found_movies'])}편 · 퀴즈 정답 {p['quiz_score']}회"
    )
    st.markdown("</div>", unsafe_allow_html=True)
    show_toast()


# ---------- 별도 순위 퀴즈 페이지 ----------
def show_quiz():
    nav_header("quiz")
    st.markdown(
        '<div class="hero"><div class="eyebrow">DAILY CHALLENGE</div>'
        '<h1>Can you guess<br>the rank?</h1>'
        '<p>영화 제목만 보고 일일 박스오피스 순위를 추리해 보세요. '
        '정답을 제출하기 전까지 순위표는 공개되지 않아요.</p></div>',
        unsafe_allow_html=True,
    )

    p = st.session_state.profile
    a, b, c = st.columns(3)
    a.metric("누적 정답", f"{p['quiz_score']}회")
    b.metric(
        "정답률",
        f"{p['quiz_score'] / p['quiz_total'] * 100:.0f}%"
        if p["quiz_total"] else "—",
    )
    c.metric("최고 연속 정답", f"{p['best_streak']}회")

    df = st.session_state.df
    if st.session_state.load_error:
        st.error(st.session_state.load_error)
        return
    if df is None or df.empty:
        st.warning("퀴즈 데이터가 없어요. 홈에서 집계된 날짜를 선택해 주세요.")
        if st.button("홈으로 돌아가기"):
            st.session_state.page = "home"
            st.rerun()
        return
    if len(df) < 2:
        st.info("퀴즈에 사용할 영화가 부족해요.")
        return

    if st.session_state.quiz_movie is None:
        st.markdown(
            '<div class="surface" style="text-align:center;padding:38px;">'
            '<div style="font-size:48px;">🎭</div><div class="eyebrow">MYSTERY SCREENING</div>'
            '<h2>오늘의 미스터리 영화</h2>'
            '<p class="muted">새 퀴즈를 시작하면 영화 한 편이 무작위로 선택돼요.</p></div>',
            unsafe_allow_html=True,
        )
        if st.button("새 퀴즈 시작하기 ✦", use_container_width=True):
            st.session_state.quiz_movie = random.choice(df.to_dict("records"))
            st.session_state.quiz_answered = False
            st.session_state.quiz_feedback = None
            st.session_state.quiz_balloons_shown = False
            st.rerun()
        return

    movie = st.session_state.quiz_movie
    rank = int(movie.get("rank", 0))
    poster_col, info_col = st.columns([1, 2.4], gap="large")

    with poster_col:
        show_poster(movie.get("movieNm", ""))

    with info_col:
        st.markdown(
            f'<div class="feature"><div class="eyebrow">MYSTERY FILM</div>'
            f'<h1 style="font-size:2.2rem;margin-top:16px;">{safe(movie.get("movieNm", ""))}</h1>'
            f'<p style="color:#756b87;">개봉일 {safe(movie.get("openDt") or "정보 없음")}</p>'
            f'<hr><p>이 영화의 일일 박스오피스 순위는 몇 위였을까요?</p></div>',
            unsafe_allow_html=True,
        )

        if not st.session_state.quiz_answered:
            guess = st.selectbox(
                "나의 추리",
                list(range(1, len(df) + 1)),
                format_func=lambda n: f"{n}위",
                key=f"guess_{st.session_state.loaded_date}_{movie.get('movieCd', movie.get('movieNm'))}",
            )

            if st.button("최종 답안 제출하기", use_container_width=True):
                correct = guess == rank
                st.session_state.quiz_answered = True
                st.session_state.quiz_feedback = {"correct": correct, "rank": rank}

                p["quiz_total"] += 1
                if correct:
                    p["quiz_score"] += 1
                    p["quiz_streak"] += 1
                    p["best_streak"] = max(p["best_streak"], p["quiz_streak"])
                else:
                    p["quiz_streak"] = 0

                persist()
                check_achievements()
                st.rerun()

        else:
            feedback = st.session_state.quiz_feedback or {}
            if feedback.get("correct"):
                st.success(f"정답이에요! 이 영화는 {rank}위였어요. 🎉")
                if not st.session_state.quiz_balloons_shown:
                    st.balloons()
                    st.session_state.quiz_balloons_shown = True
            else:
                st.info(f"아쉬워요! 실제 순위는 {rank}위예요. 다음 추리에 도전해 봐요.")

            st.metric("당일 관객 수", f"{fmt(movie.get('audiCnt'))}명")

            if st.button("다음 영화로 도전하기 →", use_container_width=True):
                st.session_state.quiz_movie = random.choice(df.to_dict("records"))
                st.session_state.quiz_answered = False
                st.session_state.quiz_feedback = None
                st.session_state.quiz_balloons_shown = False
                st.rerun()

    st.caption("TIP · 영화의 인지도와 개봉일을 떠올려 순위를 추리해 보세요.")
    show_toast()


# ---------- 스티커 도감 페이지 ----------
def show_stickers():
    nav_header("stickers")
    check_achievements()
    p = st.session_state.profile
    unlocked = len(p["stickers"])

    st.markdown(
        '<div class="hero"><div class="eyebrow">YOUR PERSONAL FILM ARCHIVE</div>'
        '<h1>Every sticker tells<br>a movie story.</h1>'
        '<p>영화를 발견하고 퀴즈에 도전해 컬렉션을 채워 보세요. '
        '잠긴 스티커에는 달성해야 할 미션이 적혀 있어요.</p></div>',
        unsafe_allow_html=True,
    )

    st.markdown(f"### My sticker archive · {unlocked}/{len(STICKERS)}")
    st.progress(unlocked / len(STICKERS))

    a, b, c = st.columns(3)
    a.metric("발견한 영화", f"{len(p['found_movies'])}편")
    b.metric("퀴즈 정답", f"{p['quiz_score']}회")
    c.metric("랜덤 탐험", f"{p['explore_count']}회")

    st.markdown(
        '<div class="section"><h2>Sticker shelf</h2>'
        '<span class="muted">LOCKED & UNLOCKED</span></div>',
        unsafe_allow_html=True,
    )

    cols = st.columns(4)
    for i, item in enumerate(STICKERS):
        earned = item["id"] in p["stickers"]
        with cols[i % 4]:
            emoji = item["emoji"] if earned else "🔒"
            name = item["name"] if earned else "Hidden Sticker"
            detail = "획득 완료 · " + item["name"] if earned else "미션 · " + item["mission"]
            st.markdown(
                f'<div class="surface" style="min-height:185px;text-align:center;margin-bottom:13px;">'
                f'<div style="font-size:35px;margin:7px 0;">{emoji}</div>'
                f'<div class="eyebrow">{"UNLOCKED" if earned else "LOCKED"}</div>'
                f'<div style="font-weight:800;margin:8px 0;">{safe(name)}</div>'
                f'<div class="muted">{safe(detail)}</div></div>',
                unsafe_allow_html=True,
            )

    remaining = [x for x in STICKERS if x["id"] not in p["stickers"]]
    st.markdown(
        '<div class="section"><h2>Next mission</h2>'
        '<span class="muted">ONE STEP CLOSER</span></div>',
        unsafe_allow_html=True,
    )

    if remaining:
        item = remaining[0]
        st.markdown(
            f'<div class="feature"><span class="tag">NEXT ACHIEVEMENT</span>'
            f'<h2 style="margin-top:16px;">{item["emoji"]} {safe(item["name"])}</h2>'
            f'<p style="color:#756b87;">미션 · {safe(item["mission"])}</p></div>',
            unsafe_allow_html=True,
        )
    else:
        st.success("모든 스티커를 모았어요! 당신은 시네마 마스터예요. ✨")

    st.write("")
    if supabase_ready():
        st.caption("Supabase 영구 저장 설정이 감지되었어요.")
    else:
        st.caption(
            "현재 기록은 세션에 저장돼요. 영구 저장을 원하면 Supabase 설정을 완료하세요."
        )
    show_toast()


# ---------- 앱 실행 ----------
if st.session_state.loaded_date is None:
    load_date_data(st.session_state.selected_date)

if st.session_state.page == "quiz":
    show_quiz()
elif st.session_state.page == "stickers":
    show_stickers()
else:
    show_home()

footer()
