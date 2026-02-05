#!/usr/bin/env python
"""
System Health Check Skill

Queries comprehensive system health metrics using Python's standard libraries.
Returns structured JSON with system status, resource usage, and running processes.
"""

import json
import sys
import os
import platform
import psutil

def get_system_health():
    """
    Gather comprehensive system health metrics.
    
    Returns:
        dict: System health data including OS info, memory, CPU, processes, etc.
    """
    health_data = {}
    
    try:
        # Get system information
        health_data['hostname'] = platform.node()
        health_data['os_version'] = f"{platform.system()} {platform.release()}"
        health_data['cpu_count'] = psutil.cpu_count()
        health_data['cpu_percent'] = psutil.cpu_percent(interval=1)
        
        # Get memory usage
        mem = psutil.virtual_memory()
        health_data['memory'] = {
            'total_gb': round(mem.total / (1024**3), 2),
            'available_gb': round(mem.available / (1024**3), 2),
            'used_gb': round(mem.used / (1024**3), 2),
            'percent': mem.percent
        }
        
        # Get disk usage
        disk = psutil.disk_usage('/')
        health_data['disk'] = {
            'total_gb': round(disk.total / (1024**3), 2),
            'used_gb': round(disk.used / (1024**3), 2),
            'free_gb': round(disk.free / (1024**3), 2),
            'percent': disk.percent
        }
        
        # Get top processes by memory
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
            try:
                info = proc.info
                if info.get('memory_percent') is not None:
                    processes.append(info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        processes.sort(key=lambda x: x.get('memory_percent', 0) or 0, reverse=True)
        health_data['top_processes'] = [
            {
                'name': p['name'],
                'pid': p['pid'],
                'memory_percent': round(p.get('memory_percent', 0), 2)
            }
            for p in processes[:10]
        ]
        
        # Get network info
        net_if = psutil.net_if_stats()
        health_data['network_interfaces'] = len(net_if)
        
        # Get boot time / uptime
        boot_time = psutil.boot_time()
        health_data['uptime_hours'] = round((psutil.time.time() - boot_time) / 3600, 2)
        
        health_data['status'] = 'healthy'
        
    except Exception as e:
        health_data['status'] = 'error'
        health_data['error'] = str(e)
    
    return health_data


def main():
    """Main entry point for the skill."""
    health_data = get_system_health()
    
    # Output as clean JSON
    print(json.dumps(health_data, indent=2))
    
    # Exit with appropriate code
    if health_data.get('status') == 'error':
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
