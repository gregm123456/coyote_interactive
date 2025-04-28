import unittest
from src.services.audio import AudioService

class TestAudioService(unittest.TestCase):

    def setUp(self):
        self.audio_service = AudioService()

    def test_get_microphone_names(self):
        microphones = self.audio_service.get_microphone_names()
        self.assertIsInstance(microphones, list)

    def test_get_microphone_volume(self):
        volumes = self.audio_service.get_microphone_volumes()
        self.assertIsInstance(volumes, list)

    def test_get_audio_output_device_names(self):
        output_devices = self.audio_service.get_audio_output_device_names()
        self.assertIsInstance(output_devices, list)

    def test_get_audio_output_volumes(self):
        output_volumes = self.audio_service.get_audio_output_volumes()
        self.assertIsInstance(output_volumes, list)

    def test_indexed_microphone_info(self):
        indexed_info = self.audio_service.get_indexed_microphone_info()
        self.assertIsInstance(indexed_info, list)

    def test_indexed_audio_output_info(self):
        indexed_info = self.audio_service.get_indexed_audio_output_info()
        self.assertIsInstance(indexed_info, list)

if __name__ == '__main__':
    unittest.main()