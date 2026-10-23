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
from src.greedy_solver import GreedySolver


class TentsGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Tents and Trees - AI Visualizer (CO3061)")
        self.root.geometry("1060x740")
        self.root.minsize(900, 660)
        self.root.configure(bg="#f8fafc")

        # Đường dẫn thư mục
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(self.base_dir, "data")

        # Khởi động ở trạng thái sạch: KHÔNG ghi nhớ/tự nạp file cũ
        self.available_files = self._scan_data_files()
        self.current_file = ""
        self.board = None
        self.solver = None
        self.steps = []          # Danh sách các bước thử của solver
        self.current_step_idx = 0
        self.displayed_tents = set()
        self.last_action_info = None  # (action, r, c, tree_idx, dir_name, tree_coord)
        self.is_auto_playing = False

        # Thiết lập giao diện
        self._setup_ui()
        # Vẽ trạng thái chờ ban đầu
        self.draw_board()

    def _scan_data_files(self) -> list:
        """Quét và sắp xếp danh sách các file puzzle trong thư mục data/."""
        if not os.path.exists(self.data_dir):
            return []
        files = [
            os.path.join(self.data_dir, f)
            for f in os.listdir(self.data_dir)
            if f.endswith(".txt") and not f.startswith(".")
        ]
        files.sort(key=lambda x: os.path.basename(x).lower())
        return files

    def _setup_ui(self):
        # 1. Header Bar
        header_frame = tk.Frame(self.root, bg="#0f172a", padx=16, pady=12)
        header_frame.pack(fill=tk.X)

        title_lbl = tk.Label(
            header_frame,
            text="TENTS AND TREES - TÌM KIẾM STEP-BY-STEP",
            font=("Segoe UI", 16, "bold"),
            fg="#38bdf8",
            bg="#0f172a"
        )
        title_lbl.pack(anchor=tk.W)

        sub_lbl = tk.Label(
            header_frame,
            text="CO3061: Nhập môn Trí tuệ Nhân tạo | Blind Search (DFS Backtracking) & Heuristic Search (Greedy Best-First)",
            font=("Segoe UI", 10),
            fg="#94a3b8",
            bg="#0f172a"
        )
        sub_lbl.pack(anchor=tk.W)

        # 2. Main container
        main_frame = tk.Frame(self.root, bg="#f8fafc", padx=14, pady=12)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Cột trái: Bàn cờ Canvas + Action Banner
        left_frame = tk.Frame(main_frame, bg="#ffffff", bd=1, relief=tk.SOLID)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 12))

        # Tiêu đề bàn cờ
        self.canvas_title = tk.Label(
            left_frame, text="Bàn cờ trạng thái", font=("Segoe UI", 12, "bold"),
            bg="#ffffff", fg="#1e293b", pady=6
        )
        self.canvas_title.pack()

        # Canvas vẽ ma trận
        self.canvas = tk.Canvas(left_frame, bg="#ffffff", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 6))

        # Action Banner: Khung hiển thị mô tả trực quan bước hiện tại
        self.action_banner = tk.Frame(left_frame, bg="#f1f5f9", bd=1, relief=tk.GROOVE, padx=10, pady=8)
        self.action_banner.pack(fill=tk.X, padx=10, pady=(0, 10))

        banner_top = tk.Frame(self.action_banner, bg="#f1f5f9")
        banner_top.pack(fill=tk.X)

        self.lbl_action_badge = tk.Label(
            banner_top, text="[CHỜ INPUT]", font=("Segoe UI", 10, "bold"),
            bg="#cbd5e1", fg="#334155", padx=8, pady=2
        )
        self.lbl_action_badge.pack(side=tk.LEFT)

        self.lbl_step_num = tk.Label(
            banner_top, text="Bước 0 / 0", font=("Segoe UI", 9, "bold"),
            bg="#f1f5f9", fg="#475569", padx=8
        )
        self.lbl_step_num.pack(side=tk.LEFT)

        self.lbl_action_desc = tk.Label(
            self.action_banner,
            text="Chưa có dữ liệu bài toán. Vui lòng chọn file input (.txt) ở bảng bên phải để bắt đầu.",
            font=("Segoe UI", 10), bg="#f1f5f9", fg="#1e293b", wraplength=480, justify=tk.LEFT, pady=4
        )
        self.lbl_action_desc.pack(anchor=tk.W, fill=tk.X)

        # Cột phải: Bảng điều khiển & Thống kê
        right_frame = tk.Frame(main_frame, width=340, bg="#f8fafc")
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)
        right_frame.pack_propagate(False)

        # Card 1: Chọn bài toán & Thuật toán
        cfg_card = tk.LabelFrame(
            right_frame, text=" 1. Đưa Input Bài toán & Thuật toán ",
            font=("Segoe UI", 10, "bold"), bg="#ffffff", padx=10, pady=8
        )
        cfg_card.pack(fill=tk.X, pady=(0, 10))

        tk.Label(cfg_card, text="Chọn bài test từ data/:", font=("Segoe UI", 9), bg="#ffffff").pack(anchor=tk.W)

        # Hàng chọn file + nút reload
        file_select_row = tk.Frame(cfg_card, bg="#ffffff")
        file_select_row.pack(fill=tk.X, pady=(2, 6))

        combo_values = ["--- Chọn file input (.txt) ---"] + [os.path.basename(f) for f in self.available_files]
        self.file_combo = ttk.Combobox(
            file_select_row, values=combo_values,
            state="readonly", font=("Segoe UI", 9)
        )
        self.file_combo.current(0)
        self.file_combo.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 4))
        self.file_combo.bind("<<ComboboxSelected>>", self.on_combo_file_selected)

        btn_reload = tk.Button(
            file_select_row, text="🔄 Tải lại", font=("Segoe UI", 8, "bold"),
            command=self.on_reload_current, bg="#f1f5f9", relief=tk.GROOVE, padx=4, pady=2
        )
        btn_reload.pack(side=tk.RIGHT)

        btn_load = tk.Button(
            cfg_card, text="📁 Mở file khác từ máy tính...", font=("Segoe UI", 9),
            command=self.on_choose_file, bg="#f8fafc", relief=tk.GROOVE, pady=3
        )
        btn_load.pack(fill=tk.X, pady=(0, 8))

        tk.Label(cfg_card, text="Chọn giải thuật:", font=("Segoe UI", 9, "bold"), bg="#ffffff").pack(anchor=tk.W)
        self.algo_var = tk.StringVar(value="DFS")
        rb_dfs = tk.Radiobutton(
            cfg_card, text="DFS (Blind Search + Backtracking)", variable=self.algo_var,
            value="DFS", bg="#ffffff", font=("Segoe UI", 9), command=self._on_algo_changed
        )
        rb_dfs.pack(anchor=tk.W)
        rb_greedy = tk.Radiobutton(
            cfg_card, text="Greedy (Best-First Search + MRV)", variable=self.algo_var,
            value="GREEDY", bg="#ffffff", font=("Segoe UI", 9), command=self._on_algo_changed
        )
        rb_greedy.pack(anchor=tk.W)

        # Chế độ diễn hoạt cho Greedy
        self.greedy_explore_var = tk.BooleanVar(value=True)
        self.chk_greedy_mode = tk.Checkbutton(
            cfg_card, text="Diễn hoạt chi tiết tìm kiếm Heuristic (MRV + h)",
            variable=self.greedy_explore_var, bg="#ffffff", font=("Segoe UI", 8),
            fg="#1e40af", state=tk.DISABLED
        )
        self.chk_greedy_mode.pack(anchor=tk.W, padx=16, pady=(0, 4))

        # Card 2: Điều khiển Demo Step-by-Step
        ctrl_card = tk.LabelFrame(
            right_frame, text=" 2. Điều khiển Diễn hoạt (Visualizer) ",
            font=("Segoe UI", 10, "bold"), bg="#ffffff", padx=10, pady=8
        )
        ctrl_card.pack(fill=tk.X, pady=(0, 10))

        btn_solve = tk.Button(
            ctrl_card, text="⚡ Khởi động Tìm kiếm", font=("Segoe UI", 10, "bold"),
            bg="#2563eb", fg="white", activebackground="#1d4ed8", activeforeground="white",
            relief=tk.FLAT, pady=6, command=self.on_start_solve
        )
        btn_solve.pack(fill=tk.X, pady=(0, 6))

        # Hàng nút điều khiển từng bước
        nav_frame = tk.Frame(ctrl_card, bg="#ffffff")
        nav_frame.pack(fill=tk.X, pady=(0, 6))

        self.btn_reset = tk.Button(
            nav_frame, text="⏮ Đầu", font=("Segoe UI", 8, "bold"),
            state=tk.DISABLED, command=self.on_reset_steps, width=5, pady=4
        )
        self.btn_reset.pack(side=tk.LEFT, padx=(0, 2))

        self.btn_prev = tk.Button(
            nav_frame, text="◀ Lùi", font=("Segoe UI", 9),
            state=tk.DISABLED, command=self.on_prev_step, pady=4
        )
        self.btn_prev.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 2))

        self.btn_next = tk.Button(
            nav_frame, text="Tiến ▶", font=("Segoe UI", 9, "bold"),
            state=tk.DISABLED, command=self.on_next_step, pady=4, bg="#dbeafe"
        )
        self.btn_next.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 2))

        self.btn_end = tk.Button(
            nav_frame, text="Đích ⏭", font=("Segoe UI", 8, "bold"),
            state=tk.DISABLED, command=self.on_jump_to_end, width=5, pady=4
        )
        self.btn_end.pack(side=tk.LEFT)

        # Nút tự động chạy
        self.btn_auto = tk.Button(
            ctrl_card, text="▶ Chạy tự động (Auto Play)", font=("Segoe UI", 9, "bold"),
            state=tk.DISABLED, command=self.on_toggle_auto, bg="#10b981", fg="white",
            activebackground="#059669", activeforeground="white", relief=tk.FLAT, pady=5
        )
        self.btn_auto.pack(fill=tk.X, pady=(0, 6))

        # Tốc độ
        speed_box = tk.Frame(ctrl_card, bg="#ffffff")
        speed_box.pack(fill=tk.X)
        tk.Label(speed_box, text="Tốc độ diễn hoạt (ms/bước):", font=("Segoe UI", 8), bg="#ffffff").pack(side=tk.LEFT)
        self.lbl_speed_val = tk.Label(speed_box, text="300ms", font=("Segoe UI", 8, "bold"), bg="#ffffff", fg="#2563eb")
        self.lbl_speed_val.pack(side=tk.RIGHT)

        self.speed_slider = tk.Scale(
            ctrl_card, from_=50, to=1000, orient=tk.HORIZONTAL,
            bg="#ffffff", highlightthickness=0, resolution=25,
            command=lambda v: self.lbl_speed_val.config(text=f"{v}ms")
        )
        self.speed_slider.set(300)
        self.speed_slider.pack(fill=tk.X)

        # Card 3: Thống kê & Benchmark
        stats_card = tk.LabelFrame(
            right_frame, text=" 3. Thống kê & Benchmark ",
            font=("Segoe UI", 10, "bold"), bg="#ffffff", padx=10, pady=8
        )
        stats_card.pack(fill=tk.X, pady=(0, 10))

        self.lbl_status = tk.Label(
            stats_card, text="Trạng thái: Chưa có bài toán", font=("Segoe UI", 9, "bold"),
            fg="#64748b", bg="#ffffff"
        )
        self.lbl_status.pack(anchor=tk.W, pady=1)

        self.lbl_steps = tk.Label(
            stats_card, text="Tiến trình bước: 0 / 0", font=("Segoe UI", 8), bg="#ffffff"
        )
        self.lbl_steps.pack(anchor=tk.W, pady=1)

        self.lbl_sub_steps = tk.Label(
            stats_card, text="Đặt thử: 0 lần | Quay lui: 0 lần", font=("Segoe UI", 8),
            fg="#64748b", bg="#ffffff"
        )
        self.lbl_sub_steps.pack(anchor=tk.W, pady=1)

        self.lbl_nodes = tk.Label(
            stats_card, text="Số nodes đã duyệt: 0", font=("Segoe UI", 8), bg="#ffffff"
        )
        self.lbl_nodes.pack(anchor=tk.W, pady=1)

        self.lbl_time = tk.Label(
            stats_card, text="Thời gian giải: 0.000 ms", font=("Segoe UI", 8), bg="#ffffff"
        )
        self.lbl_time.pack(anchor=tk.W, pady=1)

        self.lbl_tents = tk.Label(
            stats_card, text="Số lều đã ghép: 0 / 0 cây", font=("Segoe UI", 8), bg="#ffffff"
        )
        self.lbl_tents.pack(anchor=tk.W, pady=1)

        # Card 4: Chú thích màu sắc (Legend)
        legend_card = tk.LabelFrame(
            right_frame, text=" 4. Chú thích Ký hiệu ",
            font=("Segoe UI", 9, "bold"), bg="#ffffff", padx=8, pady=6
        )
        legend_card.pack(fill=tk.X)

        leg_text = "🌲 Cây xanh   |   ⛺ Lều đã đặt\n" \
                   "🟨 Viền vàng: Vừa đặt thử lều\n" \
                   "🟥 Viền đỏ đứt nét: Vừa quay lui (rút lều)\n" \
                   "┄ Nét đứt: Nối giữa Cây và Lều đang xét"
        tk.Label(
            legend_card, text=leg_text, font=("Segoe UI", 8),
            justify=tk.LEFT, bg="#ffffff", fg="#475569"
        ).pack(anchor=tk.W)

    def _on_algo_changed(self):
        """Bật/tắt tùy chọn diễn hoạt Heuristic khi chuyển giải thuật."""
        if self.algo_var.get() == "GREEDY":
            self.chk_greedy_mode.config(state=tk.NORMAL)
        else:
            self.chk_greedy_mode.config(state=tk.DISABLED)

    def on_reload_current(self):
        """Quét lại thư mục data/ và đọc mới trực tiếp file từ ổ đĩa."""
        self.available_files = self._scan_data_files()
        combo_values = ["--- Chọn file input (.txt) ---"] + [os.path.basename(f) for f in self.available_files]
        self.file_combo['values'] = combo_values

        if self.current_file and os.path.exists(self.current_file):
            self.load_puzzle(self.current_file)
        else:
            messagebox.showinfo("Thông báo", "Đã cập nhật danh sách file trong thư mục data/. Vui lòng chọn bài test để nạp.")

    def on_combo_file_selected(self, event=None):
        selected_name = self.file_combo.get()
        if selected_name.startswith("---"):
            return
        fpath = os.path.join(self.data_dir, selected_name)
        if os.path.exists(fpath):
            self.load_puzzle(fpath)

    def on_choose_file(self):
        fpath = filedialog.askopenfilename(
            title="Chọn file test Tents and Trees",
            initialdir=self.data_dir if os.path.exists(self.data_dir) else self.base_dir,
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if fpath:
            self.load_puzzle(fpath)

    def load_puzzle(self, filepath: str):
        """Nạp tươi mới 100% từ ổ đĩa, không dùng cache cũ."""
        try:
            self.current_file = filepath
            fname = os.path.basename(filepath)

            # Cập nhật combobox hiển thị tên file
            if fname in self.file_combo['values']:
                self.file_combo.set(fname)
            else:
                self.file_combo.set(fname)

            # Luôn tạo mới đối tượng Board đọc trực tiếp từ đĩa
            self.board = Board(filepath)
            self.steps = []
            self.current_step_idx = 0
            self.displayed_tents = set()
            self.last_action_info = None
            self.is_auto_playing = False
            self.btn_auto.config(text="▶ Chạy tự động (Auto Play)", bg="#10b981")
            self.btn_next.config(state=tk.DISABLED)
            self.btn_prev.config(state=tk.DISABLED)
            self.btn_reset.config(state=tk.DISABLED)
            self.btn_end.config(state=tk.DISABLED)
            self.btn_auto.config(state=tk.DISABLED)

            self.lbl_status.config(text="Trạng thái: Đã nạp bàn cờ mới", fg="#2563eb")
            self.lbl_steps.config(text="Tiến trình bước: 0 / 0")
            self.lbl_sub_steps.config(text="Đặt thử: 0 lần | Quay lui: 0 lần")
            self.lbl_nodes.config(text="Số nodes đã duyệt: 0")
            self.lbl_time.config(text="Thời gian giải: 0.000 ms")
            self.lbl_tents.config(text=f"Số lều đã ghép: 0 / {len(self.board.trees)} cây")

            self.lbl_action_badge.config(text="[ĐÃ NẠP MỚI]", bg="#cbd5e1", fg="#334155")
            self.lbl_step_num.config(text="Bước 0 / 0")
            self.lbl_action_desc.config(
                text=f"Đã đọc file '{fname}' từ đĩa ({self.board.rows}x{self.board.cols}, {len(self.board.trees)} cây). Bấm 'Khởi động Tìm kiếm' để chạy."
            )

            self.draw_board()
        except Exception as e:
            messagebox.showerror("Lỗi nạp file", f"Không thể đọc file: {e}")

    def on_start_solve(self):
        if not self.current_file or not os.path.exists(self.current_file):
            messagebox.showwarning("Chưa có bài toán", "Vui lòng chọn một file input (.txt) trước khi bắt đầu!")
            return

        algo = self.algo_var.get()

        # ĐỌC MỚI TRỰC TIẾP TỪ Ổ CỨNG mỗi lần bấm Giải (Zero Cache)
        self.board = Board(self.current_file)
        self.displayed_tents = set()
        self.current_step_idx = 0
        self.last_action_info = None

        if algo == "DFS":
            self.solver = DFSSolver(self.board)
        else:
            self.solver = GreedySolver(self.board)

        self.lbl_status.config(text="Đang giải...", fg="#f59e0b")
        self.root.update()

        success = self.solver.solve()

        if success:
            if algo == "GREEDY" and self.greedy_explore_var.get() and hasattr(self.solver, 'exploration_history') and self.solver.exploration_history:
                self.steps = self.solver.exploration_history
            else:
                self.steps = self.solver.step_history

            self.lbl_status.config(text="Trạng thái: Đã tìm ra lời giải!", fg="#16a34a")
            max_op = getattr(self.solver, 'max_open', 'N/A')
            self.lbl_nodes.config(text=f"Nodes duyệt: {self.solver.nodes_explored} | Max Open: {max_op}")
            self.lbl_time.config(text=f"Thời gian giải: {self.solver.execution_time * 1000:.3f} ms")
            self.lbl_steps.config(text=f"Tiến trình bước: 0 / {len(self.steps)}")

            places = sum(1 for s in self.steps if s[0] == "place")
            removes = sum(1 for s in self.steps if s[0] == "remove")
            if algo == "GREEDY":
                self.lbl_sub_steps.config(text=f"Mở rộng: {places} lần | Đổi nhánh: {removes} lần")
            else:
                self.lbl_sub_steps.config(text=f"Đặt thử: {places} lần | Quay lui: {removes} lần")

            self.btn_next.config(state=tk.NORMAL)
            self.btn_prev.config(state=tk.DISABLED)
            self.btn_reset.config(state=tk.DISABLED)
            self.btn_end.config(state=tk.NORMAL)
            self.btn_auto.config(state=tk.NORMAL)

            self.lbl_action_badge.config(text="[SẴN SÀNG CHẠY]", bg="#bfdbfe", fg="#1e40af")
            self.lbl_step_num.config(text=f"0 / {len(self.steps)} bước")
            self.lbl_action_desc.config(
                text=f"Thuật toán {algo} đã hoàn tất tìm kiếm ({len(self.steps)} bước). Bấm 'Tiến ▶' hoặc 'Auto Play' để theo dõi chi tiết."
            )
        else:
            self.lbl_status.config(text="Trạng thái: Vô nghiệm!", fg="#dc2626")
            self.lbl_action_badge.config(text="[VÔ NGHIỆM]", bg="#fecaca", fg="#991b1b")
            self.lbl_action_desc.config(text="Không tìm thấy cấu hình đặt lều nào thỏa mãn toàn bộ ràng buộc của file này!")
            messagebox.showwarning("Thông báo", "Bàn cờ này vô nghiệm (không tìm thấy cấu hình lều hợp lệ)!")

        self.draw_board()

    def _unpack_step(self, step):
        """Bóc tách dữ liệu linh hoạt tương thích cả DFS và Greedy."""
        action = step[0]
        r = step[1]
        c = step[2]
        tree_idx = step[3] if len(step) > 3 else None
        dir_name = step[4] if len(step) > 4 else None
        tree_coord = step[5] if len(step) > 5 else None
        note = step[6] if len(step) > 6 else ""

        if tree_idx is not None and tree_coord is None and self.board and tree_idx < len(self.board.trees):
            tree_coord = self.board.trees[tree_idx]

        return action, r, c, tree_idx, dir_name, tree_coord, note

    def on_next_step(self):
        if self.current_step_idx < len(self.steps):
            step = self.steps[self.current_step_idx]
            action, r, c, tree_idx, dir_name, tree_coord, note = self._unpack_step(step)

            if action == "place":
                self.displayed_tents.add((r, c))
            elif action == "remove":
                self.displayed_tents.discard((r, c))

            self.last_action_info = (action, r, c, tree_idx, dir_name, tree_coord, note)
            self.current_step_idx += 1
            self.update_step_ui()

    def on_prev_step(self):
        if self.current_step_idx > 0:
            self.current_step_idx -= 1
            step = self.steps[self.current_step_idx]
            action, r, c, tree_idx, dir_name, tree_coord, note = self._unpack_step(step)

            # Đảo ngược hành động để hoàn tác
            if action == "place":
                self.displayed_tents.discard((r, c))
            elif action == "remove":
                self.displayed_tents.add((r, c))

            # Xác định action trước đó để highlight
            if self.current_step_idx > 0:
                prev_step = self.steps[self.current_step_idx - 1]
                self.last_action_info = self._unpack_step(prev_step)
            else:
                self.last_action_info = None

            self.update_step_ui()

    def on_reset_steps(self):
        """Đưa về trạng thái ban đầu chưa đặt bước nào."""
        self.displayed_tents.clear()
        self.current_step_idx = 0
        self.last_action_info = None
        self.update_step_ui()

    def on_jump_to_end(self):
        """Nhảy trực tiếp đến trạng thái kết quả cuối cùng."""
        self.displayed_tents.clear()
        for step in self.steps:
            act, r, c, _, _, _, _ = self._unpack_step(step)
            if act == "place":
                self.displayed_tents.add((r, c))
            elif act == "remove":
                self.displayed_tents.discard((r, c))

        self.current_step_idx = len(self.steps)
        if self.steps:
            self.last_action_info = self._unpack_step(self.steps[-1])
        self.update_step_ui()

    def update_step_ui(self):
        self.draw_board()
        self.lbl_steps.config(text=f"Tiến trình bước: {self.current_step_idx} / {len(self.steps)}")
        self.lbl_tents.config(text=f"Số lều đã ghép: {len(self.displayed_tents)} / {len(self.board.trees)} cây")

        # Đếm số bước place/remove đến thời điểm hiện tại
        cur_places = sum(1 for s in self.steps[:self.current_step_idx] if s[0] == "place")
        cur_removes = sum(1 for s in self.steps[:self.current_step_idx] if s[0] == "remove")
        algo = self.algo_var.get()
        if algo == "GREEDY":
            self.lbl_sub_steps.config(text=f"Mở rộng: {cur_places} lần | Đổi nhánh: {cur_removes} lần")
        else:
            self.lbl_sub_steps.config(text=f"Đặt thử: {cur_places} lần | Quay lui: {cur_removes} lần")

        self.btn_reset.config(state=tk.NORMAL if self.current_step_idx > 0 else tk.DISABLED)
        self.btn_prev.config(state=tk.NORMAL if self.current_step_idx > 0 else tk.DISABLED)
        self.btn_next.config(state=tk.NORMAL if self.current_step_idx < len(self.steps) else tk.DISABLED)
        self.btn_end.config(state=tk.NORMAL if self.current_step_idx < len(self.steps) else tk.DISABLED)

        # Cập nhật Action Banner trực quan
        self.lbl_step_num.config(text=f"Bước {self.current_step_idx} / {len(self.steps)}")

        if self.current_step_idx == len(self.steps) and len(self.steps) > 0:
            self.lbl_action_badge.config(text="[HOÀN THÀNH 🎉]", bg="#bbf7d0", fg="#166534")
            self.lbl_action_desc.config(
                text="Chúc mừng! Thuật toán đã hoàn thành ghép lều cho tất cả các cây và thỏa mãn 100% ràng buộc."
            )
        elif self.last_action_info:
            act, r, c, t_idx, d_name, t_coord, note = self.last_action_info
            tree_str = f"Cây #{t_idx} tại {t_coord}" if t_coord else (f"Cây #{t_idx}" if t_idx is not None else "")
            dir_str = f"hướng {d_name}" if d_name else ""

            if act == "place":
                if algo == "GREEDY":
                    self.lbl_action_badge.config(text="[🟢 GREEDY CHỌN NODE]", bg="#dbeafe", fg="#1e40af")
                    if note:
                        self.lbl_action_desc.config(
                            text=f"👉 {note}: Cắm lều tại ô ({r}, {c}) {dir_str} cho {tree_str}."
                        )
                    else:
                        self.lbl_action_desc.config(
                            text=f"👉 Chọn mở rộng: Cắm lều tại ô ({r}, {c}) {dir_str} cho {tree_str}."
                        )
                else:
                    self.lbl_action_badge.config(text="[🟢 ĐẶT THỬ LỀU]", bg="#dcfce7", fg="#15803d")
                    self.lbl_action_desc.config(
                        text=f"👉 Đặt thử: Thử cắm lều tại ô ({r}, {c}) {dir_str} cho {tree_str}. Tiếp tục đi sâu vào cây kế tiếp..."
                    )
            elif act == "remove":
                if algo == "GREEDY":
                    self.lbl_action_badge.config(text="[🔄 ĐỔI NHÁNH OPEN SET]", bg="#fef3c7", fg="#92400e")
                    if note:
                        self.lbl_action_desc.config(
                            text=f"⚠️ {note}: Rút lều tại ô ({r}, {c}) để chuyển sang nhánh trạng thái tốt hơn."
                        )
                    else:
                        self.lbl_action_desc.config(
                            text=f"⚠️ Chuyển trạng thái: Rút lều tại ô ({r}, {c}) để đi theo nhánh có h(n) tốt hơn."
                        )
                else:
                    self.lbl_action_badge.config(text="[🔴 QUAY LUI - BACKTRACK]", bg="#fee2e2", fg="#b91c1c")
                    self.lbl_action_desc.config(
                        text=f"⚠️ Bế tắc! Nhánh tìm kiếm phía sau không có ô hợp lệ. Rút lều tại ô ({r}, {c}) của {tree_str} để thử hướng khác."
                    )
        else:
            self.lbl_action_badge.config(text="[ĐẦU TIÊN]", bg="#cbd5e1", fg="#334155")
            self.lbl_action_desc.config(text="Chưa thực hiện bước nào. Nhấn 'Tiến ▶' để xem bước tiếp theo.")

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

        c_width = self.canvas.winfo_width()
        c_height = self.canvas.winfo_height()

        if c_width <= 1 or c_height <= 1:
            c_width, c_height = 500, 500

        # Nếu chưa có bài toán nạp vào: hiển thị hướng dẫn
        if not self.board:
            self.canvas.create_text(
                c_width // 2, c_height // 2,
                text="📂 CHƯA CHỌN BÀI TOÁN\n\nVui lòng chọn file test ở bảng '1. Đưa Input Bài toán'\nhoặc bấm '📁 Mở file khác từ máy tính' để bắt đầu.",
                font=("Segoe UI", 12), fill="#64748b", justify=tk.CENTER
            )
            return

        grid_rows = self.board.rows + 1
        grid_cols = self.board.cols + 1

        # Tự động co giãn theo kích thước bàn cờ (hỗ trợ mượt từ 6x6 đến 20x20 không bị tràn)
        cell_size = min((c_width - 20) // grid_cols, (c_height - 20) // grid_rows, 55)
        cell_size = max(cell_size, 14)

        offset_x = (c_width - grid_cols * cell_size) // 2
        offset_y = (c_height - grid_rows * cell_size) // 2
        pad = max(int(cell_size * 0.12), 2)

        # 1. Vẽ Header cột (ràng buộc số lều từng cột)
        for c in range(self.board.cols):
            x1 = offset_x + (c + 1) * cell_size
            y1 = offset_y
            x2 = x1 + cell_size
            y2 = y1 + cell_size

            self.canvas.create_rectangle(x1, y1, x2, y2, fill="#e2e8f0", outline="#94a3b8", width=1)
            current_col_cnt = sum(1 for (tr, tc) in self.displayed_tents if tc == c)
            req = self.board.col_constraints[c]
            color = "#15803d" if current_col_cnt == req else ("#b91c1c" if current_col_cnt > req else "#1e293b")
            self.canvas.create_text(
                (x1 + x2) // 2, (y1 + y2) // 2,
                text=str(req), font=("Segoe UI", max(int(cell_size * 0.4), 8), "bold"), fill=color
            )

        # 2. Vẽ Header hàng và các ô bàn cờ
        for r in range(self.board.rows):
            # Số chỉ dẫn hàng ở cột đầu tiên
            hx1 = offset_x
            hy1 = offset_y + (r + 1) * cell_size
            hx2 = hx1 + cell_size
            hy2 = hy1 + cell_size

            self.canvas.create_rectangle(hx1, hy1, hx2, hy2, fill="#e2e8f0", outline="#94a3b8", width=1)
            current_row_cnt = sum(1 for (tr, tc) in self.displayed_tents if tr == r)
            req = self.board.row_constraints[r]
            color = "#15803d" if current_row_cnt == req else ("#b91c1c" if current_row_cnt > req else "#1e293b")
            self.canvas.create_text(
                (hx1 + hx2) // 2, (hy1 + hy2) // 2,
                text=str(req), font=("Segoe UI", max(int(cell_size * 0.4), 8), "bold"), fill=color
            )

            # Các ô trong ma trận
            for c in range(self.board.cols):
                x1 = offset_x + (c + 1) * cell_size
                y1 = offset_y + (r + 1) * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size

                # Nền ô cờ sọc caro dịu mắt
                bg_color = "#f8fafc" if (r + c) % 2 == 0 else "#ffffff"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=bg_color, outline="#cbd5e1", width=1)

                # Vẽ Cây hoặc Lều
                if self.board.grid[r][c] == 'T':
                    # Cây xanh mát
                    self.canvas.create_oval(
                        x1 + pad, y1 + pad, x2 - pad, y2 - pad,
                        fill="#bbf7d0", outline="#16a34a", width=max(int(cell_size * 0.06), 1)
                    )
                    self.canvas.create_text(
                        (x1 + x2) // 2, (y1 + y2) // 2,
                        text="🌲", font=("Segoe UI Emoji", max(int(cell_size * 0.45), 9))
                    )
                elif (r, c) in self.displayed_tents:
                    # Lều màu cam ấm
                    self.canvas.create_rectangle(
                        x1 + pad, y1 + pad, x2 - pad, y2 - pad,
                        fill="#fed7aa", outline="#ea580c", width=max(int(cell_size * 0.06), 1)
                    )
                    self.canvas.create_text(
                        (x1 + x2) // 2, (y1 + y2) // 2,
                        text="⛺", font=("Segoe UI Emoji", max(int(cell_size * 0.45), 9))
                    )

        # 3. Vẽ hiệu ứng Highlight cho ô vừa thao tác (Active Cell) & Đường nối Cây - Lều
        if self.last_action_info:
            act, ar, ac, t_idx, d_name, t_coord = self.last_action_info[:6]
            ax1 = offset_x + (ac + 1) * cell_size
            ay1 = offset_y + (ar + 1) * cell_size
            ax2 = ax1 + cell_size
            ay2 = ay1 + cell_size

            # Vẽ đường nét đứt nối giữa cây và vị trí lều đang xét
            if t_coord:
                tr, tc = t_coord
                tx = offset_x + (tc + 1) * cell_size + cell_size // 2
                ty = offset_y + (tr + 1) * cell_size + cell_size // 2
                lx = ax1 + cell_size // 2
                ly = ay1 + cell_size // 2
                line_color = "#f59e0b" if act == "place" else "#ef4444"
                self.canvas.create_line(tx, ty, lx, ly, dash=(3, 3), fill=line_color, width=2)

            if act == "place":
                # Ô vừa ĐẶT THỬ: Viền vàng kim nổi bật
                self.canvas.create_rectangle(
                    ax1 + 2, ay1 + 2, ax2 - 2, ay2 - 2,
                    outline="#eab308", width=3
                )
            elif act == "remove":
                # Ô vừa QUAY LUI: Viền đỏ đứt nét + chữ cảnh báo "Rút"
                self.canvas.create_rectangle(
                    ax1 + 2, ay1 + 2, ax2 - 2, ay2 - 2,
                    fill="#fee2e2", outline="#ef4444", width=2, dash=(4, 3)
                )
                self.canvas.create_text(
                    (ax1 + ax2) // 2, (ay1 + ay2) // 2,
                    text="↩ RÚT", font=("Segoe UI", max(int(cell_size * 0.25), 8), "bold"), fill="#b91c1c"
                )


def main():
    root = tk.Tk()
    app = TentsGUI(root)
    root.bind("<Configure>", lambda event: app.draw_board())
    root.mainloop()


if __name__ == "__main__":
    main()
