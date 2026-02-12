import pandas as pd

# 강의실별 데이터 확인
for room in ['1', '4', '8']:
    print(f"\n\n{'='*60}")
    print(f"강의실 {room} 성적일람표")
    print('='*60)
    
    try:
        file = f'2025물리학Ⅰ성적일람표{room}.xlsx'
        df = pd.read_excel(file, sheet_name=0, header=None, engine='openpyxl', nrows=15)
        
        print(f"파일: {file}")
        print(f"크기: {df.shape}")
        print("\n첫 15행 (전체 열):")
        print(df.to_string())
        
        # 학번이 있는 열 찾기
        print("\n\n학번/이름 정보가 있는 영역:")
        df2 = pd.read_excel(file, sheet_name=0, header=None, engine='openpyxl', nrows=30)
        print(df2.iloc[:, :10].to_string())
        
    except Exception as e:
        print(f"오류: {e}")
