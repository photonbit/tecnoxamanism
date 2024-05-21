import numpy as np
from dtaidistance import dtw
import concurrent.futures
import time

# Generate dummy data
np.random.seed(0)  # For reproducibility
sequence1 = np.random.rand(2500)
sequence2 = np.random.rand(2500)

# Single DTW calculation timing
start_time = time.time()
distance = dtw.distance_fast(sequence1, sequence2)
end_time = time.time()
print(f"Single DTW calculation time: {end_time - start_time} seconds")


# Parallel DTW calculations
def calculate_dtw(seq1, seq2):
    return dtw.distance_fast(seq1, seq2)


with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = [executor.submit(calculate_dtw, sequence1, sequence2) for _ in range(3)]
    start_time = time.time()
    results = [future.result() for future in futures]
    end_time = time.time()
    print(f"Parallel DTW calculations time: {end_time - start_time} seconds")

