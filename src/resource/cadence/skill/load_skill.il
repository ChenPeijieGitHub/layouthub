;*******************************************************
; 递归加载指定目录下所有 *.il skill 文件
; load_skill("/software/pdk/skill/")
;*******************************************************


; 全局后缀变量，外部可修改
defvar(SKILL_SUFFIX, list("il" "ile"))
; 黑名单目录：过滤跳过的文件夹
defvar(HIER_LOAD_BLACK_LIST, list(".", ".."))


procedure(
load_skill(str_path, @optional (hier t))
prog(
(abs_path, is_black, file_full_path, ext, t_match)
	abs_path = truename(str_path)
	if(!isDir(abs_path) then
		printf("[ERROR] Directory not exist: %s\n" abs_path)
		return(nil)
	)
	foreach(m_file getDirFiles(abs_path)
		; 先判断是否在黑名单目录，直接跳过
		is_black = exists(x HIER_LOAD_BLACK_LIST strcmp(m_file x)==0 )
		if(!is_black then
			file_full_path = strcat(abs_path "/" m_file)
			; 子目录：递归
			if(isDir(file_full_path) then
				if(hier then
					load_skill(file_full_path, hier)
				)
			else
				; 判断后缀 .il
				ext = lowerCase(car(last(parseString(m_file "."))))
				t_match = exists(x SKILL_SUFFIX strcmp(ext x)==0)
				if(t_match then
					printf("Loading : %s\n" file_full_path)
					if(!load(file_full_path) then
						printf("[WARN] Load failed: %s\n" file_full_path)
					)
				); end of if
			); end of if
		); endo of if
	); end of foreach
); end of prog
); end of procedure
