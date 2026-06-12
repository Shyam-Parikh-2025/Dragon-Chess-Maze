# Note: This benchmarking program was generated using AI assistance to quickly and accurately analyze the custom engine's performance.

import time
import numpy as np
from numba import njit

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Setup dummy data
# 10,000 sets of 50 moves each (simulating many minimax branches)
NUM_SETS = 10_000
MOVE_COUNT = 50
test_data_moves = [np.random.randint(0, 1000, MOVE_COUNT) for _ in range(NUM_SETS)]
test_data_scores = [np.random.randint(0, 1000, MOVE_COUNT) for _ in range(NUM_SETS)]

# --- VERSION 1: Direct List Access ---
@njit
def sort_v1(moves, scores):
    n = len(moves)
    for i in range(n):
        for j in range(0, n-i-1):
            if scores[j] < scores[j+1]:
                # Swap Scores
                temp_s = scores[j]
                scores[j] = scores[j+1]
                scores[j+1] = temp_s
                # Swap Moves
                temp_m = moves[j]
                moves[j] = moves[j+1]
                moves[j+1] = temp_m
    return moves

# --- VERSION 2: Local Variable Swap (Corrected to write back) ---
@njit
def sort_v2(moves, scores):
    n = len(moves)
    for i in range(n):
        for j in range(0, n-i-1):
            s_j = scores[j]
            s_next = scores[j+1]
            if s_j < s_next:
                # We have to write back to memory for the sort to count!
                scores[j] = s_next
                scores[j+1] = s_j
                
                m_j = moves[j]
                moves[j] = moves[j+1]
                moves[j+1] = m_j
    return moves

# --- VERSION 3: Index Caching ---
@njit
def sort_v3(moves, scores):
    n = len(moves)
    for i in range(n):
        for j in range(0, n-i-1):
            h = j + 1
            if scores[j] < scores[h]:
                temp_s = scores[j]
                scores[j] = scores[h]
                scores[h] = temp_s
                
                temp_m = moves[j]
                moves[j] = moves[h]
                moves[h] = temp_m
    return moves

def run_benchmarks():
    print("\n" + "="*50)
    print(" 🏁  MOVE SORTING PERFORMANCE TEST")
    print("="*50)

    # Pre-compile
    sort_v1(test_data_moves[0].copy(), test_data_scores[0].copy())
    sort_v2(test_data_moves[0].copy(), test_data_scores[0].copy())
    sort_v3(test_data_moves[0].copy(), test_data_scores[0].copy())

    results = []
    for name, func in [("V1: Direct Swap", sort_v1), 
                       ("V2: Variable Caching", sort_v2), 
                       ("V3: Index Caching", sort_v3)]:
        
        # Copy data to ensure every test starts with same unsorted data
        moves_copy = [m.copy() for m in test_data_moves]
        scores_copy = [s.copy() for s in test_data_scores]
        
        start = time.perf_counter()
        for i in range(NUM_SETS):
            func(moves_copy[i], scores_copy[i])
        duration = time.perf_counter() - start
        results.append((name, duration))
        print(f"{name}: {duration:.5f} seconds")

if __name__ == "__main__":
    run_benchmarks()