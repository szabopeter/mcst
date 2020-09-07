#!/usr/bin/python3
import os
import sys
import tkinter as tk
from abc import ABC, abstractmethod
from typing import List


class McstFrontend(tk.Frame):
    def __init__(self, master, backend: "McstBackendInterface"):
        super().__init__(master)
        self.master = master
        self.backend = backend
        self.pack()

        self.directories_prop = tk.StringVar(master=master, value=())
        self.directories = []
        self.config_loaded = False
        self.selected_dir = None

        self.directory_selection_frame = None
        self.refresh_directories_button = None
        self.directories_list = None
        self.quit_btn = None

        self.directory_operations_frame = None
        self.config_frame = None
        self.config_operations_frame = None
        self.config_load_button = None
        self.config_save_button = None
        self.config_editor_textbox = None
        self.directory_start_button = None

        self.create_widgets()
        self.arrange_widgets()
        self.refresh_directories()

    def create_widgets(self):
        self.directory_selection_frame = tk.Frame(self)

        self.refresh_directories_button = tk.Button(
            master=self.directory_selection_frame,
            text="Refresh",
            command=self.refresh_directories
        )

        self.quit_btn = tk.Button(
            master=self.directory_selection_frame,
            text="Quit",
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
            state=tk.DISABLED,
            command=self.load_config
        )

        self.config_save_button = tk.Button(
            master=self.config_operations_frame,
            text="Save",
            state=tk.DISABLED,
            command=self.save_config
        )

        self.config_editor_textbox = tk.Text(
            master=self.config_frame,
            width=80,
            height=40,
            state=tk.DISABLED
        )

        self.directory_start_button = tk.Button(
            master=self.directory_operations_frame,
            text="START!",
            state=tk.DISABLED,
            command=self.start
        )

    def arrange_widgets(self):
        self.directory_selection_frame.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        self.refresh_directories_button.pack()
        self.directories_list.pack(fill=tk.Y, expand=True)
        self.quit_btn.pack()
        self.directory_operations_frame.pack()
        self.config_frame.pack()
        self.config_operations_frame.pack()
        self.config_load_button.pack(side=tk.LEFT)
        self.config_save_button.pack()
        self.config_editor_textbox.pack()
        self.directory_start_button.pack()

    def refresh_directories(self):
        self.directories = self.backend.list()
        self.directories_prop.set(self.directories)
        self.directories_list.selection_clear(0, tk.END)
        self.set_directory_operations_state(tk.DISABLED)

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
            return
        index = selection[0]
        self.selected_dir = self.directories[index]
        print(f"Selected {self.selected_dir}")
        self.set_directory_operations_state(tk.NORMAL)
        self.clear_config()

    def clear_config(self):
        self.config_editor_textbox.delete("1.0", tk.END)
        self.config_loaded = False

    def load_config(self):
        if self.selected_dir is None:
            print("No server directory selected")
            return

        editor_text = self.backend.settings_dump(self.selected_dir)
        self.config_editor_textbox.delete("1.0", tk.END)
        self.config_editor_textbox.insert("1.0", editor_text)
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
        self.winfo_toplevel().iconify()
        print(f"Starting {self.selected_dir}, this will be your console:")
        self.backend.start(self.selected_dir)
        self.winfo_toplevel().deiconify()


class McstBackendInterface(ABC):
    @abstractmethod
    def list(self) -> List[str]:
        pass

    @abstractmethod
    def settings_dump(self, name: str) -> str:
        pass

    @abstractmethod
    def settings_replace(self, name: str, new_content: str):
        pass

    @abstractmethod
    def start(self, name: str):
        pass


class McstBackend(McstBackendInterface):
    def __init__(self):
        self.command_template = "~/bin/mcst.sh"

    def list(self) -> List[str]:
        output = os.popen(f"{self.command_template} list").read()
        return [name for name in output.split("\n") if name]

    def settings_dump(self, name: str) -> str:
        output = os.popen(f'{self.command_template} settings-show "{name}"').read()
        return output

    def settings_replace(self, name: str, new_content: str):
        pipe = os.popen(f'{self.command_template} settings-replace "{name}"', mode="w")
        pipe.write(new_content)

    def start(self, name: str):
        os.system(f'{self.command_template} start "{name}"')


class McstBackendTest(McstBackendInterface):
    def __init__(self):
        self.directories = ["A"]

    def list(self) -> List[str]:
        self.directories.append(self.directories[-1] * 2)
        return self.directories

    def settings_dump(self, name: str) -> str:
        return f"Loremipsum...\nPlaceholder for {name} settings\n"*40

    def settings_replace(self, name: str, new_content: str):
        print(f"Replacing settings for {name}")
        print("New content will be:")
        print(new_content)

    def start(self, name: str):
        os.system("bc")


def main():
    root = tk.Tk()
    root.title("MC Server Tool Frontend")
    backend = McstBackendTest() if "--devmode" in sys.argv else McstBackend()
    app = McstFrontend(master=root, backend=backend)
    app.mainloop()


if __name__ == "__main__":
    main()
