"""A small Tkinter GUI to schedule, watch, and cancel a Windows shutdown."""

from __future__ import annotations

import subprocess
import sys
import time
import tkinter as tk
from tkinter import messagebox, ttk

MIN_DELAY_SECONDS = 60
MAX_DELAY_SECONDS = 315_360_000  # `shutdown /t` upper limit (~10 years)
ALREADY_SCHEDULED_EXIT_CODE = 1190  # "a system shutdown has already been scheduled"
_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
_SHUTDOWN_MISSING = "Could not find the Windows 'shutdown' command."


def parse_delay(hours: str, minutes: str) -> int:
    """Convert the hours/minutes field values to a delay in seconds.

    Args:
        hours: Contents of the hours field; blank counts as zero.
        minutes: Contents of the minutes field; blank counts as zero.

    Returns:
        The delay in seconds.

    Raises:
        ValueError: if a value is non-numeric or negative, or the total is
            below one minute or above the Windows ``shutdown`` limit.
    """
    try:
        hrs = int(hours) if hours.strip() else 0
        mins = int(minutes) if minutes.strip() else 0
    except ValueError:
        raise ValueError("Hours and minutes must be whole numbers.") from None

    if hrs < 0 or mins < 0:
        raise ValueError("Time values must not be negative.")

    total = (hrs * 60 + mins) * 60
    if total < MIN_DELAY_SECONDS:
        raise ValueError("Please enter at least one minute.")
    if total > MAX_DELAY_SECONDS:
        raise ValueError("That delay is too large for Windows to schedule.")
    return total


def shutdown_args(delay: int) -> list[str]:
    """Return the ``shutdown`` argv that schedules a shutdown after ``delay`` s."""
    return ["shutdown", "/s", "/t", str(delay)]


def abort_args() -> list[str]:
    """Return the ``shutdown`` argv that aborts a pending shutdown."""
    return ["shutdown", "/a"]


def run_command(args: list[str]) -> subprocess.CompletedProcess[str]:
    """Run a shutdown command without popping up a console window.

    Raises:
        FileNotFoundError: if the ``shutdown`` executable cannot be found.
    """
    return subprocess.run(
        args,
        capture_output=True,
        text=True,
        check=False,
        creationflags=_NO_WINDOW,
    )


