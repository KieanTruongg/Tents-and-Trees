"""
test_greedy.py - Kiểm tra giải thuật Greedy Best-First Search kết hợp MRV trên bài test input_6x6.txt
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
from src.greedy_solver import GreedySolver

def main():
    print("=== KIỂM THỬ THUẬT TOÁN GREEDY BEST-FIRST SEARCH (HEURISTIC SEARCH) ===")
    test_file = os.path.join(BASE_DIR, "data", "6x6 hard tents.txt")
    if not os.path.exists(test_file):
        data_files = [f for f in os.listdir(os.path.join(BASE_DIR, "data")) if f.endswith(".txt")]
        if data_files:
            test_file = os.path.join(BASE_DIR, "data", sorted(data_files)[0])
    board = Board(test_file)

    print("\nBàn cờ ban đầu:")
    board.display()

    solver = GreedySolver(board)
    print("Đang giải bài toán bằng Greedy Best-First Search + MRV...")
    success = solver.solve()

    if success:
        print("\n [THÀNH CÔNG] ĐÃ TÌM THẤY LỜI GIẢI!")
        print("Bàn cờ sau khi giải:")
        board.display()
        print(f"Tổng số lều đã đặt: {len(board.tents)}")
        print(f"Vị trí các lều: {sorted(list(board.tents))}")
        print(f"Số trạng thái đã mở rộng (Nodes explored): {solver.nodes_explored}")
        print(f"Kích thước hàng đợi cực đại (Max Open): {solver.max_open}")
        print(f"Thời gian thực thi: {solver.execution_time * 1000:.3f} ms ({solver.execution_time:.6f} giây)")
        print(f"Tổng số bước trong lời giải: {len(solver.step_history)}")
    else:
        print("\n [THẤT BẠI] Không tìm thấy lời giải phù hợp.")

if __name__ == "__main__":
    main()
