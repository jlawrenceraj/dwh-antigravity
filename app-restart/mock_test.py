import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import logging

# Add current directory to path to import modules
sys.path.append(os.getcwd())

from bobj_manager import BusinessObjectsManager
from service_manager import ServiceManager

class TestBusinessObjectsManager(unittest.TestCase):
    
    def setUp(self):
        # Create a dummy config file for testing
        with open("test_config.json", "w") as f:
            f.write('{"app_name": "TestApp", "timeout_seconds": 1, "log_file": "test.log", "stop_order": ["ServiceA", "ServiceB"], "start_order": ["ServiceB", "ServiceA"]}')

    def tearDown(self):
        # Close logging handlers to release file lock
        logger = logging.getLogger()
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)
            
        if os.path.exists("test_config.json"):
            try:
                os.remove("test_config.json")
            except OSError:
                pass
        if os.path.exists("test.log"):
            try:
                os.remove("test.log")
            except OSError:
                pass

    @patch('service_manager.subprocess.run')
    def test_start_application_success(self, mock_run):
        # Mock successful start
        # Sequence: 
        # 1. check status ServiceB (STOPPED)
        # 2. start ServiceB
        # 3. check status ServiceB (RUNNING)
        # 4. check status ServiceA (STOPPED)
        # 5. start ServiceA
        # 6. check status ServiceA (RUNNING)
        
        # We need to simulate the output of 'sc query'
        # First call: ServiceB status -> STOPPED
        # Second call: ServiceB status -> RUNNING (after start)
        # Third call: ServiceA status -> STOPPED
        # Fourth call: ServiceA status -> RUNNING (after start)
        
        def side_effect(command, **kwargs):
            result = MagicMock()
            result.returncode = 0
            result.stderr = ""
            
            if "sc query" in command:
                if "ServiceB" in command:
                    # Simulate transition
                    if mock_run.call_count < 3: # First check
                        result.stdout = "STATE : 1 STOPPED"
                    else:
                        result.stdout = "STATE : 4 RUNNING"
                elif "ServiceA" in command:
                    if mock_run.call_count < 6:
                        result.stdout = "STATE : 1 STOPPED"
                    else:
                        result.stdout = "STATE : 4 RUNNING"
            elif "sc start" in command:
                result.stdout = ""
            
            return result

        mock_run.side_effect = side_effect
        
        manager = BusinessObjectsManager("test_config.json")
        self.assertTrue(manager.start_application())

    @patch('service_manager.subprocess.run')
    def test_stop_application_success(self, mock_run):
        # Mock successful stop
        
        def side_effect(command, **kwargs):
            result = MagicMock()
            result.returncode = 0
            result.stderr = ""
            
            if "sc query" in command:
                if "ServiceA" in command:
                    if mock_run.call_count < 3:
                        result.stdout = "STATE : 4 RUNNING"
                    else:
                        result.stdout = "STATE : 1 STOPPED"
                elif "ServiceB" in command:
                    if mock_run.call_count < 6:
                        result.stdout = "STATE : 4 RUNNING"
                    else:
                        result.stdout = "STATE : 1 STOPPED"
            elif "sc stop" in command:
                result.stdout = ""
            
            return result

        mock_run.side_effect = side_effect
        
        manager = BusinessObjectsManager("test_config.json")
        self.assertTrue(manager.stop_application())

if __name__ == '__main__':
    unittest.main()
