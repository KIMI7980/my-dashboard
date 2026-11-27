# 0건 점검 파일 (hook이 app.py를 고친 직후 자동으로 실행한다)
# 지역을 모두 해제한 상황을 흉내 내서, 빨간 에러 없이 안내 문구가 나오는지 검사한다.
import os
import sys

from streamlit.testing.v1 import AppTest  # 브라우저 없이 app.py를 실행해 보는 도구

HERE = os.path.dirname(os.path.abspath(__file__))  # 이 파일이 있는 폴더 (my-dashboard)
os.chdir(HERE)  # 데이터 파일을 상대경로로 찾도록 폴더를 맞춘다

at = AppTest.from_file(os.path.join(HERE, "app.py"), default_timeout=30)
at.run()  # 처음 화면
at.sidebar.multiselect[0].set_value([])  # 지역을 모두 해제 → 0건 상황 만들기
at.run()

problems = []
if at.exception:
    problems.append("빨간 에러가 났습니다: " + at.exception[0].value)
if not any("0건" in box.value for box in at.info):
    problems.append("0건일 때 안내 문구(st.info)가 없습니다.")
if at.metric:
    problems.append("0건인데 지표 카드가 그려졌습니다. st.stop()이 지표 위에 있는지 확인하세요.")

if problems:
    print("0건 점검 실패:\n- " + "\n- ".join(problems), file=sys.stderr)
    sys.exit(2)  # 2로 끝나면 Claude Code가 실패 내용을 보고 다시 고친다
print("0건 점검 통과: 지역을 모두 해제해도 안내 문구가 나오고 화면이 깨지지 않습니다.")
