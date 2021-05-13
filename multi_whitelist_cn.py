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
disable_multi_server = False

systemreturn = '''§b[§rMulti_Whitelist§b] §r'''
error = systemreturn + '''§cError: '''
error_unknown_command = error + '''未知命令§r
输入 §7!!whitelist help§r 获取更多资讯'''
error_syntax = error + '''格式错误
输入 §7!!whitelist help§r 获取更多资讯'''
error_permission = error + '你没有权限使用此指令'
help = '''§b-----------§fMulti Whitelist§b-----------§r
''' + prefix + ' / ' + prefix1 + ''' §a显示帮助信息§r
''' + prefix + ''' on/off §a开关白名单§r
''' + prefix + ''' list §a显示白名单列表§r
''' + prefix + ''' add/del/remove + §b[PlayerID]§r§a 管理本地玩家白名单§r
''' + prefix + ''' addall/delall/removeall + §b[PlayerID]§r§a 管理多服务器玩家白名单§r
''' + prefix + ''' sync §a同步本地服务器白名单 §c(只能在本地服务器生效)§r
''' + prefix + ''' reload §a重载本服务器的whitelist.json§r
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
        server.tell(info.player, error + '服务器 §d[' + error_info + ']§c 不存在§r')
    elif num == 4:
        server.tell(info.player, error + 'Rcon 连接 §d[' + error_info + ']§c 服务器失败§r' + '''
检查文件夹 config/multi_whitelist.json 去确认服务器数据是正确的''')
    elif num == 5:
        server.tell(last_player, error + info_change_cn(3))
    elif num == 6:
        server.tell(last_player, error + info_change_cn(4))
    elif num == 7:
        server.tell(last_player, error + info_change_cn(7))
    elif num == 8:
        server.tell(last_player, error + info_change_cn(8))


def run_cmd(server, info, cmd):
    global server_listen, last_player
    server_listen = 1
    last_player = info.player
    server.execute(cmd)


def cmd_all_server(server, info, cmd, player):
    if disable_multi_server:
        server.tell(info.player, error + "多服务器功能以禁止")
        return
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


def read_config():
    with open(path, 'r') as f:
        js = json.load(f)
    return js


def sync(server, info, cmd = ''):
    if disable_multi_server:
        server.tell(info.player, error + "多服务器功能以禁止")
        return
    sub_server_info = read_config()["servers"]
    for i in range(len(sub_server_info)):
        if sub_server_info[i]["same_directory"] == 'true':
            if not os.path.exists("../" + sub_server_info[i]["folder_name"] + "/" + local_path):
                error_msg(server, info, 3, sub_server_info[i]["folder_name"])
            else:
                shutil.copyfile('./' + local_path, "../" + sub_server_info[i]["folder_name"] + "/" + local_path)
                if not rcon_send(server, info, sub_server_info[i], 'whitelist reload'):
                    server.tell(info.player, systemreturn + '同步白名单至 §d[' + sub_server_info[i]["folder_name"] + ']§r 服务器')
        else:
            server.tell(info.player, systemreturn+ '§d[' + sub_server_info["folder_name"] + ']§r 不是本地服务器')


def to_other_server(server, info, cmd = ''):
    sub_server_info = read_config()["servers"]
    for i in range(len(sub_server_info)):
        if not rcon_send(server, info, sub_server_info[i], cmd + target_player):
            if cmd == 'whitelist add ':
                server.tell(info.player, systemreturn + '增加 ' + target_player + ' 至 §d[' + sub_server_info[i]["folder_name"] + ']§r 服务器的白名单')
            elif cmd == 'whitelist remove ':
                server.tell(info.player, systemreturn + '移除 ' + target_player + ' 至 §d[' + sub_server_info[i]["folder_name"] + ']§r 服务器的白名单')


def to_other_server_confirm(server, info, cmd = ''):
    global to_server
    info.player = last_player
    if to_server == 1:
        to_server = 0
        to_other_server(server, info, cmd)


def info_change_cn(num, str = ''):
    if num == 0:
        str = str.replace('There are ', '这里有')
        str = str.replace(' whitelisted players', '个白名单玩家')
    elif num == 1:
        str = '已将' + target_player + '列入白名单'
    elif num == 2:
        str = '已将' + target_player + '移出白名单'
    elif num == 3:
        str = '玩家' + target_player + '已经在白名单了'
    elif num == 4:
        str = '玩家' + target_player + '不是白名单成员'
    elif num == 5:
        str = '白名单已开启'
    elif num == 6:
        str = '白名单已关闭'
    elif num == 7:
        str = '白名单早就开启了'
    elif num == 8:
        str = '白名单早就关闭了'
    elif num == 9:
        str = '白名单已经重新加载'
    return str


def reply(server, info):
    global to_server
    if info.content.startswith('There are'):
        server.tell(last_player, systemreturn + info_change_cn(0, info.content))
    elif info.content.startswith('Added'):
        server.tell(last_player, systemreturn + info_change_cn(1))
        to_other_server_confirm(server, info, 'whitelist add ')
    elif info.content.startswith('Removed'):
        server.tell(last_player, systemreturn + info_change_cn(2))
        to_other_server_confirm(server, info, 'whitelist remove ')
    elif info.content.startswith('Player is already'):
        to_server = 0
        error_msg(server, info, 5)
    elif info.content.startswith('Player is not'):
        to_server = 0
        error_msg(server, info, 6)
    elif info.content.startswith('Whitelist is now turned on'):
        server.tell(last_player, systemreturn + info_change_cn(5))
    elif info.content.startswith('Whitelist is now turned off'):
        server.tell(last_player, systemreturn + info_change_cn(6))
    elif info.content.startswith('Whitelist is already turned on'):
        error_msg(server, info, 7)
    elif info.content.startswith('Whitelist is already turned off'):
        error_msg(server, info, 8)
    elif info.content.startswith('Reloaded'):
        server.tell(last_player, systemreturn + info_change_cn(9))


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
    server.add_help_message('!!whitelist/!!wlist','一个用于多服务器的白名单插件')


def on_info(server, info):
    info2 = copy.deepcopy(info)
    info2.isPlayer = info2.is_player
    onServerInfo(server, info2)
