"""
데이터 로더 모듈

NEIS 엑셀 파일(문항정보표, 정오표, 성적일람표)을 파싱하고 병합하는 기능을 제공합니다.
"""

import pandas as pd
import numpy as np
import re
import streamlit as st
from typing import Tuple, List, Optional


def extract_classroom_from_data(raw_preview: pd.DataFrame) -> Optional[str]:
    """
    정오표 파일의 상단 데이터에서 강의실 번호를 추출합니다.
    
    Args:
        raw_preview (pd.DataFrame): 정오표 파일의 상위 20행 미리보기 데이터
        
    Returns:
        Optional[str]: 강의실 번호 (예: "1", "2") 또는 None
        
    Examples:
        >>> df = pd.read_excel('ans.xlsx', nrows=20, header=None)
        >>> classroom = extract_classroom_from_data(df)
        >>> print(classroom)  # "1"
    """
    for row_idx in range(min(10, len(raw_preview))):
        row_str = ' '.join([str(val) for val in raw_preview.iloc[row_idx].values])
        # "강의실" 다음의 숫자 찾기 (예: "4 강의실", "강의실 1", "강의실1")
        match = re.search(r'(\d+)\s*강의실|강의실\s*(\d+)', row_str)
        if match:
            classroom = match.group(1) if match.group(1) else match.group(2)
            return classroom.strip()
    return None


def looks_like_korean_name(s: str) -> bool:
    """
    문자열이 한글 이름인지 검증합니다.
    
    Args:
        s (str): 검증할 문자열
        
    Returns:
        bool: 한글 이름이면 True, 아니면 False
        
    Examples:
        >>> looks_like_korean_name("홍길동")
        True
        >>> looks_like_korean_name("123")
        False
    """
    if pd.isna(s) or not isinstance(s, str):
        return False
    s = s.strip()
    if len(s) < 2 or len(s) > 5:
        return False
    return all('가' <= char <= '힣' for char in s)


def is_class_num_format(s: str) -> bool:
    """
    문자열이 '반/번호' 형식인지 확인합니다.
    
    Args:
        s (str): 검증할 문자열
        
    Returns:
        bool: '1/1', '2-3' 같은 형식이면 True
        
    Examples:
        >>> is_class_num_format("1/1")
        True
        >>> is_class_num_format("홍길동")
        False
    """
    if pd.isna(s):
        return False
    return bool(re.match(r'^\d+[/\-]\d+$', str(s).strip()))


def parse_class_num_to_id(s: str) -> str:
    """
    '반/번호' 형식을 학번으로 변환합니다.
    
    Args:
        s (str): '1/1' 형식의 반/번호
        
    Returns:
        str: '20101' 형식의 학번 (2학년 01반 01번)
        
    Examples:
        >>> parse_class_num_to_id("1/1")
        '20101'
        >>> parse_class_num_to_id("3-15")
        '20315'
    """
    if pd.isna(s):
        return ''
    s = str(s).strip()
    match = re.match(r'^(\d+)[/\-](\d+)$', s)
    if match:
        class_no = match.group(1).zfill(2)
        student_no = match.group(2).zfill(2)
        return f'2{class_no}{student_no}'
    return ''


def load_item_info(info_file) -> pd.DataFrame:
    """
    문항정보표를 로드하고 파싱합니다.
    
    Args:
        info_file: 업로드된 문항정보표 파일 객체
        
    Returns:
        pd.DataFrame: 파싱된 문항정보 (No, Standard, Hard, Medium, Easy, Score, Correct_Ans, Exp_Diff)
        
    Raises:
        ValueError: 파일 형식이 올바르지 않을 때
    """
    info = pd.read_excel(info_file, skiprows=10, engine='openpyxl', dtype={'No': str}).iloc[:22]
    info = info.iloc[:, [1, 3, 14, 16, 18, 19, 21]]
    info.columns = ['No', 'Standard', 'Hard', 'Medium', 'Easy', 'Score', 'Correct_Ans']
    
    # 유효한 문항 번호만 필터링
    info = info[info['No'].apply(lambda x: str(x).replace('.0','').strip().isdigit())].copy()
    info['No'] = info['No'].astype(float).astype(int)
    
    # 배점 숫자 변환
    info['Score'] = pd.to_numeric(info['Score'], errors='coerce').fillna(0)
    
    # 난이도 계산
    info['Exp_Diff'] = info.apply(
        lambda r: '상' if r['Hard']=='○' else ('중' if r['Medium']=='○' else '하'), 
        axis=1
    )
    
    return info


