# Note: This benchmarking program was generated using AI assistance to quickly and accurately analyze the custom engine's performance.

import time
import numpy as np
from numba import njit

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# =====================================================================
# THE BENCHMARK SETUP
# =====================================================================
print("Generating 10,000,000 dummy moves for testing...")
NUM_MOVES = 10_000_000
test_moves = np.random.randint(0, 60000, size=NUM_MOVES, dtype=np.int32)

# --- BASE DECODE FUNCTIONS ---
def decode_move_func_without_njit(move):
    start = move & 63
    end = (move >> 6) & 63
    flag = move >> 12
    return start, end, flag

@njit
def decode_move_func_with_njit(move):
    start = move & 63
    end = (move >> 6) & 63
    flag = move >> 12
    return start, end, flag


# --- VERSION 1: loop without njit calling non-jit function
def loop_with_function_without_njit(moves):
    dummy_sum = 0
    for i in range(len(moves)):
        start, end, flag = decode_move_func_without_njit(moves[i])
        dummy_sum += start 
    return dummy_sum

# --- VERSION 2: loop without njit calling JIT function (Partial)
def loop_with_function_with_partial_njit(moves):
    dummy_sum = 0
    for i in range(len(moves)):
        start, end, flag = decode_move_func_with_njit(moves[i])
        dummy_sum += start 
    return dummy_sum

# --- VERSION 3: loop with njit calling JIT function
@njit
def loop_with_function_with_njit(moves):
    dummy_sum = 0
    for i in range(len(moves)):
        start, end, flag = decode_move_func_with_njit(moves[i])
        dummy_sum += start 
    return dummy_sum

# --- VERSION 4: inline without njit (multiple array accesses)
def loop_with_inline_without_njit(moves):
    dummy_sum = 0
    for i in range(len(moves)):
        start = moves[i] & 63
        end = (moves[i] >> 6) & 63
        flag = moves[i] >> 12
        dummy_sum += start
    return dummy_sum

# --- VERSION 5: inline without njit (single array access)
def loop_with_inline_with_m_as_moves_without_njit(moves):
    dummy_sum = 0
    for i in range(len(moves)):
        m = moves[i]
        start = m & 63
        end = (m >> 6) & 63
        flag = m >> 12
        dummy_sum += start
    return dummy_sum

# --- VERSION 6: inline with njit (multiple array accesses)
@njit
def loop_with_inline_with_njit(moves):
    dummy_sum = 0
    for i in range(len(moves)):
        start = moves[i] & 63
        end = (moves[i] >> 6) & 63
        flag = moves[i] >> 12
        dummy_sum += start
    return dummy_sum

# --- VERSION 7: inline with njit (single array access)
@njit
def loop_with_inline_with_m_as_moves_with_njit(moves):
    dummy_sum = 0
    for i in range(len(moves)):
        m = moves[i]
        start = m & 63
        end = (m >> 6) & 63
        flag = m >> 12
        dummy_sum += start
    return dummy_sum


# =====================================================================
# THE TEST RUNNER
# =====================================================================
def run_tests():
    tests = [
        ("V1: Pure Python Loop + Pure Python Func", loop_with_function_without_njit),
        ("V2: Pure Python Loop + JIT Func        ", loop_with_function_with_partial_njit),
        ("V3: JIT Loop + JIT Func                ", loop_with_function_with_njit),
        ("V4: Pure Python Inline (Multi-Access)  ", loop_with_inline_without_njit),
        ("V5: Pure Python Inline (Single-Access) ", loop_with_inline_with_m_as_moves_without_njit),
        ("V6: JIT Inline (Multi-Access)          ", loop_with_inline_with_njit),
        ("V7: JIT Inline (Single-Access)         ", loop_with_inline_with_m_as_moves_with_njit)
    ]

    print("\nWarming up JIT compilers...")
    # Run the JIT functions once with a tiny slice to trigger C-compilation
    # so we don't include compile time in our benchmark.
    for name, func in tests:
        if "JIT" in name:
            func(test_moves[:10])
            
    print("\n" + "="*60)
    print(" 🏎️  COMPREHENSIVE MOVE DECODING SPEED TEST")
    print("="*60)

    results = []
    
    for name, func in tests:
        start_t = time.perf_counter()
        func(test_moves)
        duration = time.perf_counter() - start_t
        results.append((name, duration))
        print(f"{name} : {duration:7.5f} seconds")

    print("\n" + "-" * 60)
    print("LEADERBOARD (Fastest to Slowest):")
    print("-" * 60)
    
    results.sort(key=lambda x: x[1])
    fastest_time = results[0][1]
    
    for rank, (name, duration) in enumerate(results, 1):
        multiplier = duration / fastest_time
        print(f"#{rank}. {name} | {duration:7.5f}s | ({multiplier:.1f}x slower)")

if __name__ == "__main__":
    run_tests()
    