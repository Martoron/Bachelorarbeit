import os
import csv
from pathlib import Path
from multiprocessing import Pool, cpu_count
import time
from datetime import datetime
from collections import defaultdict

from scipy import stats

# Define unit transformations (base_id: transformed_id)
UNIT_TRANSFORMATIONS = {
    '11354': '41355'  # Goku (Ultra Instinct -Sign-) transforms to Goku (Ultra Instinct) int
}

def get_base_unit_info(unit_id, unit_name):
    """Return the base unit ID and name for transformed units"""
    for base_id, transformed_id in UNIT_TRANSFORMATIONS.items():
        if unit_id == transformed_id:
            return base_id, unit_name.replace("(Transformed)", "").strip()
        elif unit_id == base_id:
            return base_id, unit_name
    return unit_id, unit_name

def process_file(csv_file):
    """Process a single CSV file and return aggregated stats"""
    stats = {
        'team_defeated': 0,
        'boss_defeated': 0,
        'total_received': 0,
        'total_dealt': 0,
        'turns': set(),
        'unit_stats': {},
        'special_actions': {
            'active_skill': 0,
            'heal': 0,
            'revive': 0,
            'item_used': 0
        }
    }

    with open(csv_file, mode='r') as file:
        reader = csv.reader(file)
        
        try:
            # Skip metadata lines until we find the real header
            for row in reader:
                if row and "Unit Name" in row:
                    header = row
                    break
            else:
                return stats  # No valid header found
            turn_idx = header.index("Turn") if "Turn" in header else None
            unit_id_idx = header.index("Unit ID") if "Unit ID" in header else None
            unit_name_idx = header.index("Unit Name") if "Unit Name" in header else None
            received_idx = header.index("Damage Received") if "Damage Received" in header else None
            dealt_idx = header.index("Damage Dealt") if "Damage Dealt" in header else None
            hits_idx = header.index("Hits Taken") if "Hits Taken" in header else None

            # ✅ Validate column indices
            required_indices = [turn_idx, unit_id_idx, unit_name_idx, received_idx, dealt_idx, hits_idx]
            if any(idx is None for idx in required_indices):
                print(f"Skipping file {csv_file} - missing required columns.")
                return stats 

        except (ValueError, StopIteration):
            return stats
        
        for row in reader:
            if not row:
                continue
                
            # Check for result row
            if row[0].startswith("Result:"):
                if "Boss defeated" in row[-1]:
                    stats['boss_defeated'] = 1
                elif "Team defeated" in row[-1]:
                    stats['team_defeated'] = 1
                continue
                
            # Skip summary/average rows
            if row[0].startswith("Average damage"):
                continue
                
            # Track special actions
            if len(row) > unit_name_idx and row[hits_idx] == "heal" and row[received_idx] == "heal":
                stats['special_actions']['heal'] += 1
                continue
            elif len(row) > unit_id_idx and row[unit_id_idx] == "Item":
                stats['special_actions']['item_used'] += 1
                continue
            elif len(row) > unit_name_idx and row[hits_idx] == "active skill" and row[received_idx] == "active skill":
                stats['special_actions']['active_skill'] += 1
                continue
            elif len(row) > unit_name_idx and row[hits_idx] == "revive" and row[received_idx] == "revive":
                stats['special_actions']['revive'] += 1
                continue
                
            # Process regular data rows
            if all(idx is not None for idx in [turn_idx, unit_id_idx, unit_name_idx, received_idx, dealt_idx, hits_idx]):
                try:
                    turn = int(row[turn_idx])
                    unit_id = row[unit_id_idx]
                    unit_name = row[unit_name_idx]
                    
                    # Skip rows with non-numeric damage values
                    if row[received_idx] in ["heal", "revive", "active skill"]:
                        continue
                    if row[dealt_idx] in ["heal", "revive", "active skill"]:
                        continue
                        
                    hits_taken = int(row[hits_idx]) if row[hits_idx].strip() and row[hits_idx].isdigit() else 0
                    dmg_received = float(row[received_idx]) if row[received_idx].strip() and row[received_idx].replace('.','',1).isdigit() else 0
                    dmg_dealt = float(row[dealt_idx]) if row[dealt_idx].strip() and row[dealt_idx].replace('.','',1).isdigit() else 0
                    
                    stats['turns'].add(turn)
                    stats['total_received'] += dmg_received
                    stats['total_dealt'] += dmg_dealt
                    
                    # Handle transformed units - combine both forms under base ID
                    if unit_id == '41355':  # Transformed Goku
                        unit_id = '11354'
                        unit_name = 'Goku (Ultra Instinct -Sign-)'
                    
                    unit_key = (unit_id, unit_name)
                    
                    if unit_key not in stats['unit_stats']:
                        stats['unit_stats'][unit_key] = {
                            'damage_received': 0,
                            'damage_dealt': 0,
                            'hits_taken': 0,
                            'appearances': 0
                        }
                    
                    stats['unit_stats'][unit_key]['damage_received'] += dmg_received
                    stats['unit_stats'][unit_key]['damage_dealt'] += dmg_dealt
                    stats['unit_stats'][unit_key]['hits_taken'] += hits_taken
                    stats['unit_stats'][unit_key]['appearances'] += 1
                    
                except (ValueError, IndexError):
                    continue
        
    return stats