def load_answer_sheets(ans_files: List) -> pd.DataFrame:
    """
    학생 정오표 파일들을 로드하고 병합합니다.
    
    Args:
        ans_files (List): 업로드된 정오표 파일 리스트
        
    Returns:
        pd.DataFrame: 병합된 학생 정오표 데이터
        
    Raises:
        ValueError: 파일 파싱 실패 시
    """
    all_ans = []
    
    for f in ans_files:
        # 상위 20행 미리보기
        raw_preview = pd.read_excel(f, nrows=20, header=None, engine='openpyxl', dtype=str)
        
        # 강의실 정보 추출
        classroom_no = extract_classroom_from_data(raw_preview)
        
        header_row_idx = -1
        item_start_col_idx = -1
        name_col_idx = -1
        
        # 문항 번호 헤더 찾기
        item_col_map = {}
        for r_idx, row in raw_preview.iterrows():
            row_str = row.astype(str).values
            if '1' in row_str and '2' in row_str and '3' in row_str and '4' in row_str:
                header_row_idx = r_idx
                for c_idx, val in enumerate(row_str):
                    val_clean = str(val).strip().replace('.0', '')
                    if val_clean.isdigit():
                        item_num = int(val_clean)
                        if 1 <= item_num <= 16 and item_num not in item_col_map:
                            item_col_map[item_num] = c_idx
                if 1 in item_col_map:
                    item_start_col_idx = item_col_map[1]
                if len(item_col_map) >= 4:
                    break
        
        if header_row_idx == -1 or item_start_col_idx == -1:
            st.warning(f"'{f.name}' 파일에서 문항 번호 헤더를 찾을 수 없습니다.")
            continue
        
        # 데이터 로드
        data_start_row = header_row_idx + 3
        raw = pd.read_excel(f, skiprows=data_start_row, header=None, engine='openpyxl', dtype=str)
        
        # Name 컬럼 찾기
        name_col_idx_candidate = item_start_col_idx - 2
        if name_col_idx_candidate >= 0 and name_col_idx_candidate < len(raw.columns):
            sample_names = raw.iloc[:10, name_col_idx_candidate].dropna().tolist()
            korean_name_count = sum(1 for s in sample_names if looks_like_korean_name(s))
            
            if korean_name_count >= 3:
                name_col_idx = name_col_idx_candidate
            elif item_start_col_idx - 1 >= 0:
                sample_names_alt = raw.iloc[:10, item_start_col_idx - 1].dropna().tolist()
                korean_name_count_alt = sum(1 for s in sample_names_alt if looks_like_korean_name(s))
                name_col_idx = item_start_col_idx - 1 if korean_name_count_alt >= 3 else name_col_idx_candidate
            else:
                name_col_idx = name_col_idx_candidate
        else:
            name_col_idx = -1
        
        # 반/번호 컬럼 찾기
        class_num_col_idx = -1
        for col_offset in range(1, min(name_col_idx + 1, 4)):
            check_idx = name_col_idx - col_offset
            if check_idx >= 0 and check_idx < len(raw.columns):
                sample_vals = raw.iloc[:10, check_idx].tolist()
                valid_count = sum(1 for x in sample_vals if is_class_num_format(x))
                if valid_count >= 3:
                    class_num_col_idx = check_idx
                    break
        
        data = raw.copy()
        score_col_idx = len(raw.columns) - 1
        
        # 컬럼 매핑
        col_mapping = {}
        if name_col_idx != -1 and name_col_idx < len(data.columns):
            col_mapping[name_col_idx] = 'Name'
        else:
            data['Name'] = 'Unknown_' + data.index.astype(str)
        
        if class_num_col_idx != -1 and class_num_col_idx < len(data.columns):
            col_mapping[class_num_col_idx] = 'ClassNum'
        
        if score_col_idx < len(data.columns):
            col_mapping[score_col_idx] = 'Total_Score'
        else:
            data['Total_Score'] = 0
        
        data = data.rename(columns=col_mapping)
        
        # 반/번호 → 학번 변환
        if 'ClassNum' in data.columns:
            data['ID'] = data['ClassNum'].apply(parse_class_num_to_id)
            data = data.drop(columns=['ClassNum'])
        else:
            data['ID'] = ''
        
        # 문항 컬럼 매핑
        for item_num in range(1, 17):
            if item_num in item_col_map:
                q_idx = item_col_map[item_num]
            else:
                q_idx = item_start_col_idx + (item_num - 1)
            
            if q_idx < len(raw.columns):
                data[f'Item_{item_num}'] = raw.iloc[:, q_idx]
            else:
                data[f'Item_{item_num}'] = '.'
        
        # 불필요한 행 제거
        data = data[~data['Name'].isin(['정답', '배점', '합계', '평균', 'None', 'nan'])]
        
        # 강의실 정보 추가
        if classroom_no:
            data['강의실'] = classroom_no
        
        # 필요한 컬럼만 추출
        cols = ['ID', 'Name', 'Total_Score'] + [f'Item_{i}' for i in range(1, 17)]
        if classroom_no:
            cols.append('강의실')
        final_cols = [c for c in cols if c in data.columns]
        all_ans.append(data[final_cols])
    
    if not all_ans:
        return pd.DataFrame()
    
    ans_df = pd.concat(all_ans)
    ans_df = ans_df.dropna(subset=['Name'])
    ans_df['Name'] = ans_df['Name'].astype(str).str.strip()
    
    return ans_df


