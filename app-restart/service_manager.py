import subprocess
import time
import logging

class ServiceManager:
    """
    Generic class to manage Windows services using the 'sc' command.
    """
    def __init__(self, timeout=60):
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)

    def _run_command(self, command):
        """Runs a shell command and returns the output."""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False, # We handle return codes manually
                shell=True
            )
            return result.stdout.strip(), result.stderr.strip(), result.returncode
        except Exception as e:
            self.logger.error(f"Failed to execute command '{command}': {e}")
            return "", str(e), -1

    def get_status(self, service_name):
        """
        Returns the status of a service.
        Common states: 'RUNNING', 'STOPPED', 'START_PENDING', 'STOP_PENDING'.
        """
        cmd = f"sc query \"{service_name}\""
        stdout, _, _ = self._run_command(cmd)
        
        if "STATE" in stdout:
            # Output format example: 
            # STATE              : 4  RUNNING 
            for line in stdout.splitlines():
                if "STATE" in line:
                    parts = line.split()
                    if len(parts) >= 4:
                        return parts[3] # Returns RUNNING, STOPPED, etc.
        return "UNKNOWN"

    def start_service(self, service_name):
        """Starts a service and waits for it to be running."""
        self.logger.info(f"Attempting to start service: {service_name}")
        current_status = self.get_status(service_name)
        
        if current_status == "RUNNING":
            self.logger.info(f"Service {service_name} is already running.")
            return True

        cmd = f"sc start \"{service_name}\""
        stdout, stderr, code = self._run_command(cmd)
        
        if code != 0 and "1056" not in stdout: # 1056 = already running (just in case race condition)
             self.logger.error(f"Failed to start {service_name}. Output: {stdout} Error: {stderr}")
             return False

        return self._wait_for_status(service_name, "RUNNING")

    def stop_service(self, service_name):
        """Stops a service and waits for it to be stopped."""
        self.logger.info(f"Attempting to stop service: {service_name}")
        current_status = self.get_status(service_name)
        
        if current_status == "STOPPED":
            self.logger.info(f"Service {service_name} is already stopped.")
            return True

        cmd = f"sc stop \"{service_name}\""
        stdout, stderr, code = self._run_command(cmd)
        
        if code != 0 and "1062" not in stdout: # 1062 = service not started
             self.logger.error(f"Failed to stop {service_name}. Output: {stdout} Error: {stderr}")
             return False

        return self._wait_for_status(service_name, "STOPPED")

    def _wait_for_status(self, service_name, target_status):
        """Waits for a service to reach a target status."""
        self.logger.info(f"Waiting for {service_name} to reach {target_status}...")
        start_time = time.time()
        
        while time.time() - start_time < self.timeout:
            status = self.get_status(service_name)
            if status == target_status:
                self.logger.info(f"Service {service_name} reached {target_status}.")
                return True
            time.sleep(2)
            
        self.logger.error(f"Timeout waiting for {service_name} to reach {target_status}.")
        return False
