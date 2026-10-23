"""
dfs_solver.py -Blind Search: (DFS) + (Backtracking).
Môn học: Nhập môn Trí tuệ Nhân tạo (CO3061)
"""

import time
from src.board import Board

class DFSSolver:
    def __init__(self, board: Board):
        self.board = board
        self.nodes_explored = 0      # Đếm số trạng thái đã xét
        self.execution_time = 0.0    # Thời gian chạy 
        self.step_history = []       # Lưu lịch sử các bước để  demo trực quan GUI
                                     # Dạng: ("place", r, c) hoặc ("remove", r, c)
        self.solved = False

    def solve(self) -> bool:
        """
        Khởi chạy thuật toán DFS
        """
        self.nodes_explored = 0
        self.step_history = []
        self.board.tents.clear()  # clear board

        start_time = time.perf_counter()
        self.solved = self._backtrack(0)
        self.execution_time = time.perf_counter() - start_time

        return self.solved

    def _get_direction_name(self, tr: int, tc: int, nr: int, nc: int) -> str:
        """Xác định tên hướng di chuyển từ cây (tr, tc) đến ô (nr, nc)."""
        if nr < tr:
            return "Trên ↑"
        if nr > tr:
            return "Dưới ↓"
        if nc < tc:
            return "Trái ←"
        if nc > tc:
            return "Phải →"
        return "Không xác định"

    def _backtrack(self, tree_index: int) -> bool:
        """
        Hàm đệ quy DFS: tìm cách gán lều cho cây thứ tree_index
        """
        self.nodes_explored += 1

        # Early pruning: nếu vượt quá constraints thì cut nhánh
        for r in range(self.board.rows):
            cnt = sum(1 for (tr, tc) in self.board.tents if tr == r)
            if cnt > self.board.row_constraints[r]:
                return False
        for c in range(self.board.cols):
            cnt = sum(1 for (tr, tc) in self.board.tents if tc == c)
            if cnt > self.board.col_constraints[c]:
                return False

        # Đặt đủ tất cả các cây -> kiểm tra điều kiện đích (goal test)
        if tree_index == len(self.board.trees):
            return self.board.is_goal()

        tree_r, tree_c = self.board.trees[tree_index]

        # Lấy 4 ô quanh cây theo thứ tự tự nhiên: Trên -> Dưới -> Trái -> Phải
        adjacent_cells = self.board.get_adjacent_cells(tree_r, tree_c)

        for nr, nc in adjacent_cells:
            dir_name = self._get_direction_name(tree_r, tree_c, nr, nc)
            if self.board.can_place_tent(nr, nc):
                # 1. Đặt thử lều vào ô hợp lệ
                self.board.tents.add((nr, nc))
                self.step_history.append(("place", nr, nc, tree_index, dir_name, (tree_r, tree_c)))

                # 2. Đi sâu vào cây tiếp theo (Recursive DFS)
                if self._backtrack(tree_index + 1):
                    return True

                # 3. Nhánh phía sau bế tắc -> Quay lui (Backtracking), rút lều
                self.board.tents.remove((nr, nc))
                self.step_history.append(("remove", nr, nc, tree_index, dir_name, (tree_r, tree_c)))

        # Nếu không có ô nào của cây này hợp lệ hoặc dẫn đến đích -> Thất bại ở nhánh này
        return False
