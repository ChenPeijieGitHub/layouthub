import gdstk


def build_demo_layout():
    lib = gdstk.Library()

    # 底层：单个电阻cell
    res_cell = gdstk.Cell("RES_W0.2")
    # layer: 1 / 0
    res_cell.add(gdstk.rectangle((0, 0), (0.2, 2.0), layer=1, datatype=0))
    # label
    res_cell.add(gdstk.Label("RES", (0.1, 2.2), layer=5, texttype=0))
    lib.add(res_cell)

    # top testkey cell
    top_cell = gdstk.Cell("TK_RES_ARRAY_W0.20_S0.5")
    # 摆放多个电阻实例
    for i in range(5):
        inst = gdstk.Reference(res_cell, origin=(i * 0.5, 0))
        top_cell.add(inst)
    # top层label
    top_cell.add(gdstk.Label("TK_RES_ARRAY_W0.20_S0.5", (0, 3.0), layer=5, texttype=0))
    lib.add(top_cell)

    # 写出gds
    lib.write_gds("./demo_testkey.gds")
    # 可选：同时输出oas，用来测试LayoutIo的oas读取
    lib.write_oas("./demo_testkey.oas")


if __name__ == "__main__":
    build_demo_layout()