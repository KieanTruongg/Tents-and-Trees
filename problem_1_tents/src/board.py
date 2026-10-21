"""
board.py - game Tents and Trees.
Môn học: Nhập môn Trí tuệ Nhân tạo (CO3061)
"""

class Board:
    def __init__(self, filename: str):
        """
        Initial Board 
        """
        self.filename = filename
        self.rows = 0
        self.cols = 0
        self.row_constraints = []  #số lều từng hàng
        self.col_constraints = []  # Số lều từng cột
        self.grid = []             # Ma trận bản đồ ban đầu
        self.trees = []            # Danh sách tọa độ các cây
        
        # Biểu diễn trạng thái đặt lều hiện tại:
        # tents: tập hợp (set) chứa tọa độ các ô đã đặt lều: 
        self.tents = set()
        
        self.load_from_file(filename)

    def load_from_file(self, filename: str):
        """Đọc và phân tích cú pháp từ file input."""
        with open(filename, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]

        # Dòng 1: R C
        r_str, c_str = lines[0].split()
        self.rows = int(r_str)
        self.cols = int(c_str)

        # Dòng 2: số lều từng hàng
        self.row_constraints = [int(x) for x in lines[1].split()]

        # Dòng 3: lều từng cột
        self.col_constraints = [int(x) for x in lines[2].split()]

        # Ma trận bản đồ
        self.grid = []
        self.trees = []
        for r in range(self.rows):
            row_cells = lines[3 + r].split()
            self.grid.append(row_cells)
            for c in range(self.cols):
                if row_cells[c] == 'T':
                    self.trees.append((r, c))

    def is_valid_coordinate(self, r: int, c: int) -> bool:
        """Kiểm tra có nằm trong bàn cờ k"""
        return 0 <= r < self.rows and 0 <= c < self.cols

    def get_adjacent_cells(self, r: int, c: int):
        """
        lấy 4 ô xung quanh tree index đang xét
        """
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        adjacent = []
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if self.is_valid_coordinate(nr, nc):
                adjacent.append((nr, nc))
        return adjacent

    def has_neighbor_tent(self, r: int, c: int) -> bool:
        """
        Kiểm tra ô (r, c) xung quanh có lều nào nữa khum
        """
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if (nr, nc) in self.tents:
                    return True
        return False

    def can_place_tent(self, r: int, c: int) -> bool:
        """
        Kiểm tra xem có thể đặt một cái lều mới vào ô (r, c) hay không.
        Ô hợp lệ-> Ô trống (không phải cây và chưa có lều)->Xung quanh không có lều->Số lều hiện tại ở hàng r và cột c không bị vượt chỉ tiêu
        """
        #1
        if not self.is_valid_coordinate(r, c):
            return False

        #2 ô trống k trùng cây và lều
        if self.grid[r][c] == 'T' or (r, c) in self.tents:
            return False

        #3 quanh kh có lều
        if self.has_neighbor_tent(r, c):
            return False

        #4 đếm số lều của hàng và cột kiểm tra
        current_row_tents = sum(1 for (tr, tc) in self.tents if tr == r)
        current_col_tents = sum(1 for (tr, tc) in self.tents if tc == c)

        if current_row_tents + 1 > self.row_constraints[r]:
            return False
        if current_col_tents + 1 > self.col_constraints[c]:
            return False

        return True

    def is_goal(self) -> bool:
        """
        Kiểm tra bàn cờ đã đạt trạng thái đích (thắng game) hay chưa:
        1. Số lều đúng bằng số cây.
        2. Mỗi hàng có đúng số lều quy định.
        3. Mỗi cột có đúng số lều quy định.
        """
        if len(self.tents) != len(self.trees):
            return False

        # Kiểm tra số lều trên từng hàng
        for r in range(self.rows):
            count = sum(1 for (tr, tc) in self.tents if tr == r)
            if count != self.row_constraints[r]:
                return False

        # Kiểm tra số lều trên từng cột
        for c in range(self.cols):
            count = sum(1 for (tr, tc) in self.tents if tc == c)
            if count != self.col_constraints[c]:
                return False

        return True

    def display(self):
        """In bàn cờ trực quan ra console để kiểm tra."""
        print("\n--- BÀN CỜ HIỆN TẠI ---")
        # In header cột
        header = "    " + " ".join(str(c) for c in self.col_constraints)
        print(header)
        print("    " + "-" * (self.cols * 2 - 1))

        for r in range(self.rows):
            row_display = []
            for c in range(self.cols):
                if (r, c) in self.tents:
                    row_display.append("A")  # A indicate a tent
                elif self.grid[r][c] == 'T':
                    row_display.append("T")  # T indicate a tree
                else:
                    row_display.append(".")  # . = blank
            print(f"{self.row_constraints[r]} | " + " ".join(row_display))
        print("-----------------------\n")