def load_grade_reports(grade_files: List) -> pd.DataFrame:
    """
    성적일람표 파일들을 로드하고 병합합니다.
    
    Args:
        grade_files (List): 업로드된 성적일람표 파일 리스트
        
    Returns:
        pd.DataFrame: 병합된 성적일람표 데이터 (Name, Achievement, ID)
        
    Raises:
        ValueError: 파일 파싱 실패 시
    """
    all_grades = []
    
    if not isinstance(grade_files, list):
        grade_files = [grade_files]
    
    for f in grade_files:
        raw_preview = pd.read_excel(f, nrows=30, header=None, engine='openpyxl', dtype=str)
        
        name_row_idx = -1
        grade_row_idx = -1
        name_col_idx = -1
        grade_col_idx = -1
        
        # 헤더 위치 찾기
        for r_idx, row in raw_preview.iterrows():
            row_str = row.astype(str).values
            for c_idx, val in enumerate(row_str):
                val_str = str(val)
                if name_col_idx == -1 and ('성명' in val_str or '이름' in val_str):
                    name_row_idx = r_idx
                    name_col_idx = c_idx
                if grade_col_idx == -1 and ('성취도' in val_str or '등급' in val_str):
                    grade_row_idx = r_idx
                    grade_col_idx = c_idx
        
        if name_col_idx != -1 and grade_col_idx != -1:
            data_start_row = max(name_row_idx, grade_row_idx) + 1
            g_raw = pd.read_excel(f, skiprows=data_start_row, header=None, engine='openpyxl', dtype=str)
            
            # Name 컬럼 보정
            def looks_like_name(s):
                if pd.isna(s) or len(str(s)) < 2:
                    return False
                return not any(char.isdigit() for char in str(s))
            
            sample_data = g_raw.iloc[:10, name_col_idx].tolist()
            valid_count = sum(looks_like_name(x) for x in sample_data)
            
            if valid_count < 3:
                for offset in range(1, 4):
                    if name_col_idx + offset < len(g_raw.columns):
                        sample_next = g_raw.iloc[:10, name_col_idx + offset].tolist()
                        if sum(looks_like_name(x) for x in sample_next) >= 3:
                            name_col_idx += offset
                            break
            
            # 반/번호 컬럼 찾기
            class_num_col_idx = name_col_idx - 1 if name_col_idx > 0 else -1
            
            if class_num_col_idx >= 0 and class_num_col_idx < len(g_raw.columns):
                sample_class = g_raw.iloc[:10, class_num_col_idx].tolist()
                valid_class_count = sum(1 for x in sample_class if is_class_num_format(x))
                
                if valid_class_count >= 3:
                    g_raw = g_raw.iloc[:, [class_num_col_idx, name_col_idx, grade_col_idx]]
                    g_raw.columns = ['ClassNum', 'Name', 'Achievement']
                    g_raw['ID'] = g_raw['ClassNum'].apply(parse_class_num_to_id)
                    g_raw = g_raw.drop(columns=['ClassNum'])
                else:
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
    
    if not all_grades:
        return pd.DataFrame()
    
    grade = pd.concat(all_grades)
    grade = grade.dropna(subset=['Name'])
    grade['Name'] = grade['Name'].astype(str).str.strip()
    
    return grade


