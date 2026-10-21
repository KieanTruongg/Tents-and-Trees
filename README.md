# BÀI TẬP LỚN 1: CÁC GIẢI THUẬT TÌM KIẾM (SEARCH ALGORITHMS)
**Môn học:** Nhập môn Trí tuệ Nhân tạo (CO3061) — Học kỳ 1 (2026 - 2027)  
**Trường:** Đại học Bách Khoa - ĐHQG TP.HCM (HCMUT)

---

## 📌 Tổng Quan Dự Án

Dự án hiện thực và đánh giá các giải thuật tìm kiếm trong Trí tuệ Nhân tạo áp dụng cho các bài toán giải đố logic (Logic Puzzles):
1. **Problem 1: Tents and Trees Puzzle** — Tìm cách cắm $N$ lều cho $N$ cây thỏa mãn luật kề 4 hướng, không chạm nhau (kể cả kề chéo 8 hướng), và khớp chỉ tiêu hạn ngạch từng hàng/cột.
2. **Problem 2: Pipes Puzzle (Connecting Network)** — *(Chuẩn bị triển khai)*.

---

## 🔄 Cập Nhật Cốt Lõi: Chuyển Đổi từ A* sang Greedy Best-First Search & Các Cải Tiến Chuyên Sâu

Trong quá trình thực nghiệm bài toán **Tents and Trees**, nhóm nghiên cứu đã phát hiện hiện tượng thoái hóa cấu trúc của giải thuật $A^*$:
* **Hạn chế của $A^*$:** Vì mỗi bước luôn cắm đúng 1 lều cho 1 cây, chi phí thực tế $g(n) = \text{depth}(n)$, và số cây còn lại là $N - g(n)$. Do đó tổng chi phí $f(n) = g(n) + h(n) \approx g(n) + (N - g(n)) = N$ (hằng số đối với mọi trạng thái). Điều này triệt tiêu khả năng định hướng của hàng đợi Min-Heap, khiến $A^*$ thoái hóa thành tìm kiếm theo bề rộng (BFS) và bùng nổ bộ nhớ.
* **Giải pháp Greedy Best-First Search (GBFS):** Đặt $f(n) \equiv h(n) = \sum_{T \in \mathcal{U}} \frac{1}{|\mathcal{D}(T)|}$. Bằng việc loại bỏ $g(n)$, thuật toán dồn 100% sức mạnh định hướng vào áp lực ràng buộc của các ô kề, lao thẳng về đích với số node duyệt giảm đi hàng chục lần.

### Các Kỹ Thuật Tối Ưu Hóa Chuyên Sâu Đã Cài Đặt:
1. **Structural Sharing / Parent Pointer (Cắt giảm 90% RAM):** Mỗi nút trạng thái `GreedyNode` không sao chép tập lều hay lịch sử, chỉ lưu vết nước đi vi sai `action` và con trỏ `parent` trỏ về cha. Kích thước node giảm từ 1.1 KB xuống đúng **116 bytes**.
2. **Incremental Heuristic Update ($O(1)$ Vi Sai):** Chỉ tính $h_0$ một lần tại gốc. Mỗi bước chỉ tính độ lệch $\Delta h$ cho 2–3 cây lân cận trong bán kính Chebyshev $\le 2$, đưa chi phí đánh giá Heuristic từ $O(N)$ về $O(1)$.
3. **Chiến Lược Chọn Biến MRV (Minimum Remaining Values - Fail-First):** Luôn chọn cây có ít ô hợp lệ nhất để phân nhánh. Phát hiện ngõ cụt tại chỗ (khi có cây 0 ô) để cắt tỉa ngay lập tức và ép hệ số phân nhánh về cực tiểu ($b = 1$ với nước đi cưỡng bức).
4. **Cắt Tỉa Sức Chứa Hàng/Cột (Row/Col Capacity Pruning):** Lập tức hủy nhánh khi số ô trống khả dụng trên hàng/cột nhỏ hơn số lều cần cắm thêm ($\text{avail} < \text{need}$).
5. **Bộ So Sánh 3 Tầng Tinh Gọn (`__lt__`):** 
   - Tầng 1: $h$ nhỏ nhất
   - Tầng 2: `depth` lớn nhất (tiến sâu về đích)
   - Tầng 3: Tọa độ tự nhiên $(r, c)$ (Trên $\to$ Dưới, Trái $\to$ Phải — đảm bảo tất định 100%).

