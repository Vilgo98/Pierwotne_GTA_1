# Retro City Driver

Dwuwymiarowa gra akcji z widokiem z góry, inspirowana **GTA 1**, napisana
w Pythonie z użyciem **pygame**. Gracz jeździ po mieście kafelkowym, wykonuje
zlecenia, ulepsza samochód w garażu i ucieka przed policją, której poziom
pościgu („wanted level") rośnie wraz z rozgrywką.

Projekt zaliczeniowy — silnik gry napisany od zera (fizyka, AI, kolizje,
kamera, minimapa), bez gotowego frameworka gier poza `pygame`.

## Rozgrywka

### Sterowanie

| Klawisze | Akcja |
|----------|-------|
| `↑` `↓` `←` `→` lub `W` `S` `A` `D` | Jazda samochodem |
| `Spacja` (przytrzymanie) | Drift — mniejsze tarcie, ostrzejszy skręt |
| `M` | Pełna mapa miasta |
| `Esc` | Pauza |
| Mysz | Menu, garaż, ekrany końca gry |

### Pętla gry

- **MENU → CREATION → GAME** — na starcie podajesz imię postaci.
- Jeździsz po mieście i szukasz punktów misji (widoczne na mapie pod `M`).
- Za ukończone misje dostajesz pieniądze, za które w **garażu** kupujesz
  ulepszenia.
- Im więcej ukończonych misji, tym wyższy bazowy poziom pościgu.

### Typy misji

| Misja | Cel | Nagroda |
|-------|-----|---------|
| **Żółta** (dostawa) | Dojedź do wskazanego punktu (podpowiedź kierunku kompasowego) | $1000 |
| **Czerwona** (survival) | Przeżyj 2 minuty przy 6 gwiazdkach pościgu | $5000 |
| **Fioletowa** (kurier) | Zbierz 3 paczki z mapy; każda paczka podnosi poziom pościgu | $3000 |

### Garaż

| Ulepszenie | Koszt | Efekt |
|------------|-------|-------|
| Naprawa | $500 | Przywraca 100 HP |
| Silnik | $2500 | +1 do prędkości maksymalnej (kumuluje się) |
| Pancerz | $3000 | Obrażenia zmniejszone o połowę (jednorazowo) |

### Poziom pościgu i koniec gry

- **Wanted level 0–6.** Gdy policja widzi gracza przez dłuższy czas — pościg
  eskaluje (co ~60 s +1 gwiazdka). Poza zasięgiem wzroku po ~30 s pościg gaśnie.
- Warunki końca gry:
  - **WASTED** — HP spadło do zera (kolizje ze ścianami, drzewami, radiowozami),
  - **DROWNED** — wjazd do wody poza mostem,
  - **BUSTED** — zatrzymanie się blisko radiowozu przy aktywnym pościgu na ~3 s.

## Architektura

Silnik podzielony na moduły według odpowiedzialności:

| Moduł | Zawartość |
|-------|-----------|
| `main.py` | Pętla gry, maszyna stanów (`MENU` / `CREATION` / `GARAGE` / `GAME`), obsługa zdarzeń, renderowanie świata i HUD, kamera podążająca za graczem |
| `config.py` | `GameConfig` — wszystkie stałe (fizyka, ekonomia, misje, kolory) oraz `MAP_LAYOUT` — mapa miasta jako siatka znaków |
| `game_state.py` | Budowa świata z `MAP_LAYOUT` (parser kafelków), inicjalny słownik stanu gry, generowanie powierzchni minimapy |
| `physics.py` | Model jazdy (przyspieszanie, hamowanie, tarcie, drift, ograniczenie prędkości), kolizje na osiach X/Y ze ścianami, wodą, drzewami, strefą garażu, kolizje auto–auto |
| `ai.py` | Spawn policji w pierścieniu wokół gracza, AI pościgu z „czujnikami" wykrywającymi przeszkody, wychodzenie z zakleszczenia, kolizje radiowóz–radiowóz |
| `missions.py` | Logika 3 typów misji, eskalacja i wygaszanie poziomu pościgu, nagrody |
| `ui.py` | Ekrany menu, tworzenia postaci, garażu, pauzy; minimapa i pełna mapa; przyciski |
| `assets.py` | Wczytywanie i skalowanie grafik z `photos/` |
| `utils.py` | Losowa pozycja na drodze, kierunek kompasowy do celu |

Mapa jest opisana w `config.py` jako lista łańcuchów znaków — każdy znak to inny
kafelek (drogi i skrzyżowania, budynki 1×1 / 1×2 / 2×2, mosty, drzewa, woda,
teren, garaż, punkt startu gracza).

## Uruchomienie

Wymagany Python 3.10+ oraz `pygame`.

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

python main.py
```

> Uwaga: gra otwiera okno `pygame` — wymaga środowiska graficznego
> (nie działa w trybie headless).

## Struktura projektu

```
.
├── main.py            # pętla gry i maszyna stanów
├── config.py          # stałe + mapa miasta (MAP_LAYOUT)
├── game_state.py      # budowa świata i stan gry
├── physics.py         # jazda i kolizje
├── ai.py              # AI policji
├── missions.py        # misje i poziom pościgu
├── ui.py              # ekrany, mapa, minimapa
├── assets.py          # ładowanie grafik
├── utils.py           # funkcje pomocnicze
├── photos/            # grafiki (auta, budynki, drogi, tło, postać)
└── requirements.txt
```

## Technologie

- **Python**
- **pygame** — okno, pętla zdarzeń, rysowanie, obsługa klawiatury/myszy, grafiki
- Model gry oparty na słownikach stanu i funkcjach operujących na tym stanie

## Możliwy rozwój

- Dźwięk (silnik, syreny, kolizje)
- Zapis / wczytywanie postępu i pieniędzy
- Przechodnie i ruch uliczny NPC
- Przeniesienie stanu gry ze słowników na klasy / dataclassy

## Autor

Mikołaj Mazurek — WCY23IJ2S1, Wojskowa Akademia Techniczna
