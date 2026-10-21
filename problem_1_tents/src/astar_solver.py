"""
astar_solver.py - Hiện thực giải thuật Heuristic Search A* kết hợp CSP Forward Checking cho game Tents and Trees.
Môn học: Nhập môn Trí tuệ Nhân tạo (CO3061)
"""

import heapq
import time
from src.board import Board

class AStarNode:
    """
    Biểu diễn một nút trạng thái trong không gian tìm kiếm của A*.
    """
    def __init__(self, tree_index: int, tents: frozenset, g_cost: int, h_cost: int, history: list):
        self.tree_index = tree_index  # Cây tiếp theo cần gán lều
        self.tents = tents            # Tấm ảnh frozenset bất biến lưu các lều của nhánh này
        self.g = g_cost               # Chi phí thực tế đã đi (g)
        self.h = h_cost               # Ước lượng chi phí còn lại tới đích (h)
        self.f = g_cost + h_cost      # 
        self.history = history        # Lịch sử các bước đặt lều dẫn tới trạng thái này

    def __lt__(self, other):
        # bằng thì ưu tiên h nhỏ
        if self.f == other.f:
            return self.h < other.h
        return self.f < other.f


class AStarSolver:
    def __init__(self, board: Board):
        self.board = board
        self.nodes_explored = 0      # Số trạng thái đã lấy ra từ Priority Queue
        self.execution_time = 0.0    # Thời gian chạy 
        self.step_history = []       # Lịch sử các bước phục vụ demo trực quan GUI
        self.solved = False

    def _has_dead_end(self, tree_index: int, tents: frozenset, last_tent_r: int, last_tent_c: int) -> bool:
        """
        [KỸ THUẬT CSP LOCAL FORWARD CHECKING / LOCAL LOOKAHEAD]:
        Khi cắm 1 lều tại (last_tent_r, last_tent_c):
        1. Về mặt vị trí: Lều này chỉ cấm đặt lều trong 8 ô xung quanh nó (bán kính Chebyshev <= 1).
           Vì vậy, chỉ những cây cách lều <= 2 ô mới bị mất ô hợp lệ kề nó.
        2. Về mặt chỉ tiêu: Nếu hàng last_tent_r hoặc cột last_tent_c vừa đủ quota,
           các cây kề hàng/cột đó (khoảng cách hàng/cột <= 1) cũng bị ảnh hưởng.
        
        Thay vì duyệt vô ích toàn bộ bàn cờ (Full Lookahead gây chậm), ta chỉ kiểm tra cục bộ
        các cây thực sự bị ảnh hưởng -> Giảm thiểu tối đa chi phí tính toán (Overhead).
        Nếu phát hiện có cây bị rơi vào miền giá trị rỗng (0 ô) -> Cook ngay lập tức!
        """
        old_tents = self.board.tents
        self.board.tents = set(tents)

        # Kiểm tra xem hàng/cột của lều vừa đặt đã đầy chỉ tiêu chưa
        row_full = sum(1 for r, c in tents if r == last_tent_r) == self.board.row_constraints[last_tent_r]
        col_full = sum(1 for r, c in tents if c == last_tent_c) == self.board.col_constraints[last_tent_c]

        has_dead_end = False
        for idx in range(tree_index, len(self.board.trees)):
            tr, tc = self.board.trees[idx]

            # Bộ lọc cục bộ (Local Filter): Chỉ xét các cây thực sự có khả năng bị ảnh hưởng
            is_affected = (
                (abs(tr - last_tent_r) <= 2 and abs(tc - last_tent_c) <= 2) or
                (row_full and abs(tr - last_tent_r) <= 1) or
                (col_full and abs(tc - last_tent_c) <= 1)
            )

            if not is_affected:
                continue

            # Đếm số ô hợp lệ còn lại xung quanh cây bị ảnh hưởng
            valid_options = sum(
                1 for nr, nc in self.board.get_adjacent_cells(tr, tc)
                if self.board.can_place_tent(nr, nc)
            )
            if valid_options == 0:
                has_dead_end = True
                break

        self.board.tents = old_tents
        return has_dead_end

    def _calculate_heuristic(self, tree_index: int, tents: frozenset) -> int:
        """
        Hàm heuristic h(n) thuần khiết:
        1. Số cây còn lại chưa có lều.
        2. Tổng số lều còn thiếu trên từng hàng và từng cột (chia đôi).
        """
        remaining_trees = len(self.board.trees) - tree_index
        if remaining_trees == 0:
            return 0

        # Đếm số lều trên từng hàng và cột
        row_counts = [0] * self.board.rows
        col_counts = [0] * self.board.cols
        for (r, c) in tents:
            row_counts[r] += 1
            col_counts[c] += 1

        # Tổng số lều còn thiếu ở các hàng và các cột
        row_deficit = sum(max(0, self.board.row_constraints[r] - row_counts[r]) for r in range(self.board.rows))
        col_deficit = sum(max(0, self.board.col_constraints[c] - col_counts[c]) for c in range(self.board.cols))

        return remaining_trees + (row_deficit + col_deficit) // 2

    def solve(self) -> bool:
        """
        Khởi chạy giải thuật A* kết hợp Forward Checking.
        Trả về True nếu tìm thấy lời giải, False nếu không tìm thấy.
        """
        self.nodes_explored = 0
        self.board.tents.clear()
        
        start_time = time.perf_counter()

        # Khởi tạo trạng thái ban đầu: chưa gán cây nào, chưa có lều nào
        initial_tents = frozenset()
        initial_h = self._calculate_heuristic(0, initial_tents)
        initial_node = AStarNode(
            tree_index=0,
            tents=initial_tents,
            g_cost=0,
            h_cost=initial_h,
            history=[]
        )

        open_set = []
        heapq.heappush(open_set, initial_node)

        # Tập closed_set lưu các cấu hình (tree_index, tents) đã xét để tránh lặp
        closed_set = set()

        while open_set:
            current_node = heapq.heappop(open_set)
            self.nodes_explored += 1

            state_key = (current_node.tree_index, current_node.tents)
            if state_key in closed_set:
                continue
            closed_set.add(state_key)

            # Cập nhật tạm thời bàn cờ để kiểm tra đích
            self.board.tents = set(current_node.tents)

            # Kiểm tra xem đã xử lý hết tất cả các cây chưa
            if current_node.tree_index == len(self.board.trees):
                if self.board.is_goal():
                    self.solved = True
                    self.step_history = current_node.history
                    self.execution_time = time.perf_counter() - start_time
                    return True
                continue

            # Mở rộng trạng thái tiếp theo cho cây current_node.tree_index
            tree_r, tree_c = self.board.trees[current_node.tree_index]
            adjacent_cells = self.board.get_adjacent_cells(tree_r, tree_c)

            for nr, nc in adjacent_cells:
                # Kiểm tra ô (nr, nc) có hợp lệ để đặt lều với tập tents hiện tại không
                if self.board.can_place_tent(nr, nc):
                    new_tents = current_node.tents | {(nr, nc)}

                    # 👉 [LOCAL FORWARD CHECKING CHÍNH TẠI ĐÂY - CHO COOK TẠI CHỖ]:
                    # Nếu nước đi cắm lều tại (nr, nc) làm bất kỳ cây kề cận nào bị 0 ô hợp lệ
                    # -> LẬP TỨC BỎ QUA LUÔN (CONTINUE), KHÔNG NÉM VÀO HEAP!
                    if self._has_dead_end(current_node.tree_index + 1, new_tents, nr, nc):
                        continue

                    new_history = current_node.history + [("place", nr, nc, current_node.tree_index)]
                    new_g = current_node.g + 1
                    new_h = self._calculate_heuristic(current_node.tree_index + 1, new_tents)

                    next_node = AStarNode(
                        tree_index=current_node.tree_index + 1,
                        tents=new_tents,
                        g_cost=new_g,
                        h_cost=new_h,
                        history=new_history
                    )

                    heapq.heappush(open_set, next_node)

        # Hết open_set mà không tới đích -> Vô nghiệm
        self.execution_time = time.perf_counter() - start_time
        self.solved = False
        return False
