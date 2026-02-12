"""
통계 계산 모듈 테스트
"""

import pytest
import pandas as pd
import numpy as np
from modules.statistics import (
    calculate_kr20_reliability,
    calculate_discrimination_index,
    calculate_correct_rate,
    safe_binary,
    get_achievement_score_based
)


class TestStatistics:
    """통계 계산 함수 테스트"""
    
    def test_safe_binary(self):
        """이진 변환 테스트"""
        assert safe_binary('.') == 1
        assert safe_binary('1') == 0
        assert safe_binary('X') == 0
        assert safe_binary('') == 0
    
    def test_calculate_kr20_reliability(self):
        """KR-20 신뢰도 계산 테스트"""
        # 간단한 이진 행렬 생성
        data = {
            'Item_1': [1, 1, 0, 1, 0],
            'Item_2': [1, 0, 0, 1, 1],
            'Item_3': [1, 1, 1, 1, 0]
        }
        df = pd.DataFrame(data)
        
        reliability = calculate_kr20_reliability(df)
        
        # 신뢰도는 0~1 사이
        assert 0 <= reliability <= 1
    
    def test_calculate_kr20_zero_variance(self):
        """분산이 0일 때 신뢰도 테스트"""
        # 모든 학생이 같은 점수
        data = {
            'Item_1': [1, 1, 1, 1],
            'Item_2': [1, 1, 1, 1]
        }
        df = pd.DataFrame(data)
        
        reliability = calculate_kr20_reliability(df)
        assert reliability == 0.0
    
    def test_calculate_discrimination_index(self):
        """변별도 계산 테스트"""
        data = {
            'Item_1': ['.', '.', '1', '2'],
            'Item_2': ['.', '1', '2', '2'],
            'Total_Score': [95, 85, 65, 55]
        }
        df = pd.DataFrame(data)
        item_cols = ['Item_1', 'Item_2']
        
        discrimination = calculate_discrimination_index(df, item_cols, percentile=0.5)
        
        # 변별도는 -1 ~ 1 사이
        for key, value in discrimination.items():
            assert -1 <= value <= 1
    
    def test_calculate_correct_rate(self):
        """정답률 계산 테스트"""
        data = {
            'Item_1': ['.', '.', '1', '2'],  # 50% 정답률
            'Item_2': ['.', '.', '.', '2']   # 75% 정답률
        }
        df = pd.DataFrame(data)
        item_cols = ['Item_1', 'Item_2']
        
        correct_rates = calculate_correct_rate(df, item_cols)
        
        assert correct_rates[1] == 0.5
        assert correct_rates[2] == 0.75
    
    def test_get_achievement_5level(self):
        """5수준 성취도 판정 테스트"""
        # 5수준 (A, B, C, D, E)
        assert get_achievement_score_based(95, 90, 80, 70, 60) == 'A'
        assert get_achievement_score_based(85, 90, 80, 70, 60) == 'B'
        assert get_achievement_score_based(75, 90, 80, 70, 60) == 'C'
        assert get_achievement_score_based(65, 90, 80, 70, 60) == 'D'
        assert get_achievement_score_based(55, 90, 80, 70, 60) == 'E'
    
    def test_get_achievement_5level_with_incomplete(self):
        """5수준+미도달 성취도 판정 테스트"""
        assert get_achievement_score_based(95, 90, 80, 70, 60, 40) == 'A'
        assert get_achievement_score_based(45, 90, 80, 70, 60, 40) == 'E'
        assert get_achievement_score_based(35, 90, 80, 70, 60, 40) == '미도달'
    
    def test_get_achievement_3level(self):
        """3수준 성취도 판정 테스트"""
        assert get_achievement_score_based(85, 80, 60) == 'A'
        assert get_achievement_score_based(70, 80, 60) == 'B'
        assert get_achievement_score_based(50, 80, 60) == 'C'
    
    def test_get_achievement_invalid_score(self):
        """잘못된 점수 입력 처리"""
        result = get_achievement_score_based(None, 90, 80, 70, 60, 40)
        assert result == '미도달'


class TestAchievementStatistics:
    """성취수준별 통계 테스트"""
    
    def test_calculate_achievement_statistics(self):
        """성취수준별 통계 계산 테스트"""
        from modules.statistics import calculate_achievement_statistics
        
        data = {
            'Achievement': ['A', 'A', 'B', 'B', 'C'],
            'Total_Score': [95, 90, 85, 80, 70]
        }
        df = pd.DataFrame(data)
        
        stats = calculate_achievement_statistics(df, ratio=30)
        
        # 결과 검증
        assert len(stats) == 3  # A, B, C
        assert '성취수준' in stats.columns
        assert '학생수' in stats.columns
        assert '비율(%)' in stats.columns


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
