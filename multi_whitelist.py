# coding: utf8
import json
import os
import shutil

from mcdreforged.api.rcon import *
from mcdreforged.api.types import *
from mcdreforged.api.command import *
from mcdreforged.api.rtext import *
from mcdreforged.api.decorator import new_thread


PLUGIN_METADATA = {
    'id': 'multi_whitelist',
    'version': '2.4.1',
    'name': 'multi_whitelist',
    'description': 'A plugin can control whitelist with multi servers.',
    'author': 'ricky',
    'link': 'https://github.com/rickyhoho/multi_whitelist',
    'dependencies': {
        'mcdreforged': '>=1.3.0'
    }
}


permission = {
    "help" : 1,
    "list" : 1,
    "reload" : 1,
    "add" : 2,
    "del" : 2,
    "addall" : 2,
    "delall" : 2,
    "sync" : 2,
    "on" : 3,
    "off" : 3,
}


plugin = 'multi_whitelist'
prefix = '!!whitelist'
prefix1 = '!!wlist'

path = 'config/' + plugin + '.json'
server_path = 'server/'
local_path = server_path + 'whitelist.json'
 
last_player = 'test'
target_player = 'test'
server_listen = 0
to_server = 0
disable_multi_server = False

systemreturn = '''§b[§rMulti_Whitelist§b] §r'''
error = systemreturn + '''§cError: '''
error_unknown_command = error + '''Unknown command§r
Type §7!!whitelist help§r for more information'''
error_syntax = error + '''Syntax error
Type §7!!whitelist help§r for more information'''
error_permission = error + 'You have no Permission to use this command'
help = '''§b-----------§fMulti Whitelist§b-----------§r
''' + prefix + ' / ' + prefix1 + ''' §ashow help message§r
''' + prefix + ''' on/off §aon/off whitelist§r
''' + prefix + ''' list §alist all whitelist player§r
''' + prefix + ''' add/del + §b[PlayerID]§r§a manage whitelist of local server§r
''' + prefix + ''' addall/delall + §b[PlayerID]§r§a manage whitelist of all servers§r
''' + prefix + ''' sync §async whitelist in all server §c(only work for loacal server)§r
''' + prefix + ''' reload §areload all local whitelist.json§r
§b-----------------------------------§r
'''

@new_thread('wlist_process')
def help_msg(src : CommandSource):
    src.reply(help)


def permission_check(src : CommandSource, cmd):
    if src.get_permission_level() >= permission[cmd]:
        return True
    else:
        return False


@new_thread('wlist_process')
def error_msg(src : CommandSource = None, num = 0, error_info = '', server : ServerInterface = None, info : Info = None):
    if num == 0:
        src.reply(error_unknown_command)
    elif num == 1:
        src.reply(error_syntax)
    elif num == 2:
        src.reply(error_permission)
    elif num == 3:
        src.reply(error + 'Server §d[' + error_info + ']§c does not exist§r')
    elif num == 4:
        src.reply(error + 'Rcon connect failed to §d[' + error_info + ']§c server§r' + '''
    Check file config/multi_whitelist.json to ensure your data is right''')
    elif num == 5:
        server.tell(last_player, error + info.content)


@new_thread('wlist_cmd')
def run_cmd(src : CommandSource, cmd):
    global server_listen, last_player
    server_listen = 1
    last_player = src.get_info().player
    src.get_server().execute(cmd)


@new_thread('wlist_cmd')
def cmd_all_server(src : CommandSource, cmd, player):
    if disable_multi_server:
        src.reply(error + "multi_server_mode disabled")
        return
    global target_player, to_server
    to_server = 1
    target_player = player
    run_cmd(src, cmd + player)


@new_thread('wlist_cmd')
def edit(src : CommandSource, player, num):
    global target_player
    target_player = player
    if num == 1:
        msg = " add "
    else:
        msg = " remove "
    run_cmd(src, 'whitelist' + msg + player)


def rcon_send(server : ServerInterface, info : Info, sub_server_info, cmd):
    sub_server_rcon = RconConnection(sub_server_info["rcon_ip"], int(sub_server_info["rcon_port"]), sub_server_info["rcon_password"])
    try:
        sub_server_rcon.connect()
        iserror = 0
    except ConnectionRefusedError:
        error_msg(server = server, info = info, num = 4, error_info = sub_server_info["folder_name"])
        iserror = 1
    if not iserror:
        sub_server_rcon.send_command(cmd)
        sub_server_rcon.disconnect()
        return 0
    else:
        sub_server_rcon.disconnect()
        return 1


def read_config():
    with open(path, 'r') as f:
        js = json.load(f)
    return js


