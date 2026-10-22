
import random
import datetime
from zoneinfo import ZoneInfo

import requests
import pandas as pd
import plotly.express as px
import streamlit as st


# =========================
# 기본 설정
# =========================
st.set_page_config(
    page_title="Pastel Movie 🍿",
    page_icon="🎬",
    layout="wide",
)

API_URL = (
    "https://www.kobis.or.kr/kobisopenapi/"
    "webservice/rest/boxoffice/"
    "searchDailyBoxOfficeList.json"
)

KST = ZoneInfo("Asia/Seoul")
TODAY = datetime.datetime.now(KST).date()
YESTERDAY = TODAY - datetime.timedelta(days=1)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Jua&family=Noto+Sans+KR:wght@400;500;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Noto Sans KR', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #fbf5ff 0%, #fff8fb 50%, #eff8ff 100%);
    }

    h1, h2, h3 {
        color: #514778;
        font-family: 'Jua', sans-serif;
    }

    .soft-card {
        background: rgba(255,255,255,0.88);
        border: 1px solid #eee2ff;
        border-radius: 22px;
        padding: 22px;
        box-shadow: 0 8px 24px rgba(100,80,140,0.08);
        margin-bottom: 14px;
    }

    .hero {
        background: linear-gradient(120deg, #e9ddff, #ffe6f0, #e1f3ff);
        border-radius: 26px;
        padding: 26px;
        color: #514778;
        box-shadow: 0 8px 24px rgba(100,80,140,0.09);
        margin-bottom: 18px;
    }

    .ticket {
        background: #fff;
        border: 2px dashed #c8b7f4;
        border-radius: 22px;
        padding: 24px;
        text-align: center;
        box-shadow: 0 8px 20px rgba(100,80,140,0.08);
    }

    .stButton > button {
        border-radius: 14px;
        border: 1px solid #e3d5ff;
        background: linear-gradient(100deg, #efe8ff, #ffeaf3);
        color: #65518f;
        font-weight: 600;
        min-height: 42px;
        transition: transform 0.15s ease;
    }

    .stButton > button:hover {
        border-color: #c8b5ff;
        color: #514078;
        transform: translateY(-2px);
    }

    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #b6a0ff, #ffb6d3);
    }

    .stAlert {
        border-radius: 14px;
    }

    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
    }

    .stMetric {
        background: rgba(255,255,255,0.8);
        border: 1px solid #eee2ff;
        padding: 14px;
        border-radius: 18px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================
# 세션 상태
# =========================
defaults = {
    "page": "home",
    "random_movie": None,
    "found_movies": [],
    "stickers": [],
    "quiz_movie": None,
    "quiz_answered": False,
    "quiz_score": 0,
    "quiz_total": 0,
    "quiz_streak": 0,
    "best_streak": 0,
    "quiz_message": "",
    "quiz_correct": False,
    "quiz_date": None,
    "explore_count": 0,
    "quiz_history": [],
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================
# API 및 데이터
# =========================
@st.cache_data(ttl=1800, show_spinner=False)
def get_movies(date_string):
    try:
        api_key = st.secrets["KOBIS_KEY"]
    except Exception:
        return None, "Streamlit Secrets에 KOBIS_KEY를 등록해 주세요."

    try:
        response = requests.get(
            API_URL,
            params={
                "key": api_key,
                "targetDt": date_string,
            },
            timeout=15,
        )
        response.raise_for_status()
        result = response.json()

        if "faultInfo" in result:
            message = result["faultInfo"].get(
                "message", "KOBIS API 오류"
            )
            return None, message

        items = result.get("boxOfficeResult", {}).get(
            "dailyBoxOfficeList", []
        )

        if not items:
            return pd.DataFrame(), None

        df = pd.DataFrame(items)

        numeric_columns = [
            "rank", "rankInten", "audiCnt", "audiAcc",
            "scrnCnt", "showCnt",
        ]

        for column in numeric_columns:
            if column in df.columns:
                df[column] = pd.to_numeric(
                    df[column], errors="coerce"
                ).fillna(0).astype(int)

        for column in ["movieNm", "movieCd", "openDt"]:
            if column not in df.columns:
                df[column] = ""

        return df, None

    except requests.exceptions.Timeout:
        return None, "서버 응답 시간이 초과됐어요. 잠시 후 다시 시도해 주세요."
    except requests.exceptions.RequestException:
        return None, "네트워크 연결을 확인하고 다시 시도해 주세요."
    except ValueError:
        return None, "서버에서 올바른 데이터를 받지 못했어요."


def get_movie_key(movie):
    """영화별로 중복 없이 기록하기 위한 식별자."""
    code = str(movie.get("movieCd", "")).strip()
    if code and code.lower() != "nan":
        return code
    return str(movie.get("movieNm", "")).strip()


def add_movie_to_collection(movie):
    key = get_movie_key(movie)
    if key and key not in st.session_state.found_movies:
        st.session_state.found_movies.append(key)


def unlock_sticker(sticker_id):
    if sticker_id not in st.session_state.stickers:
        st.session_state.stickers.append(sticker_id)
        st.session_state.new_sticker = sticker_id


def update_achievements():
    count = len(st.session_state.found_movies)
    score = st.session_state.quiz_score
    streak = st.session_state.best_streak

    if count >= 1:
        unlock_sticker("first_movie")
    if count >= 3:
        unlock_sticker("collector_3")
    if count >= 5:
        unlock_sticker("collector_5")
    if count >= 10:
        unlock_sticker("collector_10")
    if score >= 1:
        unlock_sticker("quiz_first")
    if score >= 5:
        unlock_sticker("quiz_5")
    if streak >= 3:
        unlock_sticker("streak_3")
    if st.session_state.explore_count >= 5:
        unlock_sticker("explorer_5")


STICKER_LIST = [
    {
        "id": "first_movie",
        "emoji": "🎬",
        "name": "첫 영화 발견",
        "description": "영화 한 편을 찾아보세요.",
        "goal": "영화 1편 발견",
    },
    {
        "id": "collector_3",
        "emoji": "🍿",
        "name": "영화 새싹",
        "description": "서로 다른 영화 3편을 발견하세요.",
        "goal": "영화 3편 발견",
    },
    {
        "id": "collector_5",
        "emoji": "🎟️",
        "name": "티켓 수집가",
        "description": "서로 다른 영화 5편을 발견하세요.",
        "goal": "영화 5편 발견",
    },
    {
        "id": "collector_10",
        "emoji": "💎",
        "name": "영화 보석 사냥꾼",
        "description": "서로 다른 영화 10편을 발견하세요.",
        "goal": "영화 10편 발견",
    },
    {
        "id": "quiz_first",
        "emoji": "🔍",
        "name": "순위 탐정",
        "description": "순위 퀴즈에서 첫 정답을 맞히세요.",
        "goal": "퀴즈 정답 1회",
    },
    {
        "id": "quiz_5",
        "emoji": "🏆",
        "name": "퀴즈 챔피언",
        "description": "순위 퀴즈 정답을 5회 맞히세요.",
        "goal": "퀴즈 정답 5회",
    },
    {
        "id": "streak_3",
        "emoji": "🔥",
        "name": "연속 정답왕",
        "description": "퀴즈에서 3문제 연속 정답을 맞히세요.",
        "goal": "3연속 정답",
    },
    {
        "id": "explorer_5",
        "emoji": "🧭",
        "name": "영화 탐험가",
        "description": "랜덤 영화 뽑기를 5회 이용하세요.",
        "goal": "랜덤 탐험 5회",
    },
]


# =========================
# 공통 화면 이동
# =========================
def go_home():
    st.session_state.page = "home"
    st.session_state.quiz_answered = False
    st.session_state.quiz_message = ""


def go_quiz():
    st.session_state.page = "quiz"
    st.session_state.quiz_movie = None
    st.session_state.quiz_answered = False
    st.session_state.quiz_message = ""


def go_stickers():
    st.session_state.page = "stickers"


# =========================
# 제목
# =========================
def show_header():
    st.markdown(
        """
        <div class="hero">
            <h1>🎬 Pastel Movie</h1>
            <p>오늘의 영화 순위를 탐험하고 나만의 스티커를 모아 봐요!</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================
# 스티커 도감
# =========================
def show_stickers():
    st.markdown("## 🌟 나의 영화 스티커 도감")
    st.caption("미션을 수행하고 잠긴 스티커를 하나씩 해금해 보세요!")

    update_achievements()

    unlocked = len(st.session_state.stickers)
    total = len(STICKER_LIST)

    st.progress(unlocked / total if total else 0)
    st.write(f"**스티커 {unlocked} / {total}개 획득**")

    columns = st.columns(4)

    for index, sticker in enumerate(STICKER_LIST):
        earned = sticker["id"] in st.session_state.stickers

        with columns[index % 4]:
            emoji = sticker["emoji"] if earned else "🔒"
            title = sticker["name"] if earned else "???"

            st.markdown(
                f"""
                <div class="soft-card" style="text-align:center; min-height:210px;">
                    <div style="font-size:42px;">{emoji}</div>
                    <h3>{title}</h3>
                    <p style="font-size:13px;">{sticker["description"]}</p>
                    <p style="font-size:12px; color:#8b7da8;">
                        {"✨ 획득 완료!" if earned else "🎯 미션: " + sticker["goal"]}
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("### 🎯 다음 도전")
    remaining = [s for s in STICKER_LIST if s["id"] not in st.session_state.stickers]

    if remaining:
        next_sticker = remaining[0]
        st.info(
            f"{next_sticker['emoji']} **{next_sticker['name']}** — "
            f"{next_sticker['goal']}"
        )
    else:
        st.success("모든 스티커를 모았어요! 진정한 영화 마스터예요. 🎉")

    if st.button("🏠 메인 화면으로 돌아가기", use_container_width=True):
        go_home()
        st.rerun()


# =========================
# 퀴즈 문제 생성
# =========================
def create_quiz(df, date_string):
    if df is None or df.empty or len(df) < 2:
        st.warning("이 날짜에는 퀴즈를 만들 만큼 영화 데이터가 없어요.")
        return

    movie = random.choice(df.to_dict("records"))

    st.session_state.quiz_movie = movie
    st.session_state.quiz_date = date_string
    st.session_state.quiz_answered = False
    st.session_state.quiz_message = ""
    st.session_state.quiz_correct = False


# =========================
# 퀴즈 전용 페이지
# =========================
def show_quiz(df, date_string):
    st.markdown("## 🧩 두뇌 풀가동! 영화 순위 퀴즈")
    st.caption("영화 제목을 보고 그날의 순위를 맞혀 보세요.")

    if st.button("← 메인 화면으로 돌아가기"):
        go_home()
        st.rerun()

    if df is None or df.empty:
        st.warning("선택한 날짜에는 아직 집계된 영화 순위가 없어요.")
        return

    if len(df) < 2:
        st.warning("퀴즈를 만들기에는 영화 데이터가 부족해요.")
        return

    # 날짜가 바뀌면 이전 문제를 초기화
    if st.session_state.quiz_date != date_string:
        st.session_state.quiz_movie = None
        st.session_state.quiz_answered = False

    if st.session_state.quiz_movie is None:
        st.markdown(
            """
            <div class="soft-card" style="text-align:center;">
                <div style="font-size:48px;">🕵️</div>
                <h3>순위 탐정단</h3>
                <p>영화 제목만 보고 순위를 추리해 보세요!</p>
                <p>메인 화면의 순위표는 이 페이지에 표시되지 않아요.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("🧩 새 퀴즈 시작하기", use_container_width=True):
            create_quiz(df, date_string)
            st.rerun()
        return

    movie = st.session_state.quiz_movie

    st.markdown(
        f"""
        <div class="hero">
            <div>🔎 MYSTERY RANK</div>
            <h1>{movie.get("movieNm", "이름 없는 영화")}</h1>
            <p>{date_string[:4]}년 {date_string[4:6]}월 {date_string[6:]}일에 몇 위였을까요?</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not st.session_state.quiz_answered:
        guessed_rank = st.selectbox(
            "내가 생각하는 순위",
            options=list(range(1, len(df) + 1)),
            format_func=lambda x: f"{x}위",
            key=f"guess_{date_string}_{get_movie_key(movie)}",
        )

        if st.button("정답 확인하기 ✨", use_container_width=True):
            actual_rank = int(movie.get("rank", 0))
            correct = guessed_rank == actual_rank

            st.session_state.quiz_answered = True
            st.session_state.quiz_correct = correct
            st.session_state.quiz_total += 1

            if correct:
                st.session_state.quiz_score += 1
                st.session_state.quiz_streak += 1
                st.session_state.best_streak = max(
                    st.session_state.best_streak,
                    st.session_state.quiz_streak,
                )
                st.session_state.quiz_message = (
                    f"🎉 정답이에요! {actual_rank}위가 맞아요!"
                )
                unlock_sticker("quiz_first")
                if st.session_state.quiz_score >= 5:
                    unlock_sticker("quiz_5")
                if st.session_state.quiz_streak >= 3:
                    unlock_sticker("streak_3")
            else:
                st.session_state.quiz_streak = 0
                st.session_state.quiz_message = (
                    f"아쉽지만 정답은 {actual_rank}위예요! "
                    "다음 퀴즈에 다시 도전해 봐요."
                )

            st.rerun()

    else:
        if st.session_state.quiz_correct:
            st.success(st.session_state.quiz_message)
            st.balloons()
        else:
            st.info(st.session_state.quiz_message)

        st.markdown(
            f"""
            <div class="soft-card">
                <h3>📊 정답 정보</h3>
                <p>영화: <b>{movie.get("movieNm", "")}</b></p>
                <p>실제 순위: <b>{movie.get("rank", "?")}위</b></p>
                <p>당일 관객 수: <b>{int(movie.get("audiCnt", 0)):,}명</b></p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.metric("누적 퀴즈 정답", st.session_state.quiz_score)
        st.metric("현재 연속 정답", st.session_state.quiz_streak)

        if st.button("🎲 다음 퀴즈 풀기", use_container_width=True):
            create_quiz(df, date_string)
            st.rerun()

    st.caption("🔐 퀴즈를 푸는 동안에는 순위표와 TOP 5 그래프를 보여 주지 않아요.")


# =========================
# 메인 페이지
# =========================
def show_home(df, date_string, error):
    show_header()

    st.markdown("### 📅 오늘의 영화 탐험 날짜")

    selected_date = st.date_input(
        "날짜 선택",
        value=datetime.datetime.strptime(date_string, "%Y%m%d").date(),
        min_value=datetime.date(2004, 1, 1),
        max_value=YESTERDAY,
        help="박스오피스는 집계가 완료된 날짜를 기준으로 확인해요.",
    )

    date_string = selected_date.strftime("%Y%m%d")

    # 날짜가 바뀌면 데이터를 다시 조회
    df, error = get_movies.clear() or (df, error) if False else (df, error)

    if st.session_state.get("loaded_date") != date_string:
        df, error = get_movies(date_string)
        st.session_state.loaded_date = date_string
        st.session_state.current_df = df
        st.session_state.current_error = error
        st.session_state.quiz_movie = None
        st.session_state.quiz_date = date_string
    else:
        df = st.session_state.get("current_df", df)
        error = st.session_state.get("current_error", error)

    st.markdown("---")

    nav1, nav2, nav3 = st.columns(3)

    with nav1:
        if st.button("🧩 순위 퀴즈 입장", use_container_width=True):
            go_quiz()
            st.rerun()

    with nav2:
        if st.button("🌟 나의 스티커 도감", use_container_width=True):
            go_stickers()
            st.rerun()

    with nav3:
        if st.button("🎲 랜덤 영화 뽑기", use_container_width=True):
            if df is not None and not df.empty:
                st.session_state.random_movie = random.choice(
                    df.to_dict("records")
                )
                st.session_state.explore_count += 1
                update_achievements()
                st.rerun()
            else:
                st.warning("뽑을 영화가 없어요.")

    if error:
        st.error(f"데이터를 불러오지 못했어요: {error}")
        st.info("KOBIS API 키와 인터넷 연결을 확인해 주세요.")
        return

    if df is None or df.empty:
        st.warning("📅 그날은 아직 집계 전입니다.")
        return

    # 영화 탐험 기록
    for movie in df.to_dict("records"):
        add_movie_to_collection(movie)

    update_achievements()

    st.markdown("### 🎟️ 오늘의 영화 티켓")

    first_movie = df.iloc[0].to_dict()

    st.markdown(
        f"""
        <div class="ticket">
            <div style="font-size:36px;">🎟️🍿🎬</div>
            <h2>오늘의 박스오피스 1위</h2>
            <h1>{first_movie.get("movieNm", "")}</h1>
            <p>당일 관객 수: {int(first_movie.get("audiCnt", 0)):,}명</p>
            <p>누적 관객 수: {int(first_movie.get("audiAcc", 0)):,}명</p>
            <p>개봉일: {first_movie.get("openDt", "정보 없음")}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.random_movie:
        random_movie = st.session_state.random_movie
        st.markdown("### 🎲 오늘의 랜덤 영화")

        st.markdown(
            f"""
            <div class="soft-card">
                <h2>✨ {random_movie.get("movieNm", "")}</h2>
                <p>현재 순위: {random_movie.get("rank", "?")}위</p>
                <p>당일 관객 수: {int(random_movie.get("audiCnt", 0)):,}명</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("다른 영화 뽑기"):
            st.session_state.random_movie = random.choice(
                df.to_dict("records")
            )
            st.session_state.explore_count += 1
            update_achievements()
            st.rerun()

    st.markdown("### 🔎 영화 검색")

    search = st.text_input(
        "영화 제목을 입력하세요",
        placeholder="예: 영화 제목",
    )

    if search.strip():
        results = df[
            df["movieNm"].astype(str).str.contains(
                search.strip(), case=False, na=False
            )
        ]

        if results.empty:
            st.info("검색 결과가 없어요. 다른 제목으로 검색해 보세요.")
        else:
            for movie in results.to_dict("records"):
                st.markdown(
                    f"**🎬 {movie['movieNm']}** — "
                    f"{movie['rank']}위 · "
                    f"당일 관객 {int(movie['audiCnt']):,}명"
                )
                add_movie_to_collection(movie)

    st.markdown("### 🏆 TOP 5 관객 수")

    top5 = df.head(5).copy()
    top5["관객 수"] = top5["audiCnt"]
    top5["순위"] = top5["rank"].astype(str) + "위"

    chart = px.bar(
        top5,
        x="관객 수",
        y="movieNm",
        orientation="h",
        color="rank",
        color_continuous_scale=["#d8c9ff", "#f6cde0", "#b9e4ff"],
        labels={
            "movieNm": "영화",
            "관객 수": "관객 수(명)",
            "rank": "순위",
        },
    )

    chart.update_layout(
        yaxis={"categoryorder": "total ascending"},
        plot_bgcolor="rgba(255,255,255,0)",
        paper_bgcolor="rgba(255,255,255,0)",
        coloraxis_showscale=False,
        margin=dict(l=10, r=10, t=20, b=10),
    )

    st.plotly_chart(chart, use_container_width=True)

    st.markdown("### 🎞️ 오늘의 영화 순위표")

    display_df = df.copy()
    display_df["순위 변동"] = display_df["rankInten"].apply(
        lambda x: (
            f"🔺 +{x}" if x > 0
            else (f"🔻 {x}" if x < 0 else "➖ 0")
        )
    )

    display_df["영화 제목"] = display_df.apply(
        lambda row: (
            "🏆 " if int(row.get("audiAcc", 0)) >= 1_000_000 else ""
        ) + str(row.get("movieNm", "")),
        axis=1,
    )

    display_df["당일 관객 수"] = display_df["audiCnt"].map(
        lambda x: f"{x:,}명"
    )
    display_df["누적 관객 수"] = display_df["audiAcc"].map(
        lambda x: f"{x:,}명"
    )

    st.dataframe(
        display_df[
            [
                "rank",
                "순위 변동",
                "영화 제목",
                "당일 관객 수",
                "누적 관객 수",
                "openDt",
            ]
        ].rename(
            columns={
                "rank": "순위",
                "openDt": "개봉일",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("### 🌟 나의 도감 진행 상황")
    st.progress(
        len(st.session_state.stickers) / len(STICKER_LIST)
    )
    st.write(
        f"스티커 {len(st.session_state.stickers)} / "
        f"{len(STICKER_LIST)}개 · "
        f"발견한 영화 {len(st.session_state.found_movies)}편"
    )

    if st.button("🌟 스티커 도감 자세히 보기", use_container_width=True):
        go_stickers()
        st.rerun()


# =========================
# 앱 실행
# =========================
if "loaded_date" not in st.session_state:
    st.session_state.loaded_date = None
    st.session_state.current_df = None
    st.session_state.current_error = None

initial_date = YESTERDAY.strftime("%Y%m%d")

# 화면을 열 때 현재 날짜에 맞는 데이터를 준비
if st.session_state.loaded_date is None:
    initial_df, initial_error = get_movies(initial_date)
    st.session_state.loaded_date = initial_date
    st.session_state.current_df = initial_df
    st.session_state.current_error = initial_error

page = st.session_state.page

if page == "quiz":
    quiz_date = st.session_state.get("loaded_date", initial_date)
    quiz_df = st.session_state.get("current_df")
    quiz_error = st.session_state.get("current_error")

    if quiz_error:
        st.error(f"데이터 오류: {quiz_error}")
        if st.button("메인 화면으로 돌아가기"):
            go_home()
            st.rerun()
    else:
        show_quiz(quiz_df, quiz_date)

elif page == "stickers":
    show_stickers()

else:
    show_home(
        st.session_state.get("current_df"),
        st.session_state.get("loaded_date", initial_date),
        st.session_state.get("current_error"),
    )
