permission = {
    "help": 1,
    "list": 1,
    "reload": 1,
    "add": 2,
    "del": 2,
    "addall": 2,
    "delall": 2,
    "sync": 2,
    "on": 3,
    "off": 3,
}

plugin = "multi_whitelist"
PREFIX = "!!whitelist"
PREFIX1 = "!!wlist"

path = "config/" + plugin + ".json"
server_path = "server/"
local_path = server_path + "whitelist.json"

system_return = """§b[§rMulti_Whitelist§b] §r"""
error = system_return + """§cError: """