@new_thread('wlist_process')
def sync(src : CommandSource):
    if disable_multi_server:
        src.reply(error + "multi_server_mode disabled")
        return
    sub_server_info = read_config()["servers"]
    for i in range(len(sub_server_info)):
        if sub_server_info[i]["same_directory"] == 'true':
            if not os.path.exists("../" + sub_server_info[i]["folder_name"] + "/" + local_path):
                error_msg(src, 3, sub_server_info[i]["folder_name"])
            else:
                shutil.copyfile('./' + local_path, "../" + sub_server_info[i]["folder_name"] + "/" + local_path)
                if not rcon_send(src.get_server, src.getinfo, sub_server_info[i], 'whitelist reload'):
                    src.reply(systemreturn + 'Synced whitelist with §d[' + sub_server_info[i]["folder_name"] + ']§r server')
        else:
            src.reply(systemreturn+ '§d[' + sub_server_info["folder_name"] + ']§r is not local server')


@new_thread('wlist_process')
def to_other_server(server : ServerInterface, info : Info, cmd = ''):
    sub_server_info = read_config()["servers"]
    for i in range(len(sub_server_info)):
        if not rcon_send(server, info, sub_server_info[i], cmd + target_player):
            if cmd == 'whitelist add ':
                server.tell(info.player, systemreturn + 'Added whitelist of ' + target_player + ' for §d[' + sub_server_info[i]["folder_name"] + ']§r server')
            elif cmd == 'whitelist remove ':
                server.tell(info.player, systemreturn + 'Removed whitelist of ' + target_player + ' for §d[' + sub_server_info[i]["folder_name"] + ']§r server')


@new_thread('wlist_process')
def to_other_server_confirm(server : ServerInterface, info : Info, cmd = ''):
    global to_server
    info.player = last_player
    if to_server == 1:
        to_server = 0
        to_other_server(server, info, cmd)


@new_thread('wlist_cmd')
def reply(server : ServerInterface, info : Info):
    global to_server, server_listen
    if info.content.startswith('There are') or info.content.startswith('Reloaded') or info.content.startswith('Whitelist is now turned on') or info.content.startswith('Whitelist is now turned off'):
        server.tell(last_player, systemreturn + info.content)
    elif info.content.startswith('Added'):
        server.tell(last_player, systemreturn + info.content)
        to_other_server_confirm(server, info, 'whitelist add ')
    elif info.content.startswith('Removed'):
        server.tell(last_player, systemreturn + info.content)
        to_other_server_confirm(server, info, 'whitelist remove ')
    elif info.content.startswith('Player is already') or info.content.startswith('Player is not'):
        to_server = 0
        error_msg(server = server, info = info, num = 5)
    elif info.content.startswith('Whitelist is already turned on') or info.content.startswith('Whitelist is already turned off'):
        error_msg(server = server, info = info, num = 5)
    else:
        server_listen = 1


def fox_literal(msg):
    return Literal(msg).requires(lambda src : permission_check(src, msg))


def register_command(server : ServerInterface, prefix_use):
    server.register_command(
        Literal(prefix_use).
        requires(lambda src : permission_check(src, 'help')).
        runs(help_msg).
        on_child_error(UnknownArgument, lambda src : src.reply(error_unknown_command), handled = True).
        on_child_error(RequirementNotMet, lambda src : src.reply(error_permission), handled = True).
        then(
            fox_literal('help').
            runs(help_msg)
        ).then(
            fox_literal('list').
            runs(lambda src : run_cmd(src, 'whitelist list'))
        ).then(
            fox_literal('reload').
            runs(lambda src : run_cmd(src, 'whitelist reload'))
        ).then(
            fox_literal('on').
            runs(lambda src : run_cmd(src, 'whitelist on'))
        ).then(
            fox_literal('off').
            runs(lambda src : run_cmd(src, 'whitelist off'))
        ).then(
            fox_literal('sync').
            runs(sync)
        ).then(
            fox_literal('add').
            then(
                Text('player').
                runs(lambda src, cmdict : edit(src, cmdict['player'], 1))
            )
        ).then(
            fox_literal('del').
            then(
                Text('player').
                runs(lambda src, cmdict : edit(src, cmdict['player'], 2))
            )
        ).then(
            fox_literal('addall').
            then(
                Text('player').
                runs(lambda src, cmdict : cmd_all_server(src, 'whitelist add ', cmdict['player']))
            )
        ).then(
            fox_literal('delall').
            then(
                Text('player').
                runs(lambda src, cmdict : cmd_all_server(src, 'whitelist remove ', cmdict['player']))
            )
        )
    )



def on_info(server : ServerInterface, info : Info):
    global server_listen , last_player, target_player
    if server_listen == 1:
        server_listen = 0
        info.player = last_player
        reply(server, info)


def on_load(server : ServerInterface, old):
    register_command(server, prefix)
    register_command(server, prefix1)
    server.register_help_message('!!whitelist/!!wlist','A whitelist plugin with multi server')