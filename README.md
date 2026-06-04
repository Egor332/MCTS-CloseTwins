# MCTS Close Twins Avoidance

Projekt badający zastosowania algorytmu **Monte Carlo Tree Search (MCTS)** w grze w unikanie ciasnych bliźniaków — asymetrycznej grze turowej opartej na kombinatoryce słów.

---

## Gra

Dwóch graczy naprzemiennie buduje słowo nad ustalonym alfabetem:

- **Wskazujący (Pointer / Gracz 1)** — wybiera pozycję (indeks), na której pojawi się nowa litera. Wygrywa, gdy w słowie powstaną **ciasne bliźniaki** (podsłowo postaci `xx`, np. `aa`, `abab`).
- **Wstawiający (Inserter / Gracz 2)** — wybiera literę z alfabetu i wstawia ją na wskazaną pozycję. Wygrywa, gdy słowo osiągnie maksymalną długość **bez** ciasnych bliźniaków.

Parametry gry: rozmiar alfabetu, maksymalna długość słowa.

---

## Warianty algorytmu

Każde AI konfiguruje się niezależnie, łącząc trzy wymienialne strategie:

| Oś | Dostępne warianty |
|---|---|
| **Selekcja** | `uct` (klasyczny UCT), `ucb1_tuned` (z wariancją empiryczną) |
| **Symulacja** | `random` (losowy rollout), `heuristic` (filtruje ruchy tworzące bliźniaki) |
| **Propagacja** | `standard` (klasyczna), `solver` (MCTS-Solver z propagacją udowodnionych węzłów) |

Dodatkowo do dowolnej strategii selekcji można włączyć **Progressive Bias** (`progressive_bias: true`), który dodaje heurystyczny składnik do formuły UCT. Składnik ten faworyzuje bezpieczniejsze ruchy na początku (mało wizyt) i zanika w miarę zbierania statystyk. Parametr `bias_weight` kontroluje początkową siłę wpływu heurystyki.

---

## Wymagania

```
Python >= 3.10
PyQt6 >= 6.6.0
numpy
pyyaml
tqdm
```

Instalacja zależności:

```bash
pip install -r requirements.txt
```

---

## Uruchomienie GUI

```bash
python -m src.main
```

Po uruchomieniu wybierz:
- **tryb** — Human Inserter / Human Pointer / AI vs AI
- **rozmiar alfabetu** (2–26)
- **maksymalną długość słowa** (3–30)

Naciśnij `Esc` w trakcie gry, aby wrócić do menu.

---

## Uruchomienie eksperymentów z terminala

Eksperymenty definiuje się w plikach YAML, a następnie uruchamia headless (bez GUI):

```bash
python -m src.run_match --config experiments/example.yaml --output results/
```

Wyniki każdego meczu trafiają do:

```
results/
└── <nazwa_meczu>/
    ├── config.yaml     # kopia użytego configu
    └── results.csv     # wyniki wszystkich partii
```

### Format pliku YAML

```yaml
matches:
  - name: "ucb1tuned_vs_uct"
    alphabet_size: 3
    max_word_length: 15
    num_games: 100
    base_seed: 42
    pointer:
      name: "UCB1-Tuned + Solver + PB"
      iterations: 1000
      selection: "ucb1_tuned"      # uct | ucb1_tuned
      simulation: "heuristic"      # random | heuristic
      backpropagation: "solver"    # standard | solver
      exploration_constant: 1.414
      progressive_bias: true       # true | false (domyslnie false)
      bias_weight: 1.0             # sila progressive bias (domyslnie 1.0)
    inserter:
      name: "UCT"
      iterations: 1000
      selection: "uct"
      simulation: "random"
      backpropagation: "standard"
      exploration_constant: 1.414
      progressive_bias: false
```

### Kolumny w wynikowym CSV

| Kolumna | Opis |
|---|---|
| `match_name` | Nazwa meczu z configu |
| `game_id` | Numer partii (0-indexed) |
| `seed` | Ziarno RNG użyte w tej partii |
| `alphabet_size` | Rozmiar alfabetu |
| `max_word_length` | Limit długości słowa |
| `winner` | `P1_WINS_TWINS` lub `P2_WINS_LIMIT` |
| `num_turns` | Liczba ruchów w partii |
| `final_word` | Słowo na koniec gry |
| `duration_seconds` | Czas trwania partii (sekundy) |
| `pointer_name` / `inserter_name` | Nazwa AI |
| `pointer_iterations` / `inserter_iterations` | Liczba iteracji MCTS |
| `pointer_selection` / `inserter_selection` | Strategia selekcji (`uct` / `ucb1_tuned`) |
| `pointer_simulation` / `inserter_simulation` | Strategia symulacji (`random` / `heuristic`) |
| `pointer_backpropagation` / `inserter_backpropagation` | Strategia propagacji (`standard` / `solver`) |
| `pointer_exploration_constant` / `inserter_exploration_constant` | Stała eksploracji |
| `pointer_progressive_bias` / `inserter_progressive_bias` | Czy włączony Progressive Bias |
| `pointer_bias_weight` / `inserter_bias_weight` | Waga Progressive Bias |

---

## Struktura projektu

```
src/
├── main.py                         # Punkt wejścia GUI
├── run_match.py                    # Punkt wejścia eksperymentów (CLI)
├── domain.py                       # Typy: Role, GameStatus, GameMode
├── IGameEngine.py                  # Interfejs silnika gry
├── engine/
│   ├── game.py                     # Logika gry i stanu
│   └── twin_checker.py             # Detekcja ciasnych bliźniaków
├── mcts/
│   ├── mcts.py                     # Algorytm MCTS (orkiestrator)
│   ├── node.py                     # Węzeł drzewa MCTS
│   └── strategies/
│       ├── selection.py            # UCTStrategy, UCB1TunedStrategy, ProgressiveBias
│       ├── simulation.py           # RandomSimulation, HeuristicSimulation
│       └── backpropagation.py      # StandardBackprop, SolverBackprop
├── runner/
│   ├── player_config.py            # PlayerConfig dataclass
│   ├── player_factory.py           # build_mcts() — fabryka instancji MCTS
│   ├── match_config.py             # MatchConfig + wczytywanie YAML
│   ├── game_runner.py              # Headless pętla gry, GameResult
│   └── result_writer.py            # Zapis wyników do CSV
└── ui/
    ├── main_window.py              # Okno główne PyQt6
    ├── setup_screen.py             # Ekran konfiguracji
    ├── game_screen.py              # Ekran rozgrywki
    └── components.py               # Wspólne widżety i UIConfig
experiments/
└── example.yaml                    # Przykładowy config eksperymentu
```
