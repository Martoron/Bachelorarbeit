from turtle import width
import pandas as pd
import numpy as np
import glob
import os
import re
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# IDs der Testeinheiten
GOKU_ID = 12031
VEGETA_ID = 12034

# Bedingungen und Pfade
conditions = {
    "Baseline1": "Simulation_results/Teams/TeamsBaseline/Team1WithIntUi",
    "Baseline2": "Simulation_results/Teams/TeamsBaseline/Team2WithMaskedSaiyan",
    "Baseline3": "Simulation_results/Teams/TeamsBaseline/Team3WithRofVegeta",
    "AGL_UI_no_adv": "Simulation_results/Teams/TeamsForAglUi/TeamGvariableSlot",
    "AGL_UI_adv": "Simulation_results/Teams/TeamsForAglUi/TeamGvariableSlotTypeAdvantage",
    "INT_Vegeta_no_adv": "Simulation_results/Teams/TeamsForIntVegeta/TeamVvariableSlot",
    "INT_Vegeta_adv": "Simulation_results/Teams/TeamsForIntVegeta/TeamVvariableSlotTypeAdvantage",
    "AGL_UI_no_adv_LLM": "Simulation_results/Teams/LLMTeams/LLMGoku/LLMTeamGvariableSlot",
    "AGL_UI_adv_LLM": "Simulation_results/Teams/LLMTeams/LLMGoku/LLMTeamGvariableSlotTypeAdvantage",
    "INT_Vegeta_no_adv_LLM": "Simulation_results/Teams/LLMTeams/LLMVegeta/LLMTeamVvariableSlot",
    "INT_Vegeta_adv_LLM": "Simulation_results/Teams/LLMTeams/LLMVegeta/LLMTeamVvariableSlotTypeAdvantage"
}

# Ausgabeordner
team_dir = "ResultPlots_Team"
testunit_dir = "ResultPlots_TestUnit"
os.makedirs(team_dir, exist_ok=True)
os.makedirs(testunit_dir, exist_ok=True)

type_adv_conditions = [
    "AGL_UI_adv", "AGL_UI_adv_LLM",
    "INT_Vegeta_adv", "INT_Vegeta_adv_LLM"
]

baseline_conditions = [
    "Baseline1", "Baseline2", "Baseline3"
]

def parse_number(s):
    if s is None:
        return 0.0
    s_clean = s.replace(".", "").replace(",", "")
    m = re.search(r"(-?\d+(\.\d+)?)", s_clean)
    if m:
        try:
            return float(m.group(1))
        except:
            return 0.0
    return 0.0

def extract_metrics(file_path, condition_name, mode="team"):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]

    boss_win = any("Boss defeated" in line for line in lines)

    unit_filter = None
    if mode == "testunit":
        if "AGL_UI" in condition_name:
            unit_filter = GOKU_ID
        elif "INT_Vegeta" in condition_name:
            unit_filter = VEGETA_ID

    total_dmg_dealt = 0.0
    total_dmg_received = 0.0
    turns = []
    item_count = 0
    heal_count = 0
    revive_count = 0

    for line in lines:
        if "Item" in line:
            item_count += 1
        if "heal" in line or "Healing item used" in line:
            heal_count += 1
        if "revive" in line:
            revive_count += 1

        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 7:
            continue
        try:
            turn = int(parts[0])
        except:
            continue
        turns.append(turn)

        if mode == "team":
            total_dmg_dealt += parse_number(parts[6])
            total_dmg_received += parse_number(parts[4])
        elif mode == "testunit":
            try:
                uid = int(parts[1])
            except:
                continue
            if uid == unit_filter:
                total_dmg_dealt += parse_number(parts[6])
                total_dmg_received += parse_number(parts[4])

    total_turns = max(turns) if turns else 0

    return {
        "SimulationID": os.path.basename(file_path).replace(".csv", ""),
        "Condition": condition_name,
        "BossWin": int(boss_win),
        "TotalDmgDealt": total_dmg_dealt,
        "TotalDmgReceived": total_dmg_received,
        "Turns": total_turns,
        "ItemsUsed": item_count,
        "HealsUsed": heal_count,
        "RevivesUsed": revive_count
    }

