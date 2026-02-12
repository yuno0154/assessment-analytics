"""
시각화 모듈

Plotly 기반의 차트 및 그래프 생성 기능을 제공합니다.
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Optional


# 성취수준별 색상 정의
ACHIEVEMENT_COLORS = {
    'A': '#1DD1A1',  # 초록색
    'B': '#54A0FF',  # 파랑색
    'C': '#FFD93D',  # 노랑색
    'D': '#FF6348',  # 주황색
    'E': '#EE5A6F',  # 빨강색
    '미도달': '#868E96'  # 회색
}


def create_score_distribution_chart(
    df: pd.DataFrame,
    score_type: str = "총점",
    max_score: float = 100,
    ratio: float = 30,
    level_type: str = "5수준 (A, B, C, D, E)"
) -> go.Figure:
    """
    점수 분포 막대 그래프를 생성합니다.
    
    Args:
        df (pd.DataFrame): 학생 데이터
        score_type (str): "총점" 또는 "학기말 원점수"
        max_score (float): 만점
        ratio (float): 반영비율(%)
        level_type (str): 성취수준 유형
        
    Returns:
        go.Figure: Plotly Figure 객체
    """
    dist_df = df.copy()
    
    if score_type == "학기말 원점수":
        dist_df['Total_Score_Num'] = pd.to_numeric(dist_df['Total_Score'], errors='coerce').fillna(0)
        dist_df['학기말 원점수'] = (dist_df['Total_Score_Num'] * ratio / 100).round(1)
        score_df = dist_df[['학기말 원점수', 'Achievement']].dropna()
        score_df = score_df.rename(columns={'학기말 원점수': '점수', 'Achievement': '성취수준'})
        title_text = "<b>학기말 원점수 분포 (성취수준별)</b>"
        max_semester_score = (max_score * ratio / 100)
        nbins = max(3, int(max_semester_score / 10))
        xaxis_range = [0, max_semester_score]
    else:
        dist_df['총점'] = pd.to_numeric(dist_df['Total_Score'], errors='coerce')
        score_df = dist_df[['총점', 'Achievement']].dropna()
        score_df = score_df.rename(columns={'총점': '점수', 'Achievement': '성취수준'})
        title_text = "<b>총점 분포 (성취수준별)</b>"
        xaxis_range = [0, 100]
    
    # 성취수준 순서
    if level_type == "3수준 (A, B, C)":
        all_levels = ['A', 'B', 'C']
    elif level_type == "5수준+미도달 (A, B, C, D, E, 미도달)":
        all_levels = ['A', 'B', 'C', 'D', 'E', '미도달']
    else:
        all_levels = ['A', 'B', 'C', 'D', 'E']
    
    available_levels = [level for level in all_levels if level in score_df['성취수준'].unique()]
    score_df['성취수준'] = pd.Categorical(score_df['성취수준'], categories=available_levels, ordered=True)
    
    # 점수 범위별 binning
    import numpy as np
    bins = np.arange(int(xaxis_range[0]), int(xaxis_range[1]) + 10, 10)
    score_df['bin'] = pd.cut(score_df['점수'], bins=bins)
    
    # 각 bin별 성취수준 카운트
    bin_counts = score_df.groupby(['bin', '성취수준']).size().unstack(fill_value=0)
    bin_labels = [f"{int(interval.left)}-{int(interval.right)}" for interval in bin_counts.index]
    
    fig = go.Figure()
    
    for level in available_levels:
        if level in bin_counts.columns:
            hover_texts = [
                f"성취수준: {level}\n점수 범위: {label}\n학생 수: {int(count)}명"
                for label, count in zip(bin_labels, bin_counts[level])
            ]
            fig.add_trace(go.Bar(
                x=bin_labels,
                y=bin_counts[level],
                name=level,
                hovertext=hover_texts,
                hoverinfo="text",
                marker=dict(
                    color=ACHIEVEMENT_COLORS.get(level, '#999999'),
                    line=dict(color='rgba(0,0,0,0.4)', width=2)
                )
            ))
    
    fig.update_layout(
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
    
    return fig


def create_achievement_distribution_chart(
    dist: pd.DataFrame,
    level_order: List[str]
) -> go.Figure:
    """
    성취수준별 학생 수 수평 막대 그래프를 생성합니다.
    
    Args:
        dist (pd.DataFrame): 성취수준별 통계 (columns: 성취수준, 학생 수, 비율)
        level_order (List[str]): 성취수준 순서
        
    Returns:
        go.Figure: Plotly Figure 객체
    """
    dist['성취수준'] = pd.Categorical(dist['성취수준'], categories=level_order, ordered=True)
    dist = dist.sort_values('성취수준', ascending=False)
    
    total_students = dist['학생 수'].sum()
    dist['비율(%)'] = (dist['학생 수'] / total_students * 100).round(1)
    
    text_labels = [f"{pct:.1f}% ({cnt}명)" for pct, cnt in zip(dist['비율(%)'], dist['학생 수'])]
    
    max_label_length = max(len(label) for label in text_labels)
    right_margin = 80 + max_label_length * 10
    
    max_ratio = dist['비율(%)'].max()
    xaxis_max = max(60, max_ratio * 1.4)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=dist['비율(%)'],
        y=dist['성취수준'],
        orientation='h',
        marker=dict(
            color=[ACHIEVEMENT_COLORS.get(level, '#999999') for level in dist['성취수준']]
        ),
        text=text_labels,
        textposition='outside',
        hovertemplate="<b>%{y}</b><br>비율: %{x:.1f}%<br>학생 수: %{customdata}명<extra></extra>",
        customdata=dist['학생 수']
    ))
    
    fig.update_layout(
        title="<b>성취수준별 학생 수</b>",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(240,242,246,0.2)",
        font_family="Pretendard",
        height=400,
        showlegend=False,
        font=dict(size=11),
        xaxis_title="비율(%)",
        yaxis_title="성취수준",
        margin=dict(l=80, r=right_margin),
        xaxis=dict(range=[0, xaxis_max], showgrid=True, gridwidth=1, gridcolor='rgba(200,200,200,0.2)'),
        yaxis=dict(tickfont=dict(size=12))
    )
    
    return fig


def create_achievement_average_chart(
    avg_data: pd.DataFrame,
    level_order: List[str],
    score_type: str = "1회 정기시험",
    y_max: float = 100
) -> go.Figure:
    """
    성취수준별 평균 점수 수직 막대 그래프를 생성합니다.
    
    Args:
        avg_data (pd.DataFrame): 성취수준별 평균 데이터 (성취수준, 평균, 표준편차)
        level_order (List[str]): 성취수준 순서
        score_type (str): 점수 유형
        y_max (float): Y축 최댓값
        
    Returns:
        go.Figure: Plotly Figure 객체
    """
    avg_data['성취수준'] = pd.Categorical(avg_data['성취수준'], categories=level_order, ordered=True)
    avg_data = avg_data.sort_values('성취수준')
    
    y_title = "1회 정기시험 평균" if score_type == "1회 정기시험" else "학기말 원점수 평균"
    graph_title = f"<b>성취수준별 평균 ({score_type})</b>"
    
    hover_text = [
        f"<b style='font-size:14px'>{row['성취수준']}</b><br>" +
        f"<span style='font-size:13px'>평균: <b>{row['평균']:.2f}</b>점</span><br>" +
        f"<span style='font-size:13px'>표준편차: <b>{row['표준편차']:.2f}</b></span>"
        for _, row in avg_data.iterrows()
    ]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=avg_data['성취수준'],
        y=avg_data['평균'],
        marker=dict(
            color=[ACHIEVEMENT_COLORS.get(level, '#999999') for level in avg_data['성취수준']],
            line=dict(color='rgba(0,0,0,0.3)', width=1.5)
        ),
        text=[f"<b>{val:.2f}</b>" for val in avg_data['평균']],
        textposition='outside',
        textfont=dict(size=13, color='black'),
        hovertemplate="%{customdata}<extra></extra>",
        customdata=hover_text
    ))
    
    fig.update_layout(
        title=graph_title,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(240,242,246,0.2)",
        font_family="Pretendard",
        height=400,
        showlegend=False,
        font=dict(size=11),
        xaxis_title="성취수준",
        yaxis_title=y_title,
        margin=dict(l=60, r=60, t=80, b=60),
        yaxis=dict(range=[0, y_max * 1.15], showgrid=True, gridwidth=1, gridcolor='rgba(200,200,200,0.2)'),
        xaxis=dict(tickfont=dict(size=13))
    )
    
    return fig


def create_pd_chart(res_df: pd.DataFrame) -> go.Figure:
    """
    문항 양호도 맵(P-D Chart)을 생성합니다.
    
    Args:
        res_df (pd.DataFrame): 문항 분석 결과 (No, 정답률(P), 변별도(D), Exp_Diff, Score)
        
    Returns:
        go.Figure: Plotly Scatter 차트
    """
    res_display = res_df.copy()
    res_display = res_display.rename(columns={
        'No': '문항', 'Exp_Diff': '예상난이도', 'Score': '배점', 'Standard': '성취기준'
    })
    
    fig = px.scatter(
        res_display,
        x='정답률(P)',
        y='변별도(D)',
        text='문항',
        color='예상난이도',
        size='배점',
        title="<b>문항 난이도 및 변별력 분석</b>",
        labels={
            '정답률(P)': '정답률(난이도) - 어려움 ⟵ ⟶ 쉬움',
            '변별도(D)': '변별도(변별력) - 낮음 ⟵ ⟶ 높음'
        },
        color_discrete_map={'상': '#FF9F43', '중': '#54A0FF', '하': '#1DD1A1'}
    )
    
    fig.add_hline(
        y=0.4,
        line_dash="dash",
        line_color="gray",
        annotation_text="우수 변별 기준 (0.4)"
    )
    
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(240,242,246,0.5)",
        font_family="Pretendard",
        height=400,
        hovermode='closest'
    )
    
    return fig


def create_level_performance_curve(
    level_perf: pd.Series,
    item_num: int
) -> go.Figure:
    """
    특정 문항의 성취수준별 정답률 추이 그래프를 생성합니다.
    
    Args:
        level_perf (pd.Series): 성취수준별 정답률
        item_num (int): 문항 번호
        
    Returns:
        go.Figure: Plotly Line 차트
    """
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=level_perf.index,
        y=level_perf.values,
        mode='lines+markers+text',
        text=[f"{v:.1f}%" for v in level_perf.values],
        textposition="top center",
        name='정답률',
        line=dict(color='#636EFA', width=3)
    ))
    
    fig.update_layout(
        title=f"<b>{item_num}번 문항: 성취수준별 정답률 추이</b>",
        xaxis_title="성취수준",
        yaxis_title="정답률 (%)",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(240,242,246,0.3)",
        font_family="Pretendard",
        height=400,
        font=dict(size=12),
        hovermode='x unified'
    )
    
    return fig
