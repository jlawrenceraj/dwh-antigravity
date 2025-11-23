import json
import logging
import os
from remote_connector import SSHConnector

class RemoteBusinessObjectsManager:
    """
    Manages the Business Objects application remotely via SSH.
    """
    def __init__(self, config_path="remote_config.json"):
        self.config = self._load_config(config_path)
        self._setup_logging()
        self.connector = SSHConnector(
            hostname=self.config["windows_host"],
            username=self.config["username"],
            password=self.config.get("password"),
            key_filename=self.config.get("key_filename")
        )

    def _load_config(self, path):
        """Loads configuration from a JSON file."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Config file not found: {path}")
        with open(path, 'r') as f:
            return json.load(f)

    def _setup_logging(self):
        """Configures logging."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("RemoteBOBJManager")

    def _build_remote_command(self, action):
        """Constructs the command to run on the remote server."""
        python_cmd = self.config.get("python_command", "python")
        script_path = self.config.get("remote_script_path")
        return f"{python_cmd} \"{script_path}\" --action {action}"

    def perform_action(self, action):
        """Connects to the remote server and performs the specified action."""
        if action not in ["start", "stop", "restart"]:
            self.logger.error(f"Invalid action: {action}")
            return False

        command = self._build_remote_command(action)
        self.logger.info(f"Sending command to remote server: {command}")
        
        stdout, stderr, exit_code = self.connector.execute_command(command)
        
        if exit_code == 0:
            self.logger.info(f"Remote action '{action}' completed successfully.")
            self.logger.info(f"Remote Output:\n{stdout}")
            return True
        else:
            self.logger.error(f"Remote action '{action}' failed with exit code {exit_code}.")
            self.logger.error(f"Remote Error:\n{stderr}")
            self.logger.info(f"Remote Output:\n{stdout}")
            return False
        
    def close(self):
        self.connector.close()
