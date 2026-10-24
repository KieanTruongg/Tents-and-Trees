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
        peak_ram_kb = peak_mem / 1024.0
        solved = res

    times.sort()
    median_time_ms = times[len(times) // 2]

    return {
        "time_ms": median_time_ms,
        "nodes": nodes,
        "ram_kb": peak_ram_kb,
        "solved": solved
    }


def main():
    data_dir = os.path.join(BASE_DIR, "data")

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

        print(f"\n--> Đang đo: {fname:25} | Lưới: {grid_info}")
        
        # Đo DFS
        dfs_res = run_single_benchmark(DFSSolver, fpath, repeats=3)
        print(f"    [DFS]    Time: {dfs_res['time_ms']:7.3f} ms | Nodes: {dfs_res['nodes']:6d} | RAM: {dfs_res['ram_kb']:6.2f} KB | Ok: {dfs_res['solved']}")

        # Đo Greedy
        greedy_res = run_single_benchmark(GreedySolver, fpath, repeats=3)
        print(f"    [Greedy] Time: {greedy_res['time_ms']:7.3f} ms | Nodes: {greedy_res['nodes']:6d} | RAM: {greedy_res['ram_kb']:6.2f} KB | Ok: {greedy_res['solved']}")

        results.append({
            "filename": fname,
            "grid_info": grid_info,
            "dfs": dfs_res,
            "greedy": greedy_res
        })

    # In Bảng tổng hợp Markdown
    print("\n" + "=" * 92)
    print("BẢNG TỔNG HỢP HIỆU NĂNG THỰC NGHIỆM:")
    print("=" * 92)
    header = f"| {'Bài test (Input)':<18} | {'Quy mô':<16} | {'DFS Time (ms)':<14} | {'Greedy Time':<14} | {'DFS Nodes':<10} | {'Greedy Nodes':<12} | {'DFS RAM (KB)':<12} | {'Greedy RAM':<12} |"
    print(header)
    print("|" + "-" * 20 + "|" + "-" * 18 + "|" + "-" * 16 + "|" + "-" * 16 + "|" + "-" * 12 + "|" + "-" * 14 + "|" + "-" * 14 + "|" + "-" * 14 + "|")
    
    for r in results:
        row_str = f"| {r['filename'].replace(' tents.txt', ''):<18} | {r['grid_info']:<16} | {r['dfs']['time_ms']:14.3f} | {r['greedy']['time_ms']:14.3f} | {r['dfs']['nodes']:10d} | {r['greedy']['nodes']:12d} | {r['dfs']['ram_kb']:12.1f} | {r['greedy']['ram_kb']:12.1f} |"
        print(row_str)

    print("=" * 92)


if __name__ == "__main__":
    main()
