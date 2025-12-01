"""
OSQuery tools for system information gathering.
Provides functions to query system state using osquery.
"""

import json
import subprocess
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class OSQueryClient:
    """Client for executing osquery queries."""
    
    def __init__(self):
        """Initialize OSQuery client."""
        self.osqueryi_path = self._find_osqueryi()
    
    def _find_osqueryi(self) -> str:
        """Find osqueryi executable path."""
        try:
            result = subprocess.run(
                ["which", "osqueryi"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception as e:
            logger.warning(f"Could not find osqueryi: {e}")
        
        # Common paths
        common_paths = [
            "/usr/local/bin/osqueryi",
            "/opt/osquery/bin/osqueryi",
            "/usr/bin/osqueryi"
        ]
        
        for path in common_paths:
            try:
                result = subprocess.run([path, "--version"], capture_output=True, timeout=2)
                if result.returncode == 0:
                    return path
            except:
                pass
        
        return "osqueryi"  # Fallback to PATH lookup
    
    def query(self, sql: str) -> Dict[str, Any]:
        """
        Execute an osquery SQL query.
        
        Args:
            sql: SQL query string for osquery
            
        Returns:
            Dictionary with results or error information
        """
        try:
            result = subprocess.run(
                [self.osqueryi_path, "--json", sql],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and result.stdout:
                try:
                    return {
                        "success": True,
                        "data": json.loads(result.stdout)
                    }
                except json.JSONDecodeError as e:
                    return {
                        "success": False,
                        "error": f"Failed to parse JSON output: {e}",
                        "raw_output": result.stdout
                    }
            elif result.stderr:
                return {
                    "success": False,
                    "error": result.stderr
                }
            else:
                return {
                    "success": True,
                    "data": []
                }
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Query timed out after 30 seconds"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Query execution failed: {str(e)}"
            }


# Global client instance
_client: Optional[OSQueryClient] = None


def get_client() -> OSQueryClient:
    """Get or create the global OSQuery client."""
    global _client
    if _client is None:
        _client = OSQueryClient()
    return _client


def query_system_info() -> Dict[str, Any]:
    """Get general system information."""
    client = get_client()
    return client.query("SELECT * FROM system_info;")


def query_processes(limit: int = 10) -> Dict[str, Any]:
    """Get running processes."""
    client = get_client()
    return client.query(f"SELECT pid, name, uid, resident_size FROM processes ORDER BY resident_size DESC LIMIT {limit};")


def query_users() -> Dict[str, Any]:
    """Get system users."""
    client = get_client()
    return client.query("SELECT * FROM users;")


def query_network_interfaces() -> Dict[str, Any]:
    """Get network interfaces."""
    client = get_client()
    return client.query("SELECT interface, mac, mtu, metric FROM interface_details;")


def query_network_connections(limit: int = 20) -> Dict[str, Any]:
    """Get network connections."""
    client = get_client()
    return client.query(f"SELECT protocol, local_address, local_port, remote_address, remote_port, state FROM process_open_sockets LIMIT {limit};")


def query_open_files(pid: Optional[int] = None) -> Dict[str, Any]:
    """Get open files."""
    client = get_client()
    if pid:
        return client.query(f"SELECT pid, path FROM process_open_files WHERE pid = {pid};")
    else:
        return client.query("SELECT pid, path FROM process_open_files LIMIT 50;")


def query_installed_packages() -> Dict[str, Any]:
    """Get installed packages/applications."""
    client = get_client()
    # Works on macOS, Linux may differ
    return client.query("SELECT name, version FROM programs LIMIT 50;")


def query_disk_usage() -> Dict[str, Any]:
    """Get disk usage information."""
    client = get_client()
    return client.query("SELECT path, blocks_size, blocks_available FROM mounts;")


def query_running_services() -> Dict[str, Any]:
    """Get running services."""
    client = get_client()
    # macOS specific
    return client.query("SELECT name, state FROM launchd LIMIT 50;")


def custom_query(sql: str) -> Dict[str, Any]:
    """Execute a custom osquery SQL query."""
    client = get_client()
    return client.query(sql)
