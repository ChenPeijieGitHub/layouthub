;*******************************************************
; message_box
;*******************************************************
procedure(
message_box(str_title, str_content)
prog(
(m_form)
	if(strlen(str_title)*strlen(str_content) == 0 then
		println("title or content should not be an empty string")
		return(nil)
	)
	m_form = hiCreateAppForm(
		?name		stringToSymbol(str_title)
		?fields		list(list(hiCreateOutputStringField(
						?name	'MessageBoxContent
						?value	str_content
						) 5:5 strlen(str_content)*7+20:50 strlen(str_content)*7 )
				)
		?dialogStyle	'modal
		?formTitle	t_tistr_titletle
		?buttonLayout	'Close
		)
	hiDisplayForm(m_form)
); end of prog
); end of procedure