
# main.py
# 🎬 어제의 박스오피스 - KOBIS 공식 API를 이용한 영화 순위 앱

import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import plotly.express as px
import requests
import streamlit as st


# --------------------------------------------------
# 1. 기본 화면 설정
# --------------------------------------------------

st.set_page_config(
    page_title="어제의 박스오피스",
    page_icon="🎬",
    layout="wide",
)

st.title("🎬 어제의 박스오피스")
st.caption("영화진흥위원회(KOBIS) 공식 일별 박스오피스")


# --------------------------------------------------
# 2. 한국 시간 기준으로 어제 날짜 계산하기
# --------------------------------------------------

# 배포 서버의 시간대가 한국과 달라도 정확하게 계산하도록 설정한다.
KST = ZoneInfo("Asia/Seoul")

# 한국 시간 기준 오늘 날짜에서 하루를 뺀다.
yesterday = datetime.datetime.now(KST).date() - datetime.timedelta(days=1)

# KOBIS API가 요구하는 YYYYMMDD 형식으로 변환한다.
target_dt = yesterday.strftime("%Y%m%d")


st.info(f"📅 조회 날짜: {yesterday.strftime('%Y년 %m월 %d일')} (한국 시간 기준 어제)")


# --------------------------------------------------
# 3. API 주소 설정
# --------------------------------------------------

API_URL = (
    "https://www.kobis.or.kr/kobisopenapi/webservice/"
    "rest/boxoffice/searchDailyBoxOfficeList.json"
)


# --------------------------------------------------
# 4. KOBIS API에서 영화 정보 가져오기
# --------------------------------------------------

@st.cache_data(ttl=3600)
def fetch_boxoffice(date_str, api_key):
    """KOBIS API에 요청하고 JSON 응답을 반환한다."""

    params = {
        "key": api_key,
        "targetDt": date_str,
    }

    # 네트워크 오류나 응답 지연에 대비해 제한 시간을 설정한다.
    response = requests.get(
        API_URL,
        params=params,
        timeout=20,
    )

    # HTTP 오류가 발생하면 예외를 일으킨다.
    response.raise_for_status()

    # HTTP 상태가 200이어도 API 내부 오류가 있을 수 있다.
    return response.json()


# --------------------------------------------------
# 5. 인증키 확인 및 API 요청
# --------------------------------------------------

# 인증키는 코드에 직접 적지 않고 Streamlit Secrets에서 읽는다.
try:
    api_key = st.secrets["KOBIS_KEY"]

    if not str(api_key).strip():
        st.error("KOBIS_KEY 인증키가 비어 있습니다.")
        st.info(
            "Streamlit Cloud의 앱 설정에서 Secrets를 열고 "
            "KOBIS_KEY에 발급받은 인증키를 입력해 주세요."
        )
        st.stop()

except (KeyError, FileNotFoundError):
    st.error("KOBIS_KEY 인증키를 찾을 수 없습니다.")
    st.info(
        "Streamlit Cloud의 앱 설정 → Secrets에서 "
        "KOBIS_KEY를 등록했는지 확인해 주세요."
    )
    st.stop()


# API 요청 중 발생할 수 있는 연결 오류 등을 처리한다.
try:
    data = fetch_boxoffice(target_dt, str(api_key).strip())

except requests.exceptions.Timeout:
    st.error("KOBIS 서버의 응답 시간이 초과되었습니다.")
    st.info("잠시 기다린 뒤 앱을 새로고침해 주세요.")
    st.stop()

except requests.exceptions.HTTPError as e:
    st.error(f"KOBIS 서버에서 HTTP 오류가 발생했습니다: {e}")
    st.info("API 주소와 서버 상태를 확인한 뒤 다시 시도해 주세요.")
    st.stop()

except requests.exceptions.RequestException as e:
    st.error(f"KOBIS 서버에 연결하지 못했습니다: {e}")
    st.info("인터넷 연결과 KOBIS API 서버 상태를 확인해 주세요.")
    st.stop()

except ValueError:
    st.error("API 응답을 JSON 형식으로 읽지 못했습니다.")
    st.info("KOBIS API 서버의 응답 형식을 확인해 주세요.")
    st.stop()


# --------------------------------------------------
# 6. API 내부 오류 확인
# --------------------------------------------------

# 인증키가 틀려도 HTTP 상태코드가 200일 수 있으므로
# 응답 안에 faultInfo가 있는지 별도로 검사한다.
if not isinstance(data, dict):
    st.error("API 응답의 형식이 예상과 다릅니다.")
    st.info("KOBIS API 서버의 응답을 확인해 주세요.")
    st.stop()

if "faultInfo" in data:
    fault = data.get("faultInfo", {})

    # API가 알려 준 오류 코드와 메시지를 확인한다.
    error_code = fault.get("errorCode", "확인 불가")
    error_message = fault.get("message", "상세 오류 메시지가 없습니다.")

    st.error("KOBIS API가 오류 응답을 반환했습니다.")
    st.write(f"**오류 코드:** {error_code}")
    st.write(f"**오류 메시지:** {error_message}")

    st.info(
        "Secrets의 KOBIS_KEY가 정확한지, 인증키가 유효한지, "
        "API 이용 신청이나 사용 조건에 문제가 없는지 확인해 주세요."
    )
    st.stop()


