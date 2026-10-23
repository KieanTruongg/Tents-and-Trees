"""
benchmark.py - Tự động đo kiểm hiệu năng thực tế (Thời gian, Số Node, Bộ nhớ RAM)
giữa Blind Search (DFS Backtracking) và Heuristic Search (Greedy Best-First Search).
Môn học: Nhập môn Trí tuệ Nhân tạo (CO3061)
"""

import os
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

import time
import tracemalloc
import matplotlib.pyplot as plt
import numpy as np

# Đảm bảo import được các module trong src/
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.board import Board
from src.dfs_solver import DFSSolver
from src.greedy_solver import GreedySolver


def run_single_benchmark(solver_class, file_path, repeats=3):
    """Đo thời gian (ms), số nodes và bộ nhớ RAM đỉnh (KB)."""
    times = []
    nodes = 0
    peak_ram_kb = 0.0
    solved = False

    for _ in range(repeats):
        board = Board(file_path)
        solver = solver_class(board)
        
        tracemalloc.start()
        start_t = time.perf_counter()
        res = solver.solve()
        elapsed_ms = (time.perf_counter() - start_t) * 1000.0
        _, peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        times.append(elapsed_ms)
        nodes = solver.nodes_explored
        peak_ram_kb = max(peak_ram_kb, peak_mem / 1024.0)
        solved = res

    avg_time_ms = float(np.median(times))
    return {
        "solved": solved,
        "time_ms": avg_time_ms,
        "nodes": nodes,
        "ram_kb": peak_ram_kb
    }


