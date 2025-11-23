# Business Objects Management Script Walkthrough

I have created a Python script to manage (start/stop) Business Objects application services on Windows Server. The solution is generic, configurable, and object-oriented.

## Components

### 1. Configuration ([config.json](file:///C:/Lawrence/Workspace/Antigravity/app-restart/config.json))
Defines the services to manage, their order, and other settings.
```json
{
    "app_name": "BusinessObjects",
    "stop_order": ["BOBJ_Tomcat", "BOBJ_SIA"],
    "start_order": ["BOBJ_SIA", "BOBJ_Tomcat"]
}
```

### 2. Service Manager ([service_manager.py](file:///C:/Lawrence/Workspace/Antigravity/app-restart/service_manager.py))
A generic class that wraps the Windows `sc` command to control services. It handles:
- Checking service status
- Starting/Stopping services
- Waiting for status transitions (with timeout)

### 3. Business Objects Manager ([bobj_manager.py](file:///C:/Lawrence/Workspace/Antigravity/app-restart/bobj_manager.py))
The application-specific logic that:
- Reads [config.json](file:///C:/Lawrence/Workspace/Antigravity/app-restart/config.json)
- Orchestrates the start/stop sequence based on the configured order
- Logs actions to a file and console

### 4. CLI Entry Point ([main.py](file:///C:/Lawrence/Workspace/Antigravity/app-restart/main.py))
Provides a command-line interface to use the tool.
Usage:
```bash
python main.py --action start
python main.py --action stop
python main.py --action restart
```

## Verification

I verified the logic using a mock test script ([mock_test.py](file:///C:/Lawrence/Workspace/Antigravity/app-restart/mock_test.py)) that simulates the Windows Service Control Manager.

### Test Results
The tests verified:
- Correct order of starting services
- Correct order of stopping services
- Handling of service state transitions

```
Ran 2 tests in 0.024s

OK
```

### Manual Verification Steps
To use this on the actual server:
1. Update [config.json](file:///C:/Lawrence/Workspace/Antigravity/app-restart/config.json) with the actual service names of your Business Objects installation.
2. Run `python main.py --action stop` to stop the application.
3. Run `python main.py --action start` to start the application.