# --------------------------------------------------
# 7. 영화 목록 가져오기
# --------------------------------------------------

box_office = data.get("boxOfficeResult")

if not isinstance(box_office, dict):
    st.error("API 응답에서 박스오피스 정보를 찾을 수 없습니다.")
    st.info("KOBIS API 응답 구조와 서비스 상태를 확인해 주세요.")
    st.stop()

movies = box_office.get("dailyBoxOfficeList", [])

# 목록이 없거나 예상한 목록 형식이 아니면 안내한다.
if not isinstance(movies, list) or len(movies) == 0:
    st.warning("해당 날짜의 영화 목록이 비어 있습니다.")
    st.info(
        "아직 집계가 완료되지 않았거나 API에서 데이터를 제공하지 "
        "않을 수 있습니다. 조회 날짜와 KOBIS 서비스 상태를 확인해 주세요."
    )
    st.stop()


# --------------------------------------------------
# 8. 데이터를 표와 그래프에 맞게 정리하기
# --------------------------------------------------

df = pd.DataFrame(movies)

# 화면에 필요한 열이 모두 있는지 확인한다.
required_columns = [
    "rank",
    "movieNm",
    "openDt",
    "audiCnt",
    "audiAcc",
    "scrnCnt",
]

missing_columns = [
    col for col in required_columns if col not in df.columns
]

if missing_columns:
    st.error("API 응답에 필요한 데이터 항목이 없습니다.")
    st.write("누락된 항목:", ", ".join(missing_columns))
    st.info("KOBIS API의 응답 구조가 변경되었는지 확인해 주세요.")
    st.stop()


# 숫자 데이터가 문자열로 오므로 숫자 형식으로 바꾼다.
number_columns = ["rank", "audiCnt", "audiAcc", "scrnCnt"]

for col in number_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# 숫자로 변환할 수 없는 행은 제외한다.
df = df.dropna(subset=["rank", "audiCnt", "audiAcc", "scrnCnt"])

if df.empty:
    st.warning("표시할 수 있는 영화 데이터가 없습니다.")
    st.info("KOBIS API에서 반환한 숫자 데이터가 올바른지 확인해 주세요.")
    st.stop()

# 표와 순위를 항상 올바른 순서로 보여 준다.
df["rank"] = df["rank"].astype(int)
df = df.sort_values("rank").reset_index(drop=True)


# --------------------------------------------------
# 9. 1위 영화의 주요 지표 카드 3개
# --------------------------------------------------

top_movie = df.iloc[0]

st.subheader(f"🥇 오늘의 1위 영화: {top_movie['movieNm']}")

card1, card2, card3 = st.columns(3)

card1.metric(
    label="🎟️ 어제 관객수",
    value=f"{int(top_movie['audiCnt']):,}명",
)

card2.metric(
    label="👥 누적 관객수",
    value=f"{int(top_movie['audiAcc']):,}명",
)

card3.metric(
    label="🖥️ 스크린수",
    value=f"{int(top_movie['scrnCnt']):,}개",
)

if str(top_movie.get("openDt", "")).strip():
    st.caption(f"개봉일: {top_movie['openDt']}")


# --------------------------------------------------
# 10. 전체 박스오피스 순위표
# --------------------------------------------------

st.subheader("📋 일별 박스오피스 순위표")

# 순위표에 필요한 열만 골라 한국어 이름으로 바꾼다.
table = df[
    ["rank", "movieNm", "openDt", "audiCnt", "audiAcc", "scrnCnt"]
].copy()

table.columns = [
    "순위",
    "영화명",
    "개봉일",
    "관객수",
    "누적관객",
    "스크린수",
]

# 숫자는 천 단위 쉼표를 적용해 읽기 쉽게 표시한다.
for col in ["관객수", "누적관객", "스크린수"]:
    table[col] = table[col].map(lambda value: f"{int(value):,}")

st.dataframe(
    table,
    hide_index=True,
    use_container_width=True,
)


# --------------------------------------------------
# 11. 관객수 상위 5편 막대그래프
# --------------------------------------------------

st.subheader("📊 관객수 상위 5편")

# 하루 관객수가 많은 순서대로 최대 5편을 선택한다.
top5 = df.nlargest(5, "audiCnt").copy()

# 관객수가 큰 영화부터 위쪽에 보이도록 정렬한다.
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
    title="영화별 하루 관객수 비교",
)

# 막대 끝에 관객수를 쉼표와 함께 표시한다.
fig.update_traces(
    texttemplate="%{text:,.0f}명",
    textposition="outside",
    cliponaxis=False,
)

fig.update_layout(
    xaxis=dict(
        tickformat=",",
        title="어제 관객수(명)",
    ),
    yaxis_title="영화명",
    margin=dict(l=10, r=40, t=60, b=10),
)

st.plotly_chart(fig, use_container_width=True)


# --------------------------------------------------
# 12. 데이터 출처 안내
# --------------------------------------------------

st.divider()
st.caption(
    "데이터 출처: 영화진흥위원회 영화관입장권통합전산망(KOBIS) "
    "| 일별 박스오피스 API"
)
