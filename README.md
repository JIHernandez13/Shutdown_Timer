# Shutdown Timer

A tiny Windows GUI (Tkinter) that schedules — and can cancel — a system
shutdown after a delay you choose in hours and minutes. It's a thin wrapper
around the built-in `shutdown` command, with a live countdown so you can see
how long is left and abort without opening a terminal.

> **Platform:** Windows only. It calls `shutdown /s /t` and `shutdown /a`,
> which are Windows-specific.

## Quickstart

### Requirements

- Windows
- Python 3.14 or newer

### Run it

With [uv](https://docs.astral.sh/uv/) (no manual virtualenv needed):

```bash
uv run python shutdown_timer.py
```

Or with a plain Python install:

```bash
python shutdown_timer.py
```

### Use it

1. Set the delay with the **h** and **m** spinboxes (either may be left at 0;
   the total must be at least one minute).
2. Click **Start** (or press <kbd>Enter</kbd>). The window switches to a
   countdown showing the target time and the time remaining.
3. Click **Abort** to cancel the pending shutdown. Abort is also available
   from the start screen if a shutdown was scheduled some other way.

If Windows reports that a shutdown is already scheduled, the app offers to
replace it with your new one.

## Notable changes

- **Live countdown and a working abort.** The window used to close itself the
  moment you started a timer, which left no way to cancel from the app. It now
  stays open, shows the target time and a running `H:MM:SS` counter, and the
  **Abort** button actually cancels the shutdown.
- **Safer command handling.** The shutdown command runs without flashing a
  console window; an already-scheduled shutdown (exit code 1190) is detected
  and can be replaced; delays beyond the Windows limit (~10 years) are
  rejected up front; a missing `shutdown` executable is reported clearly.
- **Robust input parsing.** Blank, non-numeric, negative, and out-of-range
  values are caught with a clear message instead of crashing or silently
  misbehaving.
- **`ttk` widgets** and bounded spinboxes for the hour/minute fields.
- **Tooling:** [uv](https://docs.astral.sh/uv/) project setup, Ruff for
  linting and formatting (enforced by a pre-commit hook), a pytest suite for
  the time/argument logic, and GitHub Actions that run Ruff and the tests on
  every pull request.

## Development

```bash
# one-time setup
uv sync
uv run pre-commit install

# lint / format
uv run ruff check .
uv run ruff format .

# tests
uv run pytest
```

The pre-commit hook runs Ruff on every commit. CI (`.github/workflows/`) runs
Ruff and pytest on pull requests.