def bootstrap_ci(data, n_bootstrap=10000, ci=95):
    data = np.array(data)
    n = len(data)
    boot_means = []
    for _ in range(n_bootstrap):
        sample = np.random.choice(data, size=n, replace=True)
        boot_means.append(np.mean(sample))
    return np.mean(data), np.percentile(boot_means, (100-ci)/2), np.percentile(boot_means, 100-(100-ci)/2)

def bootstrap_ratio(numerators, denominators, n_bootstrap=10000, ci=95):
    numer = np.array(numerators, dtype=float)
    denom = np.array(denominators, dtype=float)
    n = len(numer)
    if n == 0:
        return np.nan, np.nan, np.nan
    denom_sum = denom.sum()
    point = np.nan if denom_sum == 0 else numer.sum() / denom_sum
    boot_stats = []
    for _ in range(n_bootstrap):
        idx = np.random.randint(0, n, size=n)
        s_num = numer[idx].sum()
        s_den = denom[idx].sum()
        if s_den != 0:
            boot_stats.append(s_num / s_den)
    return point, np.percentile(boot_stats, (100-ci)/2), np.percentile(boot_stats, 100-(100-ci)/2)

def create_summary(mode, out_dir):
    all_rows = []
    for cond, path in conditions.items():
        for file in glob.glob(os.path.join(path, "*.csv")):
            all_rows.append(extract_metrics(file, cond, mode=mode))
    df_all = pd.DataFrame(all_rows)
    results = []
    special_actions = []
    for cond, group in df_all.groupby("Condition"):
        mean_wr, low_wr, up_wr = bootstrap_ci(group["BossWin"])
        mean_dealt, low_dealt, up_dealt = bootstrap_ratio(group["TotalDmgDealt"], group["Turns"])
        mean_recv, low_recv, up_recv = bootstrap_ratio(group["TotalDmgReceived"], group["Turns"])
        # mean_heals, low_heals, up_heals = bootstrap_ci(group["HealsUsed"])
        # mean_revives, low_revives, up_revives = bootstrap_ci(group["RevivesUsed"])
        results.append({
            "Condition": cond,
            "WinRate": mean_wr, "WinRate_CI_L": low_wr, "WinRate_CI_U": up_wr,
            "DmgDealt": mean_dealt, "DmgDealt_CI_L": low_dealt, "DmgDealt_CI_U": up_dealt,
            "DmgReceived": mean_recv, "DmgReceived_CI_L": low_recv, "DmgReceived_CI_U": up_recv,
            # "HealsUsed": mean_heals, "HealsUsed_CI_L": low_heals, "HealsUsed_CI_U": up_heals,
            # "RevivesUsed": mean_revives, "RevivesUsed_CI_L": low_revives, "RevivesUsed_CI_U": up_revives
        })
        items_used = group["ItemsUsed"].sum()
        heals_used = group["HealsUsed"].sum()
        revives_used = group["RevivesUsed"].sum()
        special_actions.append({
            "Condition": cond,
            "ItemsUsed": items_used,
            "HealsUsed": heals_used,
            "RevivesUsed": revives_used
        })
    df_ci = pd.DataFrame(results)
    df_ci.to_csv(os.path.join(out_dir, f"metrics_with_bootstrap_ci_{mode}.csv"), index=False)
    df_all.to_csv(os.path.join(out_dir, f"per_simulation_totals_{mode}.csv"), index=False)
    df_special = pd.DataFrame(special_actions)
    df_special.to_csv(os.path.join(out_dir, f"special_actions_{mode}.csv"), index=False)
    return df_ci

