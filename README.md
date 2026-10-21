# BÀI TẬP LỚN 1: CÁC GIẢI THUẬT TÌM KIẾM (SEARCH ALGORITHMS)
**Môn học:** Nhập môn Trí tuệ Nhân tạo (CO3061) - Học kỳ 1 (2026 - 2027)

---

## 📁 Cấu Trúc Thư Mục Dự Án

```text
BTL1/
│
├── docs/                                # Tài liệu, đề bài & báo cáo tiến độ
│   ├── BTL1.pdf                         # Đề bài gốc của môn học
│   └── bao_cao_tien_do.html             # Báo cáo tiến độ trực quan (xem bằng Chrome/Edge)
│
├── problem_1_tents/                     # BÀI TOÁN 1: Tents and Trees Puzzle
│   ├── data/                            # Bộ test cases (5x5, 6x6, 8x8, 10x10)
│   ├── src/                             # Mã nguồn thuật toán
│   │   ├── board.py                     # Quản lý bàn cờ & ràng buộc luật chơi
│   │   ├── dfs_solver.py                # Blind Search: DFS + Backtracking + Pruning
│   │   └── astar_solver.py              # Heuristic Search: A* + Dead-end Lookahead
│   ├── tests/                           # Unit tests kiểm tra từng module
│   │   ├── test_board.py
│   │   ├── test_dfs.py
│   │   └── test_astar.py
│   ├── gui_app.py                       # Giao diện trực quan Demo Step-by-Step (Tkinter)
│   └── benchmark.py                     # Đo đạc Thời gian (ms) & Bộ nhớ RAM (KB)
│
├── problem_2_.../                       # BÀI TOÁN 2 (Chuẩn bị triển khai)
│
└── README.md                            # Hướng dẫn chạy chương trình
```

---

## 🚀 Hướng Dẫn Khởi Chạy (Bài toán 1 - Tents and Trees)

> Toàn bộ chương trình sử dụng thư viện chuẩn của Python (Python 3.10+), **không cần cài đặt thêm bất kỳ thư viện bên ngoài nào**.

### 1. Khởi động Giao diện Demo trực quan (Step-by-Step GUI)
Từ thư mục gốc dự án:
```powershell
python problem_1_tents/gui_app.py
```
* **Chức năng:**
  * Chọn bài toán qua nút `📁 Chọn file Input (.txt)...` (có sẵn các map 5x5, 6x6, 8x8, 10x10 trong thư mục `data/`).
  * Chọn thuật toán muốn chạy: **DFS** hoặc **A\***.
  * Bấm `⚡ Khởi động Tìm kiếm`.
  * Xem từng bước AI giải bằng các nút `Bước sau ▶`, `◀ Bước trước` hoặc `▶ Chạy tự động (Auto Play)` với thanh chỉnh tốc độ.

### 2. Chạy Bảng Đo Lường Hiệu Năng (Benchmark Time & RAM)
```powershell
python problem_1_tents/benchmark.py
```
* Tự động đo thời gian trung bình ($ms$), bộ nhớ tiêu tốn đỉnh ($KB$) và số node duyệt qua trên 4 kích thước map khác nhau.

### 3. Chạy các bài kiểm thử nhanh (Console Tests)
```powershell
python problem_1_tents/tests/test_board.py
python problem_1_tents/tests/test_dfs.py
python problem_1_tents/tests/test_astar.py
```
