#!/usr/bin/env python3
"""
Standalone script to check and configure system requirements for the coyote manager.

This script can be executed directly to:
- Verify the coyote.service file exists in the user's systemd directory
- Verify system dependencies are installed
- Set up systemd user lingering
- Configure NetworkManager sudo permissions for WiFi management
"""

import sys
import os
import subprocess
from pathlib import Path

def check_user_service_permissions():
    """Check if the current user has permissions to run user-level systemd services."""
    try:
        # Check if we can run a basic systemctl --user command
        result = subprocess.run(
            ['systemctl', '--user', 'list-units'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if result.returncode == 0:
            print("[OK] User has permissions to run systemd user services.")
            return True
        else:
            print("\033[93mWARNING: Cannot run systemctl --user command\033[0m")
            print("Error:", result.stderr.strip())
            print("Please ensure systemd user services are properly set up.")
            return False
    
    except Exception as e:
        print(f"Error checking user service permissions: {e}")
        return False

def check_nmcli_sudo_permissions():
    """Check if necessary NetworkManager sudo permissions exist for WiFi management."""
    # Required sudo rules for NetworkManager WiFi operations
    required_rules = [
        "robot ALL=(ALL) NOPASSWD: /usr/bin/nmcli device wifi connect *",
        "robot ALL=(ALL) NOPASSWD: /usr/bin/nmcli connection modify *"
    ]
    
    # File path for custom sudoers file
    sudoers_file_path = "/etc/sudoers.d/robot-nmcli"
    
    # Check if the sudoers file exists with correct ownership
    ownership_issue = False
    if os.path.exists(sudoers_file_path):
        # Check ownership
        try:
            stat_info = os.stat(sudoers_file_path)
            if stat_info.st_uid != 0:  # Check if not owned by root (UID 0)
                print("\033[93mWARNING: NetworkManager sudo permissions file has incorrect ownership\033[0m")
                print("The file should be owned by root (UID 0), but is owned by UID", stat_info.st_uid)
                ownership_issue = True
            else:
                # Check file permissions (should be 0440)
                if oct(stat_info.st_mode)[-4:] != '0440':
                    print("\033[93mWARNING: NetworkManager sudo permissions file has incorrect permissions\033[0m")
                    print("The file should have permissions 0440, but has", oct(stat_info.st_mode)[-4:])
                    ownership_issue = True
                else:
                    print("[OK] NetworkManager sudo permissions file exists with correct ownership and permissions.")
                    return True
        except Exception as e:
            print(f"Error checking file ownership: {e}")
            ownership_issue = True
    
    # If file doesn't exist or has ownership issues, we need to create/fix it
    if not os.path.exists(sudoers_file_path) or ownership_issue:
        if not os.path.exists(sudoers_file_path):
            print("\033[93mWARNING: NetworkManager sudo permissions are missing\033[0m")
        print("These permissions are required for WiFi management.")
        
        # Ask if the user wants to create/fix the sudoers file
        choice = input("Do you want to create/fix the necessary sudoers file? (y/n): ")
        if choice.lower() != 'y':
            print("Skipping NetworkManager sudo permissions setup.")
            return False
        
        try:
            # Create a temporary file with the rules
            temp_file = "/tmp/robot-nmcli-sudo"
            with open(temp_file, "w") as f:
                f.write("# NetworkManager WiFi management permissions for robot user\n")
                for rule in required_rules:
                    f.write(f"{rule}\n")
            
            # Set proper temporary permissions
            os.chmod(temp_file, 0o644)
            
            # Check syntax of the sudoers file
            syntax_check = subprocess.run(
                ['sudo', 'visudo', '-c', '-f', temp_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            if syntax_check.returncode != 0:
                print(f"\033[91mERROR: Syntax check failed for sudoers file:\033[0m")
                print(syntax_check.stderr)
                return False
            
            # Install the sudoers file using sudo to ensure proper ownership
            subprocess.run(['sudo', 'install', '-o', 'root', '-g', 'root', '-m', '0440', temp_file, sudoers_file_path], check=True)
            
            # Verify the file was created with correct ownership
            if os.path.exists(sudoers_file_path):
                stat_info = os.stat(sudoers_file_path)
                if stat_info.st_uid == 0:
                    print("[OK] NetworkManager sudo permissions installed with correct ownership.")
                    return True
                else:
                    print("\033[93mWARNING: Failed to set correct ownership on sudoers file\033[0m")
                    return False
            else:
                print("\033[91mERROR: Failed to create sudoers file\033[0m")
                return False
        except Exception as e:
            print(f"\033[91mERROR: Failed to set up NetworkManager sudo permissions: {e}\033[0m")
            return False

def check_service_files():
    """Check if service files are properly installed."""
    service_file = Path.home() / ".config" / "systemd" / "user" / "coyote.service"
    
    if not service_file.exists():
        src_service = Path(__file__).parent.parent / "coyote.service"
        if src_service.exists():
            print(f"Copying service file to {service_file}")
            service_file.parent.mkdir(parents=True, exist_ok=True)
            
            try:
                with open(src_service, 'r') as src, open(service_file, 'w') as dest:
                    dest.write(src.read())
                
                # Reload user systemd daemon
                subprocess.run(['systemctl', '--user', 'daemon-reload'])
                print("[OK] Service file installed and daemon reloaded.")
            except Exception as e:
                print(f"Error installing service file: {e}")
                return False
        else:
            print("\033[93mWARNING: coyote.service file not found in project root\033[0m")
            return False
    else:
        print("[OK] Service file exists.")
    
    return True

def check_system_dependencies():
    """Check if required system dependencies are installed."""
    dependencies = ["whisper-stream", "byobu", "aplay", "piper"]
    missing = []
    
    for dep in dependencies:
        try:
            subprocess.run(['which', dep], check=True, stdout=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            missing.append(dep)
    
    if missing:
        print("\033[93mWARNING: Some system dependencies are missing:\033[0m")
        for dep in missing:
            print(f"  - {dep}")
        print("Please install these dependencies before running the application.")
        return False
    
    print("[OK] System dependencies verified.")
    return True

def setup_lingering():
    """Enable lingering for the current user to allow services to run without login."""
    try:
        # Check if lingering is already enabled
        username = os.environ.get('USER', os.environ.get('USERNAME'))
        result = subprocess.run(
            ['loginctl', 'show-user', username],
            stdout=subprocess.PIPE,
            text=True
        )
        
        if 'Linger=yes' not in result.stdout:
            print("Enabling lingering for user services...")
            try:
                subprocess.run(['loginctl', 'enable-linger', username], check=True)
                print("[OK] Lingering enabled.")
            except subprocess.CalledProcessError:
                # Try with sudo if direct command fails
                print("Trying with sudo...")
                subprocess.run(['sudo', 'loginctl', 'enable-linger', username], check=True)
                print("[OK] Lingering enabled (via sudo).")
        else:
            print("[OK] Lingering already enabled.")
        
        return True
    except Exception as e:
        print(f"Error setting up lingering: {e}")
        print("To enable lingering manually, run: sudo loginctl enable-linger $USER")
        return False

def check_coyote_service_status():
    """Check if coyote.service is properly registered with systemd."""
    try:
        result = subprocess.run(
            ['systemctl', '--user', 'list-unit-files', 'coyote.service'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if 'coyote.service' in result.stdout:
            print("[OK] coyote.service is registered with systemd.")
            
            # Check if it's actually running
            status_result = subprocess.run(
                ['systemctl', '--user', 'is-active', 'coyote.service'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            status = status_result.stdout.strip()
            print(f"Current service status: {status}")
            if status != "active":
                print("\033[93mNote: Service is not currently running. You can start it with:\033[0m")
                print("  systemctl --user start coyote.service")
                print("Or use the service manager in the application.")
                
            return True
        else:
            print("\033[93mWARNING: coyote.service is not properly registered with systemd\033[0m")
            print("Try running: systemctl --user daemon-reload")
            return False
    except Exception as e:
        print(f"Error checking coyote service status: {e}")
        return False

def run_system_checks():
    """Run all system configuration checks."""
    print("Running system configuration checks...")
    checks = [
        check_user_service_permissions(),
        check_nmcli_sudo_permissions(),  # Add check for NetworkManager sudo permissions
        check_service_files(),
        check_system_dependencies(),
        setup_lingering(),
        check_coyote_service_status()
    ]
    
    if all(checks):
        print("\n\033[92mAll system configurations are set up correctly!\033[0m")
    else:
        print("\n\033[93mSome system configurations need attention. See warnings above.\033[0m")

if __name__ == "__main__":
    print("Coyote Manager System Configuration Check")
    print("========================================")
    run_system_checks()