def plot_with_highlight(df, metric, ci_lower, ci_upper, ylabel, title, filename, out_dir, legend_pos="default"):
    plt.figure(figsize=(8,5))
    colors = ["orange" if cond in type_adv_conditions else "lightgreen" if cond in baseline_conditions else "skyblue" for cond in df["Condition"]]
    plt.bar(df["Condition"], df[metric],
            yerr=[df[metric] - df[ci_lower], df[ci_upper] - df[metric]],
            capsize=5, color=colors, edgecolor='black')
    plt.ylabel(ylabel)
    plt.title(title)
    plt.xticks(rotation=45, ha='right')
    if legend_pos == "lower left":
        plt.legend(handles=[
            Patch(facecolor="lightgreen", label="Baseline"),
            Patch(facecolor="skyblue", label="Normal Condition (No Advantage)"),
            Patch(facecolor="orange", label="Type Advantage (Illustration)")
        ], loc='lower left')
    else:
        plt.legend(handles=[
            Patch(facecolor="lightgreen", label="Baseline"),
            Patch(facecolor="skyblue", label="Normal Condition (No Advantage)"),
            Patch(facecolor="orange", label="Type Advantage (Illustration)")
        ], loc='best')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, filename), dpi=300)
    plt.close()

def plot_special_actions(df, out_dir, mode="team"):
    plt.figure(figsize=(8,5))
    
    # Condition Farben wie in anderen Plots
    colors = ["orange" if cond in type_adv_conditions else "lightgreen" if cond in baseline_conditions else "skyblue" 
              for cond in df["Condition"]]
    
    # Balkenpositionen
    x = np.arange(len(df["Condition"]))
    width = 0.35
    
    # Balken für jede Metrik

    plt.bar(x - width/2, df["HealsUsed"], width, 
            label='Heals Used', color='forestgreen', edgecolor='black')
    plt.bar(x + width/2, df["RevivesUsed"], width, 
            label='Revives Used', color='firebrick', edgecolor='black')
    
    # Achsenbeschriftungen
    plt.ylabel('Count')
    plt.title(f'Special Actions Comparison ({mode.capitalize()})')
    plt.xticks(x, df["Condition"], rotation=45, ha='right')
    
    # Farbige Condition Labels wie in anderen Plots
    for label, color in zip(plt.gca().get_xticklabels(), colors):
        label.set_color(color)
    
    # Legende im Stil der anderen Plots
    plt.legend(handles = [
        Patch(facecolor="lightgreen", label="Baseline"),
        Patch(facecolor="skyblue", label="Normal Condition"),
        Patch(facecolor="orange", label="Type Advantage"),
        Patch(facecolor="forestgreen", edgecolor='black', label="Heals Used"),
        Patch(facecolor="firebrick", edgecolor='black', label="Revives Used")
    ], loc='best')
    
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, f"special_actions_combined_{mode}.png"), dpi=300, bbox_inches='tight')
    plt.close()

