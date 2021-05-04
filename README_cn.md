# multi_whitelist
-----
[english](https://github.com/rickyhoho/multi_whitelist/blob/master/README.md)

一个 [MCDReforged](https://github.com/Fallen-Breath/MCDReforged) 的插件，用于控制多服务器白名单

基于minecraft的白名单功能

需要开启`rcon`功能去使用此插件

输入 `!!whitelist` 或 `!!wlist` 去获取帮助菜单

你需要填写配置文件 `MCDR/config/multi_whitelist.json`

# permission

`user` 权限以上的用户可以查看命令和查看白名单列表
  
`helper` 权限以上的用户可以使用所有功能

# config
-----
填写`multi_whitelist.json`
|名字|type|例子|功能|
|---|---|---|---|
|"folder_name"|`str`|`"creative"`|服务器MCDR文件夹名字|
|"rcon_ip"|`str`|`"127.0.0.1"`|服务器rcon的ip|
|"rcon_port"|`int`|`"12345"`|服务器rcon的端口|
|"rcon_password"|`str`|`"password"`|服务器rcon的密码|
|"same_directory"|`bool`|`"true"`|服务器文件夹是否存在本地 (请使用`小写`)|
