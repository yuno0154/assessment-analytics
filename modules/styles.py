"""
스타일링 모듈

HTML/CSS 스타일 처리 및 테이블 렌더링 기능을 제공합니다.
"""

import pandas as pd
import re
import streamlit.components.v1 as components
from typing import Optional, List


def get_custom_css() -> str:
    """
    Streamlit 앱에 적용할 커스텀 CSS를 반환합니다.
    
    Returns:
        str: CSS 스타일 문자열
    """
    return """
    <style>
    /* 폰트 적용 (Pretendard) */
    @import url("https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css");
    
    html, body, [class*="css"] {
        font-family: 'Pretendard', sans-serif;
    }

    /* 전체 배경 */
    .stApp {
        background-color: #FFFFFF;
        color: #1E293B;
    }

    /* 타이틀 스타일 */
    h1 {
        color: #1E3A8A;
        font-weight: 800;
        font-size: 2.2rem !important;
        margin-bottom: 0.5rem;
        letter-spacing: -0.05rem;
    }
    
    h2, h3, h4 {
        color: #334155;
        font-weight: 700;
        letter-spacing: -0.03rem;
    }

    /* 메트릭 스타일 */
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

    /* 사이드바 */
    [data-testid="stSidebar"] {
        background-color: #F8F9FA;
        border-right: 1px solid #E2E8F0;
    }
    
    /* 파일 업로더 한글화 */
    [data-testid="stFileUploader"] {
        background-color: #FFFFFF;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 10px;
    }
    
    [data-testid="stFileUploader"] small {
        display: none !important;
    }

    [data-testid="stFileUploaderDropzoneInstructions"] {
        display: none !important;
    }

    [data-testid="stFileUploaderDropzone"] button {
        font-size: 0px !important;
        line-height: 0px !important;
        padding: 0px !important;
        width: 100%;
        min-height: 38px;
        background: transparent !important;
        border: none !important;
    }
    
    [data-testid="stFileUploaderDropzone"] button div {
        display: none !important;
        visibility: hidden !important;
    }

    [data-testid="stFileUploaderDropzone"] button::after {
        content: "📂 파일 열기";
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: #EFF6FF; 
        color: #1E3A8A;
        border: 1px solid #BFDBFE;
        border-radius: 6px;
        font-size: 0.9rem !important;
        font-weight: 700;
        width: 100%;
        height: 100%;
        min-height: 38px;
        padding: 8px 16px;
        cursor: pointer;
        transition: all 0.2s ease-in-out;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    
    [data-testid="stFileUploaderDropzone"] button:hover::after {
        background-color: #DBEAFE;
        border-color: #93C5FD;
        transform: translateY(-1px);
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    [data-testid="stFileUploaderDropzone"] button:active::after {
        background-color: #BFDBFE;
        transform: translateY(0px);
        box-shadow: none;
    }

    /* 데이터프레임 */
    [data-testid="stDataFrame"] {
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid #E2E8F0;
    }
    
    [data-testid="stDataFrame"] [data-testid="StyledDataFrameCell"] {
        text-align: center !important;
        justify-content: center !important;
    }
    
    [data-testid="stDataFrame"] [data-testid="StyledDataFrameHeaderCell"] {
        text-align: center !important;
        justify-content: center !important;
        font-weight: 700 !important;
    }
    </style>
    """


def get_table_style() -> str:
    """
    HTML 테이블 스타일 CSS를 반환합니다.
    
    Returns:
        str: 테이블 CSS 스타일 문자열
    """
    return """
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
    .styled-table td.left-align {
        text-align: left !important;
    }
    </style>
    """


def make_html_table(df: pd.DataFrame, left_align_cols: Optional[List[str]] = None) -> str:
    """
    DataFrame을 HTML 테이블로 변환합니다.
    
    Args:
        df (pd.DataFrame): 변환할 DataFrame
        left_align_cols (Optional[List[str]]): 왼쪽 정렬할 컬럼 리스트
        
    Returns:
        str: HTML 테이블 문자열
        
    Examples:
        >>> df = pd.DataFrame({'이름': ['홍길동'], '점수': [85]})
        >>> html = make_html_table(df, left_align_cols=['이름'])
    """
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


