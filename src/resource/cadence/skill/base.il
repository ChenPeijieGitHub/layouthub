;*******************************************************
;
;*******************************************************
procedure(
load_skill(@optional (hier t))
prog(
(l_selected)
	l_selected = geGetSelSet()
	if(l_selected==nil then
		leHiCreateRuler()
	else
		chenCreateAreaRuler()
	)
); end of prog
); end of procedure