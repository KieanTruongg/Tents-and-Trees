"""
gui_app.py - Giao diện trực quan Demo Step-by-step cho bài toán Tents and Trees.
Sử dụng thư viện chuẩn Tkinter (chạy ngay không cần cài đặt thêm thư viện bên ngoài).
Môn học: Nhập môn Trí tuệ Nhân tạo (CO3061)
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Đảm bảo import được các module trong src/
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.board import Board
from src.dfs_solver import DFSSolver
from src.astar_solver import AStarSolver


class TentsGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Tents and Trees - AI Visualizer (CO3061)")
        self.root.geometry("900x680")
        self.root.minsize(800, 600)
        self.root.configure(bg="#f8fafc")

        # Dữ liệu bài toán
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.current_file = os.path.join(self.base_dir, "data", "input_6x6.txt")
        self.board = None
        self.solver = None
        self.steps = []          # Danh sách các bước thử của solver
        self.current_step_idx = 0
        self.displayed_tents = set()
        self.is_auto_playing = False

        # Thiết lập giao diện
        self._setup_ui()

        # Tải file mặc định nếu có
        if os.path.exists(self.current_file):
            self.load_puzzle(self.current_file)

    def _setup_ui(self):
        # Header
        header_frame = tk.Frame(self.root, bg="#1e3a8a", padx=16, pady=12)
        header_frame.pack(fill=tk.X)

        title_lbl = tk.Label(
            header_frame,
            text="TENTS AND TREES - TÌM KIẾM STEP-BY-STEP",
            font=("Segoe UI", 16, "bold"),
            fg="white",
            bg="#1e3a8a"
        )
        title_lbl.pack(anchor=tk.W)

        sub_lbl = tk.Label(
            header_frame,
            text="CO3061: Nhập môn Trí tuệ Nhân tạo | Blind Search (DFS) & Heuristic Search (A*)",
            font=("Segoe UI", 10),
            fg="#cbd5e1",
            bg="#1e3a8a"
        )
        sub_lbl.pack(anchor=tk.W)

        # Main container
        main_frame = tk.Frame(self.root, bg="#f8fafc", padx=16, pady=16)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Cột trái: Bàn cờ Canvas
        left_frame = tk.Frame(main_frame, bg="#ffffff", bd=1, relief=tk.SOLID)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 12))

        self.canvas_title = tk.Label(
            left_frame, text="Bàn cờ", font=("Segoe UI", 12, "bold"), bg="#ffffff", fg="#1e293b", pady=8
        )
        self.canvas_title.pack()

        self.canvas = tk.Canvas(left_frame, bg="#ffffff", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        # Cột phải: Bảng điều khiển & Thông số
        right_frame = tk.Frame(main_frame, width=320, bg="#f8fafc")
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)
        right_frame.pack_propagate(False)

        # Card 1: Chọn bài toán & Thuật toán
        cfg_card = tk.LabelFrame(
            right_frame, text=" 1. Thiết lập ", font=("Segoe UI", 11, "bold"),
            bg="#ffffff", padx=12, pady=10
        )
        cfg_card.pack(fill=tk.X, pady=(0, 12))

        btn_load = tk.Button(
            cfg_card, text="📁 Chọn file Input (.txt)...", font=("Segoe UI", 10),
            command=self.on_choose_file, bg="#f1f5f9", relief=tk.GROOVE, pady=4
        )
        btn_load.pack(fill=tk.X, pady=(0, 8))

        self.lbl_file = tk.Label(
            cfg_card, text="File: input_6x6.txt", font=("Segoe UI", 9, "italic"),
            fg="#64748b", bg="#ffffff", wraplength=280, justify=tk.LEFT
        )
        self.lbl_file.pack(anchor=tk.W, pady=(0, 8))

        tk.Label(cfg_card, text="Chọn giải thuật:", font=("Segoe UI", 10, "bold"), bg="#ffffff").pack(anchor=tk.W)
        self.algo_var = tk.StringVar(value="DFS")
        rb_dfs = tk.Radiobutton(
            cfg_card, text="DFS (Blind Search + Backtracking)", variable=self.algo_var,
            value="DFS", bg="#ffffff", font=("Segoe UI", 9)
        )
        rb_dfs.pack(anchor=tk.W)
        rb_astar = tk.Radiobutton(
            cfg_card, text="A* (Heuristic Search)", variable=self.algo_var,
            value="ASTAR", bg="#ffffff", font=("Segoe UI", 9)
        )
        rb_astar.pack(anchor=tk.W)

        # Card 2: Nút điều khiển Demo
        ctrl_card = tk.LabelFrame(
            right_frame, text=" 2. Điều khiển Demo Step-by-Step ", font=("Segoe UI", 11, "bold"),
            bg="#ffffff", padx=12, pady=10
        )
        ctrl_card.pack(fill=tk.X, pady=(0, 12))

        btn_solve = tk.Button(
            ctrl_card, text="⚡ Khởi động Tìm kiếm", font=("Segoe UI", 10, "bold"),
            bg="#2563eb", fg="white", activebackground="#1d4ed8", activeforeground="white",
            relief=tk.FLAT, pady=6, command=self.on_start_solve
        )
        btn_solve.pack(fill=tk.X, pady=(0, 8))

        btn_row = tk.Frame(ctrl_card, bg="#ffffff")
        btn_row.pack(fill=tk.X, pady=(0, 8))

        self.btn_prev = tk.Button(
            btn_row, text="◀ Bước trước", font=("Segoe UI", 9),
            state=tk.DISABLED, command=self.on_prev_step, width=12, pady=4
        )
        self.btn_prev.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 4))

        self.btn_next = tk.Button(
            btn_row, text="Bước sau ▶", font=("Segoe UI", 9, "bold"),
            state=tk.DISABLED, command=self.on_next_step, width=12, pady=4, bg="#dbeafe"
        )
        self.btn_next.pack(side=tk.RIGHT, expand=True, fill=tk.X)

        self.btn_auto = tk.Button(
            ctrl_card, text="▶ Chạy tự động (Auto Play)", font=("Segoe UI", 10),
            state=tk.DISABLED, command=self.on_toggle_auto, bg="#10b981", fg="white",
            activebackground="#059669", activeforeground="white", relief=tk.FLAT, pady=5
        )
        self.btn_auto.pack(fill=tk.X, pady=(0, 8))

        tk.Label(ctrl_card, text="Tốc độ diễn hoạt:", font=("Segoe UI", 9), bg="#ffffff").pack(anchor=tk.W)
        self.speed_slider = tk.Scale(
            ctrl_card, from_=100, to=1000, orient=tk.HORIZONTAL,
            bg="#ffffff", highlightthickness=0
        )
        self.speed_slider.set(300)
        self.speed_slider.pack(fill=tk.X)

        # Card 3: Thông số thực thi (Benchmark Stats)
        stats_card = tk.LabelFrame(
            right_frame, text=" 3. Thống kê & Benchmark ", font=("Segoe UI", 11, "bold"),
            bg="#ffffff", padx=12, pady=10
        )
        stats_card.pack(fill=tk.BOTH, expand=True)

        self.lbl_status = tk.Label(
            stats_card, text="Trạng thái: Sẵn sàng", font=("Segoe UI", 10, "bold"),
            fg="#2563eb", bg="#ffffff"
        )
        self.lbl_status.pack(anchor=tk.W, pady=2)

        self.lbl_steps = tk.Label(
            stats_card, text="Tiến trình bước: 0 / 0", font=("Segoe UI", 9), bg="#ffffff"
        )
        self.lbl_steps.pack(anchor=tk.W, pady=2)

        self.lbl_nodes = tk.Label(
            stats_card, text="Số nodes đã duyệt: 0", font=("Segoe UI", 9), bg="#ffffff"
        )
        self.lbl_nodes.pack(anchor=tk.W, pady=2)

        self.lbl_time = tk.Label(
            stats_card, text="Thời gian chạy: 0.000 ms", font=("Segoe UI", 9), bg="#ffffff"
        )
        self.lbl_time.pack(anchor=tk.W, pady=2)

        self.lbl_tents = tk.Label(
            stats_card, text="Số lều đã đặt: 0", font=("Segoe UI", 9), bg="#ffffff"
        )
        self.lbl_tents.pack(anchor=tk.W, pady=2)

    def on_choose_file(self):
        fpath = filedialog.askopenfilename(
            title="Chọn file test Tents and Trees",
            initialdir=os.path.join(self.base_dir, "data"),
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if fpath:
            self.load_puzzle(fpath)

    def load_puzzle(self, filepath: str):
        try:
            self.current_file = filepath
            self.lbl_file.config(text=f"File: {os.path.basename(filepath)}")
            self.board = Board(filepath)
            self.steps = []
            self.current_step_idx = 0
            self.displayed_tents = set()
            self.is_auto_playing = False
            self.btn_auto.config(text="▶ Chạy tự động (Auto Play)", bg="#10b981")
            self.btn_next.config(state=tk.DISABLED)
            self.btn_prev.config(state=tk.DISABLED)
            self.btn_auto.config(state=tk.DISABLED)

            self.lbl_status.config(text="Trạng thái: Đã nạp bàn cờ", fg="#2563eb")
            self.lbl_steps.config(text="Tiến trình bước: 0 / 0")
            self.lbl_nodes.config(text="Số nodes đã duyệt: 0")
            self.lbl_time.config(text="Thời gian chạy: 0.000 ms")
            self.lbl_tents.config(text="Số lều đã đặt: 0")

            self.draw_board()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể đọc file: {e}")

    def on_start_solve(self):
        if not self.board:
            return

        algo = self.algo_var.get()
        # Nạp lại board sạch
        self.board.load_from_file(self.current_file)
        self.displayed_tents = set()
        self.current_step_idx = 0

        if algo == "DFS":
            self.solver = DFSSolver(self.board)
        else:
            self.solver = AStarSolver(self.board)

        self.lbl_status.config(text="Đang giải...", fg="#f59e0b")
        self.root.update()

        success = self.solver.solve()

        if success:
            self.steps = self.solver.step_history
            self.lbl_status.config(text="Trạng thái: Đã tìm ra lời giải!", fg="#16a34a")
            self.lbl_nodes.config(text=f"Số nodes đã duyệt: {self.solver.nodes_explored}")
            self.lbl_time.config(text=f"Thời gian chạy: {self.solver.execution_time * 1000:.3f} ms")
            self.lbl_steps.config(text=f"Tiến trình bước: 0 / {len(self.steps)}")

            self.btn_next.config(state=tk.NORMAL)
            self.btn_prev.config(state=tk.DISABLED)
            self.btn_auto.config(state=tk.NORMAL)
        else:
            self.lbl_status.config(text="Trạng thái: Vô nghiệm!", fg="#dc2626")
            messagebox.showwarning("Thông báo", "Không tìm thấy lời giải cho bàn cờ này!")

        self.draw_board()

    def on_next_step(self):
        if self.current_step_idx < len(self.steps):
            step = self.steps[self.current_step_idx]
            action = step[0]
            r, c = step[1], step[2]

            if action == "place":
                self.displayed_tents.add((r, c))
            elif action == "remove":
                self.displayed_tents.discard((r, c))

            self.current_step_idx += 1
            self.update_step_ui()

    def on_prev_step(self):
        if self.current_step_idx > 0:
            self.current_step_idx -= 1
            step = self.steps[self.current_step_idx]
            action = step[0]
            r, c = step[1], step[2]

            # Đảo ngược hành động để lùi lại
            if action == "place":
                self.displayed_tents.discard((r, c))
            elif action == "remove":
                self.displayed_tents.add((r, c))

            self.update_step_ui()

    def update_step_ui(self):
        self.draw_board()
        self.lbl_steps.config(text=f"Tiến trình bước: {self.current_step_idx} / {len(self.steps)}")
        self.lbl_tents.config(text=f"Số lều đã đặt: {len(self.displayed_tents)}")

        self.btn_prev.config(state=tk.NORMAL if self.current_step_idx > 0 else tk.DISABLED)
        self.btn_next.config(state=tk.NORMAL if self.current_step_idx < len(self.steps) else tk.DISABLED)

    def on_toggle_auto(self):
        self.is_auto_playing = not self.is_auto_playing
        if self.is_auto_playing:
            self.btn_auto.config(text="⏸ Tạm dừng", bg="#ef4444")
            self.auto_step_loop()
        else:
            self.btn_auto.config(text="▶ Tiếp tục chạy", bg="#10b981")

    def auto_step_loop(self):
        if not self.is_auto_playing:
            return

        if self.current_step_idx < len(self.steps):
            self.on_next_step()
            delay_ms = self.speed_slider.get()
            self.root.after(delay_ms, self.auto_step_loop)
        else:
            self.is_auto_playing = False
            self.btn_auto.config(text="▶ Chạy lại từ đầu", bg="#10b981")

    def draw_board(self):
        self.canvas.delete("all")
        if not self.board:
            return

        # Tính toán kích thước ô phù hợp
        c_width = self.canvas.winfo_width()
        c_height = self.canvas.winfo_height()

        if c_width <= 1 or c_height <= 1:
            c_width, c_height = 480, 480

        # Thêm 1 hàng và 1 cột cho số chỉ dẫn (header)
        grid_rows = self.board.rows + 1
        grid_cols = self.board.cols + 1

        cell_size = min((c_width - 40) // grid_cols, (c_height - 40) // grid_rows, 60)
        cell_size = max(cell_size, 30)

        offset_x = (c_width - grid_cols * cell_size) // 2
        offset_y = (c_height - grid_rows * cell_size) // 2

        # Vẽ số chỉ dẫn cột (hàng đầu tiên)
        for c in range(self.board.cols):
            x1 = offset_x + (c + 1) * cell_size
            y1 = offset_y
            x2 = x1 + cell_size
            y2 = y1 + cell_size

            self.canvas.create_rectangle(x1, y1, x2, y2, fill="#e2e8f0", outline="#cbd5e1")
            # Đếm số lều hiện tại ở cột c
            current_col_cnt = sum(1 for (tr, tc) in self.displayed_tents if tc == c)
            req = self.board.col_constraints[c]
            color = "#15803d" if current_col_cnt == req else ("#b91c1c" if current_col_cnt > req else "#1e293b")
            self.canvas.create_text(
                (x1 + x2) // 2, (y1 + y2) // 2,
                text=str(req), font=("Segoe UI", int(cell_size * 0.35), "bold"), fill=color
            )

        # Vẽ các hàng
        for r in range(self.board.rows):
            # Số chỉ dẫn hàng ở cột đầu tiên
            hx1 = offset_x
            hy1 = offset_y + (r + 1) * cell_size
            hx2 = hx1 + cell_size
            hy2 = hy1 + cell_size

            self.canvas.create_rectangle(hx1, hy1, hx2, hy2, fill="#e2e8f0", outline="#cbd5e1")
            current_row_cnt = sum(1 for (tr, tc) in self.displayed_tents if tr == r)
            req = self.board.row_constraints[r]
            color = "#15803d" if current_row_cnt == req else ("#b91c1c" if current_row_cnt > req else "#1e293b")
            self.canvas.create_text(
                (hx1 + hx2) // 2, (hy1 + hy2) // 2,
                text=str(req), font=("Segoe UI", int(cell_size * 0.35), "bold"), fill=color
            )

            # Các ô trong bàn cờ
            for c in range(self.board.cols):
                x1 = offset_x + (c + 1) * cell_size
                y1 = offset_y + (r + 1) * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size

                # Nền ô cờ
                bg_color = "#f8fafc" if (r + c) % 2 == 0 else "#ffffff"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=bg_color, outline="#cbd5e1", width=1)

                # Vẽ Cây hoặc Lều
                if self.board.grid[r][c] == 'T':
                    # Cây xanh
                    self.canvas.create_oval(
                        x1 + 6, y1 + 6, x2 - 6, y2 - 6,
                        fill="#bbf7d0", outline="#16a34a", width=2
                    )
                    self.canvas.create_text(
                        (x1 + x2) // 2, (y1 + y2) // 2,
                        text="🌲", font=("Segoe UI Emoji", int(cell_size * 0.4))
                    )
                elif (r, c) in self.displayed_tents:
                    # Lều màu cam ấm
                    self.canvas.create_rectangle(
                        x1 + 6, y1 + 6, x2 - 6, y2 - 6,
                        fill="#fed7aa", outline="#ea580c", width=2
                    )
                    self.canvas.create_text(
                        (x1 + x2) // 2, (y1 + y2) // 2,
                        text="⛺", font=("Segoe UI Emoji", int(cell_size * 0.4))
                    )


def main():
    root = tk.Tk()
    app = TentsGUI(root)
    # Lắng nghe sự kiện resize để vẽ lại cân đối
    root.bind("<Configure>", lambda event: app.draw_board())
    root.mainloop()


if __name__ == "__main__":
    main()
