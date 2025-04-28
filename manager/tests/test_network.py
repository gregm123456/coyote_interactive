import unittest
from src.services.vpn import VPNManager
from src.services.wifi import WifiManager
from src.services.ethernet import EthernetManager

class TestNetworkServices(unittest.TestCase):

    def setUp(self):
        self.vpn_manager = VPNManager()
        self.wifi_manager = WifiManager()
        self.ethernet_manager = EthernetManager()

    def test_vpn_status(self):
        status = self.vpn_manager.get_status()
        self.assertIn(status, ['connected', 'disconnected', 'connecting', 'disconnecting'])

    def test_wifi_access_points(self):
        access_points = self.wifi_manager.get_access_points()
        self.assertIsInstance(access_points, list)

    def test_select_wifi_access_point(self):
        access_points = self.wifi_manager.get_access_points()
        if access_points:
            selected = self.wifi_manager.select_access_point(access_points[0])
            self.assertTrue(selected)

    def test_ethernet_status(self):
        status = self.ethernet_manager.get_status()
        self.assertIn(status, ['connected', 'disconnected'])

if __name__ == '__main__':
    unittest.main()