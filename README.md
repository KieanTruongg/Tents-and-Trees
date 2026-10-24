# BÀI TẬP LỚN 1: CÁC GIẢI THUẬT TÌM KIẾM (LOGIC PUZZLES)
**Môn học:** Nhập môn Trí tuệ Nhân tạo (CO3061) - HK1 2026-2027  
**Trường:** Đại học Bách Khoa - ĐHQG TP.HCM (HCMUT)  

---

## 1. Tổng quan bài toán: Tents and Trees Puzzle

Dự án tập trung nghiên cứu, hiện thực và so sánh hiệu năng giữa hai phương pháp tìm kiếm cốt lõi trong Trí tuệ Nhân tạo là Tìm kiếm mù (Blind Search) và Tìm kiếm có thông tin (Heuristic Search) thông qua trò chơi giải đố logic kinh điển [Tents and Trees](https://www.puzzle-tents.com/).

Trong bài toán này, người chơi được cung cấp một lưới ô vuông kích thước $R \times C$ chứa một tập hợp gồm $N$ cây phân bố tại các tọa độ cố định. Mục tiêu là tìm ra vị trí cắm chính xác $N$ chiếc lều tương ứng sao cho thỏa mãn đồng thời tất cả các quy tắc không gian nghiêm ngặt. Thứ nhất, tồn tại một quan hệ tương ứng một-một giữa cây và lều, nghĩa là mỗi chiếc lều phải được ghép nối với đúng một cây nằm kề cận nó theo 4 hướng trực giao (trên, dưới, trái, phải). Thứ hai, các lều không được phép chạm vào nhau dưới bất kỳ hình thức nào, bao gồm cả khoảng cách kề cạnh lẫn kề góc chéo theo 8 hướng xung quanh. Cuối cùng, tổng số lượng lều thực tế xuất hiện trên mỗi hàng và mỗi cột phải khớp hoàn toàn với các con số hạn ngạch được ghi ở đầu mỗi hàng và cột của bàn cờ.

Toàn bộ chương trình được phát triển thuần túy bằng ngôn ngữ Python với các thư viện chuẩn tích hợp sẵn (`heapq`, `tkinter`, `tracemalloc`), không phụ thuộc vào bất kỳ thư viện bên ngoài.

---

## 2. Phương pháp và thuật toán giải quyết

### 2.1. Tìm kiếm mù: Depth-First Search (DFS)
Thuật toán DFS vận hành dựa trên cơ chế duyệt đệ quy quay lui (Backtracking). Quá trình tìm kiếm tiến hành duyệt tuần tự qua từng cây trên bàn cờ theo thứ tự chỉ mục cố định từ cây đầu tiên đến cây cuối cùng. Tại mỗi cây đang xét, thuật toán lần lượt thử cắm lều vào các ô trống kề 4 hướng xung quanh, đồng thời kiểm tra nhanh các điều kiện không chạm lều lân cận và chưa vượt quá hạn ngạch của hàng và cột. Nếu một nhánh thử nghiệm dẫn đến tình thế không thể cắm lều hợp lệ cho các cây tiếp theo, thuật toán sẽ quay lui, rút chiếc lều vừa cắm để thử sang phương án tiếp theo.

### 2.2. Tìm kiếm Heuristic: Greedy Best-First Search (GBFS)
Trong giai đoạn đầu khi thử nghiệm thuật toán A*, nhóm nhận thấy hàm lượng giá chuẩn $f(n) = g(n) + h(n)$ bị thoái hóa cấu trúc. Nguyên nhân là do mỗi bước đi luôn cắm đúng 1 lều cho 1 cây, khiến chi phí thực tế tích lũy $g(n)$ bằng đúng độ sâu của nút $\text{depth}(n)$, trong khi số cây còn lại cần giải quyết là $N - g(n)$. Khi đó hàm đánh giá trở thành $f(n) = g(n) + [N - g(n)] = N$ (hằng số), làm mất hoàn toàn khả năng định hướng ưu tiên của hàng đợi Min-Heap. Để giải quyết triệt để vấn đề này, nhóm chuyển sang sử dụng giải thuật Greedy Best-First Search với hàm mục tiêu dồn toàn bộ vào Heuristic:
$$f(n) \equiv h(n) = \sum_{T \in \mathcal{U}(n)} \frac{1}{|\mathcal{D}(T)|}$$

Trong công thức trên, $\mathcal{U}(n)$ đại diện cho tập hợp tất cả các cây chưa được ghép lều tại trạng thái $n$, và $|\mathcal{D}(T)|$ là kích thước miền giá trị hợp lệ còn lại của cây $T$. Việc lấy nghịch đảo số ô hợp lệ giúp đo lường mức độ ứng suất ràng buộc trên lưới: một cây có miền giá trị bị thu hẹp xuống còn rất ít ô sẽ đóng góp một giá trị Heuristic rất lớn, phát tín hiệu cảnh báo rằng nhánh tìm kiếm này đang đứng trước nguy cơ bế tắc cao.

Bên cạnh hàm Heuristic, giải thuật tích hợp chiến lược chọn biến MRV (Minimum Remaining Values - Fail-First). Tại mỗi chu trình lặp, sau khi lấy trạng thái có $h$ nhỏ nhất ra khỏi hàng đợi ưu tiên `Open`, thuật toán không chọn cây theo chỉ mục cố định mà quét lại toàn bộ các cây chưa gán lều để chọn ra cây có ít ô hợp lệ nhất:
$$T^* = \arg\min |\mathcal{D}(T)|$$
Nếu phát hiện tồn tại cây nào có miền giá trị bằng 0 ô, nhánh tìm kiếm sẽ lập tức bị hủy bỏ tại chỗ (Dead-end Pruning). Đồng thời, kỹ thuật cắt tỉa sức chứa hàng và cột (Capacity Pruning) cũng được áp dụng để loại bỏ nhánh đi ngay khi số ô trống còn lại trên hàng hoặc cột nhỏ hơn số lều cần cắm thêm.

Nhằm tối ưu hóa tài nguyên phần cứng, mỗi nút trạng thái được thiết kế theo cơ chế chia sẻ cấu trúc (Structural Sharing / Parent Pointer). Thay vì sao chép toàn bộ bàn cờ, mỗi nút chỉ lưu trữ thao tác vi sai vừa thực hiện cùng một con trỏ tham chiếu ngược về nút cha, giúp kích thước mỗi nút giảm xuống chỉ còn khoảng 116 bytes và khống chế bộ nhớ RAM đỉnh luôn ở mức an toàn. Đồng thời, kỹ thuật cập nhật vi sai Heuristic $O(1)$ chỉ tính toán lại độ lệch $\Delta h$ cho các cây lân cận chiếc lều mới cắm, loại bỏ việc quét lại toàn bộ bàn cờ tại mỗi bước mở rộng.

---

## 3. Cấu trúc thư mục

```text
BTL1/
├── docs/                                    # Tài liệu và báo cáo
│   ├── BTL_NM_AI.pdf                        # Báo cáo học thuật chính thức của BTL
│   └── BTL1.pdf                             # Đề bài gốc môn học
│
├── problem_1_tents/                         # Bài toán Tents and Trees
│   ├── data/                                # Bộ test cases
│   │   ├── 6x6 easy tents.txt
│   │   ├── 6x6 hard tents.txt
│   │   ├── 8x8 easy tents.txt
│   │   ├── 8x8 hard tents.txt
│   │   ├── 10x10 easy tents.txt
│   │   ├── 10x10 hard tents.txt
│   │   ├── 15x15 easy tents.txt
│   │   ├── 15x15 hard tents.txt
│   │   └── 20x20 special tents.txt
│   │
│   ├── src/                                 # Mã nguồn cốt lõi
│   │   ├── board.py                         # Biểu diễn bàn cờ và kiểm tra ràng buộc
│   │   ├── dfs_solver.py                    # Thuật toán DFS Backtracking
│   │   └── greedy_solver.py                 # Thuật toán Greedy Best-First Search + MRV
│   │
│   ├── tests/                               # Kiểm thử dòng lệnh
│   │   ├── test_board.py                    # Kiểm tra đọc file input và hiển thị
│   │   ├── test_dfs.py                      # Kiểm tra chạy riêng lẻ DFS
│   │   └── test_greedy.py                   # Kiểm tra chạy riêng lẻ Greedy
│   │
│   ├── gui_app.py                           # Giao diện trực quan hóa từng bước
│   └── benchmark.py                         # Script đo đạc hiệu năng tự động
│
├── .gitignore
└── README.md
```

---

## 4. Hướng dẫn cài đặt và sử dụng

Chương trình yêu cầu Python 3.10 trở lên và sử dụng các thư viện chuẩn có sẵn trong Python.

Di chuyển vào thư mục bài toán trước khi chạy:
```powershell
cd problem_1_tents
```

### 4.1. Giao diện trực quan hóa (GUI)
Giao diện đồ họa hỗ trợ nạp các file bài toán từ $6 \times 6$ đến $20 \times 20$, trực quan hóa từng bước đặt lều hoặc quay lui của thuật toán DFS và Greedy, tích hợp chế độ chạy tự động (Auto Play) và bảng theo dõi thông số thời gian thực.
```powershell
python gui_app.py
```

### 4.2. Đo đạc hiệu năng (Benchmark)
Thực thi đo đạc tự động trên toàn bộ 9 bài kiểm thử chuẩn và xuất bảng tổng hợp so sánh về thời gian thực thi, số trạng thái duyệt và dung lượng RAM đỉnh giữa hai thuật toán.
```powershell
python benchmark.py
```

### 4.3. Kiểm thử dòng lệnh
Chạy kiểm tra trực tiếp các module và in kết quả ra terminal:
- Nạp và hiển thị cấu hình bàn cờ ban đầu:
  ```powershell
  python tests/test_board.py
  ```
- Giải bài toán bằng thuật toán DFS:
  ```powershell
  python tests/test_dfs.py
  ```
- Giải bài toán bằng thuật toán Greedy kết hợp MRV:
  ```powershell
  python tests/test_greedy.py
  ```

---

## 5. Kết quả thực nghiệm tóm tắt

Dưới đây là số liệu đo đạc thực tế trên hệ thống (CPU đo bằng `time.perf_counter`, RAM đo bằng `tracemalloc`):

| Bài kiểm thử | Quy mô lưới | Thời gian DFS (ms) | Thời gian Greedy (ms) | Nodes DFS | Nodes Greedy | RAM DFS (KB) | RAM Greedy (KB) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| 6x6 easy | $6 \times 6$ (7 cây) | 0.30 | 2.14 | 8 | 8 | 5.0 | 15.9 |
| 6x6 hard | $6 \times 6$ (7 cây) | 0.59 | 2.34 | 16 | 8 | 4.1 | 12.6 |
| 8x8 easy | $8 \times 8$ (12 cây) | 0.75 | 4.58 | 17 | 13 | 5.3 | 26.3 |
| 8x8 hard | $8 \times 8$ (12 cây) | 1.91 | 5.81 | 39 | 13 | 8.2 | 23.4 |
| 10x10 easy | $10 \times 10$ (20 cây) | 1.16 | 10.36 | 21 | 21 | 6.5 | 59.8 |
| 10x10 hard | $10 \times 10$ (20 cây) | 4.56 | 14.60 | 71 | 22 | 11.5 | 50.4 |
| 15x15 easy | $15 \times 15$ (36 cây) | 32.53 | 42.56 | 352 | 42 | 103.4 | 133.1 |
| 15x15 hard | $15 \times 15$ (45 cây) | 97.85 | 65.48 | 1,041 | 54 | 246.1 | 172.4 |
| 20x20 special | $20 \times 20$ (80 cây) | 1,124.87 | 2,955.19 | 4,174 | 248 | 1,095.1 | 1,457.8 |

### Nhận xét rút ra từ thực nghiệm:
- **Về không gian trạng thái:** Thuật toán Greedy kết hợp MRV thể hiện ưu thế vượt trội khi giảm từ 85% đến hơn 94% số lượng trạng thái cần duyệt so với DFS trên các bàn cờ lớn (ở bài 15x15 hard giảm từ 1,041 xuống 54 nodes, bài 20x20 giảm từ 4,174 xuống 248 nodes).
- **Về thời gian thực thi:** Ở các bàn cờ nhỏ ($6 \times 6$ đến $10 \times 10$), DFS chiếm ưu thế do đệ quy thuần túy có overhead thấp. Ở bàn cờ phức tạp (như 15x15 hard), việc cắt giảm node giúp Greedy giải nhanh hơn DFS rõ rệt. Đối với bài cực lớn 20x20, overhead tính toán kiểm tra ràng buộc CSP của Python trên 80 cây làm thời gian của Greedy nhỉnh hơn, nhưng đổi lại số node duyệt được kiểm soát rất chặt chẽ.
- **Về bộ nhớ:** Cơ chế chia sẻ cấu trúc (Structural Sharing) giúp thuật toán tìm kiếm đồ thị Greedy giữ mức tiêu thụ bộ nhớ RAM đỉnh luôn dưới 1.5 MB trên mọi quy mô bài test.
