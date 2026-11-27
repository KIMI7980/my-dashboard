# 영업팀 매출 현황 대시보드 (Streamlit + pandas)
import os  # 파일이 있는지 확인할 때 쓰는 Python 기본 기능

import pandas as pd  # 표 데이터를 다루는 라이브러리 (Python 안의 엑셀)
import streamlit as st  # 화면을 그리는 라이브러리, st라는 별명으로 쓴다

DATA_FILE = "sales_sample.csv"  # 데이터 파일 이름 (app.py와 같은 폴더 기준 상대경로)
REQUIRED_COLUMNS = ["date", "region", "category", "sales", "quantity"]  # 꼭 있어야 하는 열

# ── 페이지 기본 설정: 화면을 넓게 쓴다 ──
st.set_page_config(page_title="영업팀 매출 현황", layout="wide")

st.title("영업팀 매출 현황")  # 맨 위 제목
st.caption("데이터 기준: 2026년 1~10월 · 출처: sales_sample.csv (수업용 샘플 데이터)")  # 제목 아래 작은 설명 글


# ── 데이터 불러오기 ──
@st.cache_data  # 결과를 기억해 두기: 조건을 바꿔 다시 실행돼도 파일은 한 번만 읽는다
def load_data(path):
    try:
        return pd.read_csv(path, parse_dates=["date"])  # 기본(UTF-8)으로 읽고 date 열은 날짜로
    except UnicodeDecodeError:
        return pd.read_csv(path, parse_dates=["date"], encoding="cp949")  # 엑셀에서 저장한 한글 CSV 대비


# 방어 코드 1) 데이터 파일이 없으면 안내하고 멈춘다
if not os.path.exists(DATA_FILE):
    st.error(f"데이터 파일 '{DATA_FILE}'을(를) 찾을 수 없습니다. app.py와 같은 폴더에 파일이 있는지, 이름이 맞는지 확인해 주세요.")
    st.stop()  # 여기서 화면 그리기를 멈춘다

# 방어 코드 2) 필요한 열이 없으면 어떤 열이 없는지 알려 주고 멈춘다
header = pd.read_csv(DATA_FILE, nrows=0, encoding_errors="ignore").columns  # 머리글(열 이름)만 먼저 읽기
missing = [c for c in REQUIRED_COLUMNS if c not in header]  # 없는 열만 골라내기
if missing:
    st.error(f"데이터에 필요한 열이 없습니다: {', '.join(missing)}. CSV 머리글(첫 줄)의 열 이름을 확인해 주세요.")
    st.stop()

df = load_data(DATA_FILE)  # 원본 데이터 (df)

# ── 사이드바: 조건 선택 위젯 ──
st.sidebar.header("조건 선택")  # 화면 왼쪽 조건 칸의 제목

regions = sorted(df["region"].unique())  # 지역 목록
selected_regions = st.sidebar.multiselect("지역", regions, default=regions)  # 여러 개 선택, 기본은 전체

categories = ["전체"] + sorted(df["category"].unique())  # 맨 앞에 '전체' 추가
selected_category = st.sidebar.selectbox("카테고리", categories)  # 드롭다운에서 하나 고르기

min_day = df["date"].min().date()  # 데이터의 첫 날짜
max_day = df["date"].max().date()  # 데이터의 마지막 날짜
start_day, end_day = st.sidebar.slider(
    "기간", min_value=min_day, max_value=max_day, value=(min_day, max_day), format="YYYY-MM-DD"
)  # 슬라이더로 기간 범위 고르기

# ── 조건으로 걸러낸 데이터: filtered (지표·그래프·표가 모두 이것을 쓴다) ──
filtered = df[df["region"].isin(selected_regions)]  # 고른 지역 중 하나인 행만
if selected_category != "전체":
    filtered = filtered[filtered["category"] == selected_category]  # 고른 카테고리만
filtered = filtered[filtered["date"].dt.date.between(start_day, end_day)]  # 기간 범위 안의 행만

st.sidebar.markdown(f"**선택 조건: {len(filtered)}건 / 전체 {len(df)}건**")  # 필터 아래 건수 표시

# 방어 코드 3) 조건 결과가 0건이면 안내하고, 지표·그래프·표는 그리지 않는다
if filtered.empty:
    st.info("선택한 조건에 맞는 데이터가 0건입니다. 왼쪽에서 지역을 하나 이상 고르거나 기간·카테고리를 넓혀 보세요.")
    st.stop()  # 0건 검사는 필터 아래, 지표·그래프 위에 둔다

# ── 본문: 탭 두 개 ──
tab_summary, tab_detail = st.tabs(["요약", "상세 데이터"])

with tab_summary:
    # 지표 카드 3개를 가로로
    total_sales = filtered["sales"].sum()  # 총 매출
    order_count = len(filtered)  # 주문 건수 (행 하나 = 주문 하나)
    avg_order = total_sales / order_count  # 평균 주문액 (0건은 위에서 막았으므로 나눗셈 안전)

    col1, col2, col3 = st.columns(3)
    col1.metric("총 매출", f"{total_sales:,.0f}원")
    col2.metric("주문 건수", f"{order_count:,}건")
    col3.metric("평균 주문액", f"{avg_order:,.0f}원")

    # 그래프 1: 월별 매출 추이 (선 그래프)
    st.subheader("월별 매출 추이")
    monthly = filtered.groupby(filtered["date"].dt.strftime("%Y-%m"))["sales"].sum()  # 월별 합계 (1월부터 순서대로)
    monthly.index.name = "월"
    st.line_chart(monthly, x_label="월", y_label="매출(원)", alt="월별 매출 추이 선 그래프")

    # 그래프 2: 지역별 매출 (막대 그래프, 큰 순서)
    st.subheader("지역별 매출 (큰 순서)")
    by_region = filtered.groupby("region")["sales"].sum().sort_values(ascending=False)  # 지역별 합계, 큰 순서
    by_region = by_region.reset_index().rename(columns={"region": "지역", "sales": "매출"})  # 그래프용 표로 바꾸기
    st.bar_chart(by_region, x="지역", y="매출", y_label="매출(원)", sort="-매출", alt="지역별 매출 막대 그래프")  # -매출 = 큰 순서

with tab_detail:
    st.subheader("상세 데이터")
    st.dataframe(filtered, hide_index=True, alt="조건으로 걸러낸 매출 상세 표")  # 화면 폭에 맞추고 행 번호 숨김

# ── 화면 아래: 이 화면으로 내릴 수 있는 경영 판단 ──
st.divider()
st.markdown(
    "**이 화면으로 내릴 수 있는 경영 판단** · 전체 기간 기준 부산·대전이 매출 1·2위이고 6월·9월 매출이 크게 줄었으므로, "
    "하반기 판촉 예산은 매출이 큰 지역을 유지하면서 부진한 달의 원인(재고·캠페인 공백)을 먼저 점검하는 데 쓴다."
)
