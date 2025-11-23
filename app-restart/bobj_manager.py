import json
import logging
import os
from service_manager import ServiceManager

class BusinessObjectsManager:
    """
    Manages the Business Objects application by orchestrating its services.
    """
    def __init__(self, config_path="config.json"):
        self.config = self._load_config(config_path)
        self.service_manager = ServiceManager(timeout=self.config.get("timeout_seconds", 60))
        self._setup_logging()

    def _load_config(self, path):
        """Loads configuration from a JSON file."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Config file not found: {path}")
        with open(path, 'r') as f:
            return json.load(f)

    def _setup_logging(self):
        """Configures logging based on config."""
        log_file = self.config.get("log_file", "bobj_manager.log")
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(self.config.get("app_name", "BusinessObjects"))
        # Also log to console
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)

    def stop_application(self):
        """Stops the application services in the configured order."""
        self.logger.info("Stopping Business Objects application...")
        services = self.config.get("stop_order", [])
        
        for service in services:
            if not self.service_manager.stop_service(service):
                self.logger.error(f"Critical error: Failed to stop {service}. Aborting stop sequence.")
                return False
        
        self.logger.info("Business Objects application stopped successfully.")
        return True

    def start_application(self):
        """Starts the application services in the configured order."""
        self.logger.info("Starting Business Objects application...")
        services = self.config.get("start_order", [])
        
        for service in services:
            if not self.service_manager.start_service(service):
                self.logger.error(f"Critical error: Failed to start {service}. Aborting start sequence.")
                return False
                
        self.logger.info("Business Objects application started successfully.")
        return True

    def restart_application(self):
        """Restarts the application."""
        self.logger.info("Restarting Business Objects application...")
        if self.stop_application():
            return self.start_application()
        return False
