"""
greedy_solver.py - giải thuật Heuristic Search: Greedy Best-First Search kết hợp MRV.
1. Parent Pointer
2. Incremental Heuristic Update (Tính toán hàm h vi sai O(1), cập nhật cục bộ).
3. CSP Pruning: Forward Checking theo Cây (Domain = 0) và theo Hàng/Cột (need > avail).
4. Tie-breaking theo Forced Trees (Ưu tiên trạng thái có nhiều cây bị ép vào 1 ô duy nhất).
Hàm heuristic: h = Σ [ 1 / (số ô còn quanh mỗi cây chưa gán) ]
Môn học: Nhập môn Trí tuệ Nhân tạo (CO3061)
"""

import heapq
import time
from src.board import Board

class GreedyNode:
    """
    Biểu diễn một nút trạng thái tối ưu bộ nhớ (Structural Sharing / Parent Pointer).
    Mỗi node chỉ lưu ĐÚNG SỰ THAY ĐỔI (Delta Action) và CON TRỎ VỀ NODE CHA (parent).
    """
    def __init__(self, action: tuple, parent, depth: int, h_cost: float):
        self.action = action            # Nước đi vi sai: (tree_idx, r, c) vừa cắm, hoặc None nếu là gốc
        self.parent = parent            # Con trỏ tham chiếu về node cha (Parent Pointer)
        self.depth = depth              # Số cây đã được cắm lều tính đến node này
        self.h = h_cost                 # Chi phí heuristic: h = Σ (1 / số ô hợp lệ quanh cây chưa gán)
        self.f = h_cost                 # Trong GBFS: f(n) = h(n)

    def get_tents(self) -> set:
        """Truy ngược theo chuỗi con trỏ cha để tái tạo tập lều của node này."""
        tents = set()
        cur = self
        while cur and cur.action:
            tents.add((cur.action[1], cur.action[2]))
            cur = cur.parent
        return tents

    def get_assigned_trees(self) -> set:
        """Truy ngược để lấy tập các chỉ số cây đã được gán lều."""
        assigned = set()
        cur = self
        while cur and cur.action:
            assigned.add(cur.action[0])
            cur = cur.parent
        return assigned

    def get_history(self) -> list:
        """Tái tạo con đường chiến thắng (Solution Path) để cấp cho GUI animation."""
        history = []
        cur = self
        while cur and cur.action:
            tree_idx, r, c = cur.action
            history.append(("place", r, c, tree_idx))
            cur = cur.parent
        history.reverse()
        return history

    def __lt__(self, other):
        # 1. So sánh tiêu chí chính: h càng nhỏ càng ưu tiên
        if abs(self.h - other.h) > 1e-9:
            return self.h < other.h
        # 2. Tie-break 1: Nếu h bằng nhau, ưu tiên trạng thái ĐÃ CẮM NHIỀU CÂY HƠN (depth lớn hơn - đi sâu về đích)
        if self.depth != other.depth:
            return self.depth > other.depth
        # 3. Tie-break 2 (Chốt hạ): Theo hướng tự nhiên (Trên -> Dưới, Trái -> Phải)
        # So sánh tọa độ (r, c) của ô lều vừa được cắm để thuật toán tất định 100%
        if self.action and other.action:
            r1, c1 = self.action[1], self.action[2]
            r2, c2 = other.action[1], other.action[2]
            if r1 != r2:
                return r1 < r2  # Trên -> Dưới (hàng nhỏ hơn ưu tiên trước)
            return c1 < c2      # Trái -> Phải (cột nhỏ hơn ưu tiên trước)
        return False


