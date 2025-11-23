import paramiko
import logging
from abc import ABC, abstractmethod

class RemoteConnector(ABC):
    """Abstract base class for remote connections."""
    
    @abstractmethod
    def execute_command(self, command):
        pass

    @abstractmethod
    def close(self):
        pass

class SSHConnector(RemoteConnector):
    """Implementation of RemoteConnector using SSH (Paramiko)."""
    
    def __init__(self, hostname, username, password=None, key_filename=None):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.key_filename = key_filename
        self.client = None
        self.logger = logging.getLogger(__name__)

    def connect(self):
        """Establishes the SSH connection."""
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            connect_args = {
                'hostname': self.hostname,
                'username': self.username
            }
            if self.password:
                connect_args['password'] = self.password
            if self.key_filename:
                connect_args['key_filename'] = self.key_filename
                
            self.client.connect(**connect_args)
            self.logger.info(f"Connected to {self.hostname} via SSH.")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to {self.hostname}: {e}")
            return False

    def execute_command(self, command):
        """Executes a command on the remote server."""
        if not self.client:
            if not self.connect():
                return "", "Connection failed", -1

        self.logger.info(f"Executing remote command: {command}")
        try:
            stdin, stdout, stderr = self.client.exec_command(command)
            exit_status = stdout.channel.recv_exit_status()
            out = stdout.read().decode().strip()
            err = stderr.read().decode().strip()
            return out, err, exit_status
        except Exception as e:
            self.logger.error(f"Failed to execute command: {e}")
            return "", str(e), -1

    def close(self):
        """Closes the SSH connection."""
        if self.client:
            self.client.close()
            self.logger.info("SSH connection closed.")
