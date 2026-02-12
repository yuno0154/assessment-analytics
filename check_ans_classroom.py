import pandas as pd

# 정오표 파일 구조 확인
for num in ['', '1', '4', '8']:
    filename = f'2025물리학Ⅰ1회지필 학생답정오표{num}.xlsx'
    print(f"\n{'='*60}")
    print(f"정오표 파일: {filename}")
    print('='*60)
    
    try:
        # 상단 20행 확인
        df = pd.read_excel(filename, sheet_name=0, header=None, engine='openpyxl', nrows=15)
        print(f"크기: {df.shape}")
        print("\n첫 15행 (첫 6열):")
        print(df.iloc[:, :6].to_string())
    except Exception as e:
        print(f"오류: {e}")
