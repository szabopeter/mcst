import json


PROP_LAST_SERVER_VERSION = "last_server_version"


class McServerDirectoryInfo:
    last_server_version = ""

    @staticmethod
    def load(output: str) -> "McServerDirectoryInfo":
        info = McServerDirectoryInfo()
        data = json.loads(output)
        info.last_server_version = data.get(PROP_LAST_SERVER_VERSION, "")
        return info
