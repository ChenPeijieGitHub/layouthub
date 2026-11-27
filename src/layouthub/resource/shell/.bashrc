# virtuoso settings
export CDS_LOG_PATH="/tmp/"
# bash只能设置为sequential，csh可以设置为pid或sequential
export CDS_LOG_VERSION=sequential

# 提示命令符
export PS1="[\t \u@\h \W]\$ "

# cd 命令增强，进入目录后显示目录下的文件列表和当前路径
cd() {
  builtin cd "$@" && ls && pwd
}
