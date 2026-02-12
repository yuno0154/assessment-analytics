import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import pointbiserialr
import streamlit.components.v1 as components
import re

# [DataTables 렌더링 함수]
def render_datatables(html_content, unique_id):
    datatables_html = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css">
        <style>
            table.dataTable thead th {{ text-align: center !important; vertical-align: middle !important; background-color: #f8f9fa !important; border: 1px solid #e0e0e0 !important; font-size: 0.9rem; }}
            table.dataTable tbody td {{ text-align: center !important; vertical-align: middle !important; border: 1px solid #e0e0e0 !important; font-size: 0.9rem; padding: 4px !important; }}
            table.dataTable thead .sorting:before, table.dataTable thead .sorting:after {{ bottom: 0.5em !important; }}
            .dataTables_wrapper .dataTables_paginate .paginate_button.current {{ background: #e0e0e0 !important; border: 1px solid #bdbdbd !important; }}
            body {{ font-family: 'Pretendard', sans-serif; }}
        </style>
        <script type="text/javascript" charset="utf8" src="https://code.jquery.com/jquery-3.7.0.js"></script>
        <script type="text/javascript" charset="utf8" src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
    </head>
    <body style="margin: 0;">
        {html_content}
        <script>
            $(document).ready(function() {{
                $('table').attr('id', 'example_{unique_id}');
                $('#example_{unique_id}').DataTable({{
                    "paging": false, 
                    "lengthChange": false, 
                    "searching": false, 
                    "ordering": true, 
                    "info": false, 
                    "autoWidth": false, 
                    "responsive": true, 
                    "order": [], 
                    "language": {{
                        "zeroRecords": "데이터가 없습니다.",
                        "infoEmpty": "데이터 없음"
                    }}
                }});
            }});
        </script>
    </body>
    </html>
    """
    return components.html(datatables_html, height=600, scrolling=True)

# [시각화 함수 정의]
def custom_bar_style(val, threshold):
    try:
        v = float(val)
        if pd.isna(v): return ''
        bg_color = '#eeeeee' if v < threshold else '#ffffff'
        return f"background: linear-gradient(90deg, #90caf9 {v}%, {bg_color} {v}%); color: black;"
    except:
        return ''

# [배경색 스타일 함수 - 성취수준별 정답률]
def style_background_level_v2(val, threshold):
    try:
        if isinstance(val, str): return ''
        v = float(val)
        # 기준 미만이면 회색(#eeeeee), 이상이면 흰색(#ffffff)
        bg_color = '#eeeeee' if v < threshold else '#ffffff'
        return f'background-color: {bg_color}; color: black;'
    except:
        return ''

# [HTML 후처리] 헤더 병합
def merge_headers(html_content, target_cols):
    thead_match = re.search(r'(<thead[^>]*>)(.*?)(</thead>)', html_content, re.DOTALL)
    if not thead_match: return html_content
    thead_open, thead_body, thead_close = thead_match.groups()
    rows = re.findall(r'(<tr[^>]*>)(.*?)(</tr>)', thead_body, re.DOTALL)
    if len(rows) < 2: return html_content
    tr1_open, tr1_content, tr1_close = rows[0]
    tr2_open, tr2_content, tr2_close = rows[1]
    for col in target_cols:
        pattern = re.compile(r'(<th\b[^>]*>)(\s*' + re.escape(col) + r'\s*)(</th>)')
        if pattern.search(tr1_content):
            def add_rowspan(match):
                tag_open = match.group(1)
                if 'rowspan' not in tag_open:
                    return tag_open.replace('<th', '<th rowspan="2"') + match.group(2) + match.group(3)
                return match.group(0)
            tr1_content = pattern.sub(add_rowspan, tr1_content)
        if pattern.search(tr2_content):
            tr2_content = pattern.sub('', tr2_content)
    new_thead = f"{thead_open}\n{tr1_open}{tr1_content}{tr1_close}\n{tr2_open}{tr2_content}{tr2_close}\n{thead_close}"
    return html_content.replace(thead_match.group(0), new_thead)

# --- 페이지 설정 (모바일 친화적 설정) ---
st.set_page_config(
    page_title="성취평가 문항 분석 시스템",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 디자인 커스텀 (CSS) ---
st.markdown("""
    <style>
    /* 폰트 적용 (Pretendard) */
    @import url("https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css");
    
    html, body, [class*="css"] {
        font-family: 'Pretendard', sans-serif;
    }

    /* 전체 배경 밝게 설정 (Config에서 설정했으나 확실하게 재적용) */
    .stApp {
        background-color: #FFFFFF;
        color: #1E293B;
    }

    /* 메인 타이틀 스타일링 */
    h1 {
        color: #1E3A8A; /* 진한 파랑 */
        font-weight: 800;
        font-size: 2.2rem !important;
        margin-bottom: 0.5rem;
        letter-spacing: -0.05rem;
    }
    
    /* 서브헤더 스타일링 */
    h2, h3, h4 {
        color: #334155;
        font-weight: 700;
        letter-spacing: -0.03rem;
    }

    /* 카드 스타일 (Metrics 등) */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
        color: #2563EB;
    }
    [data-testid="stMetricLabel"] {
        font-size: 1rem;
        color: #64748B;
        font-weight: 600;
    }
    div[data-testid="metric-container"] {
        background-color: #F8F9FA;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border: 1px solid #E2E8F0;
    }

    /* 탭 디자인 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        white-space: pre-wrap;
        background-color: #FFFFFF;
        border-radius: 8px;
        padding: 10px 20px;
        border: 1px solid #E2E8F0;
        color: #64748B;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #EFF6FF !important;
        color: #2563EB !important;
        border-color: #2563EB !important;
        font-weight: 700;
    }

    /* 사이드바 스타일 */
    [data-testid="stSidebar"] {
        background-color: #F8F9FA;
        border-right: 1px solid #E2E8F0;
    }
    
    /* 파일 업로더 커스텀 (영어 텍스트 숨김 및 한글화) */
    [data-testid="stFileUploader"] {
        background-color: #FFFFFF;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 10px;
    }
    /* Sidebar Title Size Adjustment */
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1 {
        font-size: 1.6rem !important;
        margin-bottom: 0px;
    }

    /* 파일 업로더 커스텀 (영어 텍스트 숨김 및 한글화 - 강력한 오버라이드) */
    [data-testid="stFileUploader"] {
        background-color: #FFFFFF;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 10px;
    }
    
    /* 1. Limit 텍스트 숨김 */
    [data-testid="stFileUploader"] small {
        display: none !important;
    }

    /* 2. Drag & Drop 텍스트 숨김 (완전 삭제) */
    [data-testid="stFileUploaderDropzoneInstructions"] {
        display: none !important;
    }

    /* 3. Browse files 버튼 텍스트 교체 (프리미엄 버튼 스타일) */
    /* 버튼 텍스트 크기 0으로 설정하여 숨김 - Dropzone 내부 버튼만 타겟팅 */
    [data-testid="stFileUploaderDropzone"] button {
        font-size: 0px !important;
        line-height: 0px !important;
        padding: 0px !important; /* 내부 패딩 제거 */
        width: 100%;
        min-height: 38px; /* 버튼 최소 높이 확보 */
        background: transparent !important;
        border: none !important; /* 기본 테두리 제거 */
    }
    
    /* 버튼 내부 텍스트 노드 완전 숨김 */
    [data-testid="stFileUploaderDropzone"] button div {
        display: none !important;
        visibility: hidden !important;
    }

    /* 버튼 스타일 정의 (::after 가상요소 활용) */
    [data-testid="stFileUploaderDropzone"] button::after {
        content: "📂 파일 열기";
        
        /* Flexbox 중심 정렬 */
        display: flex;
        align-items: center;
        justify-content: center;
        
        /* 버튼 디자인 (부드러운 파란색 테마) */
        background-color: #EFF6FF; 
        color: #1E3A8A;
        border: 1px solid #BFDBFE;
        border-radius: 6px;
        
        font-size: 0.9rem !important;
        font-weight: 700;
        
        /* 크기 및 여백 */
        width: 100%;
        height: 100%;
        min-height: 38px;
        padding: 8px 16px;
        
        cursor: pointer;
        transition: all 0.2s ease-in-out;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    
    /* Hover 효과 */
    [data-testid="stFileUploaderDropzone"] button:hover::after {
        background-color: #DBEAFE;
        border-color: #93C5FD;
        transform: translateY(-1px);
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Active (클릭) 효과 */
    [data-testid="stFileUploaderDropzone"] button:active::after {
        background-color: #BFDBFE;
        transform: translateY(0px);
        box-shadow: none;
    }

    /* 데이터프레임 스타일 */
    [data-testid="stDataFrame"] {
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid #E2E8F0;
    }
    
    /* 데이터프레임 셀 가운데 정렬 */
    [data-testid="stDataFrame"] [data-testid="StyledDataFrameCell"] {
        text-align: center !important;
        justify-content: center !important;
    }
    
    /* 데이터프레임 헤더 스타일 (굵게, 가운데 정렬) */
    [data-testid="stDataFrame"] [data-testid="StyledDataFrameHeaderCell"] {
        text-align: center !important;
        justify-content: center !important;
        font-weight: 700 !important;
    }
    
    /* AG Grid 기반 스타일 (백업) */
    .ag-header-cell-label {
        justify-content: center !important;
        font-weight: 700 !important;
    }
    .ag-cell {
        text-align: center !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 데이터 처리 로직 ---
# --- 데이터 처리 로직 ---
def extract_classroom_from_data(raw_preview):
    """정오표 파일의 상단 데이터에서 강의실 번호 추출"""
    import re
    # 상위 20행 탐색
    for row_idx in range(min(10, len(raw_preview))):
        row_str = ' '.join([str(val) for val in raw_preview.iloc[row_idx].values])
        # "강의실" 다음의 숫자 찾기 (예: "4 강의실", "강의실 1", "강의실1")
        match = re.search(r'(\d+)\s*강의실|강의실\s*(\d+)', row_str)
        if match:
            classroom = match.group(1) if match.group(1) else match.group(2)
            return classroom.strip()
    return None

def load_and_merge_data(info_file, ans_files, grade_files):
    try:
        # 1. 문항정보표 파싱
        # dtype={'No': str}로 읽어서 문항 번호가 숫자로 자동 변환되는 것 방지
        info = pd.read_excel(info_file, skiprows=10, engine='openpyxl', dtype={'No': str}).iloc[:22]
        info = info.iloc[:, [1, 3, 14, 16, 18, 19, 21]]
        info.columns = ['No', 'Standard', 'Hard', 'Medium', 'Easy', 'Score', 'Correct_Ans']
        
        # 유효한 문항 번호만 필터링 (숫자인 행만)
        info = info[info['No'].apply(lambda x: str(x).replace('.0','').strip().isdigit())].copy()
        info['No'] = info['No'].astype(float).astype(int) # 정수형으로 변환
        
        # 배점(Score) 숫자 변환 (에러 발생 시 0점 처리)
        info['Score'] = pd.to_numeric(info['Score'], errors='coerce').fillna(0)
        
        # 난이도(Exp_Diff) 계산
        info['Exp_Diff'] = info.apply(lambda r: '상' if r['Hard']=='○' else ('중' if r['Medium']=='○' else '하'), axis=1)

        # 2. 정오표 병합 (문항 번호 기준 상대 위치 파악)
        all_ans = []
        for f in ans_files:
            # 상위 20행 미리보기
            raw_preview = pd.read_excel(f, nrows=20, header=None, engine='openpyxl', dtype=str)
            
            header_row_idx = -1
            item_start_col_idx = -1
            name_col_idx = -1
            id_col_idx = -1
            
            # 1. 문항 번호(1, 2, 3...)가 있는 행 찾기
            item_col_map = {}  # {문항번호: 컬럼인덱스}
            for r_idx, row in raw_preview.iterrows():
                row_str = row.astype(str).values
                # 1, 2, 3, 4, 5가 연속해서 등장하거나 포함된 행 찾기
                # 간단하게 '1', '2', '3', '4'가 모두 포함되어 있는지 확인
                if '1' in row_str and '2' in row_str and '3' in row_str and '4' in row_str:
                    header_row_idx = r_idx
                    # 각 문항 번호(1~16)의 컬럼 인덱스 찾기
                    for c_idx, val in enumerate(row_str):
                        val_clean = str(val).strip().replace('.0', '')
                        if val_clean.isdigit():
                            item_num = int(val_clean)
                            if 1 <= item_num <= 16 and item_num not in item_col_map:
                                item_col_map[item_num] = c_idx
                    # '1'의 컬럼 인덱스 (기존 호환성)
                    if 1 in item_col_map:
                        item_start_col_idx = item_col_map[1]
                    if len(item_col_map) >= 4:  # 최소 4개 문항 발견
                        break
            
            if header_row_idx == -1 or item_start_col_idx == -1:
                # 문항 번호 헤더를 찾지 못한 경우, 기존 방식 (성명/이름 찾기) 시도
                st.warning(f"'{f.name}' 파일에서 문항 번호 헤더를 찾을 수 없습니다. '성명' 또는 '이름' 열을 기준으로 데이터를 파싱합니다.")
                
                name_col_idx_fallback = -1
                score_col_idx_fallback = -1
                header_row_idx_fallback = -1

                for r_idx, row in raw_preview.iterrows():
                    row_str = row.astype(str).values
                    if any('성명' in str(x) for x in row_str) or any('이름' in str(x) for x in row_str):
                        header_row_idx_fallback = r_idx
                        for c_idx, val in enumerate(row_str):
                            if '성명' in str(val) or '이름' in str(val): name_col_idx_fallback = c_idx
                            if '번호' in str(val) or 'ID' in str(val): id_col_idx = c_idx # Use global id_col_idx
                            if '점수' in str(val) or 'Total' in str(val) or '합계' in str(val): score_col_idx_fallback = c_idx
                        break
                
                if header_row_idx_fallback == -1:
                    st.error(f"'{f.name}' 파일에서 '성명' 또는 '이름' 열을 찾을 수 없습니다.")
                    with st.expander(f"❌ '{f.name}' 원본 데이터 미리보기 (상위 20행)"):
                        st.dataframe(raw_preview)
                    return None, None

                # Fallback: 데이터 다시 읽기 (기존 로직)
                raw = pd.read_excel(f, skiprows=header_row_idx_fallback + 1, header=None, engine='openpyxl', dtype=str)
                
                # 컬럼 매핑
                if score_col_idx_fallback == -1: score_col_idx_fallback = len(raw.columns) - 1 # 맨 마지막
                
                data = raw.copy()
                data = data.rename(columns={name_col_idx_fallback: 'Name'})
                
                if id_col_idx != -1:
                    data = data.rename(columns={id_col_idx: 'ID'})
                else:
                    data['ID'] = data.index # 임시
                
                data = data.rename(columns={score_col_idx_fallback: 'Total_Score'})

                # 문항 컬럼 추출 (Name 컬럼 뒤쪽으로 2칸 띄우고 시작한다고 가정 - 기존 3->5 패턴)
                # Name이 found 안되면... error.
                start_col = name_col_idx_fallback + 2
                for i in range(1, 17):
                    if start_col + i - 1 < len(data.columns):
                         data[f'Item_{i}'] = data.iloc[:, start_col + i - 1]
                    else:
                         data[f'Item_{i}'] = '.'
                
                # 불필요한 행 제거 (정답, 배점 등 문자열이 이름에 있는 경우)
                data = data[~data['Name'].isin(['정답', '배점', '합계', '평균', 'None', 'nan'])]
                
                # 필요한 컬럼만 추출
                cols = ['ID', 'Name', 'Total_Score'] + [f'Item_{i}' for i in range(1, 17)]
                final_cols = [c for c in cols if c in data.columns]
                all_ans.append(data[final_cols])
                continue # 다음 파일로 넘어감
            
            # 문항 번호 기준으로 데이터 로드 (새로운 로직)
            # 데이터 시작: 헤더 + 3 (정답, 배점 행 제외) - NEIS 표준
            data_start_row = header_row_idx + 3 
            raw = pd.read_excel(f, skiprows=data_start_row, header=None, engine='openpyxl', dtype=str)
            
            # 컬럼 매핑 (상대 위치)
            # 문항 1번이 item_start_col_idx에 있음.
            # 성명은 보통 문항 1번 보다 앞쪽 2칸 (item_start_col_idx - 2)
            # 번호/ID는 문항 1번 보다 앞쪽 4칸 (item_start_col_idx - 4)
            
            # 초기 추정
            name_col_idx_candidate = item_start_col_idx - 2
            id_col_idx_candidate = item_start_col_idx - 4 
            
            # Name 컬럼 유효성 검사 및 보정
            def looks_like_korean_name(s):
                if pd.isna(s) or not isinstance(s, str): return False
                s = s.strip()
                if len(s) < 2 or len(s) > 5: return False # 일반적인 이름 길이
                return all('가' <= char <= '힣' for char in s) # 한글 여부
            
            # name_col_idx_candidate가 유효한지 확인
            if name_col_idx_candidate >= 0 and name_col_idx_candidate < len(raw.columns):
                sample_names = raw.iloc[:10, name_col_idx_candidate].dropna().tolist()
                korean_name_count = sum(1 for s in sample_names if looks_like_korean_name(s))
                
                if korean_name_count < 3: # 충분히 한글 이름 같지 않으면
                    # item_start_col_idx - 1 위치 확인
                    if item_start_col_idx - 1 >= 0 and item_start_col_idx - 1 < len(raw.columns):
                        sample_names_alt = raw.iloc[:10, item_start_col_idx - 1].dropna().tolist()
                        korean_name_count_alt = sum(1 for s in sample_names_alt if looks_like_korean_name(s))
                        if korean_name_count_alt >= 3:
                            name_col_idx = item_start_col_idx - 1
                        else: # 둘 다 아니면 초기 추정 사용 (최악의 경우)
                            name_col_idx = name_col_idx_candidate
                    else:
                        name_col_idx = name_col_idx_candidate
                else:
                    name_col_idx = name_col_idx_candidate
            else: # name_col_idx_candidate가 범위 밖이면
                name_col_idx = -1 # 찾지 못함
            
            # ID 컬럼 (name_col_idx - 2 또는 id_col_idx_candidate)
            if name_col_idx != -1 and name_col_idx - 2 >= 0:
                id_col_idx = name_col_idx - 2
            elif id_col_idx_candidate >= 0:
                id_col_idx = id_col_idx_candidate
            else:
                id_col_idx = -1 # 찾지 못함

            score_col_idx = len(raw.columns) - 1 # 맨 뒤 컬럼을 점수로 가정
            
            data = raw.copy()
            
            # [수정] 반/번호 컬럼 찾기 - 이름 컬럼 왼쪽에서 숫자/숫자 패턴 찾기
            import re
            def is_class_num_format(s):
                if pd.isna(s): return False
                return bool(re.match(r'^\d+[/\-]\d+$', str(s).strip()))
            
            # 이름 컬럼 왼쪽에서 반/번호 컬럼 찾기
            class_num_col_idx = -1
            for col_offset in range(1, min(name_col_idx + 1, 4)):  # 최대 3칸 왼쪽까지 탐색
                check_idx = name_col_idx - col_offset
                if check_idx >= 0 and check_idx < len(data.columns):
                    sample_vals = data.iloc[:10, check_idx].tolist()
                    valid_count = sum(1 for x in sample_vals if is_class_num_format(x))
                    if valid_count >= 3:
                        class_num_col_idx = check_idx
                        break
            
            # 컬럼 이름 변경
            col_mapping = {}
            if name_col_idx != -1 and name_col_idx < len(data.columns): 
                col_mapping[name_col_idx] = 'Name'
            else:
                st.warning(f"'{f.name}' 파일에서 'Name' 컬럼을 찾을 수 없습니다. 데이터 처리에 문제가 있을 수 있습니다.")
                data['Name'] = 'Unknown_' + data.index.astype(str) # 임시 이름
            
            if class_num_col_idx != -1 and class_num_col_idx < len(data.columns): 
                col_mapping[class_num_col_idx] = 'ClassNum'
            
            if score_col_idx < len(data.columns):
                col_mapping[score_col_idx] = 'Total_Score' # 마지막 컬럼 점수
            else:
                st.warning(f"'{f.name}' 파일에서 'Total_Score' 컬럼을 찾을 수 없습니다. 0으로 처리됩니다.")
                data['Total_Score'] = 0
            
            data = data.rename(columns=col_mapping)
            
            # [신규] 반/번호 -> 학번 변환
            def parse_class_num_to_id(s):
                """'1/1' -> '20101' (2학년 01반 01번)"""
                if pd.isna(s): return ''
                s = str(s).strip()
                match = re.match(r'^(\d+)[/\-](\d+)$', s)
                if match:
                    class_no = match.group(1).zfill(2)
                    student_no = match.group(2).zfill(2)
                    return f'2{class_no}{student_no}'
                return ''
            
            if 'ClassNum' in data.columns:
                data['ID'] = data['ClassNum'].apply(parse_class_num_to_id)
                data = data.drop(columns=['ClassNum'])
            else:
                data['ID'] = ''
            
            # 문항 컬럼 매핑 (item_col_map 사용)
            for item_num in range(1, 17):
                if item_num in item_col_map:
                    q_idx = item_col_map[item_num]
                else:
                    # 매핑되지 않은 경우 순차 오프셋 사용 (fallback)
                    q_idx = item_start_col_idx + (item_num - 1)
                
                if q_idx < len(raw.columns):
                    data[f'Item_{item_num}'] = raw.iloc[:, q_idx]
                else:
                    data[f'Item_{item_num}'] = '.'

            # 불필요한 행 제거 (정답, 배점 등 문자열이 이름에 있는 경우)
            data = data[~data['Name'].isin(['정답', '배점', '합계', '평균', 'None', 'nan'])]
            
            # 필요한 컬럼만 추출
            cols = ['ID', 'Name', 'Total_Score'] + [f'Item_{i}' for i in range(1, 17)]
            final_cols = [c for c in cols if c in data.columns]
            all_ans.append(data[final_cols])
        
        if not all_ans:
            return None, None

        ans_df = pd.concat(all_ans)
        ans_df = ans_df.dropna(subset=['Name']) # 이름 없는 행 제거
        ans_df['Name'] = ans_df['Name'].astype(str).str.strip() # 공백 제거

        # 3. 성적일람표 병합 (다중 파일 지원 & 동적 헤더 탐색 & 컬럼 보정)
        all_grades = []
        if not isinstance(grade_files, list):
            grade_files = [grade_files]
            
        for f in grade_files:
            # 1. 헤더 위치 찾기 (상위 30행 탐색)
            raw_preview = pd.read_excel(f, nrows=30, header=None, engine='openpyxl', dtype=str)
            
            name_row_idx = -1
            grade_row_idx = -1
            name_col_idx = -1
            grade_col_idx = -1
            
            # 전체 셀을 순회하며 키워드 찾기
            for r_idx, row in raw_preview.iterrows():
                row_str = row.astype(str).values
                for c_idx, val in enumerate(row_str):
                    val_str = str(val)
                    # 성명 컬럼 찾기
                    if name_col_idx == -1 and ('성명' in val_str or '이름' in val_str):
                        name_row_idx = r_idx
                        name_col_idx = c_idx
                    # 성취도 컬럼 찾기
                    if grade_col_idx == -1 and ('성취도' in val_str or '등급' in val_str):
                        grade_row_idx = r_idx
                        grade_col_idx = c_idx
            
            if name_col_idx != -1 and grade_col_idx != -1:
                # 데이터 시작 행: 헤더 아래
                data_start_row = max(name_row_idx, grade_row_idx) + 1
                
                # 데이터 로드
                g_raw = pd.read_excel(f, skiprows=data_start_row, header=None, engine='openpyxl', dtype=str)
                
                # [신규] 반/번호 컬럼 찾기
                class_num_col_idx = -1
                for r_idx, row in raw_preview.iterrows():
                    row_str = row.astype(str).values
                    for c_idx, val in enumerate(row_str):
                        val_str = str(val)
                        if '반' in val_str and '번' in val_str:  # "반/번호" 또는 "반번"
                            class_num_col_idx = c_idx
                            break
                    if class_num_col_idx != -1:
                        break
                
                # [중요] Name 컬럼 보정 로직
                # 찾아낸 name_col_idx가 실제 이름이 아니라 ID(숫자) 등일 수 있음 (Merge Cell 문제)
                # 해당 컬럼의 데이터가 한글 이름인지 확인
                def looks_like_name(s):
                    # 길이가 2~5이고, 숫자가 포함되지 않아야 함
                    if pd.isna(s) or len(str(s)) < 2: return False
                    return not any(char.isdigit() for char in str(s))

                # 현재 컬럼 데이터 확인 (상위 5개)
                sample_data = g_raw.iloc[:10, name_col_idx].tolist()
                valid_count = sum(looks_like_name(x) for x in sample_data)
                
                # 만약 유효한 이름이 적다면, 오른쪽으로 이동하며 탐색 (최대 3칸)
                if valid_count < 3: 
                    found_better = False
                    for offset in range(1, 4):
                        if name_col_idx + offset < len(g_raw.columns):
                            sample_next = g_raw.iloc[:10, name_col_idx + offset].tolist()
                            if sum(looks_like_name(x) for x in sample_next) >= 3:
                                name_col_idx += offset
                                found_better = True
                                break
                
                # 찾은 인덱스로 데이터 선택
                # [수정] 반/번호 컬럼 찾기 - 성명 컬럼 왼쪽에 있음
                class_num_col_idx = name_col_idx - 1 if name_col_idx > 0 else -1
                
                # 반/번호 컬럼 유효성 확인 (숫자/숫자 형태인지)
                import re
                def is_class_num_format(s):
                    if pd.isna(s): return False
                    return bool(re.match(r'^\d+[/\-]\d+$', str(s).strip()))
                
                if class_num_col_idx >= 0 and class_num_col_idx < len(g_raw.columns):
                    sample_class = g_raw.iloc[:10, class_num_col_idx].tolist()
                    valid_class_count = sum(1 for x in sample_class if is_class_num_format(x))
                    
                    if valid_class_count >= 3:
                        # 반/번호 컬럼 포함하여 선택
                        g_raw = g_raw.iloc[:, [class_num_col_idx, name_col_idx, grade_col_idx]]
                        g_raw.columns = ['ClassNum', 'Name', 'Achievement']
                        
                        # 학번(ID) 생성: "1/1" -> "20101"
                        def parse_class_num(s):
                            if pd.isna(s): return ''
                            s = str(s).strip()
                            match = re.match(r'^(\d+)[/\-](\d+)$', s)
                            if match:
                                class_no = match.group(1).zfill(2)
                                student_no = match.group(2).zfill(2)
                                return f'2{class_no}{student_no}'
                            return ''
                        
                        g_raw['ID'] = g_raw['ClassNum'].apply(parse_class_num)
                        g_raw = g_raw.drop(columns=['ClassNum'])
                    else:
                        # 반/번호 컬럼이 없으면 기존 방식 (이름만)
                        g_raw = g_raw.iloc[:, [name_col_idx, grade_col_idx]]
                        g_raw.columns = ['Name', 'Achievement']
                        g_raw['ID'] = ''
                else:
                    g_raw = g_raw.iloc[:, [name_col_idx, grade_col_idx]]
                    g_raw.columns = ['Name', 'Achievement']
                    g_raw['ID'] = ''
                
                all_grades.append(g_raw)
            else:
                st.error(f"'{f.name}' 파일에서 '성명'과 '성취도' 열을 찾을 수 없습니다.")
                with st.expander(f"❌ '{f.name}' 원본 데이터 미리보기"):
                    st.dataframe(raw_preview.head(10))
                return None, None
        
        if not all_ans:
            # 정오표가 없는 경우 (수행평가)
            # 성적일람표에서만 데이터 생성
            if not all_grades:
                st.error("❌ 데이터를 로드할 수 없습니다. 필요한 파일을 올바르게 업로드했는지 확인하세요.")
                return None, None
            
            grade = pd.concat(all_grades)
            grade = grade.dropna(subset=['Name'])
            grade['Name'] = grade['Name'].astype(str).str.strip()
            
            # 수행평가용 기본 데이터 생성 (정오표 대신 성적일람표만 사용)
            merged = grade.copy()
            merged['Total_Score'] = 0  # 임시
            
            # 16개 문항 컬럼 추가 (더미 데이터)
            for i in range(1, 17):
                merged[f'Item_{i}'] = '.'
        else:
            # 정오표가 있는 경우 (정기고사)
            ans_df = pd.concat(all_ans)
            ans_df = ans_df.dropna(subset=['Name'])
            ans_df['Name'] = ans_df['Name'].astype(str).str.strip()
            
            if not all_grades:
                # 성적일람표가 없으면 정오표만 사용
                merged = ans_df.copy()
                # Total_Score가 없으면 생성
                if 'Total_Score' not in merged.columns:
                    merged['Total_Score'] = 0
                # Achievement가 없으면 임시 생성
                if 'Achievement' not in merged.columns:
                    merged['Achievement'] = 'E'
            else:
                # 성적일람표와 병합
                grade = pd.concat(all_grades)
                grade = grade.dropna(subset=['Name'])
                grade['Name'] = grade['Name'].astype(str).str.strip()
                
                # 학생 수 비교 (학적 변동 확인)
                ans_students = set(ans_df['Name'].unique())
                grade_students = set(grade['Name'].unique())
                
                excluded_students = ans_students - grade_students  # 정오표에만 있는 학생
                
                if excluded_students:
                    st.warning(
                        f"⚠️ **학생 수 불일치 감지**\n\n"
                        f"• 정오표 학생 수: {len(ans_students)}명\n"
                        f"• 성적일람표 학생 수: {len(grade_students)}명\n\n"
                        f"**성적일람표를 기준으로 {len(excluded_students)}명 제외** (학적변동: 전출, 자퇴 등)\n\n"
                        f"분석에는 성적일람표에 있는 {len(grade_students)}명만 포함됩니다."
                    )
                    with st.expander(f"제외된 학생 목록 ({len(excluded_students)}명) - 클릭하여 확인"):
                        st.write("**다음 학생들이 정오표에는 있지만 성적일람표에는 없어서 제외되었습니다:**")
                        st.write(", ".join(sorted(list(excluded_students))))
                
                # 정오표와 성적일람표 병합 (성적일람표 기준)
                merged = pd.merge(ans_df, grade[['Name', 'Achievement', 'ID']], on='Name', how='inner', suffixes=('', '_grade'))
                
                # ID 우선순위: 정오표 ID > 성적일람표 ID
                if 'ID' in merged.columns and 'ID_grade' in merged.columns:
                    merged['ID'] = merged.apply(
                        lambda row: row['ID'] if row['ID'] and str(row['ID']).strip() else row['ID_grade'], 
                        axis=1
                    )
                    merged = merged.drop(columns=['ID_grade'])
                elif 'ID_grade' in merged.columns:
                    merged['ID'] = merged['ID_grade']
                    merged = merged.drop(columns=['ID_grade'])
        
        # 병합 결과 확인
        if merged.empty:
            st.warning("⚠️ **분석할 데이터가 없습니다.** 정오표와 성적일람표의 '이름'이 일치하는지 확인해주세요.")
            with st.expander("🔍 데이터 불일치 상세 정보 확인 (클릭)"):
                st.write(f"**정오표(Answer Sheet) 학생 수:** {len(ans_df)}명")
                st.write(f"**성적일람표(Grade Report) 학생 수:** {len(grade)}명")
                
                c1, c2 = st.columns(2)
                with c1:
                    st.write("#### 📋 정오표 이름 예시 (상위 5명)")
                    st.dataframe(ans_df[['Name']].head())
                with c2:
                    st.write("#### 📋 성적일람표 이름 예시 (상위 5명)")
                    st.dataframe(grade[['Name']].head())
                    
                st.info("Tip: 이름 사이에 공백이 다르거나(예: '홍길동' vs '홍 길 동'), 오타가 있는지 확인해보세요.")
            return info, pd.DataFrame() # 빈 데이터프레임 반환

        merged['Total_Score'] = pd.to_numeric(merged['Total_Score'], errors='coerce').fillna(0)
        return info, merged.dropna(subset=['Achievement'])

    except Exception as e:
        st.error(f"데이터 처리 중 오류가 발생했습니다: {e}")
        import traceback
        st.error(f"```\n{traceback.format_exc()}\n```")
        return None, None

# --- 사이드바 UI ---
with st.sidebar:
    st.markdown("### 📂 성적 분석 설정")
    
    # 보안 문구 (강조)
    st.info(
        "🔒 **데이터 보안 안내**\n\n"
        "본 서비스는 **사용자의 데이터를 서버로 전송하지 않고, "
        "브라우저에서 직접 읽고 분석합니다.**"
    )
    
    st.markdown("---")
    
    # 1단계: 분석 기준 선택
    st.subheader("1️⃣ 분석 기준 선택")
    analysis_basis = st.radio(
        "분석 방식을 선택하세요",
        ["분할점수 기반", "학기말 성취도 기반"],
        help="분할점수: 각 평가의 점수로 성취도 판정\n학기말 성취도: 기존 성적일람표의 성취도 사용"
    )
    
    st.markdown("---")
    
    # 2단계: 평가 구조 선택
    st.subheader("2️⃣ 평가 구조 선택")
    exam_type = st.radio(
        "평가 종류",
        ["1회 정기고사", "2회 정기고사", "수행평가"],
        help="분석할 평가의 유형을 선택하세요"
    )
    
    st.markdown("---")
    
    # 3단계: 평가 설정 (모든 유형 공통)
    st.subheader("3️⃣ 평가 설정")
    max_score = st.number_input("만점 (점)", value=100, min_value=1, help="평가의 총 만점을 입력하세요")
    ratio = st.number_input("반영비율 (%)", value=30, min_value=0, max_value=100, help="전체 성적에서 이 평가가 차지하는 비율")
    
    st.markdown("---")
    
    # 4단계: 분할점수 설정 (분할점수 기반 선택시만 표시)
    if analysis_basis == "분할점수 기반":
        st.subheader("4️⃣ 성취수준 분할점수")
        
        # 성취수준 수 선택 (5수준 또는 5수준+미도달)
        level_type = st.radio(
            "성취수준 구분",
            ["5수준 (A, B, C, D, E)", "5수준+미도달 (A, B, C, D, E, I)"],
            key="level_type"
        )
        
        st.caption("등급 간 분할점수를 설정하세요 (총점 기준)")
        
        if level_type == "5수준 (A, B, C, D, E)":
            col1, col2 = st.columns(2)
            with col1:
                cut_AB = st.number_input("A/B 분할점수(점)", value=90, min_value=0, max_value=max_score, key="cut_AB", 
                                        help="이 점수 이상이면 A, 미만이면 B")
                cut_CD = st.number_input("C/D 분할점수(점)", value=70, min_value=0, max_value=max_score, key="cut_CD",
                                        help="이 점수 이상이면 C, 미만이면 D")
            with col2:
                cut_BC = st.number_input("B/C 분할점수(점)", value=80, min_value=0, max_value=max_score, key="cut_BC",
                                        help="이 점수 이상이면 B, 미만이면 C")
                cut_DE = st.number_input("D/E 분할점수(점)", value=60, min_value=0, max_value=max_score, key="cut_DE",
                                        help="이 점수 이상이면 D, 미만이면 E")
            cut_EI = None
        else:  # 5수준+미도달
            col1, col2 = st.columns(2)
            with col1:
                cut_AB = st.number_input("A/B 분할점수(점)", value=90, min_value=0, max_value=max_score, key="cut_AB",
                                        help="이 점수 이상이면 A, 미만이면 B")
                cut_CD = st.number_input("C/D 분할점수(점)", value=70, min_value=0, max_value=max_score, key="cut_CD",
                                        help="이 점수 이상이면 C, 미만이면 D")
                cut_EI = st.number_input("E/미도달 분할점수(점)", value=40, min_value=0, max_value=max_score, key="cut_EI",
                                        help="이 점수 이상이면 E, 미만이면 I(미도달)")
            with col2:
                cut_BC = st.number_input("B/C 분할점수(점)", value=80, min_value=0, max_value=max_score, key="cut_BC",
                                        help="이 점수 이상이면 B, 미만이면 C")
                cut_DE = st.number_input("D/E 분할점수(점)", value=60, min_value=0, max_value=max_score, key="cut_DE",
                                        help="이 점수 이상이면 D, 미만이면 E")
        
        st.markdown("---")
    else:
        # 변수 초기화
        cut_AB = 90
        cut_BC = 80
        cut_CD = 70
        cut_DE = 60
        cut_EI = 0
        level_type = "5수준 (A, B, C, D, E)"
    
    # 5단계: 파일 업로드 (분석 기준과 평가 유형에 따라 다름)
    st.subheader("5️⃣ 데이터 파일 업로드")
    
    if analysis_basis == "분할점수 기반":
        # 분할점수 기반: 성적일람표 불필요
        if exam_type in ["1회 정기고사", "2회 정기고사"]:
            st.caption("📌 정기고사 필수 파일")
            info_f = st.file_uploader(
                "📑 문항정보표 (Excel)",
                type=['xlsx'],
                key=f"info_{exam_type}_score",
                help="NEIS에서 다운로드한 문항정보표를 선택하세요"
            )
            
            ans_fs = st.file_uploader(
                "✍️ 학생 정오표 (Excel)",
                type=['xlsx'],
                accept_multiple_files=True,
                key=f"ans_{exam_type}_score",
                help="여러 학급의 정오표를 한 번에 선택할 수 있습니다"
            )
            
            grade_fs = []  # 성적일람표 불필요
            
            st.info("💡 **팁:** 학생 정오표에서 자동으로 성취도를 판정합니다.")
            
        else:  # 수행평가
            st.caption("📌 수행평가 필수 파일")
            info_f = st.file_uploader(
                "📑 평가기준표 (Excel)",
                type=['xlsx'],
                key=f"info_{exam_type}_score",
                help="수행평가 항목과 배점이 포함된 평가기준표"
            )
            ans_fs = []
            grade_fs = []
            
            st.info("💡 **팁:** 수행평가는 평가기준표만 필요합니다.")
    
    else:  # 학기말 성취도 기반
        # 학기말 성취도 기반: 성적일람표 필수
        if exam_type in ["1회 정기고사", "2회 정기고사"]:
            st.caption("📌 정기고사 필수 파일")
            info_f = st.file_uploader(
                "📑 문항정보표 (Excel)",
                type=['xlsx'],
                key=f"info_{exam_type}_term",
                help="NEIS에서 다운로드한 문항정보표를 선택하세요"
            )
            
            ans_fs = st.file_uploader(
                "✍️ 학생 정오표 (Excel)",
                type=['xlsx'],
                accept_multiple_files=True,
                key=f"ans_{exam_type}_term",
                help="여러 학급의 정오표를 한 번에 선택할 수 있습니다"
            )
            
            grade_fs = st.file_uploader(
                "📊 성적일람표 (Excel)",
                type=['xlsx'],
                accept_multiple_files=True,
                key=f"grade_{exam_type}_term",
                help="성취도가 포함된 성적일람표를 선택하세요"
            )
            
        else:  # 수행평가
            st.caption("📌 수행평가 필수 파일")
            info_f = st.file_uploader(
                "📑 평가기준표 (Excel)",
                type=['xlsx'],
                key=f"info_{exam_type}_term",
                help="수행평가 항목과 배점이 포함된 평가기준표"
            )
            ans_fs = []
            grade_fs = st.file_uploader(
                "📊 성적일람표 (Excel)",
                type=['xlsx'],
                accept_multiple_files=True,
                key=f"grade_{exam_type}_term",
                help="수행평가 점수와 성취도가 포함된 성적일람표"
            )
    
    st.markdown("---")
    
    # 6단계: 분석 필터
    st.subheader("6️⃣ 분석 필터")
    
    # 기본 선택값 동적 설정
    default_grades = ['A', 'B', 'C', 'D', 'E']
    if analysis_basis == "분할점수 기반" and level_type == "5수준+미도달 (A, B, C, D, E, I)":
        default_grades.append('I(미도달)')
        
    target_grade = st.multiselect(
        "분석 대상 성취도",
        ['A', 'B', 'C', 'D', 'E', 'I(미도달)'],
        default=default_grades,
        help="분석에 포함할 성취수준을 선택하세요"
    )
    
    # I(미도달) 표시를 'I'로 변환
    target_grade = ['I' if x == 'I(미도달)' else x for x in target_grade]
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.caption("ⓒ 2026. Data Analysis Pro for Teachers")

# --- 메인 대시보드 ---
st.title("🎓 성취평가 문항 분석 시스템")
st.markdown("#### 데이터 기반의 정확하고 세련된 문항 분석 보고서")

# 분석 기준에 따른 필요 파일 확인
if analysis_basis == "분할점수 기반":
    # 분할점수 기반: 성적일람표 불필요
    if exam_type in ["1회 정기고사", "2회 정기고사"]:
        files_ready = info_f and ans_fs
    else:  # 수행평가
        files_ready = info_f
else:  # 학기말 성취도 기반
    # 학기말 성취도 기반: 성적일람표 필수
    if exam_type in ["1회 정기고사", "2회 정기고사"]:
        files_ready = info_f and ans_fs and grade_fs
    else:  # 수행평가
        files_ready = info_f and grade_fs

if files_ready:
    with st.spinner('데이터를 분석 중입니다...'):
        try:
            if analysis_basis == "분할점수 기반":
                # 분할점수 기반: 성적일람표 없이 정오표만 사용
                result_pkg = load_and_merge_data(info_f, ans_fs, [])
            else:
                # 학기말 성취도 기반: 성적일람표 사용
                result_pkg = load_and_merge_data(info_f, ans_fs, grade_fs)
        except Exception as e:
            st.error(f"❌ 데이터 처리 중 오류 발생: {str(e)}")
            result_pkg = None
        
    if result_pkg and result_pkg[0] is not None and result_pkg[1] is not None and not result_pkg[1].empty:
        info_df, main_df = result_pkg
        
        # --- [전역] 점수 계산 및 학생 성적 데이터 전처리 ---
        # 1. 선택형/서답형 문항 컬럼 리스트 정의
        select_cols = [f'Item_{i}' for i in range(1, 10)] # 1~9번 (선택형 가정)
        essay_cols = [f'Item_{i}' for i in range(10, 17)] # 10~16번 (서답형 가정)
        
        # 2. 문항 배점 매핑 생성
        score_map = {}
        for _, row in info_df.iterrows():
            item_no = int(row['No']) if pd.notna(row['No']) and str(row['No']).replace('.0',''). strip().isdigit() else 0
            item_score = pd.to_numeric(row['Score'], errors='coerce')
            if item_no > 0 and pd.notna(item_score):
                score_map[f'Item_{item_no}'] = item_score
        
        # 3. 점수 계산 함수 정의
        def calc_select_score(row):
            total = 0
            for col in select_cols:
                # 정답 여부는 정오표에서 '.' 이면 정답으로 처리됨
                if col in row.index and str(row[col]).strip() == '.':
                    total += score_map.get(col, 0)
            return total
            
        def calc_essay_score(row):
            total = 0
            for col in essay_cols:
                if col in row.index and str(row[col]).strip() == '.':
                    total += score_map.get(col, 0)
            return total

        # 4. 점수 컬럼 추가 (이미 존재하지 않을 경우에만)
        # 단, 기존 로직에서 덮어쓰기 위해 강제 재계산 권장
        main_df['Select_Score'] = main_df.apply(calc_select_score, axis=1)
        main_df['Essay_Score'] = main_df.apply(calc_essay_score, axis=1)
        
        # 5. 학기말 원점수 계산 (반영비율 적용)
        # Total_Score가 있으면 사용 (일람표 값), 없으면 계산값 사용
        # 하지만 일람표 값이 0이거나 미비하면 계산값으로 대체하는 것이 안전함
        # 여기서는 Total_Score가 존재하면 우선시하되, 0이면 대체
        if 'Total_Score' not in main_df.columns:
            main_df['Total_Score'] = 0
            
        # Total_Score 재계산 (일람표 값이 0인 경우)
        main_df['Total_Score'] = main_df.apply(
            lambda r: r['Select_Score'] + r['Essay_Score'] if pd.isna(r['Total_Score']) or r['Total_Score'] == 0 else r['Total_Score'], 
            axis=1
        )
            
        main_df['Total_Score_Num'] = pd.to_numeric(main_df['Total_Score'], errors='coerce').fillna(0)
        
        # 학기말 원점수 (반영비율 적용)
        # 예: 100점 만점 * 30% = 30점 만점 환산
        if 'ratio' in locals():
            main_df['Semester_Score'] = (main_df['Total_Score_Num'] * ratio / 100).round(1)
        else:
            main_df['Semester_Score'] = main_df['Total_Score_Num'] # 비율 없으면 그대로
        
        # 분할점수 기반일 때 Achievement 컬럼 생성 (존재하지 않으면)
        if analysis_basis == "분할점수 기반":
            # 총점에 따라 성취도 판정
            def get_achievement_score_based(score):
                score = pd.to_numeric(score, errors='coerce')
                if pd.isna(score):
                    return 'I' if cut_EI is not None else 'E'
                
                if cut_EI is not None:  # 5수준+미도달
                    if score >= cut_AB:
                        return 'A'
                    elif score >= cut_BC:
                        return 'B'
                    elif score >= cut_CD:
                        return 'C'
                    elif score >= cut_DE:
                        return 'D'
                    elif score >= cut_EI:
                        return 'E'
                    else:
                        return 'I'
                else:  # 5수준
                    if score >= cut_AB:
                        return 'A'
                    elif score >= cut_BC:
                        return 'B'
                    elif score >= cut_CD:
                        return 'C'
                    elif score >= cut_DE:
                        return 'D'
                    else:
                        return 'E'
            
            main_df['Achievement'] = main_df['Total_Score'].apply(get_achievement_score_based)
            
            # 분할점수 정보 표시
            if cut_EI is not None:
                cut_info = f"A/B:{cut_AB}점, B/C:{cut_BC}점, C/D:{cut_CD}점, D/E:{cut_DE}점, E/미도달:{cut_EI}점"
            else:
                cut_info = f"A/B:{cut_AB}점, B/C:{cut_BC}점, C/D:{cut_CD}점, D/E:{cut_DE}점"
            
            st.success(f"✅ 분할점수 기반으로 성취도 판정 완료\n({cut_info})")
        else:
            # 학기말 성취도 기반: 기존 Achievement 컬럼 사용
            st.success(f"✅ 학기말 성취도를 기준으로 분석합니다")
        
        # 필터링
        main_df = main_df[main_df['Achievement'].isin(target_grade)]
        
        if main_df.empty:
            st.warning("선택한 성취도에 해당하는 학생이 없습니다.")
        else:
            # 통계 계산
            # '.' 문자나 기타 문자를 처리하기 위해 1/0 매핑 시 오류 방지
            item_cols = [f'Item_{i}' for i in range(1, 17)]
            
            # 안전한 이진 행렬 변환 (Applymap 대신 apply 사용 권장)
            def safe_binary(x):
                return 1 if str(x).strip() == '.' else 0
                
            binary_matrix = main_df[item_cols].applymap(safe_binary)
            
            # 신뢰도(KR-20) 계산 - 분모 0 방지
            var_sum = binary_matrix.var().sum()
            total_var = binary_matrix.sum(axis=1).var()
            
            if total_var == 0 or np.isnan(total_var):
                alpha = 0.0
            else:
                alpha = (16/15) * (1 - var_sum / total_var)

            # [지표 계산] 문항 통계 (정답률, 변별도)
            top_len = max(1, int(len(main_df)*0.25))
            top_25 = main_df.nlargest(top_len, 'Total_Score')
            bot_25 = main_df.nsmallest(top_len, 'Total_Score')
            
            discrimination_scores = {}
            item_p_scores = {}

            for i in range(1, 17):
                col = f'Item_{i}'
                # 상위권 정답률 - 하위권 정답률
                p_top = (top_25[col].astype(str) == '.').mean()
                p_bot = (bot_25[col].astype(str) == '.').mean()
                discrimination_scores[i] = p_top - p_bot
                item_p_scores[i] = (main_df[col].astype(str) == '.').mean()
            
            # 문항 분석 DataFrame 생성 (공통 사용)
            item_stats_list = []
            for i in range(1, 17):
                item_stats_list.append({
                    'No': i, 
                    '정답률(P)': item_p_scores[i], 
                    '변별도(D)': discrimination_scores[i]
                })
            res_df = pd.merge(pd.DataFrame(item_stats_list), info_df[['No', 'Exp_Diff', 'Score', 'Standard']], on='No')
            res_df['Score'] = pd.to_numeric(res_df['Score'], errors='coerce').fillna(0)

            # HTML 테이블 스타일 정의 (전역)
            table_style = """
            <style>
            .styled-table {
                width: 100%;
                border-collapse: collapse;
                font-size: 0.85rem;
                font-family: 'Pretendard', sans-serif;
            }
            .styled-table th {
                background-color: #f0f2f6;
                font-weight: 700;
                text-align: center;
                padding: 10px 8px;
                border: 1px solid #e0e0e0;
                position: sticky;
                top: 0;
            }
            .styled-table td {
                text-align: center;
                padding: 8px 6px;
                border: 1px solid #e0e0e0;
            }
            .styled-table tr:nth-child(even) {
                background-color: #fafafa;
            }
            .styled-table tr:hover {
                background-color: #f5f5f5;
            }
            .table-container {
                max-height: 350px;
                overflow-y: auto;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
            /* 성취기준 컬럼 왼쪽 정렬 */
            .styled-table td.left-align {
                text-align: left !important;
            }
            </style>
            """
            st.markdown(table_style, unsafe_allow_html=True)

            # 탭 구성 (6개)
            tab_data, tab_summary, tab_item, tab_dist, tab_std, tab_report = st.tabs([
                "데이터", "전체 성취도 분석", "문항 분석", 
                "성취수준별 답지반응-부분점수 분포", "성취기준 분석 결과", "분석 리포트"
            ])

            # --- [Tab 1] Data ---
            with tab_data:
                st.subheader("📊 데이터 미리보기")
                st.caption("업로드된 문항정보표와 병합된 학생 성적 데이터입니다.")
                
                # 문항정보표 (위)
                st.write("#### 📑 문항정보표")
                info_display = info_df.copy()
                info_rename = {
                    'No': '문항번호', 'Score': '배점', 'Correct_Ans': '정답', 
                    'Exp_Diff': '예상난이도', 'Standard': '성취기준',
                    'Hard': '상', 'Medium': '중', 'Easy': '하'
                }
                info_display = info_display.rename(columns={k: v for k, v in info_rename.items() if k in info_display.columns})
                info_display = info_display.fillna('')
                info_display = info_display.replace('None', '')
                
                # 성취기준 컬럼에 왼쪽 정렬 클래스 적용
                def make_html_table(df, left_align_cols=None):
                    """DataFrame을 HTML 테이블로 변환 (특정 컬럼 왼쪽 정렬)"""
                    left_align_cols = left_align_cols or []
                    html = '<table class="styled-table">'
                    # Header
                    html += '<thead><tr>'
                    for col in df.columns:
                        html += f'<th>{col}</th>'
                    html += '</tr></thead>'
                    # Body
                    html += '<tbody>'
                    for _, row in df.iterrows():
                        html += '<tr>'
                        for col in df.columns:
                            val = row[col]
                            if col in left_align_cols:
                                html += f'<td class="left-align">{val}</td>'
                            else:
                                html += f'<td>{val}</td>'
                        html += '</tr>'
                    html += '</tbody></table>'
                    return html
                
                info_html = make_html_table(info_display, left_align_cols=['성취기준'])
                st.markdown(f'<div class="table-container">{info_html}</div>', unsafe_allow_html=True)
                
                st.divider()
                
                # 학생 성적 데이터 (아래)
                st.write("#### 🧑‍🎓 학생 성적 데이터")
                
                # 선택된 평가 정보 표시
                basis_str = "분할점수 기반" if analysis_basis == "분할점수 기반" else "학기말 성취도 기반"
                st.caption(f"📌 **선택된 평가:** {exam_type} | **분석 기준:** {basis_str} | **만점:** {max_score}점 | **반영비율:** {ratio}%")
                
                # 성취도 분포 시각화 (테이블 위에 표시)
                st.write("**점수 분포 분석**")
                
                # 그래프 유형 선택 (기본값을 "총점"으로 설정)
                score_type = st.selectbox("표시할 점수 유형을 선택하세요", ["총점", "학기말 원점수"], index=0)
                
                # 성취수준 색상 정의 (미도달 I 추가)
                achievement_colors = {
                    'A': '#1DD1A1',  # 초록색
                    'B': '#54A0FF',  # 파랑색
                    'C': '#FFD93D',  # 노랑색
                    'D': '#FF6348',  # 주황색
                    'E': '#EE5A6F',  # 빨강색
                    'I': '#868E96'   # 회색 (미도달)
                }
                
                # 분석용 데이터 준비
                dist_df = main_df.copy()
                
                if score_type == "학기말 원점수":
                    # 학기말 원점수 계산 (총점 × 반영비율%)
                    dist_df['Total_Score_Num'] = pd.to_numeric(dist_df['Total_Score'], errors='coerce').fillna(0)
                    dist_df['학기말 원점수'] = (dist_df['Total_Score_Num'] * ratio / 100).round(1)
                    score_df = dist_df[['학기말 원점수', 'Achievement']].dropna()
                    score_df = score_df.rename(columns={'학기말 원점수': '점수', 'Achievement': '성취수준'})
                    x_axis = '점수'
                    title_text = "<b>학기말 원점수 분포 (성취수준별)</b>"
                    max_semester_score = (max_score * ratio / 100)
                    nbins = max(3, int(max_semester_score / 10))  # 10점 간격으로 변경 (더 넓은 막대)
                    xaxis_range = [0, max_semester_score]
                else:  # 총점
                    dist_df['총점'] = pd.to_numeric(dist_df['Total_Score'], errors='coerce')
                    score_df = dist_df[['총점', 'Achievement']].dropna()
                    score_df = score_df.rename(columns={'총점': '점수', 'Achievement': '성취수준'})
                    x_axis = '점수'
                    title_text = "<b>총점 분포 (성취수준별)</b>"
                    nbins = 5  # 100점 ÷ 20점 간격 = 5개 (더 넓은 막대)
                    xaxis_range = [0, 100]
                
                # 성취수준 순서 정렬 (성취도가 높은 것이 오른쪽에 배치되도록 역순)
                # I(미도달)이 있으면 포함, 없으면 제외
                all_levels = ['I', 'E', 'D', 'C', 'B', 'A']  # 역순: 왼쪽이 낮음, 오른쪽이 높음
                available_levels = [level for level in all_levels if level in score_df['성취수준'].unique()]
                score_df['성취수준'] = pd.Categorical(score_df['성취수준'], categories=available_levels, ordered=True)
                
                # 점수 범위별로 binning
                bins = np.arange(int(xaxis_range[0]), int(xaxis_range[1]) + 10, int((xaxis_range[1] - xaxis_range[0]) / nbins))
                score_df['bin'] = pd.cut(score_df['점수'], bins=bins)
                
                # 각 bin별로 성취수준 카운트
                bin_counts = score_df.groupby(['bin', '성취수준']).size().unstack(fill_value=0)
                bin_labels = [f"{int(interval.left)}-{int(interval.right)}" for interval in bin_counts.index]
                
                # go.Figure로 그룹 막대 그래프 생성
                fig_dist = go.Figure()
                
                for level in available_levels:
                    if level in bin_counts.columns:
                        hover_texts = [f"성취수준: {level}\n점수 범위: {label}\n학생 수: {int(count)}명" 
                                      for label, count in zip(bin_labels, bin_counts[level])]
                        fig_dist.add_trace(go.Bar(
                            x=bin_labels,
                            y=bin_counts[level],
                            name=level,
                            hovertext=hover_texts,
                            hoverinfo="text",
                            marker=dict(
                                color=achievement_colors[level],
                                line=dict(color='rgba(0,0,0,0.4)', width=2)
                            )
                        ))
                
                fig_dist.update_layout(
                    title=title_text,
                    paper_bgcolor="rgba(0,0,0,0)", 
                    plot_bgcolor="rgba(240,242,246,0.3)", 
                    font_family="Pretendard",
                    height=400,
                    showlegend=True,
                    xaxis_title="점수",
                    yaxis_title="학생수",
                    barmode='group',
                    bargap=0.0,
                    bargroupgap=0.0,
                    margin=dict(l=60, r=120, t=80, b=60),
                    legend=dict(
                        title="성취수준",
                        orientation="v",
                        yanchor="top",
                        y=0.99,
                        xanchor="right",
                        x=0.99,
                        traceorder="normal"
                    )
                )
                
                st.plotly_chart(fig_dist, use_container_width=True)
                
                main_display = main_df.copy()
                
                # 전역 로직에서 이미 계산된 점수 컬럼 활용 (Select_Score, Essay_Score, Total_Score, Semester_Score)
                
                # 컬럼 순서 재정렬: 학번, 이름, 문항들, 선택형점수, 서답형점수, 총점, 학기말 원점수, 성취수준
                col_order = ['ID', 'Name'] + [f'Item_{i}' for i in range(1, 17)] + ['Select_Score', 'Essay_Score', 'Total_Score', 'Semester_Score', 'Achievement']
                col_order = [c for c in col_order if c in main_display.columns]
                main_display = main_display[col_order]
                
                main_rename = {
                    'ID': '학번', 'Name': '이름', 
                    'Select_Score': '선택형점수', 'Essay_Score': '서답형점수',
                    'Total_Score': '총점', 'Semester_Score': '학기말 원점수', 
                    'Achievement': '성취수준'
                }
                for i in range(1, 17):
                    main_rename[f'Item_{i}'] = f'문{i}'
                main_display = main_display.rename(columns={k: v for k, v in main_rename.items() if k in main_display.columns})
                
                # 숫자 컬럼 소수점 처리
                if '총점' in main_display.columns:
                    main_display['총점'] = pd.to_numeric(main_display['총점'], errors='coerce').round(1)
                
                main_display = main_display.fillna('')
                main_display = main_display.replace('None', '')
                
                main_html = make_html_table(main_display)
                st.markdown(f'<div class="table-container" style="max-height:450px;">{main_html}</div>', unsafe_allow_html=True)

            # --- [Tab 2] 전체 성취도 분석 ---
            with tab_summary:
                # 1. 상단 메트릭
                m1, m2, m3 = st.columns(3)
                m1.metric("전체 학생 수", f"{len(main_df)}명")
                m2.metric("평가 종류", exam_type)
                m3.metric("수행평가", "0개 (미연동)")

                st.divider()

                # 2. 성취도 분포 차트
                # 먼저 오른쪽 그래프의 필요 너비를 계산하기 위해 데이터 준비
                dist = main_df['Achievement'].value_counts().reset_index()
                dist.columns = ['성취수준', '학생 수']
                # 성취수준 순서 정렬 (A가 맨 위, I가 맨 아래)
                level_order = ['A', 'B', 'C', 'D', 'E', 'I']
                dist['성취수준'] = pd.Categorical(dist['성취수준'], categories=level_order, ordered=True)
                dist = dist.sort_values('성취수준', ascending=False)  # 역순 정렬 (A가 위, I가 아래)
                
                # 비율 계산
                total_students = dist['학생 수'].sum()
                dist['비율(%)'] = (dist['학생 수'] / total_students * 100).round(1)
                
                # 텍스트 라벨 생성
                text_labels = [f"{pct:.1f}% ({cnt}명)" for pct, cnt in zip(dist['비율(%)'], dist['학생 수'])]
                
                # 동적 우측 margin 계산 (텍스트 길이 기반)
                max_label_length = max(len(label) for label in text_labels)
                right_margin = 80 + max_label_length * 10  # 기본 80 + 문자당 약 10px
                
                # X축 범위 동적 계산 (텍스트가 모두 표시되도록)
                max_ratio = dist['비율(%)'].max()
                xaxis_max = max(60, max_ratio * 1.4)  # 최대 비율의 140% 또는 60 중 더 큰 값
                
                # 동적 컬럼 비율 계산 (X축 범위에 따라)
                if xaxis_max > 70:
                    col_left_width = 1
                    col_right_width = 1
                elif xaxis_max > 65:
                    col_left_width = 3
                    col_right_width = 2
                else:
                    col_left_width = 2
                    col_right_width = 1
                
                # 동적으로 계산된 비율로 컬럼 생성
                col_left, col_right = st.columns([col_left_width, col_right_width])
                
                with col_left:
                    fig_hist = px.histogram(main_df, x='Total_Score', color='Achievement', 
                                        title="<b>점수 분포 히스토그램 (성취수준별)</b>",
                                        nbins=10,
                                        labels={'Total_Score': '총점', 'Achievement': '성취수준'},
                                        category_orders={'Achievement': ['I', 'E', 'D', 'C', 'B', 'A']},
                                        barmode='group')
                    fig_hist.update_traces(
                        marker_line_color='rgba(0,0,0,0.4)',
                        marker_line_width=2,
                        hovertemplate="<extra></extra>성취수준: <b>%{fullData.name}</b><br>점수 범위: %{x}<br>학생 수: %{y}명"
                    )
                    fig_hist.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)", 
                        plot_bgcolor="rgba(240,242,246,0.3)", 
                        font_family="Pretendard",
                        height=400,
                        xaxis_title="총점",
                        yaxis_title="학생 수",
                        font=dict(size=12),
                        hovermode='x unified',
                        bargap=0.0,
                        bargroupgap=0.0,
                        barmode='group',
                        margin=dict(l=60, r=120, t=80, b=60),
                        legend=dict(
                            title="성취수준",
                            orientation="v",
                            yanchor="top",
                            y=0.99,
                            xanchor="right",
                            x=0.99
                        )
                    )
                    st.plotly_chart(fig_hist, use_container_width=True)
                with col_right:
                    
                    # 수평 막대 그래프 (비율 기반)
                    fig_barh = go.Figure()
                    
                    # 막대 추가 (비율)
                    fig_barh.add_trace(go.Bar(
                        x=dist['비율(%)'],
                        y=dist['성취수준'],
                        orientation='h',
                        name='비율(%)',
                        marker=dict(
                            color=[achievement_colors.get(level, '#999999') for level in dist['성취수준']]
                        ),
                        text=text_labels,
                        textposition='outside',
                        hovertemplate="<b>%{y}</b><br>비율: %{x:.1f}%<br>학생 수: %{customdata}명<extra></extra>",
                        customdata=dist['학생 수']
                    ))
                    
                    fig_barh.update_layout(
                        title="<b>성취수준별 학생 수</b>",
                        paper_bgcolor="rgba(0,0,0,0)", 
                        plot_bgcolor="rgba(240,242,246,0.2)",
                        font_family="Pretendard",
                        height=400,
                        showlegend=False,
                        font=dict
                    # [디버깅] 스타일 적용을 위해 숫자형으로 변환 보장
                    essay_analysis[('', '정답률(%)')] = pd.to_numeric(essay_analysis[('', '정답률(%)')], errors='coerce')
                    essay_analysis[('', '변별도')] = pd.to_numeric(essay_analysis[('', '변별도')], errors='coerce')
(size=11),
                        xaxis_title="비율(%)",
                        yaxis_title="성취수준",
                        margin=dict(l=80, r=right_margin),
                        xaxis=dict(range=[0, xaxis_max], showgrid=True, gridwidth=1, gridcolor=                # [중요] 컬럼을 MultiIndex로 명시적 변환 (튜플 리스
                # [디버깅] 스타일 적용을 위해 숫자형으로 변환 보장
                # 만약 object 타입으로 되어있으면 .bar() 스타일이 적용되지 않음
                analysis_df_multi[('', '정답률(%)')] = pd.to_numeric(analysis_df_multi[('', '정답률(%)')], errors='coerce')
                analysis_df_multi[('', '변별도')] = pd.to_numeric(analysis_df_multi[('', '변별도')], errors='coerce')
트 -> MultiIndex)
                analysis_df_multi.columns = pd.MultiIndex.from_tuples(
                    analysis_df_multi.columns, 
                    names=['분류', '세부항목']
                )
                
'rgba(200,200,200,0.2)'),
                        yaxis=dict(tickfont=dict(size=12))
                    )
                    
                    st.plotly_chart(fig_barh, use_container_width=True)

                st.divider()
                
                # 3. 학생별 상세                    .format(precision=1, subset=response_cols) \
 데이터 표
                st.subheader("📋 학생별 상세 성적 데이터")
                
                # 환산 점수 계산
                main_df['Converted_Score'] = (pd.to_numeric(main_df['Total_Score'], errors='coerce').fillna(0) / max_score * ratio).round(1)
                
                # 표시용 데이터 준비
                display_df = main_df.copy()
                cols_to_show = ['ID', 'Name'] + [f'Item_{i}' for i in range(1, 17)] + ['Total_Score', 'Converted_Score', 'Achievement']
                display_df = display_df[cols_to_show]
                
                # 컬럼명 변경
                rename_dict = {'ID': '번호', 'Name': '이름', 'Total_Score': f'원점수({max_score})', 'Converted_Score': f'지필환산({ratio}%)', 'Achievement': '성취수준'}
                for i in range(1, 17):
                    rename_dict[f'Item_{i}'] = f'문{i}'
                display_df = display_df.rename(columns=rename_dict)
                
                st.caption(f"학생의 성취수준은 평가별 반영비율({ratio}%)을 고려하여 100점 만점 단위로 환산한 점수를 반올림하여 정수로 변환한 원점수({max_score}점 만점)를 기준으로 분류합니다.")
                
                display_df = display_df.fillna('')
                display_df = display_df.replace('None', '')
                detail_html = make_html_table(display_df)
                st.markdown(f'<div class="table-container" style="max-height:500px;">{detail_html}</div>', unsafe_allow_html=True)

            # --- [Tab 3] 문항 분석 ---
            with tab_item:
                st.subheader("문항 난이도 및 변별도 진단")
                
                # res_df 컬럼명 한글화 (표시용)
                res_display = res_df.copy()
                res_display = res_display.rename(columns={
                    'No': '문항', 'Exp_Diff': '예상난이도', 'Score': '배점', 'Standard': '성취기준'
                })
                
                # P-D 차트 시각화
                fig_pd = px.scatter(res_display, x='정답률(P)', y='변별도(D)', text='문항', color='예상난이도',
                                size='배점', title="<b>문항 양호도 맵 (P-D Chart)</b>",
                                labels={'정답률(P)': '정답률(난이도) - 어려움 ⟵ ⟶ 쉬움', '변별도(D)': '변별도(변별력) - 낮음 ⟵ ⟶ 높음'},
                                color_discrete_map={'상': '#FF9F43', '중': '#54A0FF', '하': '#1DD1A1'})
                fig_pd.add_hline(y=0.4, line_dash="dash", line_color="gray", annotation_text="우수 변별 기준 (0.4)")
                fig_pd.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", 
                    plot_bgcolor="rgba(240,242,246,0.5)", 
                    font_family="Pretendard",
                    height=400,
                    hovermode='closest'
                       # [중요] 컬럼을 MultiIndex로 명시적 변환
                    essay_analysis.columns = pd.MultiIndex.from_tuples(
                        essay_analysis.columns, 
                        names=['분류', '세부항목']
                    )
                    
             )
                st.plotly_chart(fig_pd, use_container_width=True)
                
                # 상세 데이터 테이블
                st.caption("※ 문항 번호를 기준으로 정렬된 상세 지표입니다.")

                # DataFrame 스타일링 (표시 형식 및 정렬)
                styler = res_display.style.format("{:.2f}", subset=['정답률(P)', '변별도(D)'])
                
                # 성취기준 제외한 모든 컬럼 중앙 정렬 (명시적 지정)
                center_cols = [c for c in res_display.columns if c != '성취기준']
                styler.set_properties(subset=center_cols, **{'text-align': 'center'})
                
                # 성취기준 좌측 정렬
                styler.set_properties(subset=['성취기준'], **{'text-align': 'left'})

                st.dataframe(
                    styler,
                    use_container_width=True, # [복구] 전체 너비 사용
                    height=600,
                    hide_index=True,
                    column_config={
                        "문항": st.column_config.NumberColumn("문항", format="%d", width="small"),
                        "정답률(P)": st.column_config.NumberColumn("정답률(P)", format="%.2f", width="small"),
                        "변별도(D)": st.column_config.NumberColumn("변별도(D)", format="%.2f", width="small"),
                        "예상난이도": st.column_config.TextColumn("예상난이도", width="small"),
                        "배점": st.column_config.NumberColumn("배점", format="%d", width="small"),
                        "성취기준": st.column_config.TextColumn(
                            "성취기준",
                            width="large" # 가로 폭 넓게 설정
                        )
                    }
                )

            # --- [Tab 4] 성취수준별 답지반응 ---
            with tab_dist:
                st.subheader("문항별 반응 상세 분석")
                col_sel, col_desc = st.columns([1, 2])
                with col_sel:
                    sel_item = st.selectbox("분석할 문항 번호를 선택하세요", options=range(1, 17))
                with col_desc:
                    # 성취기준 없을 경우 대비
                    std_text = info_df.loc[info_df['No']==sel_item, 'Standard']
                    std_val = std_text.values[0] if not std_text.empty else "(성취기준 정보 없음)"
                    st.info(f"📌 **성취기준**: {std_val}")
                
                # 수준별 정답률 곡선
                # 안전한 Groupby 계산
                if sel_item:
                    level_perf = main_df.groupby('Achievement')[f'Item_{sel_item}'].apply(
                        lambda x: (x.astype(str) == '.').mean() * 100
                    ).reindex(['A','B','C','D','E']).fillna(0)
                    
                    fig_curve = go.Figure()
                    fig_curve.add_trace(go.Scatter(
                        x=level_perf.index, y=level_perf.values, 
                        mode='lines+markers+text', 
                        text=[f"{v:.1f}%" for v in level_perf.values],
                        textposition="top center",
                        name='정답률', 
                        line=dict(color='#636EFA', width=3)
                    ))
                    fig_curve.update_layout(
                        title=f"<b>{sel_item}번 문항: 성취수준별 정답률 추이</b>", 
                        xaxis_title="성취수준", 
                        yaxis_title="정답률 (%)",
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(240,242,246,0.3)",
                        font_family="Pretendard",
                        height=400,
                        font=dict(size=12),
                        hovermode='x unified'
                    )
                    st.plotly_chart(fig_curve, use_container_width=True)

            # --- [Tab 5] 성취기준 분석 결과 ---
            with tab_std:
                st.subheader("📜 성취기준별 분석 결과")
                
                # 성취기준별 그룹화
                std_stats = res_df.groupby('Standard').agg({
                    'No': 'count',
                    'Score': 'sum',
                    '정답률(P)': 'mean',
                    '변별도(D)': 'mean'
                }).reset_index()
                
                std_stats.columns = ['성취기준', '문항 수', '배점 합계', '평균 정답률', '평균 변별도']
                
                # 스타일링 (matplotlib 없이)
                st.dataframe(
                    std_stats.style.format({
                        '평균 정답률': '{:.2f}',
                        '평균 변별도': '{:.2f}'
                    }),
                    use_container_width=True,
                    hide_index=True
                )

            # --- [Tab 6] 분석 리포트 ---
            with tab_report:
                st.subheader("📝 AI 자동 분석 리포트 및 출제 제언")
                
                good_items = res_df[res_df['변별도(D)'] >= 0.4]['No'].tolist()
                bad_items = res_df[res_df['변별도(D)'] < 0.2]['No'].tolist()
                
                st.markdown(f"""
                #### 1. 평가 도구 종합 진단
                - **신뢰도:** 본 검사의 신뢰도는 **{alpha:.3f}**로, { '매우 높은 일관성(안정적)' if alpha >= 0.8 else '수용 가능한 수준' }을 보입니다.
                - **변별력:** 전체 문항 중 **{len(good_items)}개** 문항이 상위권과 하위권을 명확히 구분하는 **우수 문항**입니다.
                
                #### 2. 문항 개선 제언
                - **🌟 우수 문항:** {', '.join(map(str, good_items[:5]))}번 ... (변별력이 뛰어나 향후 유사한 유형으로 출제 권장)
                - **🔧 재검토 필요:** {', '.join(map(str, bad_items)) if bad_items else '없음'}번 ... (변별력이 낮아, 발문 수정이나 매력적인 오답지 개발이 필요함)
                
                #### 3. 차후 출제 가이드라인
                > **Tip:** 정답률이 지나치게 높거나 낮은 문항은 수업 중 강조점을 다시 확인하거나, 난이도 조절이 필요합니다.
                """)
    
    else:
        # 데이터 로드 실패시
        st.error("⚠️ **데이터 로드에 실패했습니다.**")
        st.info("""
        다음을 확인하세요:
        
        **정기고사 (분할점수 기반):**
        - 문항정보표와 학생 정오표 파일이 올바른 NEIS 양식인지 확인
        - 파일명에 특수문자가 없는지 확인
        
        **정기고사 (학기말 성취도 기반):**
        - 위의 확인사항 + 성적일람표가 성취도 정보를 포함하고 있는지 확인
        
        **수행평가:**
        - 평가기준표와 성적일람표가 올바른 양식인지 확인
        """)

else:
    # 데이터 미업로드 시 초기 화면
    st.container()
    st.info("👈 **시작하려면 왼쪽 사이드바에서 필요한 파일을 업로드하세요.**")
    
    if analysis_basis == "분할점수 기반":
        st.success("""
        #### 분석 방식: 입력 분할점수 기반 자동 판정
        
        왼쪽 설정에서 입력한 분할점수를 기준으로 학생 성적을 분석하여 **자동으로 성취도를 판정**합니다.
        """)
        if exam_type in ["1회 정기고사", "2회 정기고사"]:
            st.write(f"### 📝 {exam_type} 준비물")
            st.write("""
            1. **📑 문항정보표** - NEIS에서 다운로드
            2. **✍️ 학생 정오표** - NEIS에서 다운로드 (여러 반 가능)
            """)
        else:
            st.write("### 📝 수행평가 준비물")
            st.write("""
            1. **📑 평가기준표** - 수행평가 항목과 배점 정보
            """)
    else:  # 학기말 성취도 기반
        st.success("""
        #### 분석 방식: 성적일람표 성취도 기준
        
        성적일람표에 이미 판정되어 있는 성취도를 **그대로 사용**합니다.
        """)
        if exam_type in ["1회 정기고사", "2회 정기고사"]:
            st.write(f"### 📝 {exam_type} 준비물")
            st.write("""
            1. **📑 문항정보표** - NEIS에서 다운로드
            2. **✍️ 학생 정오표** - NEIS에서 다운로드 (여러 반 가능)
            3. **📊 성적일람표** - 성취도 정보 포함 (여러 반 가능)
            """)
        else:
            st.write("### 📝 수행평가 준비물")
            st.write("""
            1. **📑 평가기준표** - 수행평가 항목과 배점 정보
            2. **📊 성적일람표** - 수행평가 점수와 성취도 정보
            """)
    
    st.markdown("---")
    st.caption("🔒 데이터가 서버로 전송되지 않고 브라우저에서 안전하게 처리됩니다.")