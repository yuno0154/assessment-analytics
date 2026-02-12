"""
스타일 모듈 테스트
"""

import pytest
import pandas as pd
from modules.styles import (
    make_html_table,
    custom_bar_style,
    style_background_level_v2,
    merge_headers
)


class TestStyles:
    """스타일 함수 테스트"""
    
    def test_make_html_table_basic(self):
        """기본 HTML 테이블 생성 테스트"""
        data = {
            '이름': ['홍길동', '김철수'],
            '점수': [85, 90]
        }
        df = pd.DataFrame(data)
        
        html = make_html_table(df)
        
        # HTML 구조 검증
        assert '<table class="styled-table">' in html
        assert '<thead>' in html
        assert '<tbody>' in html
        assert '홍길동' in html
        assert '85' in html
    
    def test_make_html_table_left_align(self):
        """왼쪽 정렬 컬럼 테스트"""
        data = {
            '이름': ['홍길동'],
            '점수': [85]
        }
        df = pd.DataFrame(data)
        
        html = make_html_table(df, left_align_cols=['이름'])
        
        assert 'class="left-align"' in html
    
    def test_custom_bar_style_above_threshold(self):
        """기준값 이상일 때 배경색 테스트"""
        style = custom_bar_style(70, 60)
        assert '#ffffff' in style  # 흰색 배경
        assert '#90caf9' in style  # 파란색 막대
    
    def test_custom_bar_style_below_threshold(self):
        """기준값 미만일 때 배경색 테스트"""
        style = custom_bar_style(50, 60)
        assert '#eeeeee' in style  # 회색 배경
    
    def test_custom_bar_style_invalid(self):
        """잘못된 값 처리"""
        style = custom_bar_style('invalid', 60)
        assert style == ''
        
        style = custom_bar_style(None, 60)
        assert style == ''
    
    def test_style_background_level_v2(self):
        """성취수준별 배경색 테스트"""
        # 기준값 이상
        style = style_background_level_v2(70, 60)
        assert 'background-color: #ffffff' in style
        
        # 기준값 미만
        style = style_background_level_v2(50, 60)
        assert 'background-color: #eeeeee' in style
    
    def test_merge_headers(self):
        """헤더 병합 테스트"""
        html = """
        <thead>
        <tr><th>문항</th><th>난이도</th></tr>
        <tr><th>문항</th><th>상</th></tr>
        </thead>
        """
        
        result = merge_headers(html, ['문항'])
        
        # rowspan 속성이 추가되었는지 확인
        assert 'rowspan' in result


class TestHTMLGeneration:
    """HTML 생성 함수 통합 테스트"""
    
    def test_table_container_structure(self):
        """테이블 컨테이너 구조 검증"""
        data = {
            '문항': [1, 2, 3],
            '정답률': [0.85, 0.72, 0.91]
        }
        df = pd.DataFrame(data)
        
        html = make_html_table(df)
        
        # 필수 요소 확인
        assert '<table' in html
        assert '</table>' in html
        assert '<thead>' in html
        assert '<tbody>' in html
        
        # 데이터 확인
        for val in [1, 2, 3]:
            assert str(val) in html


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
