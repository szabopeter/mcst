#!/usr/bin/python3

import argparse
import sys
import pathlib
import os
import logging


# TODO create using template
# TODO remove server directory


DEFAULT_JAR = "server.jar"


class Mcst:
    def __init__(self):
        self.servers_dir = pathlib.Path("/servers")
        self.jars_dir = pathlib.Path("/jars")
        self.minecraft_server_command = 'pwd;/usr/bin/java -Xmx1024M -Xms1024M -jar "{jarfile}" nogui'
        self.encoding = "utf-8"

    def create(self, name: str):
        directory = self.servers_dir / name
        if directory.exists():
            raise FileExistsError()
        directory.mkdir()
        self.start(name)
        self.log(f"Initialized {directory}")

    def settings_dump(self, name: str) -> str:
        directory = self.servers_dir / name
        if directory.exists() is False:
            raise FileNotFoundError()
        server_properties = self.servers_dir / name / "server.properties"
        if server_properties.exists() is False:
            raise FileNotFoundError()
        content = server_properties.read_text(encoding=self.encoding)
        self.log(f"Dumping settings from {server_properties}")
        return content

    def settings_replace(self, name: str, new_content: str):
        directory = self.servers_dir / name
        if directory.exists() is False:
            raise FileNotFoundError()
        server_properties = self.servers_dir / name / "server.properties"
        server_properties.write_text(new_content, encoding=self.encoding)
        self.log(f"Replaced settings in {server_properties}")

    def start(self, name: str, jar: str = None):
        if jar is None:
            jar = DEFAULT_JAR
        directory = self.servers_dir / name
        if directory.exists() is False:
            raise FileNotFoundError()
        jarfile = self.jars_dir / jar
        if jarfile.exists() is False:
            raise FileNotFoundError()
        eula_txt = directory / "eula.txt"
        if eula_txt.exists():
            eula_content = eula_txt.read_text(self.encoding)
            if "eula=false" in eula_content:
                eula_content = eula_content.replace("eula=false", "eula=true")
                eula_txt.write_text(eula_content, encoding=self.encoding)
        os.chdir(directory)
        command = self.minecraft_server_command.replace("{jarfile}", f"{jarfile}")
        os.system(command)

    # noinspection PyMethodMayBeStatic
    def log(self, message):
        logging.info(message)


class ArgumentsHandler:
    def __init__(self, mcst: Mcst):
        self.mcst = mcst

    def handle(self, args):
        parser = argparse.ArgumentParser(description='Minecraft Server Tools')
        subparsers = parser.add_subparsers()

        parser_create = subparsers.add_parser("create", help="Initialize a new server directory")
        parser_create.add_argument("name", type=str, help="Server directory name")
        parser_create.set_defaults(func=self.create_func)

        parser_settings_show = subparsers.add_parser("settings-show",
                                                     help="Write settings file of a server directory to stdout")
        parser_settings_show.add_argument("name", type=str, help="Server directory name")
        parser_settings_show.set_defaults(func=self.settings_show_func)

        parser_settings_replace = subparsers.add_parser("settings-replace",
                                                        help="Replace settings file of a server directory from stdin")
        parser_settings_replace.add_argument("name", type=str, help="Server directory name")
        parser_settings_replace.set_defaults(func=self.settings_replace_func)

        parser_start = subparsers.add_parser("start", help="Start server - will stay interactive")
        parser_start.add_argument("name", type=str, help="Server directory name")
        parser_start.add_argument("--jar", type=str, help="jar file to use from the jars directory",
                                  default=None)
        parser_start.set_defaults(func=self.start_func)
        parsed = parser.parse_args(args)
        parsed.func(parsed)

    def create_func(self, args):
        self.mcst.create(args.name)

    def settings_show_func(self, args):
        print(self.mcst.settings_dump(args.name))

    def settings_replace_func(self, args):
        new_content = sys.stdin.read()
        self.mcst.settings_replace(args.name, new_content)

    def start_func(self, args):
        self.mcst.start(args.name, args.jar)


def main(args):
    logging.basicConfig(level=logging.DEBUG, filename="mcst.log")
    ArgumentsHandler(Mcst()).handle(args)


if __name__ == "__main__":
    main(sys.argv[1:])
