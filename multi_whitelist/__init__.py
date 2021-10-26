# coding: utf8
import json
import os
import shutil

from mcdreforged.api.rcon import *
from mcdreforged.api.decorator import new_thread

from multi_whitelist.utils import *

last_player = "test"
target_player = "test"
server_listen = 0
to_server = 0
disable_multi_server = False


@new_thread("whitelist_process")
def help_msg(src: CommandSource):
    help_message = """§b-----------§fMulti Whitelist§b-----------§r
""" + PREFIX + " / " + PREFIX1 + f"""§a {tr("help")}§r
""" + PREFIX + f""" on/off§a {tr("on_off")}§r
""" + PREFIX + f""" list§a {tr("list")}§r
""" + PREFIX + f""" add/del + §b{tr("add_del")}§r
""" + PREFIX + f""" addall/delall + §b{tr("add_del_all")}§r
""" + PREFIX + f""" sync §a{tr("sync")}§r
""" + PREFIX + f""" reload§a {tr("reload")}§r
§b-----------------------------------§r"""
    src.reply(help_message)


@new_thread("whitelist_process")
def error_msg(src: CommandSource = None, num=0, error_info="", server: ServerInterface = None, info: Info = None):
    if num == 0:
        src.reply(error + tr("error_unknown_command", rtext_cmd(
            "!!whitelist help", f"{tr('click_msg')} {tr('help')}", "!!wlist help")))
    elif num == 1:
        src.reply(error + tr("error_syntax", rtext_cmd(
            "!!whitelist help", f"{tr('click_msg')} {tr('help')}", "!!wlist help")))
    elif num == 2:
        src.reply(error + tr("error_permission"))
    elif num == 3:
        src.reply(error + tr("error_exist", error_info))
    elif num == 4:
        if info.player is None:
            server.logger.info(error + tr("error_rcon", error_info))
        else:
            server.reply(info, error + tr("error_rcon", error_info))
    elif num == 5:
        server.tell(last_player, error + info.content)


@new_thread("whitelist_cmd")
def run_cmd(src: PlayerCommandSource, cmd):
    global server_listen, last_player
    server_listen = 1
    last_player = src.get_info().player
    src.get_server().execute(cmd)


@new_thread("whitelist_cmd")
def cmd_all_server(src: PlayerCommandSource, cmd, player):
    if disable_multi_server:
        src.reply(error + tr("disabled"))
        return
    global target_player, to_server
    to_server = 1
    target_player = player
    run_cmd(src, cmd + player)


@new_thread("whitelist_cmd")
def edit(src: PlayerCommandSource, player, num):
    global target_player
    target_player = player
    if num == 1:
        msg = " add "
    else:
        msg = " remove "
    run_cmd(src, "whitelist" + msg + player)


def rcon_send(server: ServerInterface, info: Info, sub_server_info, cmd):
    sub_server_rcon = RconConnection(sub_server_info["rcon_ip"], int(sub_server_info["rcon_port"]),
                                     sub_server_info["rcon_password"])
    try:
        sub_server_rcon.connect()
        is_error = 0
    except ConnectionRefusedError:
        error_msg(server=server, info=info, num=4, error_info=sub_server_info["folder_name"])
        is_error = 1
    if not is_error:
        sub_server_rcon.send_command(cmd)
        sub_server_rcon.disconnect()
        return 0
    else:
        sub_server_rcon.disconnect()
        return 1


def read_config():
    with open(path, "r") as f:
        js = json.load(f)
    return js


@new_thread("whitelist_process")
def sync(src: PlayerCommandSource):
    if disable_multi_server:
        src.reply(error + tr("disabled"))
        return
    sub_server_info = read_config()["servers"]
    for i in range(len(sub_server_info)):
        if sub_server_info[i]["same_directory"] == "true":
            if not os.path.exists("../" + sub_server_info[i]["folder_name"] + "/" + local_path):
                error_msg(src, 3, sub_server_info[i]["folder_name"])
            else:
                shutil.copyfile("./" + local_path, "../" + sub_server_info[i]["folder_name"] + "/" + local_path)
                if not rcon_send(src.get_server(), src.get_info(), sub_server_info[i], "whitelist reload"):
                    src.reply(
                        system_return + tr("synced", sub_server_info[i]["folder_name"]))
        else:
            src.reply(error + tr("error_not_local", sub_server_info["folder_name"]))


