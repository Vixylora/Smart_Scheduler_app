# Smart Scheduler – CPU Scheduling Simulator

A Python/CustomTkinter application for simulating, comparing, and visualizing CPU scheduling algorithms.
Created by **Younes Benamour**, **Younes Ramdani** & **Takieddine Nouar**

## What It Does

- Simulates **FCFS**, **SJF**, **Round Robin**, and **Priority** scheduling algorithms
- Compares all algorithms side-by-side with weighted scoring
- Recommends the best algorithm based on process characteristics (intelligent advisor)
- Visualizes execution via an animated **Gantt chart** with process labels
- Tracks all process attributes: PID, Arrival, Burst, Priority, Remaining, Waiting, Turnaround, Response

## Quick Start

```bash
# 1. Create virtual environment and install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Run the application
./smart-scheduler
# or
python app.py
```

## How to Use

### Managing Processes
- **Add** a process: Click `+ Add` button or menu → Add Process
- **Delete** a process: Click `− Del` button or menu → Delete Process
- **Edit** a process: Double-click any cell in the process table (PID, Arrival, Burst, Priority)

### Configuring Simulation
- **Algorithm**: Select from dropdown (FCFS, SJF, Round Robin, Priority)
- **Quantum**: Set time quantum for Round Robin (default: 2)
- **Priority Mode**: Toggle between Preemptive and Non-preemptive for Priority algorithm

### Running Simulation
- **▶ Play**: Start/Resume animated simulation
- **⏭ Step**: Advance one time unit at a time
- **↺ Reset**: Stop and reset to initial state
- **Remaining column** updates live as the cursor advances

### Viewing Results
- **Gantt Chart**: Shows execution timeline at the top with cursor and process labels
- **Statistics Table**: Per-process Waiting, Turnaround, Response, Completion times
- **Comparison Table**: All 4 algorithms ranked by score (★ marks the best)
- **Metrics Panel**: Averages for Waiting, Turnaround, Response, Throughput, CPU Utilization, Context Switches
- **Advisor Panel**: Recommends the best algorithm with reasoning (notes when comparison disagrees)

### File Operations
- **Import**: Menu → Load File → Load JSON or Load CSV
- **Export Processes**: Menu → Export → Export Processes JSON/CSV
- **Export Comparison**: Menu → Export → Export Comparison CSV
- **Session**: Algorithm, quantum, and priority mode are saved automatically on exit

## Menu Structure

```
Add Process
Delete Process
Load File → Load JSON... | Load CSV...
Select Algorithm → FCFS | SJF | Round Robin | Priority
Start Simulation
Export → Export Processes JSON... | Export Processes CSV... | Export Comparison CSV...
Exit
```

## Project Structure

```
app.py              Entry point
config.yaml         User overrides (optional)
requirements.txt    Dependencies (customtkinter, pyyaml)
smart-scheduler     Launcher script (executable)

config/
  defaults.yaml     All tunable parameters (no magic numbers)
  loader.py         Config load/validate/merge with schema validation

core/
  process.py        Process model with copy() for immutability
  algorithms.py     All 4 scheduling algorithms, CircularQueue, LinkedList
  scorer.py         Weighted scoring (waiting, turnaround, response, CPU, fairness)
  advisor.py        Rule-based recommendation + comparison
  engine.py         SimulationEngine with caching and auto-tune animation speed

ui/
  main_window.py    Single-page layout (Gantt, 3 tables, controls, metrics, advisor)
  gantt_widget.py   Canvas-based Gantt chart with progressive reveal and labels
  process_table.py  Editable treeview with inline cell editing

theme/
  manager.py        Dark/light theme from config

persistence/
  session.py        Save/restore to ~/.config/smart-scheduler/session.json
  io.py             JSON/CSV import and export for process sets

tests/
  test_advisor.py   5 tests for recommendation rules
  test_algorithms.py 8 tests for simulation + CircularQueue + LinkedList
  test_process.py   2 tests for copy() and sanitize()
  test_scorer.py    3 tests for scoring math

docs/
  report.md         PDF report template (6 sections per spec)
```

## Testing

```bash
.venv/bin/python -m pytest tests/ -v
```

18 tests covering: algorithm correctness, data structures, process immutability, scoring math, advisor logic.

## Config

Edit `config.yaml` in the project root to override defaults without touching `config/defaults.yaml`:

```yaml
# Change default algorithm
algorithms:
  defaults:
    quantum: 3

# Change animation speed
timing:
  animation_interval_ms: 500

# Change scoring weights
algorithms:
  scoring:
    weight_waiting: 0.4
    weight_turnaround: 0.3
```

All parameters are documented in `config/defaults.yaml`.

## Tech Stack

- **Python 3.13**
- **CustomTkinter 5.2.2** (modern Tkinter GUI)
- **PyYAML 6.0** (config system)
- **tkinter Canvas** (Gantt chart rendering)
