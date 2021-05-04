# coding: utf8
#ver0.9
import copy
import json
import os
import shutil
from utils.rcon import Rcon


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
''' + prefix + ''' add/del/remove + §b[PlayerID]§r§a manage whitelist of local server§r
''' + prefix + ''' addall/delall/removeall + §b[PlayerID]§r§a manage whitelist of all servers§r
''' + prefix + ''' sync §async whitelist in all server §c(only work for loacal server)§r
''' + prefix + ''' reload §areload all local whitelist.json§r
§b-----------------------------------§r
'''


def error_msg(server, info, num, error_info = ''):
    if num == 0:
        server.tell(info.player, error_unknown_command)
    elif num == 1:
        server.tell(info.player, error_syntax)
    elif num == 2:
        server.tell(info.player, error_permission)
    elif num == 3:
        server.tell(info.player, error + 'Server §d[' + error_info + ']§c does not exist§r')
    elif num == 4:
        server.tell(info.player, error + 'Rcon connect failed to §d[' + error_info + ']§c server§r' + '''
Check file config/multi_whitelist.json to ensure your data is right''')
    elif num == 5:
        server.tell(last_player, error + info.content)


def run_cmd(server, info, cmd):
    global server_listen, last_player
    server_listen = 1
    last_player = info.player
    server.execute(cmd)


def cmd_all_server(server, info, cmd, player):
    global target_player, to_server
    to_server = 1
    target_player = player
    run_cmd(server, info, cmd + player)


def rcon_send(server, info, sub_server_info, cmd):
    sub_server_rcon = Rcon(sub_server_info["rcon_ip"], int(sub_server_info["rcon_port"]), sub_server_info["rcon_password"])
    try:
        sub_server_rcon.connect()
        iserror = 0
    except ConnectionRefusedError:
        error_msg(server, info, 4, sub_server_info["folder_name"])
        iserror = 1
    if not iserror:
        sub_server_rcon.send_command(cmd)
        sub_server_rcon.disconnect()
        return 0
    else:
        sub_server_rcon.disconnect()
        return 1


def sync(server, info, cmd = ''):
    with open(path, 'r') as f:
        js = json.load(f)
        sub_server_info = js["servers"]
    for i in range(len(sub_server_info)):
        if sub_server_info[i]["same_directory"] == 'true':
            if not os.path.exists("../" + sub_server_info[i]["folder_name"] + "/" + local_path):
                error_msg(server, info, 3, sub_server_info[i]["folder_name"])
            else:
                shutil.copyfile('./' + local_path, "../" + sub_server_info[i]["folder_name"] + "/" + local_path)
                if not rcon_send(server, info, sub_server_info[i], 'whitelist reload'):
                    server.tell(info.player, systemreturn + 'Synced whitelist with §d[' + sub_server_info[i]["folder_name"] + ']§r server')
        else:
            server.tell(info.player, systemreturn+ '§d[' + sub_server_info["folder_name"] + ']§r is not local server')


def to_other_server(server, info, cmd = ''):
    with open(path, 'r') as f:
        js = json.load(f)
        sub_server_info = js["servers"]
    for i in range(len(sub_server_info)):
        if not rcon_send(server, info, sub_server_info[i], cmd + target_player):
            if cmd == 'whitelist add ':
                server.tell(info.player, systemreturn + 'Added whitelist of ' + target_player + ' for §d[' + sub_server_info[i]["folder_name"] + ']§r server')
            elif cmd == 'whitelist remove ':
                server.tell(info.player, systemreturn + 'Removed whitelist of ' + target_player + ' for §d[' + sub_server_info[i]["folder_name"] + ']§r server')


def to_other_server_confirm(server, info, cmd = ''):
    global to_server
    info.player = last_player
    if to_server == 1:
        to_server = 0
        to_other_server(server, info, cmd)


def reply(server, info):
    global to_server
    if info.content.startswith('There are'):
        server.tell(last_player, systemreturn + info.content)
    elif info.content.startswith('Added'):
        server.tell(last_player, systemreturn + info.content)
        to_other_server_confirm(server, info, 'whitelist add ')
    elif info.content.startswith('Removed'):
        server.tell(last_player, systemreturn + info.content)
        to_other_server_confirm(server, info, 'whitelist remove ')
    elif info.content.startswith('Player is already') or info.content.startswith('Player is not'):
        to_server = 0
        error_msg(server, info, 5)
    elif info.content.startswith('Whitelist is now turned on'):
        server.tell(last_player, systemreturn + info.content)
    elif info.content.startswith('Whitelist is now turned off'):
        server.tell(last_player, systemreturn + info.content)
    elif info.content.startswith('Whitelist is already turned on'):
        error_msg(server, info, 5)
    elif info.content.startswith('Whitelist is already turned off'):
        error_msg(server, info, 5)
    elif info.content.startswith('Reloaded'):
        server.tell(last_player, systemreturn + info.content)


def onServerInfo(server, info):
    global server_listen , last_player, target_player
    if server_listen == 1:
        server_listen = 0
        info.player = last_player
        reply(server, info)
    elif info.isPlayer == 1:
        if (info.content.startswith('!!wlist') or  info.content.startswith('!!whitelist')):
            permission = server.get_permission_level(info.player)
            if permission >= 1:
                args = info.content.split(' ')
                if (len(args) == 1 or args[1] == 'help'):
                    for line in help.splitlines():
                        server.tell(info.player, line)
                else:
                    if args[1] == 'list':
                        run_cmd(server, info, 'whitelist list')
                    elif args[1] == 'reload':
                        run_cmd(server, info, 'whitelist reload')
                    elif permission < 2:
                        error_msg(server, info, 2)
                    elif args[1] == 'sync':
                        sync(server, info)
                    elif args[1] == 'on':
                        run_cmd(server, info, 'whitelist on')
                    elif args[1] == 'off':
                        run_cmd(server, info, 'whitelist off')
                    elif len(args) == 2 and (args[1].startswith('add') or args[1].startswith('del') or args[1].startswith('remove')):
                        error_msg(server, info, 1)
                    elif args[1].startswith('add'):
                        if args[1] == 'addall':
                            cmd_all_server(server, info, 'whitelist add ', args[2])
                        else:
                            target_player = args[2]
                            run_cmd(server, info, 'whitelist add ' + args[2])
                    elif args[1].startswith('del') or args[1].startswith('remove'):    
                        if args[1] == 'delall' or args[1] == 'removeall':
                            cmd_all_server(server, info, 'whitelist remove ', args[2])
                        else:
                            target_player = args[2]
                            run_cmd(server, info, 'whitelist remove ' + args[2])
                    else:
                        error_msg(server, info, 0)
            else:
                error_msg(server, info, 2)


def on_load(server, old):
    server.add_help_message('!!whitelist/!!wlist','A whitelist plugin with multi server')


def on_info(server, info):
    info2 = copy.deepcopy(info)
    info2.isPlayer = info2.is_player
    onServerInfo(server, info2)