def load_and_merge_data(
    info_file, 
    ans_files: List, 
    grade_files: List
) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]:
    """
    문항정보표, 정오표, 성적일람표를 로드하고 병합합니다.
    
    Args:
        info_file: 문항정보표 파일 객체
        ans_files (List): 정오표 파일 리스트
        grade_files (List): 성적일람표 파일 리스트
        
    Returns:
        Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]: 
            (문항정보 DataFrame, 병합된 학생 데이터 DataFrame)
            
    Examples:
        >>> info_df, main_df = load_and_merge_data(info_file, [ans1, ans2], [grade1])
        >>> print(main_df.columns)
        ['ID', 'Name', 'Total_Score', 'Item_1', ..., 'Achievement']
    """
    try:
        # 1. 문항정보표 로드
        info_df = load_item_info(info_file)
        
        # 2. 정오표 로드
        if ans_files:
            ans_df = load_answer_sheets(ans_files)
        else:
            ans_df = pd.DataFrame()
        
        # 3. 성적일람표 로드
        if grade_files:
            grade_df = load_grade_reports(grade_files)
        else:
            grade_df = pd.DataFrame()
        
        # 4. 병합
        if ans_df.empty and grade_df.empty:
            st.error("❌ 데이터를 로드할 수 없습니다.")
            return None, None
        
        if ans_df.empty:
            # 성적일람표만 있는 경우 (수행평가)
            merged = grade_df.copy()
            merged['Total_Score'] = 0
            for i in range(1, 17):
                merged[f'Item_{i}'] = '.'
        elif grade_df.empty:
            # 정오표만 있는 경우
            merged = ans_df.copy()
            if 'Achievement' not in merged.columns:
                merged['Achievement'] = 'E'
        else:
            # 둘 다 있는 경우 병합
            ans_students = set(ans_df['Name'].unique())
            grade_students = set(grade_df['Name'].unique())
            excluded_students = ans_students - grade_students
            
            if excluded_students:
                st.warning(
                    f"⚠️ **학생 수 불일치 감지**\n\n"
                    f"• 정오표 학생 수: {len(ans_students)}명\n"
                    f"• 성적일람표 학생 수: {len(grade_students)}명\n\n"
                    f"**성적일람표를 기준으로 {len(excluded_students)}명 제외**"
                )
            
            merged = pd.merge(
                ans_df, 
                grade_df[['Name', 'Achievement', 'ID']], 
                on='Name', 
                how='inner', 
                suffixes=('', '_grade')
            )
            
            # ID 우선순위: 정오표 > 성적일람표
            if 'ID' in merged.columns and 'ID_grade' in merged.columns:
                merged['ID'] = merged.apply(
                    lambda row: row['ID'] if row['ID'] and str(row['ID']).strip() else row['ID_grade'],
                    axis=1
                )
                merged = merged.drop(columns=['ID_grade'])
            elif 'ID_grade' in merged.columns:
                merged['ID'] = merged['ID_grade']
                merged = merged.drop(columns=['ID_grade'])
        
        if merged.empty:
            st.warning("⚠️ 분석할 데이터가 없습니다.")
            return info_df, pd.DataFrame()
        
        merged['Total_Score'] = pd.to_numeric(merged['Total_Score'], errors='coerce').fillna(0)
        return info_df, merged.dropna(subset=['Achievement'])
        
    except Exception as e:
        st.error(f"데이터 처리 중 오류가 발생했습니다: {e}")
        import traceback
        st.error(f"```\n{traceback.format_exc()}\n```")
        return None, None
