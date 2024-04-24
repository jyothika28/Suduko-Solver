from strategies import *
from helperfunctions import *
from plottingfunctions import *
import numpy as np
import pandas as pd
import time
import matplotlib.pyplot as plt

def load_and_prepare_data(filename):
    """Load and prepare the puzzle data from CSV."""
    df = pd.read_csv(filename)
    df['puzzle'] = df['puzzle'].apply(lambda x: x.replace('.', '0'))
    df['difficulty'] = df['difficulty'].apply(categorize_difficulty)
    return df

def categorize_difficulty(x):
    """Categorize difficulty based on the given rating."""
    if x < 2.8:
        return "Easy"
    elif x < 5.7:
        return "Medium"
    else:
        return "Difficult"
    
def calculate_entropy(puzzle):
    """Calculate the entropy of a Sudoku puzzle based on the count of possible numbers per cell."""
    entropy = 0
    for cell in puzzle:
        if cell == '0':  
            entropy += 1  # Simple measure of entropy: more unfilled cells, higher the entropy
    return entropy

def solve_puzzles(df, n):
    """Solve n puzzles and record times, complexities, and strategy usage."""
    time_data = {'Easy': [], 'Medium': [], 'Difficult': []}
    complexity_data = []
    strategy_efficiency_data = []

    if n > len(df):
        print("Insufficient puzzles available. Solving available puzzles only.")
        n = len(df)

    df_subset = df.head(n)
    for index, row in df_subset.iterrows():
        puzzle_name = f"Puzzle {row['id']} ({row['difficulty']})"
        print(f"\n{puzzle_name}")
        print(row['puzzle'])

        start_time = time.time()
        solution, report_list = solve_from_line(row['puzzle'], verbose=True)
        elapsed_time = time.time() - start_time

        time_data[row['difficulty']].append(elapsed_time)
        complexity_data.append(calculate_entropy(row['puzzle']))  # Calculate and collect entropy
        strategy_efficiency_data.append(report_list)

        print("Time taken: {:.2f}s".format(elapsed_time))
        print("Report List:", report_list)
        print("=" * 45)

    # Convert time_data to a single list of times corresponding to each puzzle
    total_times = [time for sublist in time_data.values() for time in sublist]
    
    return time_data, report_list, complexity_data, strategy_efficiency_data, total_times

def main():
    filename = "sudoku-3m.csv"
    print("Sudoku Solver Demo")
    print("Preparing the data")
    df = load_and_prepare_data(filename)
    print(df.head())

    print("Please Enter the number of puzzles to solve: ")
    n = int(input().strip())
    time_data, report_list, complexity_data, strategy_efficiency_data, total_times = solve_puzzles(df, n)

    # Before plotting, check if the data lengths match
    # print("Length of complexity data:", len(complexity_data))
    # print("Length of total times data:", len(total_times))
    # Graph1
    # Plotting usage count of strategies
    plot_strategy_count(report_list,n)



    # Graph2
    # Plotting a bar graph of average times by difficulty
    # We take the average time for each difficulty level for a simple bar graph
    average_times = {key: np.mean(val) if val else 0 for key, val in time_data.items()}
    difficulties = list(average_times.keys())
    times = list(average_times.values())
    plot_time_difficulty(difficulties, times,n)
    
    
    
    # Graph3: Complexity Analysis
    #plot_complexity_analysis(complexity_data, total_times)
    # print("Strategy Efficiency Data:", strategy_efficiency_data)
    # print("total_times:", total_times)
    # Graph4: Strategy Efficiency
    #flattened_strategy_efficiency_data = [sum(strategy) for strategy in strategy_efficiency_data]
    #plot_strategy_efficiency(report_list, total_times)
    


    
if __name__ == "__main__":
    main()