def make_multi_header_table(df: pd.DataFrame) -> str:
    """
    2단계 헤더를 가진 HTML 테이블을 생성합니다.
    
    Args:
        df (pd.DataFrame): 통계 데이터 (성취수준, 학생수, 비율, 평균, 표준편차 등)
        
    Returns:
        str: HTML 테이블 문자열
    """
    html = '<table class="styled-table" style="width:100%; border-collapse: collapse;">'
    
    # 2-level Header
    html += '<thead>'
    html += '<tr style="text-align: center;">'
    html += '<th rowspan="2" style="vertical-align: middle; border: 1px solid #ddd; padding: 12px;">성취수준</th>'
    html += '<th rowspan="2" style="vertical-align: middle; border: 1px solid #ddd; padding: 12px;">학생수</th>'
    html += '<th rowspan="2" style="vertical-align: middle; border: 1px solid #ddd; padding: 12px;">비율(%)</th>'
    html += '<th colspan="2" style="border: 1px solid #ddd; padding: 12px; background-color: #f8f9fa;">1회 정기시험</th>'
    html += '<th colspan="2" style="border: 1px solid #ddd; padding: 12px; background-color: #f8f9fa;">학기말 원점수</th>'
    html += '</tr>'
    html += '<tr style="text-align: center;">'
    html += '<th style="border: 1px solid #ddd; padding: 12px; background-color: #f8f9fa;">평균</th>'
    html += '<th style="border: 1px solid #ddd; padding: 12px; background-color: #f8f9fa;">표준편차</th>'
    html += '<th style="border: 1px solid #ddd; padding: 12px; background-color: #f8f9fa;">평균</th>'
    html += '<th style="border: 1px solid #ddd; padding: 12px; background-color: #f8f9fa;">표준편차</th>'
    html += '</tr>'
    html += '</thead>'
    
    # Body
    html += '<tbody>'
    for _, row in df.iterrows():
        html += '<tr style="text-align: center;">'
        html += f'<td style="border: 1px solid #ddd; padding: 10px;"><b>{row["성취수준"]}</b></td>'
        html += f'<td style="border: 1px solid #ddd; padding: 10px;">{int(row["학생수"])}</td>'
        html += f'<td style="border: 1px solid #ddd; padding: 10px;">{row["비율(%)"]:.1f}</td>'
        html += f'<td style="border: 1px solid #ddd; padding: 10px;">{row["정기시험평균"]:.2f}</td>'
        html += f'<td style="border: 1px solid #ddd; padding: 10px;">{row["정기시험표준편차"]:.2f}</td>'
        html += f'<td style="border: 1px solid #ddd; padding: 10px;">{row["원점수평균"]:.2f}</td>'
        html += f'<td style="border: 1px solid #ddd; padding: 10px;">{row["원점수표준편차"]:.2f}</td>'
        html += '</tr>'
    html += '</tbody></table>'
    
    return html


def merge_headers(html_content: str, target_cols: List[str]) -> str:
    """
    HTML 테이블의 특정 컬럼 헤더를 rowspan으로 병합합니다.
    
    Args:
        html_content (str): HTML 테이블 문자열
        target_cols (List[str]): 병합할 컬럼명 리스트
        
    Returns:
        str: 수정된 HTML 문자열
    """
    thead_match = re.search(r'(<thead[^>]*>)(.*?)(</thead>)', html_content, re.DOTALL)
    if not thead_match:
        return html_content
    
    thead_open, thead_body, thead_close = thead_match.groups()
    rows = re.findall(r'(<tr[^>]*>)(.*?)(</tr>)', thead_body, re.DOTALL)
    
    if len(rows) < 2:
        return html_content
    
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


def render_datatables(html_content: str, unique_id: str) -> None:
    """
    DataTables.js를 사용하여 정렬 가능한 테이블을 렌더링합니다.
    
    Args:
        html_content (str): HTML 테이블 컨텐츠
        unique_id (str): 테이블 고유 ID
        
    Note:
        Streamlit components.html()을 사용하여 렌더링됩니다.
    """
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
    components.html(datatables_html, height=600, scrolling=True)


def custom_bar_style(val, threshold: float) -> str:
    """
    셀에 배경 막대 그래프 스타일을 적용합니다.
    
    Args:
        val: 셀 값
        threshold (float): 기준값 (이상이면 흰색, 미만이면 회색 배경)
        
    Returns:
        str: CSS 스타일 문자열
    """
    try:
        v = float(val)
        if pd.isna(v):
            return ''
        bg_color = '#eeeeee' if v < threshold else '#ffffff'
        return f"background: linear-gradient(90deg, #90caf9 {v}%, {bg_color} {v}%); color: black;"
    except:
        return ''


def style_background_level_v2(val, threshold: float) -> str:
    """
    성취수준별 정답률에 배경색을 적용합니다.
    
    Args:
        val: 셀 값
        threshold (float): 기준값
        
    Returns:
        str: CSS 스타일 문자열
    """
    try:
        if isinstance(val, str):
            return ''
        v = float(val)
        bg_color = '#eeeeee' if v < threshold else '#ffffff'
        return f'background-color: {bg_color}; color: black;'
    except:
        return ''
