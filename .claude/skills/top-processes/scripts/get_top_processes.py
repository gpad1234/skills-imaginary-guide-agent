#!/usr/bin/env python
"""
Top Processes Skill

Query and return the top processes by memory or CPU usage.
Useful for identifying resource-heavy applications and potential issues.
"""

import json
import sys
import os
import argparse
import psutil


def get_top_processes(limit=10):
    """
    Get top processes by memory usage.
    
    Args:
        limit (int): Number of processes to return
        
    Returns:
        dict: Top processes with their resource usage
    """
    try:
        processes = []
        
        # Iterate through all processes
        for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'cpu_percent', 'username']):
            try:
                pinfo = proc.info
                pinfo['memory_mb'] = proc.memory_info().rss / (1024 * 1024)
                processes.append(pinfo)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # Sort by memory usage
        processes.sort(key=lambda x: x.get('memory_mb', 0), reverse=True)
        
        # Get top N processes
        top_procs = processes[:limit]
        
        if not top_procs:
            return {
                "status": "error",
                "message": "No process data available"
            }
        
        # Format for better readability
        formatted_processes = []
        for proc in top_procs:
            formatted_processes.append({
                "name": proc.get("name", "N/A"),
                "pid": proc.get("pid", "N/A"),
                "memory_mb": round(proc.get("memory_mb", 0), 2),
                "memory_percent": round(proc.get("memory_percent", 0), 2),
                "cpu_percent": round(proc.get("cpu_percent", 0), 2),
                "username": proc.get("username", "N/A")
            })
        
        return {
            "status": "success",
            "count": len(formatted_processes),
            "total_memory_mb": round(sum(p['memory_mb'] for p in formatted_processes), 2),
            "processes": formatted_processes
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


def main():
    """Main entry point for the skill."""
    parser = argparse.ArgumentParser(description='Get top processes by resource usage')
    parser.add_argument('--limit', type=int, default=10, 
                       help='Number of processes to return (default: 10)')
    args = parser.parse_args()
    
    result = get_top_processes(limit=args.limit)
    
    # Output as clean JSON
    print(json.dumps(result, indent=2))
    
    # Exit with appropriate code
    if result.get('status') == 'error':
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
