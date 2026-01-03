import os
import time
import glob
from algorithms import grasp, grasp_pr
from structure import instance

def run_comparison():
    # Get all instances
    files = glob.glob("instances/*.txt")
    files.sort()
    
    iters = 20
    alpha = 0.8 # Best alpha found from tuning
    
    print(f"{'Instance':<25} | {'GRASP OF':<10} | {'GRASP Time':<10} | {'GRASP+PR OF':<12} | {'PR Time':<10} | {'Improv %':<8}")
    print("-" * 90)
    
    results = []

    for fpath in files:
        inst_name = os.path.basename(fpath)
        inst = instance.readInstance(fpath)
        
        # Run Class GRASP
        start_time = time.time()
        sol_grasp = grasp.execute(inst, iters, alpha)
        grasp_time = time.time() - start_time
        grasp_of = sol_grasp['of']
        
        # Run GRASP + PR
        start_time = time.time()
        # Use same iters for fairness, or adjusted?
        # PR is more expensive, so maybe fewer iters? 
        # But let's keep iters same to show quality improvement.
        sol_pr = grasp_pr.execute(inst, iters, alpha)
        pr_time = time.time() - start_time
        pr_of = sol_pr['of']
        
        # Calculate improvement
        improv = ((pr_of - grasp_of) / grasp_of) * 100
        
        print(f"{inst_name:<25} | {round(grasp_of, 2):<10} | {round(grasp_time, 2):<10} | {round(pr_of, 2):<12} | {round(pr_time, 2):<10} | {round(improv, 2):<8}%")
        
        results.append({
            'instance': inst_name,
            'grasp_of': grasp_of,
            'grasp_time': grasp_time,
            'pr_of': pr_of,
            'pr_time': pr_time,
            'improv': improv
        })

    # Summary
    avg_improv = sum(r['improv'] for r in results) / len(results)
    print("-" * 90)
    print(f"Average Improvement: {avg_improv:.2f}%")
    
    # Save to CSV
    with open("results.csv", "w") as f:
        f.write("Instance,GRASP_OF,GRASP_Time,PR_OF,PR_Time,Improv_Percentage\n")
        for r in results:
            f.write(f"{r['instance']},{r['grasp_of']},{r['grasp_time']},{r['pr_of']},{r['pr_time']},{r['improv']}\n")
            
    print("Results saved to results.csv")

if __name__ == '__main__':
    # Seed for reproducibility?
    import random
    random.seed(42)
    run_comparison()