def calculate_bis_adjusted(df_team, df_testunit):
    base_df = df_team[df_team["Condition"].isin(["Baseline1", "Baseline2", "Baseline3"])]
    baseline = base_df[["WinRate", "DmgReceived", "DmgDealt"]].mean()
    pairs = [
        ("AGL_UI_no_adv", "AGL_UI_no_adv_LLM", "Goku_no_adv"),
        ("INT_Vegeta_no_adv", "INT_Vegeta_no_adv_LLM", "Vegeta_no_adv"),
        ("AGL_UI_adv", "AGL_UI_adv_LLM", "Goku_adv"),
        ("INT_Vegeta_adv", "INT_Vegeta_adv_LLM", "Vegeta_adv"),
    ]
    # print("Conditions in df_team:", df_team["Condition"].unique())
    rows = []
    diag_rows = []
    tolerance = 0.05
    for power_cond, llm_cond, label in pairs:
        # print(f"Calculating BIS for {label} with power condition '{power_cond}' and LLM condition '{llm_cond}'")
        p_team = df_team.loc[df_team["Condition"] == power_cond].iloc[0]
        l_team = df_team.loc[df_team["Condition"] == llm_cond].iloc[0]
        p_test = df_testunit.loc[df_testunit["Condition"] == power_cond].iloc[0]
        # print(f"Power Test Values: {p_test}")
        l_test = df_testunit.loc[df_testunit["Condition"] == llm_cond].iloc[0]
        # print(f"LLM Test Values: {l_test}")
        row = {"Condition": llm_cond, "Case": label}
        diag = {"Case": label}
        for metric in ["WinRate", "DmgReceived", "DmgDealt"]:
            base = float(baseline[metric])
            pval = float(p_team[metric])
            lval = float(l_team[metric])
            denom = abs(pval - base)
            num = abs(lval - base)
            if denom >= num:
                bis_val = np.nan if denom == 0 else num / denom
            elif num > denom:
                bis_val = np.nan if denom == 0 else denom / num
            # row[f"BIS_{metric}"] = bis_val
            diag[f"{metric}_baseline"] = base
            diag[f"{metric}_power"] = pval
            diag[f"{metric}_llm"] = lval

            if metric in ["DmgDealt", "DmgReceived"]:
                p_test_val = float(p_test[metric])
                diag[f"{metric}_test_power"] = p_test_val
                l_test_val = float(l_test[metric])
                diag[f"{metric}_test_llm"] = l_test_val
                rel_diff = abs(p_test_val - l_test_val) / abs(p_test_val) if p_test_val != 0 else 0
                diag[f"{metric}_test_rel_diff"] = rel_diff
                if rel_diff <= tolerance:
                    bis_val = 1.0
           
            diag[f"BIS_{metric}"] = bis_val
            row[f"BIS_{metric}"] = bis_val

        rows.append(row)
        diag_rows.append(diag)
    df_bis_adj = pd.DataFrame(rows)
    df_bis_adj.to_csv(os.path.join(team_dir, "bis_values_adjusted.csv"), index=False)
    pd.DataFrame(diag_rows).to_csv(os.path.join(team_dir, "bis_diagnostics_adjusted.csv"), index=False)
    return df_bis_adj

# ===== Ausführung =====
df_team = create_summary(mode="team", out_dir=team_dir)
df_special_actions_team = pd.read_csv(os.path.join(team_dir, "special_actions_team.csv"))
df_testunit = create_summary(mode="testunit", out_dir=testunit_dir)
df_bis = calculate_bis_adjusted(df_team, df_testunit)

for mode, df, out_dir in [("team", df_team, team_dir), ("testunit", df_testunit, testunit_dir)]:
    plot_with_highlight(df, "WinRate", "WinRate_CI_L", "WinRate_CI_U", "Win Rate", f"WinRate_{mode}", f"WinRate_{mode}.png", out_dir, legend_pos="lower left")
    plot_with_highlight(df, "DmgDealt", "DmgDealt_CI_L", "DmgDealt_CI_U", "Avg Damage Dealt / Turn", f"DmgDealt_{mode}", f"DmgDealt_{mode}.png", out_dir)
    plot_with_highlight(df, "DmgReceived", "DmgReceived_CI_L", "DmgReceived_CI_U", "Avg Damage Received / Turn", f"DmgReceived_{mode}", f"DmgReceived_{mode}.png", out_dir)

plot_special_actions(df_special_actions_team, team_dir, mode="team")

