"""
test_board.py - Kiểm tra nạp và hiển thị cấu hình bàn cờ từ file input
"""
import os
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.board import Board

def main():
    test_file = os.path.join(BASE_DIR, "data", "6x6 easy tents.txt")
    if not os.path.exists(test_file):
        data_files = [f for f in os.listdir(os.path.join(BASE_DIR, "data")) if f.endswith(".txt")]
        if data_files:
            test_file = os.path.join(BASE_DIR, "data", sorted(data_files)[0])

    print(f"Đọc dữ liệu từ file: {os.path.basename(test_file)}")
    board = Board(test_file)
    
    print(f"- Kích thước: {board.rows} hàng x {board.cols} cột")
    print(f"- Hạn ngạch lều từng hàng: {board.row_constraints}")
    print(f"- Hạn ngạch lều từng cột:  {board.col_constraints}")
    print(f"- Tổng số cây: {len(board.trees)}")
    print(f"- Tọa độ các cây: {board.trees}")
    
    print("\nMa trận bàn cờ ban đầu:")
    board.display()

if __name__ == "__main__":
    main()