class GreedySolver:
    """
    Giải thuật Heuristic Search: Greedy Best-First Search kết hợp MRV,
    Structural Sharing, Incremental Heuristic Update (O(1)), và CSP Pruning (Cây & Hàng/Cột).
    """
    def __init__(self, board: Board):
        self.board = board
        self.nodes_explored = 0      # Số trạng thái thực sự được mở rộng (đếm sau closed_set)
        self.max_open = 0            # Kích thước cực đại của hàng đợi ưu tiên Open Set (Frontier Peak)
        self.execution_time = 0.0    # Thời gian chạy
        self.step_history = []       # Lịch sử các bước phục vụ demo trực quan GUI
        self.solved = False

    def _calculate_initial_heuristic(self):
        """
        Chỉ tính toán toàn diện một lần duy nhất tại Node Gốc (Root Node).
        Các node sau sẽ áp dụng tính toán vi sai O(1) dựa trên node cha.
        Trả về: init_h (hoặc None nếu vô nghiệm ngay từ đầu)
        """
        old_tents = self.board.tents
        self.board.tents = set()

        h_val = 0.0
        for idx in range(len(self.board.trees)):
            tr, tc = self.board.trees[idx]
            valid_cnt = sum(
                1 for nr, nc in self.board.get_adjacent_cells(tr, tc)
                if self.board.can_place_tent(nr, nc)
            )
            if valid_cnt == 0:
                self.board.tents = old_tents
                return None
            h_val += 1.0 / valid_cnt

        self.board.tents = old_tents
        return h_val

    def _is_row_col_satisfiable(self, new_tents: set, nr: int, nc: int) -> bool:
        """
        [KỸ THUẬT CẮT TỈA HÀNG/CỘT - NEED > AVAIL PRUNING]:
        Kiểm tra xem các hàng và cột lân cận bị ảnh hưởng bởi lều vừa cắm tại (nr, nc)
        có còn đủ số ô trống hợp lệ (avail) để đáp ứng số lều còn thiếu (need) hay không.
        Nếu need > avail -> Chắc chắn vô nghiệm, cắt tỉa ngay lập tức
        """
        # 1. Kiểm tra các hàng bị ảnh hưởng (nr-1, nr, nr+1) do cấm 8 hướng
        affected_rows = {r for r in (nr - 1, nr, nr + 1) if 0 <= r < self.board.rows}
        for r in affected_rows:
            current_r_tents = sum(1 for tr, tc in new_tents if tr == r)
            row_need = self.board.row_constraints[r] - current_r_tents
            if row_need > 0:
                # Đếm số ô còn có thể đặt lều trên hàng r
                avail = sum(1 for c in range(self.board.cols) if self.board.can_place_tent(r, c))
                if avail < row_need:
                    return False

        # 2. Kiểm tra các cột bị ảnh hưởng (nc-1, nc, nc+1) do cấm 8 hướng
        affected_cols = {c for c in (nc - 1, nc, nc + 1) if 0 <= c < self.board.cols}
        for c in affected_cols:
            current_c_tents = sum(1 for tr, tc in new_tents if tc == c)
            col_need = self.board.col_constraints[c] - current_c_tents
            if col_need > 0:
                # Đếm số ô còn có thể đặt lều trên cột c
                avail = sum(1 for r in range(self.board.rows) if self.board.can_place_tent(r, c))
                if avail < col_need:
                    return False

        return True

    def solve(self) -> bool:
        """
        Khởi chạy giải thuật Greedy Best-First Search với Incremental Delta Update & CSP Pruning.
        """
        self.nodes_explored = 0
        self.max_open = 0
        self.board.tents.clear()
        start_time = time.perf_counter()

        # 1. Tính toán Heuristic ban đầu cho Node Gốc
        init_h = self._calculate_initial_heuristic()
        if init_h is None:
            self.execution_time = time.perf_counter() - start_time
            self.solved = False
            return False

        initial_node = GreedyNode(
            action=None,
            parent=None,
            depth=0,
            h_cost=init_h
        )

        open_set = []
        heapq.heappush(open_set, initial_node)
        self.max_open = len(open_set)
        closed_set = set()

        while open_set:
            current_node = heapq.heappop(open_set)

            # Tái tạo nhanh trạng thái hiện tại từ con trỏ cha
            current_tents = current_node.get_tents()
            current_assigned = current_node.get_assigned_trees()

            # Chống lặp trạng thái
            state_key = (frozenset(current_assigned), frozenset(current_tents))
            if state_key in closed_set:
                continue
            closed_set.add(state_key)

            # tăng nodes_explored sau khi đã qua bộ lọc closed_set
            self.nodes_explored += 1

            # Cập nhật tạm thời bàn cờ để kiểm tra đích
            self.board.tents = set(current_tents)

            # Kiểm tra xem đã xử lý hết tất cả các cây chưa
            if current_node.depth == len(self.board.trees):
                if self.board.is_goal():
                    self.solved = True
                    self.step_history = current_node.get_history()
                    self.execution_time = time.perf_counter() - start_time
                    return True
                continue

            # [KỸ THUẬT MRV - MINIMUM REMAINING VALUES]:
            # Quét tất cả các cây chưa được gán lều để chọn cây có ít ô hợp lệ nhất
            unassigned_indices = [
                idx for idx in range(len(self.board.trees))
                if idx not in current_assigned
            ]

            best_tree_idx = None
            min_valid_count = float('inf')
            tree_valid_cells = {}
            has_empty_domain = False

            for tree_idx in unassigned_indices:
                tr, tc = self.board.trees[tree_idx]
                valid_cells = [
                    (nr, nc) for nr, nc in self.board.get_adjacent_cells(tr, tc)
                    if self.board.can_place_tent(nr, nc)
                ]
                cnt = len(valid_cells)

                # Nếu có cây không còn ô nào hợp lệ --> vứt
                if cnt == 0:
                    has_empty_domain = True
                    break

                tree_valid_cells[tree_idx] = valid_cells
                if cnt < min_valid_count:
                    min_valid_count = cnt
                    best_tree_idx = tree_idx

            if has_empty_domain or best_tree_idx is None:
                continue

            # Giá trị đóng góp cũ của cây vừa chọn vào hàm h và forced_trees
            best_tree_old_cnt = len(tree_valid_cells[best_tree_idx])
            assigned_tree_old_contrib = 1.0 / best_tree_old_cnt

            # Mở rộng cây tốt nhất theo MRV
            for nr, nc in tree_valid_cells[best_tree_idx]:
                new_tents = current_tents | {(nr, nc)}
                new_assigned = current_assigned | {best_tree_idx}

                # Cập nhật tạm thời bàn cờ để kiểm tra vi sai
                self.board.tents = set(new_tents)

                # Nếu lều này làm bất kỳ hàng hoặc cột nào bị thiếu ô trống để đạt chỉ tiêu -> Vứt kẹt rùi
                if not self._is_row_col_satisfiable(new_tents, nr, nc):
                    self.board.tents = set(current_tents)
                    continue

                row_full = sum(1 for r, c in new_tents if r == nr) == self.board.row_constraints[nr]
                col_full = sum(1 for r, c in new_tents if c == nc) == self.board.col_constraints[nc]

                # [TÍNH TOÁN HEURISTIC VI SAI - INCREMENTAL UPDATE]:
                # Chỉ kiểm tra và tính toán lại các cây thực sự bị ảnh hưởng lân cận
                delta_h = 0.0
                is_dead_end = False

                for t_idx in unassigned_indices:
                    if t_idx == best_tree_idx:
                        continue

                    tr, tc = self.board.trees[t_idx]
                    is_affected = (
                        (abs(tr - nr) <= 2 and abs(tc - nc) <= 2) or
                        (row_full and abs(tr - nr) <= 1) or
                        (col_full and abs(tc - nc) <= 1)
                    )

                    # Cây không bị ảnh hưởng -> Giữ nguyên 
                    if not is_affected:
                        continue

                    old_cnt = len(tree_valid_cells[t_idx])
                    new_cnt = sum(
                        1 for ar, ac in self.board.get_adjacent_cells(tr, tc)
                        if self.board.can_place_tent(ar, ac)
                    )

                    # [CHO RA ĐẢO NGAY LẬP TỨC]: Cây lân cận bị 0 ô hợp lệ -> bỏ luôn
                    if new_cnt == 0:
                        is_dead_end = True
                        break

                    delta_h += (1.0 / new_cnt) - (1.0 / old_cnt)

                # Khôi phục lại bàn cờ của node hiện tại
                self.board.tents = set(current_tents)

                if is_dead_end:
                    continue  # Bế tắc -> bỏ lun

                # Tính h mới siêu tốc: h_mới = h_cũ - đóng_góp_cây_đã_cắm + delta_hàng_xóm
                new_h = current_node.h - assigned_tree_old_contrib + delta_h
                if new_h < 1e-9:
                    new_h = 0.0

                next_node = GreedyNode(
                    action=(best_tree_idx, nr, nc),
                    parent=current_node,
                    depth=current_node.depth + 1,
                    h_cost=new_h
                )
                heapq.heappush(open_set, next_node)

                # Cập nhật độ dài đỉnh của hàng đợi ưu tiên 
                if len(open_set) > self.max_open:
                    self.max_open = len(open_set)

        self.execution_time = time.perf_counter() - start_time
        self.solved = False
        return False