def plot_bis_adjusted(df_bis, out_dir):
    metrics = ["BIS_WinRate", "BIS_DmgReceived", "BIS_DmgDealt"]
    labels = {
        "BIS_WinRate": "BIS (Win Rate)",
        "BIS_DmgReceived": "BIS (Damage Received)",
        "BIS_DmgDealt": "BIS (Damage Dealt)"
    }
    
    for metric in metrics:
        plt.figure(figsize=(8,5))
        # Farben wie bei den normalen Plots: Cases mit "adv" orange, sonst blau
        colors = ["skyblue" if "no_adv" in case.lower() else "orange" for case in df_bis["Case"]]

        plt.bar(df_bis["Case"], df_bis[metric], color=colors, edgecolor='black')
        plt.ylabel(labels[metric], fontsize=20)
        plt.ylim(0, 1.05)  # BIS ist normiert, daher 0–1
        plt.title(labels[metric], fontsize=22)
        plt.xticks(rotation=45, ha='right', fontsize=16)
        plt.yticks(fontsize=16)
        plt.axhline(0.3, color="green", linestyle="--", label="Erfolgreich (≤0.3)")
        plt.axhline(0.7, color="red", linestyle="--", label="Unzureichend (>0.7)")
        # if metric == "BIS_DmgDealt":
        #     plt.legend(handles=[
        #         Patch(facecolor="red", label="Failure Threshold"),
        #         Patch(facecolor="green", label="Success Threshold"),
        #         Patch(facecolor="skyblue", label="Normal Condition (No Advantage)"),
        #         Patch(facecolor="orange", label="Type Advantage (Illustration)")
        #     ], loc='lower left', fontsize=16)
        # else:
        #     plt.legend(handles=[
        #         Patch(facecolor="red", label="Failure Threshold"),
        #         Patch(facecolor="green", label="Success Threshold"),
        #         Patch(facecolor="skyblue", label="Normal Condition (No Advantage)"),
        #         Patch(facecolor="orange", label="Type Advantage (Illustration)")
        #     ], loc='best', fontsize=16)
        plt.tight_layout()
        plt.savefig(os.path.join(out_dir, f"{metric}_adjusted.png"), dpi=300)
        plt.close()

# Nach der BIS-Berechnung aufrufen:
plot_bis_adjusted(df_bis, team_dir)

# Legende für BIS-Plot speichern für Layout
def save_bis_legend(out_dir):
    fig, ax = plt.subplots(figsize=(6, 1))  # Breite ggf. anpassen
    ax.axis('off')

    legend_elements = [
        Patch(facecolor="red", label="Failure Threshold"),
        Patch(facecolor="green", label="Success Threshold"),
        Patch(facecolor="skyblue", label="Normal Condition (No Advantage)"),
        Patch(facecolor="orange", label="Type Advantage (Illustration)")
    ]

    legend = ax.legend(handles=legend_elements, loc="center", fontsize=14, frameon=False)
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "bis_legend.png"), dpi=300, bbox_inches='tight', transparent=True)
    plt.close()

# Legende für BIS-Plot speichern für Layout
save_bis_legend(team_dir)

