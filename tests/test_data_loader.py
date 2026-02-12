"""
데이터 로더 모듈 테스트
"""

import pytest
import pandas as pd
import numpy as np
from modules.data_loader import (
    extract_classroom_from_data,
    looks_like_korean_name,
    is_class_num_format,
    parse_class_num_to_id
)


class TestDataLoader:
    """데이터 로더 함수 테스트"""
    
    def test_extract_classroom_from_data(self):
        """강의실 번호 추출 테스트"""
        # 테스트 데이터 생성
        data = {
            0: ['학급', '1 강의실', '', '', ''],
            1: ['과목', '수학', '', '', '']
        }
        df = pd.DataFrame(data).T
        
        result = extract_classroom_from_data(df)
        assert result == '1'
    
    def test_extract_classroom_pattern_variations(self):
        """다양한 강의실 표기 패턴 테스트"""
        # "강의실 2" 패턴
        data1 = pd.DataFrame({0: ['', '강의실 2', '']}).T
        assert extract_classroom_from_data(data1) == '2'
        
        # "3강의실" 패턴
        data2 = pd.DataFrame({0: ['', '3강의실', '']}).T
        assert extract_classroom_from_data(data2) == '3'
    
    def test_looks_like_korean_name_valid(self):
        """올바른 한글 이름 검증"""
        assert looks_like_korean_name("홍길동") == True
        assert looks_like_korean_name("김철수") == True
        assert looks_like_korean_name("이영희") == True
    
    def test_looks_like_korean_name_invalid(self):
        """잘못된 이름 패턴 검증"""
        assert looks_like_korean_name("123") == False
        assert looks_like_korean_name("홍") == False  # 너무 짧음
        assert looks_like_korean_name("홍길동철수영희") == False  # 너무 김
        assert looks_like_korean_name("Hong") == False  # 영문
        assert looks_like_korean_name("") == False  # 빈 문자열
    
    def test_is_class_num_format_valid(self):
        """반/번호 형식 검증"""
        assert is_class_num_format("1/1") == True
        assert is_class_num_format("2-15") == True
        assert is_class_num_format("10/30") == True
    
    def test_is_class_num_format_invalid(self):
        """잘못된 반/번호 형식"""
        assert is_class_num_format("홍길동") == False
        assert is_class_num_format("123") == False
        assert is_class_num_format("1/") == False
    
    def test_parse_class_num_to_id(self):
        """반/번호를 학번으로 변환"""
        assert parse_class_num_to_id("1/1") == "20101"
        assert parse_class_num_to_id("3/15") == "20315"
        assert parse_class_num_to_id("10-5") == "21005"
    
    def test_parse_class_num_to_id_invalid(self):
        """잘못된 입력 처리"""
        assert parse_class_num_to_id("") == ""
        assert parse_class_num_to_id("abc") == ""
        assert parse_class_num_to_id(None) == ""


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
