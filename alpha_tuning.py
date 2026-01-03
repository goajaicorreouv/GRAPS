import glob
import os
import time
from algorithms import grasp
from structure import instance

def tune_alpha():
    # Helper to get instances
    files = glob.glob("instances/*.txt")
    # Let's pick a representative subset or all small ones to be fast?
    # Or just run on all. There are 15, let's run on all but fewer iters per alpha to save time,
    # or just run properly. 15 instances * 11 alphas * 20 iters might take a while.
    # Let's try 5 iterations per alpha first to get a quick idea, or just use the small ones.
    # The user didn't specify subset. Let's use all but limit iters.
    
    iters = 20 # Keep it reasonable
    alphas = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, -1]
    
    results = {a: [] for a in alphas}
    
    print(f"Tuning Alpha on {len(files)} instances with {iters} iterations each...")
    print(f"{'Instance':<20} | " + " | ".join([f"{str(a):^6}" for a in alphas]))
    print("-" * (20 + 9 * len(alphas)))

    for fpath in files:
        inst_name = os.path.basename(fpath)
        inst = instance.readInstance(fpath)
        
        row_str = f"{inst_name:<20}"
        
        for alpha in alphas:
            # We want to measure the quality of the CONSTRUCTIVE phase mostly for alpha,
            # but usually we tune the whole GRASP.
            sol = grasp.execute(inst, iters, alpha)
            results[alpha].append(sol['of'])
            row_str += f" | {round(sol['of'], 1):^6}"
        
        print(row_str)

    print("-" * 30)
    print("AVERAGE OBJECTIVE VALUES:")
    best_alpha = None
    best_avg_of = -1
    
    # Normalize results? Or just sum? 
    # Since instances have vastly different scales (350 vs 7000), summing is biased towards large instances.
    # Better to rank them or use % deviation from best known.
    # Simple approach: Deviation from best alpha for that instance.
    
    # Calculate best OF for each instance
    instance_best_ofs = []
    for i in range(len(files)):
        best_in_inst = max(results[a][i] for a in alphas)
        instance_best_ofs.append(best_in_inst)
    
    avg_deviations = {}
    
    print(f"{'Alpha':<6} | {'Avg Dev %':<10} | {'Avg Raw OF':<12}")
    
    for alpha in alphas:
        # Calculate average deviation % from best found for this instance
        devs = []
        raw_sum = 0
        for i, val in enumerate(results[alpha]):
            best = instance_best_ofs[i]
            if best > 0:
                dev = (best - val) / best * 100
            else:
                dev = 0
            devs.append(dev)
            raw_sum += val
            
        avg_dev = sum(devs) / len(devs)
        avg_raw = raw_sum / len(devs)
        avg_deviations[alpha] = avg_dev
        
        print(f"{str(alpha):<6} | {avg_dev:^10.2f} | {avg_raw:^12.2f}")
        
        if best_alpha is None or avg_dev < avg_deviations[best_alpha]:
            best_alpha = alpha

    print(f"\nBest Alpha (lowest deviation): {best_alpha}")

if __name__ == '__main__':
    # Mute prints from grasp.py
    import sys
    import io
    
    # Simple context manager to supress stdout from grasp.execute
    class SuppressPrints:
        def __enter__(self):
            self._original_stdout = sys.stdout
            sys.stdout = io.StringIO()
        def __exit__(self, exc_type, exc_val, exc_tb):
            sys.stdout = self._original_stdout

    # Actually, grasp.py prints a lot. We really need to verify if we can modify grasp.py or just suppress.
    # I'll just suppress it in the loop.
    
    # Re-import to ensure fresh start if needed (not needed here)
    tune_alpha()
