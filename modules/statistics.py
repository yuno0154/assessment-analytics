"""
통계 계산 모듈

문항 분석에 필요한 통계량(신뢰도, 변별도, 정답률 등)을 계산하는 기능을 제공합니다.
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple


def calculate_kr20_reliability(binary_matrix: pd.DataFrame) -> float:
    """
    KR-20 신뢰도를 계산합니다.
    
    Kuder-Richardson Formula 20은 이분형 문항(정답/오답)의 내적 일관성을 측정합니다.
    
    Args:
        binary_matrix (pd.DataFrame): 이진 행렬 (1=정답, 0=오답)
        
    Returns:
        float: KR-20 신뢰도 계수 (0~1)
        
    Formula:
        alpha = (k/(k-1)) * (1 - sum(p*q) / var_total)
        where k = 문항 수, p = 정답률, q = 오답률
        
    Examples:
        >>> binary_matrix = pd.DataFrame({
        ...     'Item_1': [1, 1, 0, 1],
        ...     'Item_2': [1, 0, 0, 1]
        ... })
        >>> reliability = calculate_kr20_reliability(binary_matrix)
        >>> print(f"{reliability:.3f}")
        0.667
    """
    var_sum = binary_matrix.var().sum()
    total_var = binary_matrix.sum(axis=1).var()
    
    if total_var == 0 or np.isnan(total_var):
        return 0.0
    
    k = len(binary_matrix.columns)  # 문항 수
    alpha = (k / (k - 1)) * (1 - var_sum / total_var)
    
    return alpha


def calculate_discrimination_index(
    df: pd.DataFrame, 
    item_cols: list, 
    total_score_col: str = 'Total_Score',
    percentile: float = 0.25
) -> Dict[int, float]:
    """
    문항별 변별도 지수를 계산합니다.
    
    변별도는 상위권 학생과 하위권 학생의 정답률 차이로 계산됩니다.
    높을수록 학생의 실력을 잘 구분하는 문항입니다.
    
    Args:
        df (pd.DataFrame): 학생 데이터
        item_cols (list): 문항 컬럼 리스트 ['Item_1', 'Item_2', ...]
        total_score_col (str): 총점 컬럼명 (기본값: 'Total_Score')
        percentile (float): 상위/하위 분할 비율 (기본값: 0.25 = 상위 25%, 하위 25%)
        
    Returns:
        Dict[int, float]: {문항번호: 변별도} 딕셔너리
        
    Note:
        - 변별도 해석 기준:
          * 0.40 이상: 매우 우수
          * 0.30~0.39: 우수
          * 0.20~0.29: 보통
          * 0.19 이하: 재검토 필요
          
    Examples:
        >>> discrimination = calculate_discrimination_index(df, ['Item_1', 'Item_2'])
        >>> print(discrimination)
        {1: 0.45, 2: 0.32}
    """
    top_len = max(1, int(len(df) * percentile))
    top_students = df.nlargest(top_len, total_score_col)
    bottom_students = df.nsmallest(top_len, total_score_col)
    
    discrimination_scores = {}
    
    for i, col in enumerate(item_cols, start=1):
        # 상위권과 하위권의 정답률 계산 ('.'가 정답 표시)
        p_top = (top_students[col].astype(str) == '.').mean()
        p_bottom = (bottom_students[col].astype(str) == '.').mean()
        discrimination_scores[i] = p_top - p_bottom
    
    return discrimination_scores


def calculate_correct_rate(df: pd.DataFrame, item_cols: list) -> Dict[int, float]:
    """
    문항별 정답률을 계산합니다.
    
    Args:
        df (pd.DataFrame): 학생 데이터
        item_cols (list): 문항 컬럼 리스트
        
    Returns:
        Dict[int, float]: {문항번호: 정답률(%)} 딕셔너리
        
    Examples:
        >>> correct_rate = calculate_correct_rate(df, ['Item_1', 'Item_2'])
        >>> print(correct_rate)
        {1: 0.85, 2: 0.67}
    """
    correct_rates = {}
    
    for i, col in enumerate(item_cols, start=1):
        correct_rates[i] = (df[col].astype(str) == '.').mean()
    
    return correct_rates


def calculate_achievement_statistics(
    df: pd.DataFrame, 
    achievement_col: str = 'Achievement',
    score_col: str = 'Total_Score',
    ratio: float = 1.0
) -> pd.DataFrame:
    """
    성취수준별 통계를 계산합니다.
    
    Args:
        df (pd.DataFrame): 학생 데이터
        achievement_col (str): 성취수준 컬럼명 (기본값: 'Achievement')
        score_col (str): 점수 컬럼명 (기본값: 'Total_Score')
        ratio (float): 반영비율 (기본값: 1.0 = 100%)
        
    Returns:
        pd.DataFrame: 성취수준별 통계 (학생수, 비율, 평균, 표준편차)
        
    Examples:
        >>> stats = calculate_achievement_statistics(df)
        >>> print(stats)
          성취수준  학생수  비율(%)  정기시험평균  원점수평균
        0       A     10    20.0       92.5     27.8
        1       B     25    50.0       78.3     23.5
    """
    df_copy = df.copy()
    df_copy[score_col] = pd.to_numeric(df_copy[score_col], errors='coerce').fillna(0)
    
    stat_list = []
    for achievement in sorted(df_copy[achievement_col].unique()):
        subset = df_copy[df_copy[achievement_col] == achievement][score_col]
        환산점수_subset = (subset * ratio / 100)
        
        stat_dict = {
            '성취수준': achievement,
            '학생수': len(subset),
            '비율(%)': (len(subset) / len(df_copy) * 100),
            '정기시험평균': subset.mean(),
            '정기시험표준편차': subset.std(),
            '원점수평균': 환산점수_subset.mean(),
            '원점수표준편차': 환산점수_subset.std()
        }
        stat_list.append(stat_dict)
    
    return pd.DataFrame(stat_list).round(2)


def calculate_item_response_distribution(
    df: pd.DataFrame, 
    item_num: int,
    correct_ans: str = ''
) -> Dict[str, int]:
    """
    특정 문항의 선택지별 응답 분포를 계산합니다.
    
    Args:
        df (pd.DataFrame): 학생 데이터
        item_num (int): 문항 번호 (1~16)
        correct_ans (str): 정답 번호 ('1'~'5')
        
    Returns:
        Dict[str, int]: {선택지: 응답수} 딕셔너리
        
    Examples:
        >>> dist = calculate_item_response_distribution(df, 1, '2')
        >>> print(dist)
        {'1': 3, '2': 25, '3': 5, '4': 2, '5': 1, '무응답': 0}
    """
    col = f'Item_{item_num}'
    item_responses = df[col].astype(str).value_counts()
    
    # 선택지별 카운트 (1~5번)
    choice_counts = {str(j): item_responses.get(str(j), 0) for j in range(1, 6)}
    
    # 정답 표시('.')를 해당 정답 번호에 합산
    correct_mark_count = item_responses.get('.', 0)
    if correct_ans in choice_counts:
        choice_counts[correct_ans] += correct_mark_count
    
    # 무응답 카운트
    no_response = item_responses.get('nan', 0) + item_responses.get('', 0)
    choice_counts['무응답'] = no_response
    
    return choice_counts


def calculate_level_correct_rate(
    df: pd.DataFrame,
    item_num: int,
    achievement_levels: list
) -> Dict[str, float]:
    """
    특정 문항의 성취수준별 정답률을 계산합니다.
    
    Args:
        df (pd.DataFrame): 학생 데이터
        item_num (int): 문항 번호
        achievement_levels (list): 성취수준 리스트 ['A', 'B', 'C', 'D', 'E']
        
    Returns:
        Dict[str, float]: {성취수준: 정답률(%)} 딕셔너리
        
    Examples:
        >>> rates = calculate_level_correct_rate(df, 1, ['A', 'B', 'C'])
        >>> print(rates)
        {'A': 95.0, 'B': 78.5, 'C': 45.2}
    """
    col = f'Item_{item_num}'
    level_rates = {}
    
    for level in achievement_levels:
        level_data = df[df['Achievement'] == level]
        if len(level_data) > 0:
            rate = (level_data[col].astype(str) == '.').mean() * 100
        else:
            rate = 0.0
        level_rates[level] = rate
    
    return level_rates


def safe_binary(x) -> int:
    """
    문항 응답을 이진값(1=정답, 0=오답)으로 변환합니다.
    
    Args:
        x: 응답 값 ('.' 또는 기타)
        
    Returns:
        int: 1 (정답) 또는 0 (오답)
        
    Examples:
        >>> safe_binary('.')
        1
        >>> safe_binary('1')
        0
    """
    return 1 if str(x).strip() == '.' else 0


def get_achievement_score_based(
    score: float, 
    cut_AB: float, 
    cut_BC: float, 
    cut_CD: Optional[float] = None,
    cut_DE: Optional[float] = None,
    cut_EI: Optional[float] = None
) -> str:
    """
    분할점수 기반으로 성취도를 판정합니다.
    
    Args:
        score (float): 학생 점수
        cut_AB (float): A/B 분할점수
        cut_BC (float): B/C 분할점수
        cut_CD (Optional[float]): C/D 분할점수 (5수준 이상일 때)
        cut_DE (Optional[float]): D/E 분할점수 (5수준 이상일 때)
        cut_EI (Optional[float]): E/미도달 분할점수 (5수준+미도달일 때)
        
    Returns:
        str: 성취수준 ('A', 'B', 'C', 'D', 'E', '미도달')
        
    Examples:
        >>> get_achievement_score_based(95, 90, 80, 70, 60, 40)
        'A'
        >>> get_achievement_score_based(35, 90, 80, 70, 60, 40)
        '미도달'
    """
    score = pd.to_numeric(score, errors='coerce')
    
    if pd.isna(score):
        return '미도달' if cut_EI is not None else 'E' if cut_CD is not None else 'C'
    
    if cut_CD is not None:  # 5수준 또는 5수준+미도달
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
                return '미도달'
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
    else:  # 3수준
        if score >= cut_AB:
            return 'A'
        elif score >= cut_BC:
            return 'B'
        else:
            return 'C'