---

## 📁 Cấu Trúc Thư Mục Dự Án

```text
BTL1/
│
├── docs/                                                # Tài liệu học thuật & báo cáo
│   ├── BTL1.pdf                                         # Đề bài gốc của môn học
│   ├── Bao_Cao_Thuat_Toan_Heuristic_BTL1.pdf            # Báo cáo Heuristic (Bản chuẩn kèm Lưu đồ 2 cột)
│   ├── bao_cao_thuat_toan_heuristic.tex                 # File nguồn LaTeX (TikZ Vector Flowchart)
│   ├── bao_cao_thuat_toan_heuristic.html                # File nguồn HTML hiển thị báo cáo
│   └── greedy_deep_dive.html                            # Cẩm nang mổ xẻ mã nguồn chi tiết 11 chương
│
├── problem_1_tents/                                     # BÀI TOÁN 1: Tents and Trees Puzzle
│   ├── data/                                            # Bộ test cases (.txt)
│   ├── src/                                             # Mã nguồn thuật toán
│   │   ├── board.py                                     # Quản lý ma trận bàn cờ & luật chơi
│   │   ├── dfs_solver.py                                # Blind Search: DFS + Backtracking
│   │   └── greedy_solver.py                             # Heuristic: Greedy Best-First Search + MRV
│   ├── tests/                                           # Unit tests kiểm tra từng module
│   │   ├── test_board.py
│   │   ├── test_dfs.py
│   │   └── test_greedy.py
│   ├── gui_app.py                                       # Giao diện trực quan Demo Step-by-Step (Tkinter)
│   └── benchmark.py                                     # Đo đạc Thời gian (ms), Bộ nhớ RAM (KB) & Max Open
│
├── problem_2_.../                                       # BÀI TOÁN 2 (Chuẩn bị triển khai)
│
├── .gitignore
└── README.md                                            # Hướng dẫn chạy chương trình & tài liệu dự án
```

---

## 🚀 Hướng Dẫn Khởi Chạy

> Toàn bộ chương trình được phát triển bằng thư viện chuẩn của Python (Python 3.10+), **không yêu cầu cài đặt thêm bất kỳ thư viện bên ngoài nào**.

### 1. Khởi động Giao diện Demo trực quan (Step-by-Step GUI)
Từ thư mục gốc dự án:
```powershell
python problem_1_tents/gui_app.py
```
* **Chức năng chính:**
  * Bấm `📁 Chọn file Input (.txt)...` để nạp ma trận bài toán từ thư mục `data/`.
  * Lựa chọn giải thuật: **DFS (Blind Search)** hoặc **Greedy (Best-First Search + MRV)**.
  * Bấm `⚡ Khởi động Tìm kiếm` để giải mã.
  * Điều khiển trực quan từng bước bằng các nút: `Bước sau ▶`, `◀ Bước trước`, hoặc `▶ Chạy tự động (Auto Play)` với thanh chỉnh tốc độ thời gian thực.
  * Theo dõi bảng thông số: Trạng thái, Số bước đi, Số node duyệt qua và Thời gian thực thi.

### 2. Chạy Bảng Đo Lường Hiệu Năng (Benchmark Time & RAM)
```powershell
python problem_1_tents/benchmark.py
```
* Đo đạc chính xác thời gian chạy trung bình ($ms$), bộ nhớ tiêu tốn đỉnh ($KB$), số trạng thái đã duyệt (`Nodes`) và kích thước cực đại của tập biên (`Max Open`) trên nhiều kích thước bàn cờ.

### 3. Chạy các bài kiểm thử nhanh (Console Tests)
```powershell
python problem_1_tents/tests/test_board.py
python problem_1_tents/tests/test_dfs.py
python problem_1_tents/tests/test_greedy.py
```