# Gegenüberstellung von Einflüssen auf die winrate
# Special Acitions
# Balkendiagramm
def plot_actions_vs_winrate(df_combined_metrics, out_dir, mode="team"):
    fig = plt.figure(figsize=(8, 5))
    ax1 = fig.add_subplot()

    colors = ["orange" if cond in type_adv_conditions else 
             "lightgreen" if cond in baseline_conditions else 
             "skyblue" for cond in df_combined_metrics["Condition"]]
        

    if "HealsUsed" in df_combined_metrics.columns and "RevivesUsed" in df_combined_metrics.columns:
        # Balkenpositionierung
        x = np.arange(len(df_combined_metrics["Condition"])) 
        width = 0.35  # Gleiche Breite wie in deinen anderen Plots
        
        # ZWEI getrennte Balken (nicht addiert!)
        rects1 = ax1.bar(x - width/2, df_combined_metrics["HealsUsed"], width,
                        label='Heals Used', color='forestgreen', edgecolor='black')
        rects2 = ax1.bar(x + width/2, df_combined_metrics["RevivesUsed"], width,
                        label='Revives Used', color='firebrick', edgecolor='black')
        
        ax1.set_ylabel('Action Count', color='black')
        ax1.tick_params(axis='y', labelcolor='black')

    elif "DmgDealt" in df_combined_metrics.columns or "DmgReceived" in df_combined_metrics.columns:
        metric_col = "DmgDealt" if "DmgDealt" in df_combined_metrics.columns else "DmgReceived"
        x = np.arange(len(df_combined_metrics["Condition"]))
        width = 0.6

        rects = ax1.bar(x, df_combined_metrics[metric_col], width,
                        label=metric_col.replace("Dmg", "Damage "), color=colors, edgecolor='black')

        ax1.set_ylabel(metric_col.replace("Dmg", "Damage ") + "/Turn", color='black')
        ax1.tick_params(axis='y', labelcolor='black')

        # Manuelle Farb-Legende
        legend_elements = [
            Patch(facecolor='lightgreen', label='Baseline'),
            Patch(facecolor='skyblue', label='Normal Condition (No Advantage)'),
            Patch(facecolor='orange', label='Type Advantage (Illustration)')
            ]
    
    # WinRate-Linie (unverändert)
    ax2 = ax1.twinx()
    ax2.plot(x, df_combined_metrics["WinRate"]*100, 'ko-', 
             linewidth=2, markersize=8, label='Win Rate (%)')
    ax2.set_ylabel('Win Rate (%)', color='black')
    ax2.tick_params(axis='y', labelcolor='black')
    ax2.set_ylim(0, 100)
    
    # Titel & Labels
    if "HealsUsed" in df_combined_metrics.columns:
        plt.title(f'Heals/Revives vs Win Rate ({mode.capitalize()})')
    elif "DmgDealt" in df_combined_metrics.columns:
        plt.title(f'Damage Dealt vs Win Rate ({mode.capitalize()})')
    elif "DmgReceived" in df_combined_metrics.columns:
        plt.title(f'Damage Received vs Win Rate ({mode.capitalize()})')

    # Achsenbeschriftung sauber setzen
    ax1.set_xticks(x)
    ax1.set_xticklabels(df_combined_metrics["Condition"], rotation=45, ha='right')

    # Farbige Condition-Labels (wie gehabt)
    if "HealsUsed" in df_combined_metrics.columns:
        for label, color in zip(ax1.get_xticklabels(), colors):
            label.set_color(color)
    
    # Kombinierte Legende
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    if "HealsUsed" in df_combined_metrics.columns:
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    else:
        handles = legend_elements + lines2
        labels = [h.get_label() for h in handles]
        ax1.legend(handles, labels, loc='lower left')
    plt.tight_layout()
    if "HealsUsed" in df_combined_metrics.columns:
        plt.savefig(os.path.join(out_dir, f"actions_vs_winrate_{mode}.png"), dpi=300)
    elif "DmgDealt" in df_combined_metrics.columns:
        plt.savefig(os.path.join(out_dir, f"dmgDealt_vs_winrate_{mode}.png"), dpi=300)
    elif "DmgReceived" in df_combined_metrics.columns:
        plt.savefig(os.path.join(out_dir, f"dmgReceived_vs_winrate_{mode}.png"), dpi=300)
    plt.close()

