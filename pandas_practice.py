# pandas 연습용 파일 (화면 파일 app.py와 따로 실행한다. 결과는 터미널에 글자로 나온다)
import pandas as pd  # pandas를 pd라는 별명으로 가져온다

# ── 미션 2: 데이터 건강검진 ──
df = pd.read_csv("sales_sample.csv", parse_dates=["date"])  # CSV 읽기, date 열은 날짜로

print("=== 위에서 5행 미리보기 ===")
print(df.head())
print("\n=== (행 수, 열 수) ===")
print(df.shape)
print("\n=== 열 이름, 빈칸, 자료형 ===")
df.info()
print("\n=== 빈칸 개수 ===")
print(df.isna().sum())
print("\n=== 숫자 열 요약(평균·최소·최대) ===")
print(df.describe())

# ── 조건으로 걸러내기: 서울 + 매출 10만 원 이상 ──
seoul_big = df[(df["region"] == "서울") & (df["sales"] >= 100000)]  # 두 조건 모두 만족(&)
print("\n=== 서울 & 매출 10만 원 이상 주문 건수 ===")
print(len(seoul_big))

# ── 집계 1: 월별 매출 합계 (엑셀 피벗: 행=월, 값=sales 합계) ──
monthly = df.groupby(df["date"].dt.month)["sales"].sum()  # 날짜에서 월만 뽑아 묶고 합계
print("\n=== 월별 매출 합계 ===")
print(monthly)

# ── 집계 2: 지역별 매출 합계, 큰 순서 ──
by_region = df.groupby("region")["sales"].sum().sort_values(ascending=False)
print("\n=== 지역별 매출 합계(큰 순서) ===")
print(by_region)

# ── 검산용 숫자 ──
print("\n=== 검산용: 전체 총 매출 / 서울 총 매출 ===")
print(df["sales"].sum(), df[df["region"] == "서울"]["sales"].sum())

# ── 미니 퀴즈 3줄 ──
print("\n=== 미니 퀴즈 ===")
print("1) 부산 매출 합계:", df[df["region"] == "부산"]["sales"].sum())
print("2) 카테고리별 평균 매출(큰 순서):")
print(df.groupby("category")["sales"].mean().sort_values(ascending=False))
print("3) 3월 & 매출 20만 원 이상 건수:", len(df[(df["date"].dt.month == 3) & (df["sales"] >= 200000)]))
