; 快捷键绑定


hiSetBindKey("Layout" "<Key>a" "leHiMove()")
hiSetBindKey("Layout" "Ctrl<Key>a" "geSelectAllFig()")

hiSetBindKey("Layout" "<Key>b" "geReturn()")
hiSetBindKey("Layout" "Shift<Key>b" "leReturnToLevel()")

hiSetBindKey("Layout" "<Key>c" "leHiCopy()")
hiSetBindKey("Layout" "Shift<Key>c" "leHiChop()")

hiSetBindKey("Layout" "<Key>d" "leHiCreateRuler()")
hiSetBindKey("Layout" "Shift<Key>d" "leHiClearRuler()")
hiSetBindKey("Layout" "Ctrl<Key>d" "geDeselectAll()")

hiSetBindKey("Layout" "<Key>e" "leHiCreatePath()")
hiSetBindKey("Layout" "Shift<Key>e" "leHiCreatePolygon()")

hiSetBindKey("Layout" "<Key>f" "hiZoomAbsoluteScale(hiGetCurrentWindow() 0.9)")
hiSetBindKey("Layout" "Shift<Key>f" "hiGetCurrentWindow()->stopLevel = dbGetMaxHierDepth()")
hiSetBindKey("Layout" "Ctrl<Key>f" "hiGetCurrentWindow()->stopLevel = 0")

hiSetBindKey("Layout" "<Key>g" "leHiCreateGuardRing()")
;hiSetBindKey("Layout" "Shift<Key>g" "leHiCreateGuardRing()")

;hiSetBindKey("Layout" "<Key>h" "leHiCreatePath")
hiSetBindKey("Layout" "Shift<Key>h" "leHiMoveOrigin()")

hiSetBindKey("Layout" "<Key>i" "leHiCreateInst()")
;hiSetBindKey("Layout" "<Key>i" "leHiCreatePath")

;hiSetBindKey("Layout" "<Key>j" "leHiCreatePath")
;hiSetBindKey("Layout" "<Key>j" "leHiCreatePath")

;hiSetBindKey("Layout" "<Key>k" "leHiCreatePath")
;hiSetBindKey("Layout" "<Key>k" "leHiCreatePath")

hiSetBindKey("Layout" "<Key>l" "leHiCreateLabel()")
;hiSetBindKey("Layout" "Shift<Key>l" "leHiCreatePath")

;hiSetBindKey("Layout" "<Key>m" "leHiCreatePath")
hiSetBindKey("Layout" "Ctrl<Key>m" "leHiMerge()")

hiSetBindKey("Layout" "Shift<Key>n" "leHiFlatten()")
;hiSetBindKey("Layout" "<Key>n" "leHiCreatePath")

hiSetBindKey("Layout" "<Key>o" "leHiCreateVia()")

hiSetBindKey("Layout" "<Key>p" "leHiEditDisplayOptions()")

hiSetBindKey("Layout" "<Key>q" "leHiEditProp()")
;hiSetBindKey("Layout" "<Key>q" "leHiCreatePath")

hiSetBindKey("Layout" "<Key>r" "leHiCreateRect()")
hiSetBindKey("Layout" "Ctrl<Key>r" "leMakeHierReadonlyOrEditableMC(hiGetCurrentWindow())")

hiSetBindKey("Layout" "<Key>s" "leHiStretch()")
hiSetBindKey("Layout" "Shift<Key>s" "leHiSearch()")

hiSetBindKey("Layout" "<Key>t" "leZoomToSelSet()")
;hiSetBindKey("Layout" "<Key>t" "leHiCreatePath")

hiSetBindKey("Layout" "<Key>u" "hiUndo()")
hiSetBindKey("Layout" "Shift<Key>u" "hiRedo()")

hiSetBindKey("Layout" "<Key>v" "chenCrossRuler()")
hiSetBindKey("Layout" "Shift<Key>v" "chenFullCrossRuler()")

;hiSetBindKey("Layout" "<Key>w" "leHiCreatePath")
;hiSetBindKey("Layout" "<Key>e" "leHiCreatePath")

;hiSetBindKey("Layout" "<Key>x" "leHiCreatePath")
hiSetBindKey("Layout" "Shift<Key>x" "leHiDescend()")

;hiSetBindKey("Layout" "<Key>y" "leHiCreatePath")
hiSetBindKey("Layout" "Shift<Key>y" "leHiMakeCell()")

hiSetBindKey("Layout" "<Key>z" "hiZoomRelativeScale(hiGetCurrentWindow() 1.2)")
hiSetBindKey("Layout" "Shift<Key>z" "hiZoomRelativeScale(hiGetCurrentWindow() 0.8)")

hiSetBindKey("Layout" "<Key>space" "leHiSave()")
hiSetBindKey("Layout" "Ctrl<Key>space" "leHiSaveACopy()")

hiSetBindKey("Layout" "<Btn4Down>" "hiZoomInAtMouse()")
hiSetBindKey("Layout" "<Btn5Down>" "hiZoomOutAtMouse()")


hiSetBindKey("Layout" "<Key>F12" "ddsHiCloseData()")