# Streudiagramm
def plot_action_winrate_correlation(df, out_dir, mode="team"):
    plt.figure(figsize=(8, 6))
    
    # Farbdefinition pro Condition
    colors = ["orange" if cond in type_adv_conditions else 
              "lightgreen" if cond in baseline_conditions else 
              "skyblue" for cond in df["Condition"]]
    
    # Bestimmen, welche Metrik verwendet wird
    if "HealsUsed" in df.columns and "RevivesUsed" in df.columns:
        x_vals = df["HealsUsed"] + df["RevivesUsed"]
        x_label = "Total Special Actions Used"
        file_suffix = "correlation_actions_winrate"
    elif "HealsUsed" in df.columns:
        x_vals = df["HealsUsed"]
        x_label = "Heals Used"
        file_suffix = "correlation_healsUsed_winrate"
    elif "RevivesUsed" in df.columns:
        x_vals = df["RevivesUsed"]
        x_label = "Revives Used"
        file_suffix = "correlation_revivesUsed_winrate"
    elif "DmgDealt" in df.columns:
        x_vals = df["DmgDealt"]
        x_label = "Damage Dealt"
        file_suffix = "correlation_dmgDealt_winrate"
    elif "DmgReceived" in df.columns:
        x_vals = df["DmgReceived"]
        x_label = "Damage Received"
        file_suffix = "correlation_dmgReceived_winrate"
    else:
        raise ValueError("Keine gültige Metrik-Spalte gefunden.")
    
    y_vals = df["WinRate"] * 100

    # Scatter-Plot
    for i, cond in enumerate(df["Condition"]):
        plt.scatter(x_vals[i], y_vals[i], c=colors[i], s=100, 
                    label=cond if i < 3 else "", alpha=0.7)

    # Regressionslinie
    z = np.polyfit(x_vals, y_vals, 1)
    p = np.poly1d(z)
    sorted_idx = np.argsort(x_vals)
    plt.plot(x_vals[sorted_idx], p(x_vals[sorted_idx]), "k--", label="Regression")

    # Achsentitel & Diagrammtitel
    plt.xlabel(x_label, fontsize=20)
    plt.ylabel("Win Rate (%)", fontsize=20)
    plt.title(f'{x_label} vs Win Rate ({mode.capitalize()})', fontsize=22)

    # Achsenbeschriftungen größe(Tick-Labels)
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)

    # Legende mit Farbcode
    legend_elements = [
        Patch(facecolor='lightgreen', label='Baseline'),
        Patch(facecolor='skyblue', label='Normal Condition'),
        Patch(facecolor='orange', label='Type Advantage'),
    ]
    plt.legend(handles=legend_elements, loc="best", fontsize=16)
    
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, f"{file_suffix}_{mode}.png"), dpi=300)
    plt.close()

df_team_for_additional_plots = pd.read_csv(os.path.join(team_dir, "metrics_with_bootstrap_ci_team.csv"))
df_special_team = pd.read_csv(os.path.join(team_dir, "special_actions_team.csv"))

# Zusammenführen der Daten für die Visualisierung
df_actions_vs_winRate = pd.merge(
    df_special_team,
    df_team_for_additional_plots[["Condition", "WinRate"]],
    on="Condition"
)

df_heals_vs_winRate = pd.merge(
    df_special_team[["Condition", "HealsUsed"]],
    df_team_for_additional_plots[["Condition", "WinRate"]],
    on="Condition"
)

df_revives_vs_winRate = pd.merge(
    df_special_team[["Condition", "RevivesUsed"]],
    df_team_for_additional_plots[["Condition", "WinRate"]],
    on="Condition"
)

df_dmgDealt_vs_winRate = df_team_for_additional_plots[["Condition", "DmgDealt", "WinRate"]]
df_dmgReceived_vs_winRate = df_team_for_additional_plots[["Condition", "DmgReceived", "WinRate"]]

df_actions_vs_winRate.to_csv(os.path.join(team_dir, "combined_actions_winrate_team.csv"), index=False)

plot_actions_vs_winrate(df_actions_vs_winRate, team_dir)
plot_actions_vs_winrate(df_dmgDealt_vs_winRate, team_dir)
plot_actions_vs_winrate(df_dmgReceived_vs_winRate, team_dir)

plot_action_winrate_correlation(df_actions_vs_winRate, team_dir)
plot_action_winrate_correlation(df_dmgDealt_vs_winRate, team_dir)
plot_action_winrate_correlation(df_dmgReceived_vs_winRate, team_dir)
plot_action_winrate_correlation(df_heals_vs_winRate, team_dir)
plot_action_winrate_correlation(df_revives_vs_winRate, team_dir)

print("Fertig: Team- und Testunit-Auswertungen inkl. Adjusted BIS erstellt.")