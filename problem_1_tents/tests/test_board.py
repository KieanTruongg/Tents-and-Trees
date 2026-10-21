"""
test_board.py - Kiểm tra module Board với file input_6x6.txt
"""
import os
import sys
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.board import Board

def main():
    test_file = os.path.join(BASE_DIR, "data", "input_6x6.txt")
    print(f"Đang đọc file {test_file}...")
    board = Board(test_file)
    
    print(f"Kích thước bàn cờ: {board.rows} hàng x {board.cols} cột")
    print(f"Ràng buộc hàng: {board.row_constraints}")
    print(f"Ràng buộc cột: {board.col_constraints}")
    print(f"Số lượng cây tìm thấy: {len(board.trees)}")
    print(f"Tọa độ các cây: {board.trees}")
    
    print("\nHiển thị bàn cờ ban đầu:")
    board.display()
    
    print("Kiểm tra thử đặt 1 lều tại ô (0, 0)...")
    if board.can_place_tent(0, 0):
        print("-> Ô (0, 0) hợp lệ để đặt lều!")
        board.tents.add((0, 0))
        board.display()
    else:
        print("-> Ô (0, 0) KHÔNG hợp lệ.")

    print("Kiểm tra thử đặt tiếp 1 lều tại ô kề chéo (1, 1)...")
    if board.can_place_tent(1, 1):
        print("-> Ô (1, 1) hợp lệ.")
    else:
        print("-> Ô (1, 1) KHÔNG hợp lệ vì chạm lều tại (0, 0) theo đường chéo! (Ràng buộc hoạt động chính xác)")

if __name__ == "__main__":
    main()
