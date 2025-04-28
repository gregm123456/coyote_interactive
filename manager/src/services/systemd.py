from subprocess import run, PIPE, CalledProcessError

def start_service(service_name, user_service=True):
    """
    Start a systemd service and return success status and any output/error messages.
    
    Args:
        service_name: Name of the service to start
        user_service: Whether this is a user service (--user flag needed)
        
    Returns:
        tuple: (success, message) where success is a boolean and message is a string
    """
    try:
        cmd = ['systemctl', 'start', service_name]
        if user_service:
            cmd.insert(1, '--user')  # Add --user flag after systemctl
            
        result = run(['sudo'] + cmd if not user_service else cmd, 
                    stdout=PIPE, stderr=PIPE, check=True, text=True)
        
        # Verify service actually started by checking status immediately after
        status_cmd = ['systemctl', 'is-active', service_name]
        if user_service:
            status_cmd.insert(1, '--user')  # Add --user flag
            
        status_result = run(status_cmd, stdout=PIPE, stderr=PIPE, text=True)
        
        if status_result.stdout.strip() == 'active':
            return True, f"Service {service_name} started successfully."
        else:
            return False, f"Service {service_name} failed to start. Current status: {status_result.stdout.strip()}"
    
    except CalledProcessError as e:
        error_msg = e.stderr.strip() if e.stderr else str(e)
        return False, f"Error starting {service_name}: {error_msg}"

def stop_service(service_name, user_service=True):
    """
    Stop a systemd service and return success status and any output/error messages.
    
    Args:
        service_name: Name of the service to stop
        user_service: Whether this is a user service (--user flag needed)
        
    Returns:
        tuple: (success, message) where success is a boolean and message is a string
    """
    try:
        cmd = ['systemctl', 'stop', service_name]
        if user_service:
            cmd.insert(1, '--user')  # Add --user flag
            
        result = run(['sudo'] + cmd if not user_service else cmd, 
                   stdout=PIPE, stderr=PIPE, check=True, text=True)
        
        # Verify service actually stopped
        status_cmd = ['systemctl', 'is-active', service_name]
        if user_service:
            status_cmd.insert(1, '--user')  # Add --user flag
            
        status_result = run(status_cmd, stdout=PIPE, stderr=PIPE, text=True)
        
        if status_result.stdout.strip() != 'active':
            return True, f"Service {service_name} stopped successfully."
        else:
            return False, f"Service {service_name} failed to stop. It's still active."
    
    except CalledProcessError as e:
        error_msg = e.stderr.strip() if e.stderr else str(e)
        return False, f"Error stopping {service_name}: {error_msg}"

def restart_service(service_name, user_service=True):
    """
    Restart a systemd service and return success status and any output/error messages.
    
    Args:
        service_name: Name of the service to restart
        user_service: Whether this is a user service (--user flag needed)
        
    Returns:
        tuple: (success, message) where success is a boolean and message is a string
    """
    try:
        cmd = ['systemctl', 'restart', service_name]
        if user_service:
            cmd.insert(1, '--user')  # Add --user flag
            
        result = run(['sudo'] + cmd if not user_service else cmd, 
                   stdout=PIPE, stderr=PIPE, check=True, text=True)
        
        # Verify service is running after restart
        status_cmd = ['systemctl', 'is-active', service_name]
        if user_service:
            status_cmd.insert(1, '--user')  # Add --user flag
            
        status_result = run(status_cmd, stdout=PIPE, stderr=PIPE, text=True)
        
        if status_result.stdout.strip() == 'active':
            return True, f"Service {service_name} restarted successfully."
        else:
            return False, f"Service {service_name} failed to restart. Current status: {status_result.stdout.strip()}"
    
    except CalledProcessError as e:
        error_msg = e.stderr.strip() if e.stderr else str(e)
        return False, f"Error restarting {service_name}: {error_msg}"

def get_service_status(service_name, user_service=True):
    """
    Get the status of a systemd service.
    
    Args:
        service_name: Name of the service
        user_service: Whether this is a user service (--user flag needed)
        
    Returns:
        str: Status of the service (active, inactive, failed, etc.)
    """
    try:
        cmd = ['systemctl', 'is-active', service_name]
        if user_service:
            cmd.insert(1, '--user')  # Add --user flag
            
        result = run(cmd, stdout=PIPE, stderr=PIPE, text=True)
        return result.stdout.strip()
    except Exception:
        return "unknown"

def get_service_details(service_name, user_service=True):
    """
    Get detailed information about a service.
    
    Args:
        service_name: Name of the service
        user_service: Whether this is a user service (--user flag needed)
        
    Returns:
        str: Detailed status information
    """
    try:
        cmd = ['systemctl', 'status', service_name]
        if user_service:
            cmd.insert(1, '--user')  # Add --user flag
            
        result = run(cmd, stdout=PIPE, stderr=PIPE, text=True)
        return result.stdout.strip()
    except Exception as e:
        return f"Error getting service details: {e}"

def enable_service(service_name, user_service=True):
    """
    Enable a systemd service to start on boot.
    
    Args:
        service_name: Name of the service to enable
        user_service: Whether this is a user service (--user flag needed)
        
    Returns:
        tuple: (success, message) where success is a boolean and message is a string
    """
    try:
        cmd = ['systemctl', 'enable', service_name]
        if user_service:
            cmd.insert(1, '--user')  # Add --user flag
            
        result = run(['sudo'] + cmd if not user_service else cmd, 
                   stdout=PIPE, stderr=PIPE, check=True, text=True)
        return True, f"Service {service_name} enabled successfully."
    except CalledProcessError as e:
        error_msg = e.stderr.strip() if e.stderr else str(e)
        return False, f"Error enabling {service_name}: {error_msg}"

def disable_service(service_name, user_service=True):
    """
    Disable a systemd service from starting on boot.
    
    Args:
        service_name: Name of the service to disable
        user_service: Whether this is a user service (--user flag needed)
        
    Returns:
        tuple: (success, message) where success is a boolean and message is a string
    """
    try:
        cmd = ['systemctl', 'disable', service_name]
        if user_service:
            cmd.insert(1, '--user')  # Add --user flag
            
        result = run(['sudo'] + cmd if not user_service else cmd, 
                   stdout=PIPE, stderr=PIPE, check=True, text=True)
        return True, f"Service {service_name} disabled successfully."
    except CalledProcessError as e:
        error_msg = e.stderr.strip() if e.stderr else str(e)
        return False, f"Error disabling {service_name}: {error_msg}"