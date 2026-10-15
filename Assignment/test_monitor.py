import unittest
from main import safety_stop, spoof_check

class TestMonitoring(unittest.TestCase):
    def test_threshold(self):
        self.assertIn("torque_nm", safety_stop({"torque_nm":70,"temperature_c":50,"vibration_mm_s":1}))
    def test_safe_reading(self):
        self.assertEqual(safety_stop({"torque_nm":20,"temperature_c":40,"vibration_mm_s":1}), [])
    def test_implausible_value(self):
        self.assertTrue(spoof_check({"torque_nm":200,"temperature_c":40,"vibration_mm_s":1}))
if __name__ == "__main__":
    unittest.main()
