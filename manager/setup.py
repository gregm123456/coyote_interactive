from setuptools import setup, find_packages, Command
import os
import subprocess
from pathlib import Path
import sys

# Define the project's root directory
PROJECT_ROOT = Path(__file__).parent

def check_sudoers_config():
    """Check if necessary sudoers configuration exists and guide the user to add it if not."""
    # Required sudoers rule for non-password systemctl operations
    required_rule = "%sudo ALL=(ALL) NOPASSWD: /bin/systemctl"
    
    try:
        # Check if the rule exists in sudoers
        result = subprocess.run(
            ['sudo', 'grep', required_rule, '/etc/sudoers'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if result.returncode != 0:
            print("\033[93mWARNING: Required sudoers configuration is missing\033[0m")
            print("To enable passwordless systemctl operations, run:")
            print(f"\033[1msudo visudo\033[0m")
            print(f"Then add this line to the file:")
            print(f"\033[1m{required_rule}\033[0m")
            print("Save and exit the editor.")
            return False
        
        print("[OK] Sudo configuration verified.")
        return True
    
    except Exception as e:
        print(f"Error checking sudoers configuration: {e}")
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
            subprocess.run(['sudo', 'loginctl', 'enable-linger', username], check=True)
            print("[OK] Lingering enabled.")
        else:
            print("[OK] Lingering already enabled.")
        
        return True
    except Exception as e:
        print(f"Error setting up lingering: {e}")
        print("To enable lingering manually, run: sudo loginctl enable-linger $USER")
        return False

def run_system_checks():
    """Run all system configuration checks."""
    print("Running system configuration checks...")
    checks = [
        check_sudoers_config(),
        check_nmcli_sudo_permissions(),
        check_service_files(),
        check_system_dependencies(),
        setup_lingering()
    ]
    
    if all(checks):
        print("\n\033[92mAll system configurations are set up correctly!\033[0m")
    else:
        print("\n\033[93mSome system configurations need attention. See warnings above.\033[0m")

class SystemChecksCommand(Command):
    """Command to run system configuration checks without installing."""
    description = "Run system configuration checks"
    user_options = []
    
    def initialize_options(self):
        pass
    
    def finalize_options(self):
        pass
    
    def run(self):
        run_system_checks()

# Run system checks if this is an install operation
if len(sys.argv) > 1 and sys.argv[1] in ['install', 'develop']:
    run_system_checks()

# Make sure we're in the right directory for setup
os.chdir(PROJECT_ROOT)

setup(
    name='manager',
    version='0.1.0',
    description='A utility application for managing network and audio settings',
    author='Your Name',
    author_email='your.email@example.com',
    packages=['src', 'src.ui', 'src.services', 'src.utils'],
    package_dir={'': '.'},
    # Keep package metadata and build artifacts inside the manager directory
    package_data={
        '': ['*.md', '*.txt'],
    },
    install_requires=[
        'textual',
        'gpiozero>=2.0.1',
        'psutil>=5.9.5',
        'requests>=2.32.3',
    ],
    entry_points={
        'console_scripts': [
            'coyote-manager=src.main:main',
        ],
    },
    cmdclass={
        'check_system': SystemChecksCommand,
    },
    # Specify where to put build and egg-info artifacts
    options={
        'bdist_egg': {'dist_dir': 'dist'},
        'build': {'build_base': 'build'},
    },
    # Don't install outside of our controlled directories
    zip_safe=False,
)