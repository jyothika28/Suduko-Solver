import numpy as np
import time
from strategies import *
from helperfunctions import *
from mpl_toolkits.mplot3d import Axes3D
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt # plotting
import os # accessing directory structure
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import seaborn as sns


def plot_time_difficulty(difficulties, times,n):
    plt.figure(figsize=(10, 6))
    bars=plt.bar(difficulties, times, color=['green', 'orange', 'red'])
    plt.xlabel('Difficulty')
    plt.ylabel('Average Time (s)')
    plt.title('Average Solving Time by Puzzle Difficulty for n={}'.format(n))
    plt.legend(bars, difficulties)
    plt.savefig("time-difficulty.png")  # Save the plot as a PNG file
    #plt.show()

def plot_strategy_count(usage_data,n):
    total_usage = np.sum(usage_data, axis=0)

    # Names of the strategies in the order they are applied
    strategy_names = [
        'Simple Elimination',
        'Hidden Single',
        'CSP',
        'Intersection',
        'X-Wing',
        '3D Medusa',
        'Backtracking'
    ]

    # Plotting
    plt.figure(figsize=(10, 6))
    bars=plt.bar(strategy_names, total_usage, color=['blue','red','green','purple','orange','yellow','brown'])
    plt.xlabel('Sudoku Solving Strategies')
    plt.ylabel('Total Usage Count')
    plt.title('Usage of Different Strategies in Solving {} Sudoku Puzzles'.format(n))
    plt.xticks(rotation=45)
    plt.legend(bars, strategy_names)
    plt.tight_layout()
    plt.savefig("strategy_count_graph.png") 


def plot_complexity_analysis(entropies, times):
    """Plot the entropy of puzzles against the time taken to solve them."""
    plt.figure(figsize=(10, 6))
    plt.scatter(entropies, times, alpha=0.7, edgecolors='w')
    plt.xlabel('Puzzle Entropy (Count of Empty Cells)')
    plt.ylabel('Time Taken to Solve (s)')
    plt.title('Puzzle Complexity vs. Solving Time')
    plt.grid(True)
    plt.savefig("Graph3.png") 
    plt.show()
   
def plot_strategy_efficiency(usage_data, times):
    """Create a heatmap showing the efficiency of each strategy per puzzle."""
    # Assuming usage_data contains flat lists of strategy usage, not lists of lists.
    efficiency = [list(map(lambda x: x/t if t else 0, usage)) for usage, t in zip(usage_data, times)]
    
    plt.figure(figsize=(12, 8))
    sns.heatmap(efficiency, annot=True, cmap='coolwarm', fmt=".2f",
                xticklabels=['Simple Elimination', 'Hidden Single', 'CSP', 'Intersection', 'X-Wing', '3D Medusa', 'Backtracking'],
                yticklabels=['Puzzle {}'.format(i+1) for i in range(len(times))])
    plt.xlabel('Strategy')
    plt.ylabel('Puzzle')
    plt.title('Strategy Efficiency (Normalized Performance per Second)')
    plt.show()
