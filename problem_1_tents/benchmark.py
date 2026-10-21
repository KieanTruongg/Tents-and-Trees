"""
benchmark.py - Thu thập số liệu đo lường hiệu năng: Thời gian, Bộ nhớ (RAM), Max Frontier (Open Set) và Số node duyệt.
Môn học: Nhập môn Trí tuệ Nhân tạo (CO3061)
"""

import sys
import os
import time
import tracemalloc

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from src.board import Board
from src.dfs_solver import DFSSolver
from src.greedy_solver import GreedySolver

def measure_algorithm(solver_class, test_file: str, repeat: int = 5):
    """
    Đo thời gian chạy (lấy trung bình 'repeat' lần), lượng RAM đỉnh (Peak Memory)
    và kích thước cực đại của hàng đợi (Max Open / Frontier).
    """
    # 1. Đo bộ nhớ tiêu tốn bằng tracemalloc
    board = Board(test_file)
    tracemalloc.start()
    solver = solver_class(board)
    solver.solve()
    current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    peak_kb = peak_mem / 1024  # Chuyển đổi sang Kilobytes
    max_open = getattr(solver, 'max_open', getattr(solver, 'nodes_explored', 0))

    # 2. Đo thời gian chính xác bằng vòng lặp nhiều lần để khử nhiễu
    times = []
    nodes = solver.nodes_explored
    for _ in range(repeat):
        b = Board(test_file)
        s = solver_class(b)
        t0 = time.perf_counter()
        s.solve()
        t1 = time.perf_counter()
        times.append((t1 - t0) * 1000)  # ms

    avg_time_ms = sum(times) / len(times)
    return avg_time_ms, peak_kb, nodes, max_open

def run_all_benchmarks():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    benchmark_sets = [
        ("SET 1: BỘ TEST TIÊU CHUẨN (STANDARD)", [
            (os.path.join(base_dir, "data", "input_5x5.txt"), "5x5 (Nhỏ)"),
            (os.path.join(base_dir, "data", "input_6x6.txt"), "6x6 (Vừa)"),
            (os.path.join(base_dir, "data", "input_8x8.txt"), "8x8 (Khá)"),
            (os.path.join(base_dir, "data", "input_10x10.txt"), "10x10 (Lớn)")
        ]),
        ("SET 2: BỘ TEST PHỨC TẠP / NHIỀU NHÁNH RẼ (HARD)", [
            (os.path.join(base_dir, "data", "input_5x5_hard.txt"), "5x5 (Hard)"),
            (os.path.join(base_dir, "data", "input_6x6_hard.txt"), "6x6 (Hard)"),
            (os.path.join(base_dir, "data", "input_8x8_hard.txt"), "8x8 (Hard)"),
            (os.path.join(base_dir, "data", "input_10x10_hard.txt"), "10x10 (Hard)"),
            (os.path.join(base_dir, "data", "input_15x15_hard.txt"), "15x15 (Hard)")
        ])
    ]

    results = {}

    for set_title, test_cases in benchmark_sets:
        print("\n" + "=" * 86)
        print(f"       {set_title}")
        print("=" * 86)
        print(f"{'Kích thước':<14} | {'Thuật toán':<6} | {'Thời gian (ms)':<15} | {'Peak RAM (KB)':<14} | {'Max Open':<10} | {'Nodes duyệt'}")
        print("-" * 86)

        set_results = []
        for fpath, label in test_cases:
            if not os.path.exists(fpath):
                continue

            # DFS
            dfs_time, dfs_ram, dfs_nodes, _ = measure_algorithm(DFSSolver, fpath)
            print(f"{label:<14} | {'DFS':<6} | {dfs_time:<15.4f} | {dfs_ram:<14.2f} | {'N/A (Stack)':<10} | {dfs_nodes:<10}")

            # Greedy Best-First Search
            greedy_time, greedy_ram, greedy_nodes, greedy_open = measure_algorithm(GreedySolver, fpath)
            print(f"{label:<14} | {'Greedy':<6} | {greedy_time:<15.4f} | {greedy_ram:<14.2f} | {greedy_open:<10} | {greedy_nodes:<10}")
            print("-" * 86)

            set_results.append({
                "map": label,
                "dfs": {"time": dfs_time, "ram": dfs_ram, "nodes": dfs_nodes},
                "greedy": {"time": greedy_time, "ram": greedy_ram, "nodes": greedy_nodes, "max_open": greedy_open}
            })
        results[set_title] = set_results

    return results

if __name__ == "__main__":
    run_all_benchmarks()
