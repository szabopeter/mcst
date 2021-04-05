#!/usr/bin/python3
import sys
import tkinter as tk

from backendinterface import McstBackendInterface, McstBackend, McstBackendTest

BUTTON_WIDTH = 16


class McstFrontend(tk.Frame):
    def __init__(self, master, backend: McstBackendInterface):
        super().__init__(master)
        self.master = master
        self.backend = backend
        self.pack()

        self.directories_prop = tk.StringVar(master=master, value=())
        self.directories = []
        self.config_loaded = False
        self.selected_dir = None
        self.new_name = None
        self.default_version = "1.16.1"
        self.versions = [self.default_version, "1.16.4", "1.16.5", "21w11a"]
        self.selected_version = tk.StringVar(master=master)
        self.port = "25565"

        self.directory_selection_frame = None
        self.refresh_directories_button = None
        self.directories_list = None
        self.new_name_textbox = None
        self.new_name_button = None
        self.quit_button = None

        self.directory_operations_frame = None
        self.config_frame = None
        self.config_operations_frame = None
        self.config_load_button = None
        self.config_save_button = None
        self.config_editor_version = None
        self.config_editor_textbox = None
        self.port_textbox = None
        self.versions_list = None
        self.directory_start_button = None

        self.create_widgets()
        self.arrange_widgets()
        self.refresh_directories()
        self.new_name_modified(None)

    def create_widgets(self):
        self.directory_selection_frame = tk.Frame(self)

        self.refresh_directories_button = tk.Button(
            master=self.directory_selection_frame,
            text="Refresh",
            width=BUTTON_WIDTH,
            command=self.refresh_directories
        )

        self.new_name_textbox = tk.Text(
            master=self.directory_selection_frame,
            height=1,
            width=22
        )
        self.new_name_textbox.bind("<<Modified>>", self.new_name_modified)

        self.new_name_button = tk.Button(
            master=self.directory_selection_frame,
            text="Create",
            width=BUTTON_WIDTH,
            command=self.create_server_directory
        )

        self.quit_button = tk.Button(
            master=self.directory_selection_frame,
            text="Quit",
            width=BUTTON_WIDTH,
            command=self.master.destroy
        )

        self.directories_list = tk.Listbox(
            master=self.directory_selection_frame,
            selectmode=tk.SINGLE,
            listvariable=self.directories_prop,
        )
        self.directories_list.bind('<<ListboxSelect>>', self.dir_selected)

        self.directory_operations_frame = tk.Frame(self)
        self.config_frame = tk.Frame(self.directory_operations_frame)
        self.config_operations_frame = tk.Frame(self.config_frame)

        self.config_load_button = tk.Button(
            master=self.config_operations_frame,
            text="Load",
            width=BUTTON_WIDTH,
            state=tk.DISABLED,
            command=self.load_config
        )

        self.config_save_button = tk.Button(
            master=self.config_operations_frame,
            text="Save",
            width=BUTTON_WIDTH,
            state=tk.DISABLED,
            command=self.save_config
        )

        self.config_editor_textbox = tk.Text(
            master=self.config_frame,
            width=80,
            height=40,
            state=tk.DISABLED
        )

        self.config_editor_version = tk.Text(
            master=self.config_frame,
            width=20,
            height=1,
            state=tk.DISABLED
        )

        self.port_textbox = tk.Text(
            master=self.directory_operations_frame,
            height=1,
            width=20
        )
        self.port_textbox.insert("1.0", self.port)
        self.port_textbox.bind("<<Modified>>", self.port_modified)

        self.selected_version.set(self.default_version)
        other_values = [x for x in self.versions if x != self.default_version]
        self.versions_list = tk.OptionMenu(
            self.directory_operations_frame,
            self.selected_version,
            self.selected_version.get(),
            *other_values
        )

        self.directory_start_button = tk.Button(
            master=self.directory_operations_frame,
            text="START!",
            width=BUTTON_WIDTH*2,
            state=tk.DISABLED,
            command=self.start
        )

    def arrange_widgets(self):
        self.directory_selection_frame.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        self.refresh_directories_button.pack()
        self.directories_list.pack(fill=tk.Y, expand=True)
        self.new_name_textbox.pack()
        self.new_name_button.pack()
        self.quit_button.pack()
        self.directory_operations_frame.pack()
        self.config_frame.pack()
        self.config_operations_frame.pack()
        self.config_load_button.pack(side=tk.LEFT)
        self.config_save_button.pack()
        self.config_editor_textbox.pack()
        self.config_editor_version.pack()
        self.port_textbox.pack()
        self.versions_list.pack()
        self.directory_start_button.pack()

    def refresh_directories(self):
        self.directories = self.backend.list()
        self.directories_prop.set(self.directories)
        self.directories_list.selection_clear(0, tk.END)
        self.set_directory_operations_state(tk.DISABLED)
        self.dir_selected(None)

    def set_directory_operations_state(self, state):
        for button in (
            self.config_load_button,
            self.config_save_button,
            self.config_editor_textbox,
            self.directory_start_button
        ):
            button.config(state=state)

    # noinspection PyUnusedLocal
    def dir_selected(self, event):
        selection = self.directories_list.curselection()
        if len(selection) == 0:
            self.selected_dir = None
            self.set_directory_operations_state(tk.DISABLED)
            self.new_name_button.config(text="Create")
            self.clear_config()
            self.update_dirversion("")
            return
        index = selection[0]
        self.selected_dir = self.directories[index]
        print(f"Selected {self.selected_dir}")
        self.set_directory_operations_state(tk.NORMAL)
        self.new_name_button.config(text="Clone")
        self.clear_config()
        self.update_dirversion(self.backend.load_info(self.selected_dir).last_server_version)

    def port_modified(self, event):
        new_port = self.port_textbox.get("1.0", tk.END).strip()
        self.port = new_port
        self.port_textbox.edit_modified(False)

    def new_name_modified(self, event):
        new_name = self.new_name_textbox.get("1.0", tk.END).strip()
        if new_name == self.new_name:
            return
        self.new_name = new_name
        button_state = tk.NORMAL if self.is_new_name_valid() else tk.DISABLED
        self.new_name_button.config(state=button_state)
        self.new_name_textbox.edit_modified(False)

    def is_new_name_valid(self):
        return self.new_name and self.new_name not in self.directories

    def create_server_directory(self):
        if self.is_new_name_valid() is False:
            print("Invalid name specified!")
            return
        self.winfo_toplevel().iconify()
        if self.selected_dir is None:
            self.backend.create(self.new_name)
        else:
            self.backend.clone(self.new_name, self.selected_dir)
        self.winfo_toplevel().deiconify()
        self.refresh_directories()
        self.new_name_textbox.delete("1.0", tk.END)

    def clear_config(self):
        self.config_editor_textbox.delete("1.0", tk.END)
        self.config_loaded = False

    def update_dirversion(self, version_text: str):
        self.config_editor_version.config(state=tk.NORMAL)
        self.config_editor_version.delete("1.0", tk.END)
        self.config_editor_version.insert("1.0", version_text)
        self.config_editor_version.config(state=tk.DISABLED)
        if version_text in self.versions:
            self.choose_version(version_text)
        else:
            self.choose_version(self.default_version)

    def load_config(self):
        if self.selected_dir is None:
            print("No server directory selected")
            return

        editor_text = self.backend.settings_dump(self.selected_dir)
        self.config_editor_textbox.delete("1.0", tk.END)
        self.config_editor_textbox.insert("1.0", editor_text)
        self.update_dirversion(self.backend.load_info(self.selected_dir).last_server_version)
        self.config_loaded = True

    def save_config(self):
        if self.selected_dir is None:
            print("No server directory selected")
            return
        if self.config_loaded is False:
            print("Config has not yet been loaded!")
            return

        editor_text = self.config_editor_textbox.get("1.0", tk.END)
        self.backend.settings_replace(self.selected_dir, editor_text)

    def start(self):
        if self.selected_dir is None:
            print("No server directory selected")
            return
        version = self.selected_version.get()
        port = self.port
        if self.is_port_valid(port) is False:
            print("Invalid port number")
            return
        self.winfo_toplevel().iconify()
        print(f"Starting {self.selected_dir} using v{version} on port {port}, this will be your console:")
        self.backend.start(self.selected_dir, port, version)
        print(f"Server stopped, you can continue on the GUI")
        self.winfo_toplevel().deiconify()

    def choose_version(self, version):
        self.selected_version.set(version)

    def is_port_valid(self, port: str) -> bool:
        try:
            port = int(port)
        except:
            return False
        return 1000 < port < 65536


def main():
    root = tk.Tk()
    root.title("MC Server Tool Frontend")
    root.eval(f'tk::PlaceWindow . center')
    backend = McstBackendTest() if "--devmode" in sys.argv else McstBackend()
    app = McstFrontend(master=root, backend=backend)
    app.mainloop()


if __name__ == "__main__":
    main()
