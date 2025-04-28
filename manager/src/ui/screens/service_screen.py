from textual.widget import Widget
from textual.widgets import Static, Button
from textual.containers import Container
from services.systemd import get_service_status, start_service, stop_service, restart_service

# Define the specific service name
COYOTE_SERVICE_NAME = "coyote.service"

class ServiceScreen(Widget):
    """Service management screen for controlling coyote.service."""
    
    def compose(self):
        """Compose the service screen widgets."""
        yield Static("Service Management", classes="title")
        
        # Service status container
        self.status_container = Container(id="service-status")
        yield Static(f"Service: {COYOTE_SERVICE_NAME}")
        yield self.status_container
        
        # Control buttons
        yield Button("Start Service", id="start-service", variant="success")
        yield Button("Stop Service", id="stop-service", variant="error")
        yield Button("Restart Service", id="restart-service", variant="primary")
        yield Button("Refresh Status", id="refresh-status", variant="default")
        
        # Service output container for logs
        self.output_container = Container(id="service-output")
        yield Static("Service Output:")
        yield self.output_container

    def on_mount(self):
        """Initialize and update service information when mounted."""
        self.update_service_status()

    def update_service_status(self):
        """Update the service status display."""
        status = get_service_status(COYOTE_SERVICE_NAME)
        
        self.status_container.remove_children()
        # Add a color class based on status
        status_class = "status-active" if status == "active" else "status-inactive"
        self.status_container.mount(Static(f"Status: {status}", classes=status_class))
        
        # Optionally fetch recent service logs
        self.update_service_logs()
    
    def update_service_logs(self):
        """Update the service logs display."""
        try:
            import subprocess
            # Get last 5 lines of service journal
            result = subprocess.run(
                ['journalctl', '-u', COYOTE_SERVICE_NAME, '-n', '5', '--no-pager'], 
                capture_output=True, 
                text=True
            )
            logs = result.stdout.strip()
            
            self.output_container.remove_children()
            if not logs:
                self.output_container.mount(Static("No recent logs available"))
            else:
                for line in logs.split('\n'):
                    self.output_container.mount(Static(line))
        except Exception as e:
            self.output_container.remove_children()
            self.output_container.mount(Static(f"Error fetching logs: {str(e)}"))

    def on_button_pressed(self, event):
        """Handle button press events."""
        button_id = event.button.id
        
        if button_id == "start-service":
            start_service(COYOTE_SERVICE_NAME)
            self.update_service_status()
        
        elif button_id == "stop-service":
            stop_service(COYOTE_SERVICE_NAME)
            self.update_service_status()
        
        elif button_id == "restart-service":
            restart_service(COYOTE_SERVICE_NAME)
            self.update_service_status()
        
        elif button_id == "refresh-status":
            self.update_service_status()