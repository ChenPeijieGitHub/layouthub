#!/usr/bin/env csh

# 必须是脚本第一条可执行命令,捕获被 source 的脚本路径
set SCRIPT_FILE = "$_"
# 转成绝对路径并提取脚本所在目录
set ROOT_PATH = `cd "`dirname "$SCRIPT_FILE"`" && pwd`
# 设为环境变量,全局可用
setenv ROOT_PATH "$ROOT_PATH"