import tkinter as tk

# Function that sets notification frames/labels
class NotificationFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bd=1, relief="ridge", pady=5, bg="white")
        self.notification_label = tk.Label(self, fg="green", bg="white")
        self.notification_label.pack(fill="x")

    def show_notification(self, message):
        self.notification_label.config(text=message)
        self.pack(side="top", fill="x", padx=5, pady=5)
        self.notification_label.after(3000, self.hide_notification)

    def hide_notification(self):
        self.pack_forget()
        self.notification_label.config(text="")

    def protocol(self, configuration, event=None):
        # Implement protocol functionality here
        # Example: Change border color, adjust size, etc.
        pass

# Function that sets notification frame/Shows notification
class NotificationManager:
    def __init__(self, master):
        self.master = master
        self.notification_frame = NotificationFrame(self.master)

    def show_notification(self, message):
        self.notification_frame.show_notification(message)