@new_thread("whitelist_process")
def to_other_server(server: ServerInterface, info: Info, cmd=""):
    sub_server_info = read_config()["servers"]
    for i in range(len(sub_server_info)):
        if not rcon_send(server, info, sub_server_info[i], cmd + target_player):
            player = info.player
            if cmd == "whitelist add ":
                server.tell(player, system_return + tr("added", target_player, sub_server_info[i]["folder_name"]))
            elif cmd == "whitelist remove ":
                server.tell(player, system_return + tr("removed", target_player, sub_server_info[i]["folder_name"]))


@new_thread("whitelist_process")
def to_other_server_confirm(server: ServerInterface, info: Info, cmd=""):
    global to_server
    info.player = last_player
    if to_server == 1:
        to_server = 0
        to_other_server(server, info, cmd)


@new_thread("whitelist_cmd")
def reply(server: ServerInterface, info: Info):
    global to_server, server_listen
    if info.content.startswith("There are") or info.content.startswith("Reloaded") or info.content.startswith(
            "Whitelist is now turned on") or info.content.startswith("Whitelist is now turned off"):
        server.tell(last_player, system_return + info.content)
    elif info.content.startswith("Added"):
        server.tell(last_player, system_return + info.content)
        to_other_server_confirm(server, info, "whitelist add ")
    elif info.content.startswith("Removed"):
        server.tell(last_player, system_return + info.content)
        to_other_server_confirm(server, info, "whitelist remove ")
    elif info.content.startswith("Player is already") or info.content.startswith("Player is not"):
        to_server = 0
        error_msg(server=server, info=info, num=5)
    elif info.content.startswith("Whitelist is already turned on") or info.content.startswith(
            "Whitelist is already turned off"):
        error_msg(server=server, info=info, num=5)
    else:
        server_listen = 1


def fox_literal(msg):
    return Literal(msg).requires(lambda src: permission_check(src, msg))


def register_command(server: PluginServerInterface, prefix_use):
    server.register_command(
        Literal(prefix_use).
            requires(lambda src: permission_check(src, "help")).
            runs(help_msg).
            on_child_error(UnknownArgument, lambda src: error_msg(src, 0), handled=True).
            on_child_error(RequirementNotMet, lambda src: error_msg(src, 2), handled=True).
            then(
            fox_literal("help").
                runs(help_msg)
        ).then(
            fox_literal("list").
                runs(lambda src: run_cmd(src, "whitelist list"))
        ).then(
            fox_literal("reload").
                runs(lambda src: run_cmd(src, "whitelist reload"))
        ).then(
            fox_literal("on").
                runs(lambda src: run_cmd(src, "whitelist on"))
        ).then(
            fox_literal("off").
                runs(lambda src: run_cmd(src, "whitelist off"))
        ).then(
            fox_literal("sync").
                runs(sync)
        ).then(
            fox_literal("add").
                then(
                Text("player").
                    runs(lambda src, cmd_dict: edit(src, cmd_dict["player"], 1))
            )
        ).then(
            fox_literal("del").
                then(
                Text("player").
                    runs(lambda src, cmd_dict: edit(src, cmd_dict["player"], 2))
            )
        ).then(
            fox_literal("addall").
                then(
                Text("player").
                    runs(lambda src, cmd_dict: cmd_all_server(src, "whitelist add ", cmd_dict["player"]))
            )
        ).then(
            fox_literal("delall").
                then(
                Text("player").
                    runs(lambda src, cmd_dict: cmd_all_server(src, "whitelist remove ", cmd_dict["player"]))
            )
        )
    )


def on_info(server: PluginServerInterface, info: Info):
    global server_listen, last_player, target_player
    if server_listen == 1:
        server_listen = 0
        info.player = last_player
        reply(server, info)


def on_load(server: PluginServerInterface, old):
    register_command(server, PREFIX)
    register_command(server, PREFIX1)
    server.register_help_message("!!whitelist/!!wlist", tr("main_msg"))
