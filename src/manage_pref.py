from customtkinter import *
import os, configparser

class ManagePreferences:
    def __init__(self, master, right_frame):
        # Initial manage_pref configurations
        self.master = master
        self.right_frame = right_frame

        self.dark_mode = None
        self.time_format = None
        self.load_preferences()

    # Function to configure preferences frame
    def preferences(self):
        pref_frame = CTkFrame(self.right_frame, width=600, height=700)
        pref_frame.place(relx=0.61, rely=0, anchor="n")

        def close_frame():
            pref_frame.destroy()

        x_button = CTkButton(pref_frame, command=close_frame, text="❌", fg_color="white", border_color="black", text_color="black", hover_color="red", border_width=2, width=50, height=20, cursor="hand2")
        x_button.place(relx=0.8, rely=0.03, anchor="ne")

        title_label = CTkLabel(pref_frame, text="Preferences", font=("Helvetica", 30, "bold", "underline"))
        title_label.place(relx=0.2, rely=0.08, anchor="center")

        # Function to configure dark mode toggle
        def color_callback():
            self.dark_mode = color_var.get()
            config = configparser.ConfigParser()
            if os.path.exists('preferences.ini'):
                config.read('preferences.ini')
            else:
                self.save_preferences()
            
            if 'Preferences' not in config:
                config['Preferences'] = {}

            config.set('Preferences', 'dark_mode', self.dark_mode)

            with open('preferences.ini', 'w') as configfile:
                config.write(configfile)

            if self.dark_mode == 'on':
                set_appearance_mode("dark")
            else:
                set_appearance_mode("light")

        color_var = StringVar(value="off")
        color_var.set(value="on" if self.dark_mode == "on" else "off")
        color_switch = CTkSwitch(pref_frame, text="Dark Mode", command=color_callback, variable=color_var, onvalue="on", offvalue="off", fg_color="red", font=("Helvetica", 26, "bold"))
        color_switch.place(relx=0.05, rely=0.15, anchor="w")

        color_desc = CTkLabel(pref_frame, text="Switch to Dark Mode to make the interface easier on your eyes.", font=("Helvetica", 16))
        color_desc.place(relx=0.05, rely=0.2, anchor="w")

        # Function to configure time format toggle
        def time_callback():
            self.time_format = color_var.get()
            config = configparser.ConfigParser()
            if os.path.exists('preferences.ini'):
                config.read('preferences.ini')
            else:
                self.save_preferences()
            
            if 'Preferences' not in config:
                config['Preferences'] = {}

            config.set('Preferences', 'time_format', self.time_format)

            with open('preferences.ini', 'w') as configfile:
                config.write(configfile)

            if self.time_format == 'on':
                pass
            else:
                pass

        time_var = StringVar(value="off")
        time_var.set(value="on" if self.time_format == "on" else "off")
        time_var = CTkSwitch(pref_frame, text="Military Time", command=time_callback, variable=time_var, onvalue="on", offvalue="off", fg_color="red", font=("Helvetica", 26, "bold"))
        time_var.place(relx=0.05, rely=0.25, anchor="w")

        time_desc = CTkLabel(pref_frame, text="Switch the time format between Military and Standard Time.", font=("Helvetica", 16))
        time_desc.place(relx=0.05, rely=0.3, anchor="w")

    # Function to save Preferences section
    def save_preferences(self):
        config = configparser.ConfigParser()

        if os.path.exists('preferences.ini'):
            config.read('preferences.ini')
        
        if 'Preferences' not in config:
            config['Preferences'] = {}
            
        dark_mode_status = "on" if self.dark_mode == "on" else "off"
        time_format_status = "on" if self.time_format == "on" else "off"
        
        config['Preferences']['dark_mode'] = dark_mode_status
        config['Preferences']['time_format'] = time_format_status
        
        with open('preferences.ini', 'w') as configfile:
            config.write(configfile)

    # Function to load Preferences section 
    def load_preferences(self):
        config = configparser.ConfigParser()
        if os.path.exists('preferences.ini'):
            config.read('preferences.ini')
        self.dark_mode = config.get('Preferences', 'dark_mode', fallback='off')
        self.time_format = config.get('Preferences', 'time_format', fallback='off')
