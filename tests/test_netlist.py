import unittest

from layouthub.generator.netlist import NetlistCell, DeviceInstance, NetlistLibrary

class TestNetlist(unittest.TestCase):
    def test_netlist_cell_initialization(self):

        cell_name = "TestCell"
        netlist_cell = NetlistCell(cell_name)

        self.assertEqual(netlist_cell.name, cell_name)
        self.assertEqual(netlist_cell.instances, [])
        self.assertEqual(netlist_cell.connections, [])