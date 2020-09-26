#!/usr/bin/python3

import argparse
import sys
import pathlib
import os
import logging


# TODO Create backup: tar -c habo3t1/ >/jars/habo3b.tar
# TODO remove server directory
# TODO Restore backup: tar -x </jars/habo3b.tar


DEFAULT_JAR = "server.jar"


class Mcst:
    def __init__(self):
        self.servers_dir = pathlib.Path("/servers")
        self.jars_dir = pathlib.Path("/jars")
        self.minecraft_server_command = 'pwd;/usr/bin/java -Xmx1024M -Xms1024M -jar "{jarfile}" {additional_args}'
        self.encoding = "utf-8"

    def list(self):
        subdirs = [subdir.name
                   for subdir in self.get_server_directories()]
        return "\n".join(subdirs)

    def get_server_directories(self):
        return (subdir
                for subdir in self.servers_dir.iterdir()
                if subdir.is_dir())

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

    def start(self, name: str, jar: str = None, port: str = None):
        if jar is None:
            jar = DEFAULT_JAR
        directory = self.servers_dir / name
        additional_args = ["--nogui"]
        if port is not None:
            additional_args.append(f"--port {port}")
        additional_args_str = " ".join(additional_args)
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
        command = (self.minecraft_server_command
                   .replace("{jarfile}", f"{jarfile}")
                   .replace("{additional_args}", f"{additional_args_str}")
                   )
        os.system(command)

    def clone(self, name: str, template: str):
        if template is None:
            template = self.get_a_random_name()
            if template is None:
                self.create(name)
                self.log(f"There was nothing that could be used as a template, so {name} was created from scratch.")
                return
        target_dir = self.servers_dir / name
        if target_dir.exists():
            raise FileExistsError()
        source_dir = self.servers_dir / template
        if source_dir.exists() is False:
            raise FileNotFoundError()
        target_dir.mkdir()
        for filename in ["eula.txt", "server.properties"]:
            (target_dir / filename).write_bytes((source_dir / filename).read_bytes())
        self.log(f"Initialized {target_dir} from {template}")

    def get_a_random_name(self):
        for subdir in self.get_server_directories():
            return subdir.name

    # noinspection PyMethodMayBeStatic
    def log(self, message):
        logging.info(message)


class ArgumentsHandler:
    def __init__(self, mcst: Mcst):
        self.mcst = mcst

    def handle(self, args):
        parser = argparse.ArgumentParser(description='Minecraft Server Tools')
        subparsers = parser.add_subparsers()

        parser_list = subparsers.add_parser("list", help="List server directories")
        parser_list.set_defaults(func=self.list_func)

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
        parser_start.add_argument("--port", type=int, help="Port to use, overrides server.properties",
                                  default=None)
        parser_start.set_defaults(func=self.start_func)

        parser_clone = subparsers.add_parser("clone", help="Initialize a new server directory based on another")
        parser_clone.add_argument("name", type=str, help="New server directory name")
        parser_clone.add_argument("--template", type=str, help="Server directory to use as template", default=None)
        parser_clone.set_defaults(func=self.clone_func)

        parsed = parser.parse_args(args)
        parsed.func(parsed)

    def list_func(self, args):
        print(self.mcst.list())

    def create_func(self, args):
        # TODO This should also have a jar argument
        self.mcst.create(args.name)

    def settings_show_func(self, args):
        print(self.mcst.settings_dump(args.name))

    def settings_replace_func(self, args):
        new_content = sys.stdin.read()
        self.mcst.settings_replace(args.name, new_content)

    def start_func(self, args):
        self.mcst.start(args.name, args.jar, args.port)

    def clone_func(self, args):
        self.mcst.clone(args.name, args.template)


def main(args):
    logging.basicConfig(level=logging.DEBUG, filename="mcst.log")
    ArgumentsHandler(Mcst()).handle(args)


if __name__ == "__main__":
    main(sys.argv[1:])