def save_results(folder_name, total_simulations, weighted_metrics, unweighted_metrics, 
                victory_stats, unit_stats, special_actions, output_folder=os.path.join("TurnSimulation","Simulation_results","Analysis_results")):
    """Save analysis results to a timestamped file"""
    os.makedirs(output_folder, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{folder_name}_analysis_{timestamp}.txt"
    filepath = os.path.join(output_folder, filename)
    
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        f.write(f"Analysis of {folder_name} dataset\n")
        f.write("="*90 + "\n")
        f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total simulations analyzed: {total_simulations}\n")
        
        # Battle Outcome Metrics
        f.write("\nBattle Outcome Metrics:\n")
        f.write("-"*90 + "\n")
        f.write(f"Team defeated: {victory_stats['team_defeated']} times ({victory_stats['team_defeated_pct']:.1f}%)\n")
        f.write(f"Boss defeated: {victory_stats['boss_defeated']} times ({victory_stats['boss_defeated_pct']:.1f}%)\n")
        
        # Special Actions
        f.write("\nSpecial Actions Triggered:\n")
        f.write("-"*90 + "\n")
        for action, count in special_actions.items():
            if action == "heal" or action == "revive":
                f.write(f"{action.replace('_', ' ').title()}: {count} times ({count/total_simulations*100:.1f}% of simulations)\n")
            else:
                f.write(f"{action.replace('_', ' ').title()}: {count} times\n")
        # Weighted Averages
        f.write("\nWeighted Averages (Total Damage/Total Turns):\n")
        f.write("-"*90 + "\n")
        f.write(f"Total turns: {weighted_metrics['total_turns']}\n")
        f.write(f"Avg damage received per turn: {weighted_metrics['avg_received']:.2f}\n")
        f.write(f"Avg damage dealt per turn: {weighted_metrics['avg_dealt']:.2f}\n")
        
        # Unweighted Averages
        f.write("\nUnweighted Averages (Per Simulation):\n")
        f.write("-"*90 + "\n")
        f.write(f"Avg turns per simulation: {unweighted_metrics['avg_turns']:.1f}\n")
        f.write(f"Avg damage received per simulation: {unweighted_metrics['avg_received']:.2f}\n")
        f.write(f"Avg damage dealt per simulation: {unweighted_metrics['avg_dealt']:.2f}\n")
        
        # Unit Offensive Performance
        f.write("\nUnit Offensive Performance:\n")
        f.write("-"*90 + "\n")
        f.write(f"{'Unit ID':<8} | {'Unit Name':<20} | {'Avg Dmg/App':>12} | {'Total Dmg':>12} | {'Appearances':>12}\n")
        f.write("-"*90 + "\n")
        
        sorted_offensive = sorted(
            unit_stats.items(),
            key=lambda x: x[1]['damage_dealt']/x[1]['appearances'] if x[1]['appearances'] > 0 else 0,
            reverse=True
        )
        
        for (unit_id, unit_name), stats in sorted_offensive[:15]:  # Top 15 offensive units
            avg_dealt = stats['damage_dealt'] / stats['appearances'] if stats['appearances'] > 0 else 0
            f.write(f"{unit_id:<8} | {unit_name:<20} | {avg_dealt:>12.2f} | {stats['damage_dealt']:>12.2f} | {stats['appearances']:>12}\n")
        
        # Unit Defensive Performance
        f.write("\nUnit Defensive Performance:\n")
        f.write("-"*90 + "\n")
        header = (
            f"{'Unit ID':<8} | {'Unit Name':<20} | {'Dmg/Hit':>10} | {'Hits/App':>10} | "
            f"{'Dmg/App':>10} | {'Total Dmg':>12} | {'Total Hits':>12} | {'Appearances':>12}"
        )
        f.write(header + "\n")
        f.write("-"*90 + "\n")
        
        sorted_defensive = sorted(
            unit_stats.items(),
            key=lambda x: (
                # Primary: Damage per Hit (lower = better mitigation)
                x[1]['damage_received'] / x[1]['hits_taken'] if x[1]['hits_taken'] > 0 else float('inf'),
                # Secondary: Total Damage Taken (lower = less overall burden)
                x[1]['damage_received']
            ),
            reverse=False
        )
        
        for (unit_id, unit_name), stats in sorted_defensive[:15]:  # Top 15 defensive units
            dmg_per_hit = stats['damage_received'] / stats['hits_taken'] if stats['hits_taken'] > 0 else 0
            hits_per_app = stats['hits_taken'] / stats['appearances'] if stats['appearances'] > 0 else 0
            dmg_per_app = stats['damage_received'] / stats['appearances'] if stats['appearances'] > 0 else 0
            f.write(
                f"{unit_id:<8} | {unit_name:<20} | {dmg_per_hit:>10.2f} | {hits_per_app:>10.2f} | "
                f"{dmg_per_app:>10.2f} | {stats['damage_received']:>12.2f} | "
                f"{stats['hits_taken']:>12} | {stats['appearances']:>12}\n"
            )
        
        # Interpretation Guide
        f.write("\nMetrics Interpretation Guide:\n")
        f.write("-"*90 + "\n")
        f.write("Offensive Metrics:\n")
        f.write("Avg Dmg/App - Average damage dealt per appearance (higher = better)\n")
        f.write("Total Dmg   - Total damage dealt across all appearances\n\n")
        f.write("Defensive Metrics:\n")
        f.write("Dmg/Hit     - Damage taken per hit (lower = better defense)\n")
        f.write("Hits/App    - Hits taken per appearance (higher = more targeted)\n")
        f.write("Dmg/App     - Damage taken per appearance\n")
        f.write("Total Dmg   - Total damage taken across all appearances\n")
        f.write("Total Hits  - Total hits taken across all appearances\n")
    
    print(f"\nResults saved to: {filepath}")

def calculate_folder_averages(folder_path, folder_name):
    """Calculate and compare both weighted and unweighted averages for a dataset"""
    csv_files = [f for f in Path(folder_path).glob('*.csv') if f.is_file()]
    
    if not csv_files:
        print(f"No CSV files found in {folder_path}")
        return
    
    print(f"\nProcessing {len(csv_files)} simulations in '{folder_name}'...")
    start_time = time.time()
    
    with Pool() as pool:
        results = pool.map(process_file, csv_files)
    
    # Calculate totals
    total_received = sum(r['total_received'] for r in results)
    total_dealt = sum(r['total_dealt'] for r in results)
    total_turns = sum(len(r['turns']) for r in results)
    total_team_defeated = sum(r['team_defeated'] for r in results)
    total_boss_defeated = sum(r['boss_defeated'] for r in results)
    
    # Aggregate special actions
    special_actions = defaultdict(int)
    for result in results:
        for action, count in result['special_actions'].items():
            special_actions[action] += count
    
    # Aggregate unit stats
    unit_stats = defaultdict(lambda: {
        'damage_received': 0,
        'damage_dealt': 0,
        'hits_taken': 0,
        'appearances': 0
    })
    for result in results:
        for (unit_id, unit_name), stats in result['unit_stats'].items():
            unit_stats[(unit_id, unit_name)]['damage_received'] += stats['damage_received']
            unit_stats[(unit_id, unit_name)]['damage_dealt'] += stats['damage_dealt']
            unit_stats[(unit_id, unit_name)]['hits_taken'] += stats['hits_taken']
            unit_stats[(unit_id, unit_name)]['appearances'] += stats['appearances']
    
    if total_turns == 0:
        print("Error: No valid turn data found")
        return
    
    # Prepare metrics
    weighted_metrics = {
        'total_turns': total_turns,
        'avg_received': total_received / total_turns,
        'avg_dealt': total_dealt / total_turns
    }
    
    # Calculate unweighted averages
    valid_sims = [r for r in results if len(r['turns']) > 0]
    unweighted_metrics = {
        'avg_turns': total_turns / len(csv_files),
        'avg_received': sum(r['total_received']/len(r['turns']) for r in valid_sims) / len(valid_sims),
        'avg_dealt': sum(r['total_dealt']/len(r['turns']) for r in valid_sims) / len(valid_sims)
    }
    
    # Calculate victory stats
    total_sims = len(csv_files)
    victory_stats = {
        'team_defeated': total_team_defeated,
        'boss_defeated': total_boss_defeated,
        'team_defeated_pct': (total_team_defeated / total_sims) * 100 if total_sims > 0 else 0,
        'boss_defeated_pct': (total_boss_defeated / total_sims) * 100 if total_sims > 0 else 0
    }
    
    # Print results
    print(f"\n{'='*80}")
    print(f"ANALYSIS REPORT: {folder_name.upper()}")
    print(f"{'-'*80}")
    print(f"Total simulations: {len(csv_files)}")
    print(f"Processing time: {time.time() - start_time:.2f}s")
    
    print(f"\nSpecial Actions:")
    for action, count in special_actions.items():
        print(f"- {action.replace('_', ' ').title()}: {count} times ({count/len(csv_files)*100:.1f}% of simulations)")
    
    print(f"\nWeighted Averages (Turn-Based):")
    print(f"- Total turns: {weighted_metrics['total_turns']}")
    print(f"- Avg damage received: {weighted_metrics['avg_received']:.2f}")
    print(f"- Avg damage dealt: {weighted_metrics['avg_dealt']:.2f}")
    
    print(f"\nUnweighted Averages (Simulation-Based):")
    print(f"- Avg turns/simulation: {unweighted_metrics['avg_turns']:.1f}")
    print(f"- Avg damage received: {unweighted_metrics['avg_received']:.2f}")
    print(f"- Avg damage dealt: {unweighted_metrics['avg_dealt']:.2f}")
    
    print(f"\nVictory Stats:")
    print(f"- Team defeated: {victory_stats['team_defeated']} times ({victory_stats['team_defeated_pct']:.1f}%)")
    print(f"- Boss defeated: {victory_stats['boss_defeated']} times ({victory_stats['boss_defeated_pct']:.1f}%)")
    
    # Print top defensive units
    print(f"\nTop Defensive Units:")
    sorted_defensive = sorted(
        [(k, v) for k, v in unit_stats.items()], 
        key=lambda x: (
            # Primary: Damage per Hit (lower = better mitigation)
            x[1]['damage_received'] / x[1]['hits_taken'] if x[1]['hits_taken'] > 0 else float('inf'),
            # Secondary: Total Damage Taken (lower = less overall burden)
            x[1]['damage_received']
        ),
        reverse=False
    )[:5]
    
    for (unit_id, unit_name), stats in sorted_defensive:
        dmg_per_hit = stats['damage_received'] / stats['hits_taken'] if stats['hits_taken'] > 0 else 0
        hits_per_app = stats['hits_taken'] / stats['appearances'] if stats['appearances'] > 0 else 0
        dmg_per_app = stats['damage_received'] / stats['appearances'] if stats['appearances'] > 0 else 0
        print(f"- {unit_name} (ID: {unit_id}):")
        print(f"  Damage per hit: {dmg_per_hit:.2f}")
        print(f"  Hits per appearance: {hits_per_app:.2f}")
        print(f"  Damage per appearance: {dmg_per_app:.2f}")
        print(f"  Appearances: {stats['appearances']}")
    
    print("="*80)
    
    # Save results
    save_results(
        folder_name=folder_name,
        total_simulations=len(csv_files),
        weighted_metrics=weighted_metrics,
        unweighted_metrics=unweighted_metrics,
        victory_stats=victory_stats,
        unit_stats=unit_stats,
        special_actions=special_actions
    )

def select_folder(start_path):
    """Interactive folder selection with hierarchical navigation"""
    current_path = start_path
    
    while True:
        # Get all subdirectories and CSV files in current path
        entries = list(os.scandir(current_path))
        folders = [e for e in entries if e.is_dir() and not e.name.startswith('.')]
        csv_files = [e for e in entries if e.is_file() and e.name.lower().endswith('.csv')]
        
        # If we've reached a folder with CSV files, return it
        if csv_files and not folders:
            return current_path
            
        # Show available folders
        print(f"\nCurrent location: {os.path.relpath(current_path, start_path) or 'Root'}")
        print("Available folders:")
        for i, folder in enumerate(folders, 1):
            print(f"{i}. {folder.name}")
            
        if csv_files:
            print(f"{len(folders)+1}. Process CSV files in this folder")
            
        print("0. Go back" if current_path != start_path else "0. Exit")
        
        # Get user selection
        try:
            choice = int(input("Enter your choice: "))
            
            # Handle navigation
            if choice == 0:
                if current_path == start_path:
                    return None  # User wants to exit
                current_path = os.path.dirname(current_path)  # Go up one level
                
            elif 1 <= choice <= len(folders):
                current_path = folders[choice-1].path  # Enter selected folder
                
            elif len(folders)+1 == choice and csv_files:
                return current_path  # User chose to process this folder's CSVs
                
            else:
                print("Invalid selection")
                
        except ValueError:
            print("Please enter a number")

def main():
    """Main function with interactive folder navigation"""
    base_folder = os.path.join("TurnSimulation", "Simulation_results")
    
    # Debug: Show the exact path being used
    print(f"Base input folder: {os.path.abspath(base_folder)}")
    
    try:
        selected_path = select_folder(base_folder)
        if selected_path:
            folder_name = os.path.relpath(selected_path, base_folder)
            print(f"\nProcessing folder: {os.path.abspath(selected_path)}")
            calculate_folder_averages(selected_path, folder_name)
            
    except FileNotFoundError:
        print(f"\nERROR: Directory not found - {os.path.abspath(base_folder)}")
        print("Please verify:")
        print(f"1. The folder 'TurnSimulation/Simulation_results' exists")
        print(f"2. Your working directory is: {os.getcwd()}")

if __name__ == "__main__":
    main()