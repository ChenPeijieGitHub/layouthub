from parser.gds_parser import LayoutIo

with LayoutIo("E:\\workspace\\layouthub\\test\\mock_gds\\demo_testkey.gds") as io:
    io.parse()
    fmt = io.format
    print(fmt)  # 输出 "gds"
