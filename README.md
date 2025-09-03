# Dokkan Battle Simulation – Bachelorarbeit

Dieses Repository enthält den Code und die Daten für meine Bachelorarbeit.
Neben dem eigentlichen Simulator sind auch die verwendeten **LLM Prompts und Antworten** enthalten.

---

## 📂 Projektstruktur

- `TurnSimulation/`  
  Enthält den Simulator:
  - `battle.py` → Originalversion (für Simulationen genutzt)  
  - `battle_fully_commented.py` → Kommentierte Version für bessere Nachvollziehbarkeit  
  - `boss.py`, `links.py`, `superAttack.py` (+ kommentierte Versionen)  
  - `metric_plot_with_LLM.py` → erstellt vollständige Metriken und Plots
  - `ResultPlots_(Team/Testunit)` → Enthält die vollständige Metriken und Plots   
  - `Logs/` → wird automatisch beim Ausführen erstellt (nicht versioniert)  
  - `Simulation_results/` → Enthält automatisch erzeugte Ergebnisse und Analysen (in Teams die csv in Analysis_results die Zusammenfassungen)  

- `Teams/`  
  Enthält JSON-Dateien mit Teamzusammenstellungen:
  - `TeamsBaseline/` → Baseline Teams  
  - `LLMTeams/` → Teams mit LLM-Anpassungen  
  - `TeamsForAglUi/`, `TeamsForIntVegeta/` → Teams für Testeinheiten 
  - `TEST/` → Falls man etwas asurpobieren möchte ohne die Struktur zu verändern  

- `LLMPrompts+Answers/`  
  Enthält die Prompts und Antworten der LLMs, die im Rahmen der Arbeit verwendet wurden

- `simulation_analysis.py`  
  Skript zur schnellen Aggregation von Metriken aus CSV-Ergebnissen.  

- `n-times_simulation.bat`  
  Batch-Datei zum mehrfachen automatisierten Ausführen der Simulation (Standard: 100 Runs).  

---

## ⚙️ Installation

1. Repository klonen:
   ```bash
   git clone https://github.com/USERNAME/DokkanBachelorarbeit.git
   cd DokkanBachelorarbeit
   ```

2. Abhängigkeiten installieren:
   ```bash
   pip install -r requirements.txt
   ```

---

## ▶️ Nutzung

### Einzelne Simulation starten
1. In `TurnSimulation/battle.py` oder `battle_fully_commented.py` im `main`-Block ein Team auswählen:
   ```python
   load_units_from_json("../Teams/TEST/LLMTeamVvariableSlotTypeAdvantage.json")
   ```
2. Simulation starten:
   ```bash
   cd TurnSimulation
   python battle_fully_commented.py
   ```
   Ergebnis wird als CSV unter `Simulation_results/Teams/...` gespeichert.

### Mehrfachsimulation
Mit Batch-Datei im Root:
```bash
n-times_simulation.bat
```
Standardmäßig werden 100 Runs ausgeführt.  
Falls man die Originalversion nutzen möchtest, ersetze in der BAT-Datei:
```
python battle_fully_commented.py
```
durch
```
python battle.py
```

### Analyse
Zur schnellen Aggregation:
```bash
python simulation_analysis.py
```

Zur vollständigen Auswertung mit Plots:
```bash
cd TurnSimulation
python metric_plot_with_LLM.py
```

---

## 📝 Hinweise
- **Original vs. Fully Commented**: Simulationen wurden mit `battle.py` durchgeführt.  
  `battle_fully_commented.py` ist für die Nachvollziehbarkeit und Dokumentation und wurde für diesen Zweck, relativ am Ende gerafactored und kommentiert. Ich habe ausgiebig getestet und es sollte alles gleich sein aber da die Standard-PRNG von Python zur Simulation von Zufall bzw für Wahrscheinlichkeiten verwendet wurde, können Kleinigkeiten, wie eine leicht geänderte Reihenfolge die RNG verändern und da ich dahingehend recht Paranoid bin habe ich beide Versionen hinterlegt. 