def format_hms(seconds: int) -> str:
    """Format a non-negative second count as ``M:SS`` or ``H:MM:SS``."""
    seconds = max(seconds, 0)
    hours, rem = divmod(seconds, 3600)
    minutes, secs = divmod(rem, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


class Application(ttk.Frame):
    """Two views in one window: time entry, then a live countdown."""

    def __init__(self, master: tk.Tk) -> None:
        super().__init__(master, padding=12)
        self.master = master
        self.master.title("Shutdown Timer")
        self.grid()

        self._deadline: float | None = None
        self._tick_job: str | None = None

        self._build_input_view()
        self._build_countdown_view()
        self._show_input()
        self.master.bind("<Return>", lambda _event: self._on_start())

    # -- view construction ------------------------------------------------

    def _build_input_view(self) -> None:
        self.input_frame = ttk.Frame(self)
        self.hours_var = tk.StringVar(value="0")
        self.minutes_var = tk.StringVar(value="30")

        ttk.Label(self.input_frame, text="Shut down after").grid(
            row=0, column=0, columnspan=4, pady=(0, 8)
        )
        ttk.Spinbox(
            self.input_frame, from_=0, to=23, width=4, textvariable=self.hours_var
        ).grid(row=1, column=0)
        ttk.Label(self.input_frame, text="h").grid(row=1, column=1, padx=(2, 10))
        ttk.Spinbox(
            self.input_frame, from_=0, to=59, width=4, textvariable=self.minutes_var
        ).grid(row=1, column=2)
        ttk.Label(self.input_frame, text="m").grid(row=1, column=3, padx=(2, 0))

        ttk.Button(self.input_frame, text="Start", command=self._on_start).grid(
            row=2, column=0, columnspan=4, pady=(12, 0), sticky="ew"
        )
        ttk.Button(
            self.input_frame,
            text="Abort any scheduled shutdown",
            command=self._on_abort,
        ).grid(row=3, column=0, columnspan=4, pady=(6, 0), sticky="ew")

    def _build_countdown_view(self) -> None:
        self.countdown_frame = ttk.Frame(self)
        self.countdown_title = ttk.Label(self.countdown_frame, text="")
        self.countdown_title.grid(row=0, column=0, pady=(0, 4))
        self.countdown_value = ttk.Label(
            self.countdown_frame, font=("TkDefaultFont", 24, "bold")
        )
        self.countdown_value.grid(row=1, column=0)
        ttk.Button(self.countdown_frame, text="Abort", command=self._on_abort).grid(
            row=2, column=0, pady=(12, 0), sticky="ew"
        )

    def _show_input(self) -> None:
        self.countdown_frame.grid_remove()
        self.input_frame.grid(row=0, column=0)

    def _show_countdown(self) -> None:
        self.input_frame.grid_remove()
        self.countdown_frame.grid(row=0, column=0)

    # -- actions --------------------------------------------------------

    def _run(self, args: list[str]) -> subprocess.CompletedProcess[str] | None:
        """Run ``args``; report a missing ``shutdown`` binary and return None."""
        try:
            return run_command(args)
        except FileNotFoundError:
            messagebox.showerror("Unavailable", _SHUTDOWN_MISSING)
            return None

    def _on_start(self) -> None:
        if self._deadline is not None:  # already counting down
            return
        try:
            delay = parse_delay(self.hours_var.get(), self.minutes_var.get())
        except ValueError as exc:
            messagebox.showerror("Invalid time", str(exc))
            return
        if not self._schedule(delay):
            return

        self._deadline = time.monotonic() + delay
        eta = time.strftime("%H:%M:%S", time.localtime(time.time() + delay))
        self.countdown_title.config(text=f"Shutting down at {eta}")
        self._show_countdown()
        self._tick()

    def _schedule(self, delay: int) -> bool:
        """Schedule the shutdown, replacing an existing one on request."""
        result = self._run(shutdown_args(delay))
        if result is None:
            return False
        if result.returncode == 0:
            return True

        if result.returncode == ALREADY_SCHEDULED_EXIT_CODE and messagebox.askyesno(
            "Already scheduled",
            "A shutdown is already scheduled. Replace it with this one?",
        ):
            if self._run(abort_args()) is None:
                return False
            result = self._run(shutdown_args(delay))
            if result is None:
                return False
            if result.returncode == 0:
                return True

        messagebox.showerror(
            "Failed", result.stderr.strip() or "Could not schedule shutdown."
        )
        return False

    def _on_abort(self) -> None:
        result = self._run(abort_args())
        if result is None:
            return

        self._stop_tick()
        self._deadline = None
        self._show_input()
        if result.returncode == 0:
            messagebox.showinfo("Aborted", "Scheduled shutdown cancelled.")
        else:
            messagebox.showwarning("Nothing to abort", "No shutdown was scheduled.")

    # -- countdown loop ------------------------------------------------

    def _tick(self) -> None:
        if self._deadline is None:
            return
        remaining = round(self._deadline - time.monotonic())
        if remaining > 0:
            self.countdown_value.config(text=format_hms(remaining))
            self._tick_job = self.after(250, self._tick)
        else:
            self.countdown_value.config(text="Shutting down…")
            self._tick_job = None

    def _stop_tick(self) -> None:
        if self._tick_job is not None:
            self.after_cancel(self._tick_job)
            self._tick_job = None


def main() -> int:
    """Program entry point."""
    root = tk.Tk()
    root.resizable(width=False, height=False)
    Application(master=root).mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
