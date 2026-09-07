"""A small Tkinter GUI to schedule or cancel a Windows shutdown."""

from __future__ import annotations

import subprocess
import sys
import tkinter as tk
from tkinter import messagebox


class Application(tk.Frame):  # pylint: disable=too-many-ancestors
    """Main application frame: two entry boxes plus start/cancel buttons."""

    def __init__(self, master: tk.Tk) -> None:
        super().__init__(master)
        self.master = master
        self.master.title("Shutdown Timer")
        self.pack(padx=10, pady=10)
        self._build_widgets()

    def _build_widgets(self) -> None:
        """Create and lay out the widgets."""
        tk.Label(self, text="Enter time").grid(row=0, column=0, columnspan=2)

        tk.Label(self, text="Hours").grid(row=1, column=0)
        tk.Label(self, text="Minutes").grid(row=1, column=1)

        self.hours = tk.Entry(self, width=6)
        self.hours.grid(row=2, column=0, padx=4)

        self.minutes = tk.Entry(self, width=6)
        self.minutes.grid(row=2, column=1, padx=4)

        tk.Button(self, text="Start timer", command=self.begin_shutdown).grid(
            row=3, column=0, pady=(8, 0)
        )
        tk.Button(self, text="Cancel shutdown", command=self.cancel_shutdown).grid(
            row=3, column=1, pady=(8, 0)
        )

    def interpret_time(self) -> int:
        """Return the delay in seconds from the entry fields.

        Raises:
            ValueError: if the input is non-numeric, negative, or under one minute.
        """
        hours = int(self.hours.get() or 0)
        minutes = int(self.minutes.get() or 0)
        if hours < 0 or minutes < 0:
            raise ValueError("Time values must not be negative.")

        total_seconds = (hours * 60 + minutes) * 60
        if total_seconds < 60:
            raise ValueError("Please enter at least one minute.")
        return total_seconds

    def begin_shutdown(self) -> None:
        """Validate input, confirm, and schedule the shutdown."""
        try:
            delay = self.interpret_time()
        except ValueError as exc:
            messagebox.showerror("Invalid time", str(exc))
            return

        if not messagebox.askyesno("Confirm", f"Schedule shutdown in {delay} seconds?"):
            return

        result = subprocess.run(
            ["shutdown", "/s", "/t", str(delay)],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            messagebox.showinfo("Scheduled", f"Shutting down in {delay} seconds.")
            self.master.destroy()
        else:
            messagebox.showerror(
                "Failed",
                result.stderr.strip() or "Could not schedule shutdown.",
            )

    def cancel_shutdown(self) -> None:
        """Abort any pending shutdown."""
        result = subprocess.run(
            ["shutdown", "/a"], capture_output=True, text=True, check=False
        )
        if result.returncode == 0:
            messagebox.showinfo("Canceled", "Shutdown canceled.")
        else:
            messagebox.showwarning(
                "Nothing to cancel", "No shutdown timer is currently active."
            )
        self.master.destroy()


def main() -> int:
    """Program entry point."""
    root = tk.Tk()
    Application(master=root).mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
