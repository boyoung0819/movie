
import random
import datetime as dt
from zoneinfo import ZoneInfo

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

st.set_page_config(
    page_title="Pastel Movie — 오늘의 영화 발견",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

KST = ZoneInfo("Asia/Seoul")
YESTERDAY = dt.datetime.now(KST).date() - dt.timedelta(days=1)
API_URL = (
    "https://www.kobis.or.kr/kobisopenapi/webservice/rest/"
    "boxoffice/searchDailyBoxOfficeList.json"
)

STICKERS = [
    {"id": "first_movie", "emoji": "🎬", "name": "첫 장면", "desc": "영화 한 편 발견", "goal": "영화 1편 발견"},
    {"id": "collector_3", "emoji": "🍿", "name": "팝콘 수집가", "desc": "서로 다른 영화 3편 발견", "goal": "영화 3편 발견"},
    {"id": "collector_5", "emoji": "🎟️", "name": "티켓 컬렉터", "desc": "서로 다른 영화 5편 발견", "goal": "영화 5편 발견"},
    {"id": "collector_10", "emoji": "💎", "name": "시네마 보석", "desc": "서로 다른 영화 10편 발견", "goal": "영화 10편 발견"},
    {"id": "quiz_first", "emoji": "🔍", "name": "순위 탐정", "desc": "퀴즈 첫 정답", "goal": "퀴즈 정답 1회"},
    {"id": "quiz_5", "emoji": "🏆", "name": "퀴즈 챔피언", "desc": "퀴즈 정답 5회", "goal": "퀴즈 정답 5회"},
    {"id": "streak_3", "emoji": "🔥", "name": "연속 정답왕", "desc": "3문제 연속 정답", "goal": "3연속 정답"},
    {"id": "explorer_5", "emoji": "🧭", "name": "영화 탐험가", "desc": "랜덤 영화 5회 뽑기", "goal": "랜덤 탐험 5회"},
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
@import url('https://fonts.googleapis.com/css2?family=Jua&family=Noto+Sans+KR:wght@400;500;600;700&display=swap');
html, body, [class*="css"] {font-family:'Noto Sans KR',sans-serif;}
.stApp {background:linear-gradient(150deg,#fbf8ff,#fff9fc 48%,#f4faff);color:#342d50;}
#MainMenu,footer {visibility:hidden;}
header[data-testid="stHeader"] {background:transparent;}
.block-container {max-width:1240px;padding-top:1.25rem;padding-bottom:3rem;}
h1,h2,h3 {font-family:'Jua','Noto Sans KR',sans-serif;color:#342d50;}
.brand {font-family:'Jua',sans-serif;font-size:1.5rem;color:#514675;}
.hero {border:1px solid white;border-radius:26px;padding:28px;background:linear-gradient(115deg,#e9e0ff,#fce7f2 52%,#e2f3ff);box-shadow:0 14px 38px #6c5b8e12;margin:12px 0 22px;}
.hero p {color:#6e638b;}
.surface {background:#ffffffdf;border:1px solid #eee7f8;border-radius:22px;padding:20px;box-shadow:0 8px 25px #75658c0b;}
.movie-feature {background:linear-gradient(125deg,#f0e9ff,#fff0f6 58%,#e9f7ff);border-radius:26px;padding:26px;border:1px solid white;box-shadow:0 12px 32px #75658c12;}
.rank-pill {display:inline-block;border-radius:999px;padding:6px 12px;background:#ffffffc9;color:#7865a9;font-size:.78rem;font-weight:700;}
.stat {background:white;border:1px solid #eee7f8;border-radius:18px;padding:15px 17px;}
.stButton>button {border:1px solid #e4d9f7;border-radius:13px;color:#5e5083;background:linear-gradient(105deg,#eee7ff,#ffeaf3);font-weight:600;min-height:43px;transition:transform .15s ease;}
.stButton>button:hover {border-color:#cbb9f4;color:#493b70;transform:translateY(-1px);}
.stTextInput input,.stSelectbox div[data-baseweb="select"]>div,.stDateInput input {border-radius:12px!important;border-color:#e8e0f4!important;}
div[data-testid="stMetric"] {background:#ffffffc9;border:1px solid #eee7f8;border-radius:17px;padding:13px 16px;}
.stProgress>div>div>div>div {background:linear-gradient(90deg,#b7a2ff,#f5b8d2,#a9ddff);}
.stPlotlyChart {background:#ffffffad;border:1px solid #eee7f8;border-radius:20px;padding:8px;}
</style>
""", unsafe_allow_html=True)

for key, value in {
    "page": "home",
    "loaded_date": None,
    "current_df": None,
    "current_error": None,
    "profile": DEFAULT_PROFILE.copy(),
    "quiz_movie": None,
    "quiz_answered": False,
    "quiz_feedback": None,
    "random_movie": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = value


def supabase_configured():
    return all(st.secrets.get(k, "") for k in (
        "SUPABASE_URL", "SUPABASE_KEY", "PROFILE_ID"
    ))


def load_profile():
    if not supabase_configured():
        return DEFAULT_PROFILE.copy()
    base = str(st.secrets["SUPABASE_URL"]).rstrip("/")
    key = st.secrets["SUPABASE_KEY"]
    profile_id = str(st.secrets["PROFILE_ID"])
    table = st.secrets.get("SUPABASE_TABLE", "movie_profiles")
    try:
        r = requests.get(
            f"{base}/rest/v1/{table}",
            params={"profile_id": f"eq.{profile_id}", "select": "profile_id,data"},
            headers={"apikey": key, "Authorization": f"Bearer {key}"},
            timeout=10,
        )
        r.raise_for_status()
        rows = r.json()
        if rows:
            profile = DEFAULT_PROFILE.copy()
            profile.update(rows[0].get("data") or {})
            return profile
    except (requests.RequestException, ValueError, TypeError):
        pass
    return DEFAULT_PROFILE.copy()


def save_profile():
    if not supabase_configured():
        return
    base = str(st.secrets["SUPABASE_URL"]).rstrip("/")
    key = st.secrets["SUPABASE_KEY"]
    table = st.secrets.get("SUPABASE_TABLE", "movie_profiles")
    try:
        requests.post(
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
        ).raise_for_status()
    except requests.RequestException:
        st.warning("기록을 저장하지 못했어요. Supabase 설정을 확인해 주세요.")


if "profile_loaded" not in st.session_state:
    st.session_state.profile = load_profile()
    st.session_state.profile_loaded = True


def persist():
    save_profile()


def unlock(sticker_id):
    p = st.session_state.profile
    if sticker_id not in p["stickers"]:
        p["stickers"].append(sticker_id)
        persist()
        st.session_state.new_sticker = sticker_id


def check_achievements():
    p = st.session_state.profile
    checks = [
        (len(p["found_movies"]) >= 1, "first_movie"),
        (len(p["found_movies"]) >= 3, "collector_3"),
        (len(p["found_movies"]) >= 5, "collector_5"),
        (len(p["found_movies"]) >= 10, "collector_10"),
        (p["quiz_score"] >= 1, "quiz_first"),
        (p["quiz_score"] >= 5, "quiz_5"),
        (p["best_streak"] >= 3, "streak_3"),
        (p["explore_count"] >= 5, "explorer_5"),
    ]
    for condition, sticker_id in checks:
        if condition:
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
        return None, "KOBIS 서버 응답 시간이 초과됐습니다."
    except requests.RequestException:
        return None, "네트워크 연결을 확인해 주세요."
    except (ValueError, TypeError):
        return None, "KOBIS에서 읽을 수 없는 응답을 받았습니다."


def load_date_data(date_string, force=False):
    if force or st.session_state.loaded_date != date_string:
        df, error = fetch_boxoffice(date_string)
        st.session_state.loaded_date = date_string
        st.session_state.current_df = df
        st.session_state.current_error = error
        st.session_state.quiz_movie = None
        st.session_state.quiz_answered = False
        st.session_state.quiz_feedback = None
    return st.session_state.current_df, st.session_state.current_error


def format_num(value):
    try:
        return f"{int(value):,}"
    except (ValueError, TypeError):
        return "0"


def brand_header(active):
    st.markdown('<div class="brand">🎬 PASTEL MOVIE</div><p>Find your next favorite scene.</p>', unsafe_allow_html=True)
    nav = st.columns([1, 1, 1, 4])
    for col, page, label in zip(nav[:3], ["home", "quiz", "stickers"], ["🏠 홈", "🧩 순위 퀴즈", "🌟 스티커 도감"]):
        with col:
            if st.button(label, key=f"nav_{active}_{page}", use_container_width=True):
                st.session_state.page = page
                if page == "quiz":
                    st.session_state.quiz_movie = None
                    st.session_state.quiz_answered = False
                    st.session_state.quiz_feedback = None
                st.rerun()
    with nav[3]:
        st.markdown('<div style="text-align:right;padding-top:10px;color:#8c83a1;font-size:.82rem;">DAILY BOX OFFICE · MOVIE DISCOVERY</div>', unsafe_allow_html=True)
    st.markdown("<hr style='border:none;border-top:1px solid #eee6f7;margin-bottom:18px;'>", unsafe_allow_html=True)


def show_new_sticker():
    sticker_id = st.session_state.get("new_sticker")
    if sticker_id:
        sticker = next((s for s in STICKERS if s["id"] == sticker_id), None)
        if sticker:
            st.toast(f"새 스티커 획득! {sticker['emoji']} {sticker['name']}", icon="🌟")
        st.session_state.new_sticker = None


def render_stickers():
    p = st.session_state.profile
    cols = st.columns(4)
    for i, sticker in enumerate(STICKERS):
        earned = sticker["id"] in p["stickers"]
        with cols[i % 4]:
            icon = sticker["emoji"] if earned else "🔒"
            name = sticker["name"] if earned else "미공개 스티커"
            desc = sticker["desc"] if earned else f"미션: {sticker['goal']}"
            st.markdown(
                f'<div class="surface" style="text-align:center;min-height:170px;margin-bottom:12px;">'
                f'<div style="font-size:36px;">{icon}</div><h3>{name}</h3>'
                f'<p style="font-size:.8rem;">{desc}</p>'
                f'<span class="rank-pill">{"✦ 획득 완료" if earned else "○ 도전 가능"}</span></div>',
                unsafe_allow_html=True,
            )


def show_quiz():
    brand_header("quiz")
    st.markdown("""
    <div class="hero"><div class="rank-pill">MYSTERY RANK · DAILY CHALLENGE</div>
    <h1>두뇌 풀가동! 영화 순위 퀴즈</h1>
    <p>영화 제목만 보고 그날의 순위를 추리해 보세요. 이 화면에는 순위표가 표시되지 않아요.</p></div>
    """, unsafe_allow_html=True)

    p = st.session_state.profile
    a, b, c = st.columns(3)
    a.metric("누적 정답", f"{p['quiz_score']}개")
    b.metric("정답률", f"{p['quiz_score'] / p['quiz_total'] * 100:.0f}%" if p["quiz_total"] else "—")
    c.metric("최고 연속 정답", f"{p['best_streak']}문제")

    df = st.session_state.current_df
    error = st.session_state.current_error
    date_string = st.session_state.loaded_date
    if error:
        st.error(error)
        return
    if df is None or df.empty:
        st.warning("📅 그날은 아직 집계 전입니다. 홈에서 다른 날짜를 선택해 주세요.")
        if st.button("홈으로 돌아가기"):
            st.session_state.page = "home"
            st.rerun()
        return
    if len(df) < 2:
        st.info("퀴즈에 사용할 영화가 부족해요.")
        return

    if st.session_state.quiz_movie is None:
        st.markdown('<div class="surface" style="text-align:center;"><div style="font-size:50px;">🕵️</div><h2>오늘의 미스터리 영화</h2><p>새 퀴즈를 시작하면 영화 한 편이 무작위로 선택돼요.</p></div>', unsafe_allow_html=True)
        if st.button("✨ 새 퀴즈 시작하기", use_container_width=True):
            st.session_state.quiz_movie = random.choice(df.to_dict("records"))
            st.session_state.quiz_answered = False
            st.session_state.quiz_feedback = None
            st.rerun()
        return

    movie = st.session_state.quiz_movie
    rank = int(movie.get("rank", 0))
    st.markdown(
        f'<div class="movie-feature"><span class="rank-pill">🔎 MYSTERY RANK</span>'
        f'<h1 style="margin-top:18px;">{movie.get("movieNm", "영화 제목")}</h1>'
        f'<p>{date_string[:4]}년 {date_string[4:6]}월 {date_string[6:]}일의 순위를 맞혀 보세요.</p></div>',
        unsafe_allow_html=True,
    )

    if not st.session_state.quiz_answered:
        guess = st.selectbox("몇 위였을까요?", list(range(1, len(df) + 1)), format_func=lambda x: f"{x}위", key=f"guess_{date_string}_{movie.get('movieCd', movie.get('movieNm'))}")
        if st.button("정답 확인하기 ✨", use_container_width=True):
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
            st.success(f"🎉 정답이에요! {rank}위가 맞아요.")
            if not st.session_state.get("quiz_balloons_shown", False):
                st.balloons()
                st.session_state.quiz_balloons_shown = True
        else:
            st.info(f"아쉽지만 정답은 {rank}위예요. 다음 문제에 도전해 봐요.")
        a, b = st.columns(2)
        a.metric("실제 순위", f"{rank}위")
        b.metric("당일 관객 수", f"{format_num(movie.get('audiCnt'))}명")
        if st.button("🎲 다음 문제", use_container_width=True):
            st.session_state.quiz_movie = random.choice(df.to_dict("records"))
            st.session_state.quiz_answered = False
            st.session_state.quiz_feedback = None
            st.session_state.quiz_balloons_shown = False
            st.rerun()
    show_new_sticker()
    st.caption("🔐 퀴즈가 끝날 때까지 순위표와 TOP 5 그래프는 공개되지 않습니다.")


def show_stickers():
    brand_header("stickers")
    check_achievements()
    p = st.session_state.profile
    unlocked = len(p["stickers"])
    st.markdown("""
    <div class="hero"><div class="rank-pill">MY COLLECTION · ACHIEVEMENTS</div>
    <h1>나의 영화 스티커 도감</h1><p>영화를 탐험하고 퀴즈를 풀며 나만의 컬렉션을 완성하세요.</p></div>
    """, unsafe_allow_html=True)
    st.markdown(f"### ✨ 스티커 {unlocked}/{len(STICKERS)}개")
    st.progress(unlocked / len(STICKERS))
    a, b = st.columns(2)
    a.metric("발견한 영화", f"{len(p['found_movies'])}편")
    b.metric("퀴즈 정답", f"{p['quiz_score']}개")
    st.markdown("### 🏅 My sticker shelf")
    render_stickers()

    remaining = [s for s in STICKERS if s["id"] not in p["stickers"]]
    st.markdown("### 🎯 다음 도전 미션")
    if remaining:
        s = remaining[0]
        st.markdown(f'<div class="surface"><div style="font-size:30px;">{s["emoji"]}</div><h3>{s["name"]}</h3><p>{s["desc"]}</p><span class="rank-pill">미션 · {s["goal"]}</span></div>', unsafe_allow_html=True)
    else:
        st.success("모든 스티커를 모았어요! 시네마 마스터예요. 🌟")

    a, b, c = st.columns(3)
    a.metric("랜덤 영화 탐험", f"{p['explore_count']}회")
    b.metric("현재 연속 정답", f"{p['quiz_streak']}문제")
    c.metric("최고 연속 정답", f"{p['best_streak']}문제")
    show_new_sticker()


def show_home():
    brand_header("home")
    st.markdown("""
    <div class="hero"><div class="rank-pill">YOUR DAILY CINEMA GUIDE</div>
    <h1>오늘, 어떤 영화를 발견할까요? 🍿</h1>
    <p>매일의 박스오피스를 살펴보고 퀴즈를 풀고 나만의 영화 컬렉션을 모아 보세요.</p></div>
    """, unsafe_allow_html=True)

    dcol, rcol, _ = st.columns([2, 1, 4])
    with dcol:
        selected_date = st.date_input(
            "박스오피스 날짜",
            value=YESTERDAY,
            min_value=dt.date(2004, 1, 1),
            max_value=YESTERDAY,
            key="boxoffice_date",
        )
    with rcol:
        st.markdown("<div style='height:27px'></div>", unsafe_allow_html=True)
        refresh = st.button("↻ 새로고침", use_container_width=True)
    date_string = selected_date.strftime("%Y%m%d")
    df, error = load_date_data(date_string, force=refresh)

    if error:
        st.error(f"데이터를 불러오지 못했어요: {error}")
        st.info("Streamlit Cloud의 Settings → Secrets에서 KOBIS_KEY를 확인해 주세요.")
        return
    if df is None or df.empty:
        st.warning("📅 그날은 아직 집계 전입니다.")
        return

    for movie in df.to_dict("records"):
        add_movie(movie)
    check_achievements()
    p = st.session_state.profile

    q1, q2, q3 = st.columns(3)
    with q1:
        st.markdown('<div class="surface"><div style="font-size:28px;">🧩</div><h3>순위 퀴즈</h3><p>영화 제목만 보고 순위를 추리해요.</p></div>', unsafe_allow_html=True)
        if st.button("퀴즈 도전하기 →", key="home_quiz", use_container_width=True):
            st.session_state.page = "quiz"
            st.session_state.quiz_movie = None
            st.session_state.quiz_answered = False
            st.session_state.quiz_feedback = None
            st.rerun()
    with q2:
        st.markdown('<div class="surface"><div style="font-size:28px;">🌟</div><h3>스티커 도감</h3><p>미션을 달성하고 스티커를 모아요.</p></div>', unsafe_allow_html=True)
        if st.button("도감 열기 →", key="home_stickers", use_container_width=True):
            st.session_state.page = "stickers"
            st.rerun()
    with q3:
        st.markdown('<div class="surface"><div style="font-size:28px;">🎲</div><h3>랜덤 영화 발견</h3><p>오늘의 영화 중 한 편을 무작위로 골라요.</p></div>', unsafe_allow_html=True)
        if st.button("랜덤 뽑기 →", key="home_random", use_container_width=True):
            st.session_state.random_movie = random.choice(df.to_dict("records"))
            p["explore_count"] += 1
            persist()
            check_achievements()
            st.rerun()

    if st.session_state.random_movie:
        movie = st.session_state.random_movie
        st.markdown("### 🎲 오늘 발견한 랜덤 영화")
        st.markdown(f'<div class="surface"><span class="rank-pill">RANK {movie.get("rank", "?")}</span><h2>{movie.get("movieNm", "")}</h2><p>당일 관객 {format_num(movie.get("audiCnt"))}명 · 누적 관객 {format_num(movie.get("audiAcc"))}명</p></div>', unsafe_allow_html=True)
        if st.button("다른 영화 뽑기", key="reroll_movie"):
            st.session_state.random_movie = random.choice(df.to_dict("records"))
            p["explore_count"] += 1
            persist()
            check_achievements()
            st.rerun()

    first = df.iloc[0].to_dict()
    st.markdown("## 🏆 오늘의 박스오피스")
    left, right = st.columns([1.45, 1])
    with left:
        st.markdown(f'<div class="movie-feature" style="min-height:285px;"><span class="rank-pill">TODAY’S #1 · DAILY BOX OFFICE</span><div style="font-size:42px;margin-top:22px;">🎞️</div><h1>{first.get("movieNm", "")}</h1><p>개봉일 {first.get("openDt") or "정보 없음"}</p><p>누적 관객 수 {format_num(first.get("audiAcc"))}명</p></div>', unsafe_allow_html=True)
    with right:
        st.markdown("### 📊 오늘의 기록")
        for label, value in [
            ("1위 당일 관객 수", f"{format_num(first.get('audiCnt'))}명"),
            ("상영 스크린 수", f"{format_num(first.get('scrnCnt'))}개"),
            ("상영 횟수", f"{format_num(first.get('showCnt'))}회"),
        ]:
            st.markdown(f'<div class="stat"><span style="color:#89819b;font-size:.8rem;">{label}</span><div style="font-size:1.3rem;font-weight:700;">{value}</div></div><br>', unsafe_allow_html=True)

    st.markdown("## 🔎 영화 탐색")
    search = st.text_input("영화 제목 검색", placeholder="영화 제목을 입력하세요", key="movie_search")
    if search.strip():
        results = df[df["movieNm"].astype(str).str.contains(search.strip(), case=False, na=False)]
        if results.empty:
            st.info("검색 결과가 없어요. 다른 제목으로 검색해 보세요.")
        else:
            for row in results.to_dict("records"):
                st.markdown(f'<div class="surface"><span class="rank-pill">{row.get("rank")}위</span><h3>{row.get("movieNm", "")}</h3><p>당일 관객 {format_num(row.get("audiCnt"))}명 · 누적 관객 {format_num(row.get("audiAcc"))}명</p></div><br>', unsafe_allow_html=True)
                add_movie(row)

    st.markdown("## 📈 TOP 5 관객 수")
    top5 = df.head(5).copy()
    chart = px.bar(
        top5, x="audiCnt", y="movieNm", orientation="h", text="audiCnt",
        labels={"audiCnt": "당일 관객 수(명)", "movieNm": "영화"},
        color="rank", color_continuous_scale=["#b8a5f7", "#efc5df", "#b6e3fa"],
    )
    chart.update_traces(texttemplate="%{text:,.0f}", textposition="outside", cliponaxis=False)
    chart.update_layout(
        yaxis={"categoryorder": "total ascending"},
        xaxis={"tickformat": ",", "gridcolor": "#eee8f5"},
        plot_bgcolor="rgba(255,255,255,0)",
        paper_bgcolor="rgba(255,255,255,0)",
        coloraxis_showscale=False,
        margin=dict(l=10, r=45, t=15, b=10),
        font=dict(color="#655b7b"),
    )
    st.plotly_chart(chart, use_container_width=True)

    st.markdown("## 🎞️ 데일리 랭킹")
    st.caption(f"{selected_date.strftime('%Y년 %m월 %d일')} 기준 · KOBIS 일별 박스오피스")
    display = df.copy()
    display["변동"] = display["rankInten"].apply(
        lambda x: f"🔺 +{x}" if x > 0 else (f"🔻 {x}" if x < 0 else "➖")
    )
    display["영화"] = display.apply(
        lambda r: ("🏆 " if int(r.get("audiAcc", 0)) >= 1_000_000 else "") + str(r.get("movieNm", "")),
        axis=1,
    )
    display["당일 관객"] = display["audiCnt"].map(lambda x: f"{x:,}명")
    display["누적 관객"] = display["audiAcc"].map(lambda x: f"{x:,}명")
    display = display[["rank", "변동", "영화", "당일 관객", "누적 관객", "openDt"]].rename(
        columns={"rank": "순위", "openDt": "개봉일"}
    )
    st.dataframe(display, use_container_width=True, hide_index=True, height=420)

    st.markdown("## 🌟 나의 컬렉션")
    st.progress(len(p["stickers"]) / len(STICKERS))
    st.caption(f"스티커 {len(p['stickers'])}/{len(STICKERS)}개 · 발견한 영화 {len(p['found_movies'])}편 · 퀴즈 정답 {p['quiz_score']}개")
    show_new_sticker()


def footer():
    st.markdown("<hr><div style='text-align:center;color:#a39ab4;font-size:.78rem;padding:8px;'>PASTEL MOVIE · A little movie magic, every day ✦<br>박스오피스 데이터 제공: 영화진흥위원회(KOBIS)</div>", unsafe_allow_html=True)


if st.session_state.loaded_date is None:
    load_date_data(YESTERDAY.strftime("%Y%m%d"))

if st.session_state.page == "quiz":
    show_quiz()
elif st.session_state.page == "stickers":
    show_stickers()
else:
    show_home()

footer()
