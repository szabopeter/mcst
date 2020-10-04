import os
from abc import ABC, abstractmethod
from typing import List, Optional


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

    @abstractmethod
    def create(self, name: str):
        pass

    @abstractmethod
    def clone(self, name: str, template:str):
        pass


class McstBackend(McstBackendInterface):
    def __init__(self):
        self.command_template = "~/bin/mcst.sh"

    def list(self) -> List[str]:
        output = os.popen(f"{self.command_template} list").read()
        return [name for name in output.split("\n") if name]

    def create(self, name: str):
        os.system(f'{self.command_template} create "{name}"')

    def settings_dump(self, name: str) -> str:
        output = os.popen(f'{self.command_template} settings-show "{name}"').read()
        return output

    def settings_replace(self, name: str, new_content: str):
        pipe = os.popen(f'{self.command_template} settings-replace "{name}"', mode="w")
        pipe.write(new_content)

    def start(self, name: str):
        os.system(f'{self.command_template} start "{name}"')

    def clone(self, name: str, template: Optional[str]):
        if template is None:
            os.system(f'{self.command_template} clone "{name}"')
        else:
            os.system(f'{self.command_template} clone --template "{template}" "{name}"')


class McstBackendTest(McstBackendInterface):
    def __init__(self):
        self.directories = ["easy", "normal", "hard", "hardcore", "creative"]

    def list(self) -> List[str]:
        return self.directories

    def create(self, name: str):
        os.system("bc -v")
        self.directories.append(name)
        print(f"Created new server directory {name}")

    def settings_dump(self, name: str) -> str:
        return f"Loremipsum...\nPlaceholder for {name} settings\n"*40

    def settings_replace(self, name: str, new_content: str):
        print(f"Replacing settings for {name}")
        print("New content will be:")
        print(new_content)

    def start(self, name: str):
        os.system("bc")

    def clone(self, name: str, template: Optional[str]):
        self.directories.append(name)
        print(f"Created {name} based on {template}")