# 🎓 성취평가 문항 분석 시스템

교육 현장을 위한 데이터 기반 문항 분석 자동화 시스템

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 📋 목차

- [소개](#소개)
- [주요 기능](#주요-기능)
- [설치 방법](#설치-방법)
- [사용 방법](#사용-방법)
- [프로젝트 구조](#프로젝트-구조)
- [테스트](#테스트)
- [문서](#문서)

## 🌟 소개

성취평가 문항 분석 시스템은 NEIS 데이터를 활용하여 정기고사 및 수행평가의 문항 분석을 자동화하는 Streamlit 기반 웹 애플리케이션입니다.

### 특징

- ✅ **자동 데이터 파싱**: NEIS 엑셀 파일의 다양한 형식 자동 인식
- 📊 **시각화**: Plotly 기반 인터랙티브 차트
- 🔒 **보안**: 브라우저에서 직접 처리 (서버 미전송)
- 📱 **반응형**: 모바일/태블릿 지원
- 🎨 **세련된 UI**: Pretendard 폰트 및 현대적 디자인

## 🚀 주요 기능

### 1. 데이터 분석

- 문항정보표 자동 파싱
- 학생 정오표 병합 (다중 학급 지원)
- 성적일람표 통합
- 학번 자동 생성 (반/번호 → 20101)

### 2. 통계 계산

- **신뢰도(KR-20)**: 내적 일관성 측정
- **변별도**: 상위권/하위권 구분력
- **정답률**: 문항별 난이도
- **성취수준별 분석**: A~E 또는 A~미도달

### 3. 시각화

- 점수 분포 그래프
- 성취수준별 통계
- P-D Chart (문항 양호도 맵)
- 성취수준별 정답률 추이

### 4. 분석 리포트

- AI 기반 문항 진단
- 우수 문항 식별
- 개선 제언
- 출제 가이드라인

## 📦 설치 방법

### 1. 저장소 클론

```bash
git clone https://github.com/your-repo/grade-analysis.git
cd grade-analysis
```

### 2. 가상환경 생성 및 활성화

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. 의존성 설치

```bash
pip install -r requirements.txt
```

### 4. 애플리케이션 실행

```bash
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 접속

## 💻 사용 방법

### 1단계: 분석 기준 선택

- **분할점수 기반**: 입력한 분할점수로 자동 성취도 판정
- **학기말 성취도 기반**: 성적일람표의 기존 성취도 사용

### 2단계: 평가 계획 설정

- 정기고사/수행평가 항목 추가/수정
- 만점 및 반영비율 설정

### 3단계: 파일 업로드

**정기고사 필수 파일**:
- 📑 문항정보표 (NEIS)
- ✍️ 학생답정오표 (다중 학급 가능)
- 📊 성적일람표 (학기말 성취도 기반 시)

**수행평가 필수 파일**:
- 📑 평가기준표
- 📊 성적일람표 (학기말 성취도 기반 시)

### 4단계: 결과 확인

6개 탭에서 다양한 분석 결과 확인:
- 데이터 미리보기
- 전체 성취도 분석
- 문항 분석
- 답지반응 분포
- 성취기준 분석
- AI 리포트

## 📂 프로젝트 구조

```
성적분석프로그램(개인용)/
│
├── app.py                      # 메인 애플리케이션
├── requirements.txt            # 의존성 패키지
├── pytest.ini                  # pytest 설정
│
├── modules/                    # 기능 모듈
│   ├── __init__.py
│   ├── data_loader.py         # 데이터 로딩/파싱
│   ├── statistics.py          # 통계 계산
│   ├── visualizations.py      # Plotly 차트
│   └── styles.py              # HTML/CSS 처리
│
├── tests/                      # 테스트 코드
│   ├── test_data_loader.py
│   ├── test_statistics.py
│   └── test_styles.py
│
└── README.md                   # 문서 (본 파일)
```

## 🧪 테스트

### 전체 테스트 실행

```bash
pytest
```

### 특정 모듈 테스트

```bash
# 데이터 로더 테스트
pytest tests/test_data_loader.py

# 통계 모듈 테스트
pytest tests/test_statistics.py

# 스타일 모듈 테스트
pytest tests/test_styles.py
```

### 커버리지 확인

```bash
pytest --cov=modules --cov-report=html
```

## 📚 문서

### API 문서

각 모듈은 상세한 Docstring을 포함하고 있습니다:

```python
from modules.statistics import calculate_kr20_reliability

# Docstring 확인
help(calculate_kr20_reliability)
```

### 주요 함수 예제

#### 데이터 로딩

```python
from modules.data_loader import load_and_merge_data

info_df, main_df = load_and_merge_data(
    info_file=info_file,
    ans_files=[ans1, ans2],
    grade_files=[grade1]
)
```

#### 신뢰도 계산

```python
from modules.statistics import calculate_kr20_reliability

binary_matrix = df[['Item_1', 'Item_2', 'Item_3']]
reliability = calculate_kr20_reliability(binary_matrix)
print(f"KR-20 신뢰도: {reliability:.3f}")
```

#### 변별도 계산

```python
from modules.statistics import calculate_discrimination_index

discrimination = calculate_discrimination_index(
    df=student_df,
    item_cols=['Item_1', 'Item_2'],
    total_score_col='Total_Score',
    percentile=0.25
)
```

#### 차트 생성

```python
from modules.visualizations import create_pd_chart

fig = create_pd_chart(item_analysis_df)
fig.show()
```

## 🔧 기술 스택

- **Frontend**: Streamlit
- **Data Processing**: Pandas, NumPy
- **Visualization**: Plotly
- **Statistics**: SciPy
- **Testing**: pytest
- **Styling**: Custom CSS

## 📊 통계 지표 해석

### KR-20 신뢰도
- **0.80 이상**: 매우 높은 일관성 (우수)
- **0.70~0.79**: 높은 일관성 (양호)
- **0.60~0.69**: 수용 가능
- **0.60 미만**: 재검토 필요

### 변별도
- **0.40 이상**: 매우 우수
- **0.30~0.39**: 우수
- **0.20~0.29**: 보통
- **0.19 이하**: 재검토 필요

## 🛠️ 개발

### 개발 환경 설정

```bash
# 개발용 의존성 설치
pip install -r requirements-dev.txt

# Pre-commit 훅 설치
pre-commit install
```

### 코드 스타일

- **PEP 8** 준수
- **Docstring**: Google 스타일
- **Type Hints**: 주요 함수에 적용

### 커밋 메시지 규칙

```
feat: 새로운 기능 추가
fix: 버그 수정
docs: 문서 수정
style: 코드 포맷팅
refactor: 코드 리팩토링
test: 테스트 추가
chore: 기타 작업
```

## 🐛 문제 해결

### 일반적인 문제

**1. 파일 업로드 실패**
- NEIS 파일 형식 확인
- 엑셀 파일 손상 여부 확인

**2. 데이터 파싱 오류**
- 헤더 행 위치 확인
- 학생 이름 열 확인

**3. 성취도 불일치**
- 정오표와 성적일람표의 이름 일치 확인
- 공백 및 오타 확인

## 📝 라이선스

MIT License

Copyright (c) 2026 사곡고등학교

## 👥 기여

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'feat: Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📧 연락처

프로젝트 링크: [https://github.com/your-repo/grade-analysis](https://github.com/your-repo/grade-analysis)

## 🙏 감사의 말

- Streamlit 개발팀
- NEIS 시스템
- 사곡고등학교 교직원

---

⭐ 이 프로젝트가 도움이 되셨다면 Star를 눌러주세요!
