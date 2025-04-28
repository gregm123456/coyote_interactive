import unittest
from src.services.systemd import manage_service_status

class TestServiceManagement(unittest.TestCase):

    def test_service_status(self):
        # Test to check if the service status can be retrieved correctly
        status = manage_service_status('coyote.service')
        self.assertIn(status, ['active', 'inactive', 'failed'])

    def test_start_service(self):
        # Test to check if the service can be started
        result = manage_service_status('coyote.service', action='start')
        self.assertTrue(result)

    def test_stop_service(self):
        # Test to check if the service can be stopped
        result = manage_service_status('coyote.service', action='stop')
        self.assertTrue(result)

    def test_restart_service(self):
        # Test to check if the service can be restarted
        result = manage_service_status('coyote.service', action='restart')
        self.assertTrue(result)

    def test_enable_service(self):
        # Test to check if the service can be enabled
        result = manage_service_status('coyote.service', action='enable')
        self.assertTrue(result)

    def test_disable_service(self):
        # Test to check if the service can be disabled
        result = manage_service_status('coyote.service', action='disable')
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()