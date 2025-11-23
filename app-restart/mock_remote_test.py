import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import logging

# Add current directory to path
sys.path.append(os.getcwd())

# Mock paramiko before importing modules that use it
mock_paramiko = MagicMock()
sys.modules["paramiko"] = mock_paramiko

from remote_bobj_manager import RemoteBusinessObjectsManager

class TestRemoteBusinessObjectsManager(unittest.TestCase):
    
    def setUp(self):
        with open("test_remote_config.json", "w") as f:
            f.write('{"windows_host": "1.2.3.4", "username": "user", "remote_script_path": "C:\\\\path\\\\to\\\\main.py"}')

    def tearDown(self):
        # Close logging handlers
        logger = logging.getLogger()
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)
            
        if os.path.exists("test_remote_config.json"):
            try:
                os.remove("test_remote_config.json")
            except OSError:
                pass

    @patch('remote_connector.paramiko.SSHClient')
    def test_remote_start_success(self, mock_ssh_client):
        # Mock SSH connection and command execution
        mock_client_instance = MagicMock()
        mock_ssh_client.return_value = mock_client_instance
        
        # Mock exec_command return values (stdin, stdout, stderr)
        mock_stdout = MagicMock()
        mock_stdout.channel.recv_exit_status.return_value = 0
        mock_stdout.read.return_value = b"Action 'start' completed successfully."
        
        mock_stderr = MagicMock()
        mock_stderr.read.return_value = b""
        
        mock_client_instance.exec_command.return_value = (MagicMock(), mock_stdout, mock_stderr)
        
        manager = RemoteBusinessObjectsManager("test_remote_config.json")
        self.assertTrue(manager.perform_action("start"))
        
        # Verify correct command sent
        mock_client_instance.exec_command.assert_called_with('python "C:\\path\\to\\main.py" --action start')

    @patch('remote_connector.paramiko.SSHClient')
    def test_remote_connection_failure(self, mock_ssh_client):
        # Mock connection failure
        mock_client_instance = MagicMock()
        mock_ssh_client.return_value = mock_client_instance
        mock_client_instance.connect.side_effect = Exception("Connection refused")
        
        manager = RemoteBusinessObjectsManager("test_remote_config.json")
        # Should fail gracefully
        self.assertFalse(manager.perform_action("stop"))

if __name__ == '__main__':
    unittest.main()
