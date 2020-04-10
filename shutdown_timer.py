"""Windows based timer to turn off computer"""

import os
import tkinter as tk


class Application(tk.Frame):  # pylint: disable=too-many-ancestors
    """."""

    def __init__(self, master=None):
        """."""
        super().__init__(master=master)
        self.master = master
        self.master.title("Shutdown Timer")
        # self.master.minsize(width=200, height=200)
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        """initialize objects in the frame"""

        self.label1 = tk.Label(self, text="enter time")
        self.label1.pack(side="bottom")

        self.start_timer = tk.Button(
            self, text="start timer", command=self.begin_shutdown)
        # self.start_timer.event_add()
        self.start_timer.pack(side="right")

        self.quit = tk.Button(self, text="cancel",
                              command=self.cancel_shutdown)
        self.quit.pack(side="right")

        # TODO: input grayed out temporary input to show user hh:mm in the boxes
        self.hours = tk.Entry(self)
        self.hours.pack(side="left")

        self.minutes = tk.Entry(self)
        self.minutes.pack(side="right")

    def interpret_time(self):
        """ Get values in text boxes and return time in seconds """
        try:
            hrs = (self.hours.get())  # get input
            minutes = (self.minutes.get())

            if hrs == '':
                hrs = 0
            if minutes == '':
                minutes = 0

            minutes = int(minutes)  # cast as str
            minutes += int(hrs)*60  # convert hrs to mins
            seconds = int(minutes)*60  # convert mins to seconds

        except ValueError as input_error:
            print(input_error)

        return seconds

    def begin_shutdown(self):
        """ Start windows shutdown timer """
        shutdown_time = self.interpret_time()
        assert shutdown_time >= 60, "At least one minute pls!"

        status = os.system(f'shutdown /s /t {shutdown_time}')

        if status == 0:  # command successful
            print(f"shutting down in {shutdown_time} seconds")
        else:
            print(f'invalid time')
        self.master.destroy()

    def cancel_shutdown(self):
        """ Cancel windows shutdown timer """
        status = os.system(f'shutdown -a')

        if status == 0:  # command successful
            print("shutdown canceled")
        else:
            print("no shutdown timer started!")
        self.master.destroy()

        return status


def main():
    """."""
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()
    return 0


if __name__ == "__main__":
    main()