def main():
    print("==================================================================")
    print("   BẮT ĐẦU ĐO KIỂM HIỆU NĂNG THỰC TẾ (BENCHMARK DFS VS GREEDY)    ")
    print("==================================================================")

    data_dir = os.path.join(BASE_DIR, "data")
    docs_dir = os.path.join(os.path.dirname(BASE_DIR), "docs")
    os.makedirs(docs_dir, exist_ok=True)

    test_files = [
        "6x6 easy tents.txt",
        "6x6 hard tents.txt",
        "8x8 easy tents.txt",
        "8x8 hard tents.txt",
        "10x10 easy tents.txt",
        "10x10 hard tents.txt",
        "15x15 easy tents.txt",
        "15x15 hard tents.txt",
        "20x20 special tents.txt"
    ]

    results = []

    for fname in test_files:
        fpath = os.path.join(data_dir, fname)
        if not os.path.exists(fpath):
            print(f"Bỏ qua file không tồn tại: {fname}")
            continue

        board = Board(fpath)
        grid_info = f"{board.rows}x{board.cols} ({len(board.trees)} cây)"
        label_short = fname.replace(" tents.txt", "").replace(" easy", "-E").replace(" hard", "-H").replace(" special", "-S")

        print(f"\n--> Đang đo: {fname:25} | Lưới: {grid_info}")
        
        # Đo DFS
        dfs_res = run_single_benchmark(DFSSolver, fpath, repeats=3)
        print(f"    [DFS]    Time: {dfs_res['time_ms']:7.3f} ms | Nodes: {dfs_res['nodes']:6d} | RAM: {dfs_res['ram_kb']:6.2f} KB | Ok: {dfs_res['solved']}")

        # Đo Greedy
        greedy_res = run_single_benchmark(GreedySolver, fpath, repeats=3)
        print(f"    [Greedy] Time: {greedy_res['time_ms']:7.3f} ms | Nodes: {greedy_res['nodes']:6d} | RAM: {greedy_res['ram_kb']:6.2f} KB | Ok: {greedy_res['solved']}")

        results.append({
            "filename": fname,
            "label_short": label_short,
            "grid_info": grid_info,
            "rows": board.rows,
            "trees": len(board.trees),
            "dfs": dfs_res,
            "greedy": greedy_res
        })

    # In Bảng Markdown
    print("\n" + "=" * 90)
    print("BẢNG TỔNG HỢP HIỆU NĂNG THỰC NGHIỆM:")
    print("=" * 90)
    header = f"| {'Bài test (Input)':<18} | {'Quy mô':<16} | {'DFS Time (ms)':<14} | {'Greedy Time':<14} | {'DFS Nodes':<10} | {'Greedy Nodes':<12} | {'DFS RAM (KB)':<12} | {'Greedy RAM':<12} |"
    print(header)
    print("|" + "-" * 20 + "|" + "-" * 18 + "|" + "-" * 16 + "|" + "-" * 16 + "|" + "-" * 12 + "|" + "-" * 14 + "|" + "-" * 14 + "|" + "-" * 14 + "|")
    
    for r in results:
        row_str = f"| {r['filename'].replace(' tents.txt', ''):<18} | {r['grid_info']:<16} | {r['dfs']['time_ms']:14.3f} | {r['greedy']['time_ms']:14.3f} | {r['dfs']['nodes']:10d} | {r['greedy']['nodes']:12d} | {r['dfs']['ram_kb']:12.1f} | {r['greedy']['ram_kb']:12.1f} |"
        print(row_str)

    # VẼ 3 BIỂU ĐỒ
    print("\nĐang tạo và lưu 3 biểu đồ trực quan vào thư mục docs/...")
    labels = [r['label_short'] for r in results]
    x = np.arange(len(labels))
    width = 0.35

    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    plt.rcParams['font.family'] = 'DejaVu Sans'

    # 1. BIỂU ĐỒ THỜI GIAN
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    dfs_times = [r['dfs']['time_ms'] for r in results]
    greedy_times = [r['greedy']['time_ms'] for r in results]

    ax.bar(x - width/2, dfs_times, width, label='Blind Search (DFS Backtracking)', color='#ef4444', alpha=0.9)
    ax.bar(x + width/2, greedy_times, width, label='Heuristic Search (Greedy Best-First)', color='#2563eb', alpha=0.9)

    ax.set_title('So Sánh Thời Gian Thực Thi (Execution Time) Giữa DFS và Greedy', fontsize=13, fontweight='bold', pad=12)
    ax.set_ylabel('Thời gian thực thi (mili-giây - ms)', fontsize=11, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=15, ha='right', fontsize=9.5)
    ax.legend(fontsize=10, loc='upper left')
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    fig.tight_layout()
    chart1_path = os.path.join(docs_dir, "benchmark_time.png")
    fig.savefig(chart1_path)
    plt.close(fig)
    print(f" -> Đã lưu biểu đồ 1: {chart1_path}")

    # 2. BIỂU ĐỒ SỐ NÚT DUYỆT (LOG SCALE)
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    dfs_nodes = [r['dfs']['nodes'] for r in results]
    greedy_nodes = [r['greedy']['nodes'] for r in results]

    ax.bar(x - width/2, dfs_nodes, width, label='Blind Search (DFS)', color='#f97316', alpha=0.9)
    ax.bar(x + width/2, greedy_nodes, width, label='Heuristic Search (Greedy MRV)', color='#059669', alpha=0.9)

    ax.set_yscale('log')
    ax.set_title('So Sánh Số Trạng Thái Đã Duyệt (Nodes Explored - Thang Logarit)', fontsize=13, fontweight='bold', pad=12)
    ax.set_ylabel('Số Nodes duyệt (Log Scale)', fontsize=11, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=15, ha='right', fontsize=9.5)
    ax.legend(fontsize=10, loc='upper left')
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    # Thêm giá trị trên đầu cột cho 2 bài lớn nhất
    for i in [-2, -1]:
        ax.annotate(f"{dfs_nodes[i]}", (x[i] - width/2, dfs_nodes[i]), textcoords="offset points", xytext=(0, 4), ha='center', fontsize=8, fontweight='bold', color='#c2410c')
        ax.annotate(f"{greedy_nodes[i]}", (x[i] + width/2, greedy_nodes[i]), textcoords="offset points", xytext=(0, 4), ha='center', fontsize=8, fontweight='bold', color='#047857')

    fig.tight_layout()
    chart2_path = os.path.join(docs_dir, "benchmark_nodes.png")
    fig.savefig(chart2_path)
    plt.close(fig)
    print(f" -> Đã lưu biểu đồ 2: {chart2_path}")

    # 3. BIỂU ĐỒ TIÊU TỐN BỘ NHỚ RAM
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    dfs_rams = [r['dfs']['ram_kb'] for r in results]
    greedy_rams = [r['greedy']['ram_kb'] for r in results]

    ax.plot(x, dfs_rams, marker='o', linewidth=2.5, markersize=7, label='DFS (Call Stack Memory)', color='#dc2626')
    ax.plot(x, greedy_rams, marker='s', linewidth=2.5, markersize=7, label='Greedy (Structural Sharing Memory)', color='#1d4ed8')

    ax.set_title('So Sánh Dung Lượng RAM Đỉnh Tiêu Thụ (Peak RAM Usage)', fontsize=13, fontweight='bold', pad=12)
    ax.set_ylabel('Dung lượng RAM đỉnh (KB)', fontsize=11, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=15, ha='right', fontsize=9.5)
    ax.legend(fontsize=10, loc='upper left')
    ax.grid(True, linestyle='--', alpha=0.7)
    fig.tight_layout()
    chart3_path = os.path.join(docs_dir, "benchmark_ram.png")
    fig.savefig(chart3_path)
    plt.close(fig)
    print(f" -> Đã lưu biểu đồ 3: {chart3_path}")

    print("\nHOÀN TẤT ĐO KIỂM VÀ TẠO BIỂU ĐỒ THÀNH CÔNG!")


if __name__ == "__main__":
    main()
