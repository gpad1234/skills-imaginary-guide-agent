#!/usr/bin/env python3
"""
audit_logger.py

Comprehensive audit logging system for OSQuery MCP server operations.
Tracks all tool executions, security events, and system access patterns.

Features:
- Structured logging with JSON format
- Security event classification
- Rate limiting integration
- Compliance reporting
"""

import json
import logging
import time
import hashlib
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import threading
from contextlib import contextmanager


class EventType(Enum):
    TOOL_EXECUTION = "tool_execution"
    SECURITY_VIOLATION = "security_violation"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    SYSTEM_EVENT = "system_event"
    ERROR = "error"


class Severity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AuditEvent:
    event_id: str
    timestamp: datetime
    event_type: EventType
    severity: Severity
    user_id: Optional[str]
    session_id: Optional[str]
    tool_name: Optional[str]
    parameters: Dict[str, Any]
    result_hash: Optional[str]
    execution_time_ms: float
    source_ip: Optional[str]
    user_agent: Optional[str]
    error_message: Optional[str]
    additional_data: Dict[str, Any]


class AuditLogger:
    """Enterprise-grade audit logging system"""
    
    def __init__(self, log_dir: str = "logs", max_log_size_mb: int = 100):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        self.max_log_size = max_log_size_mb * 1024 * 1024
        self._setup_logging()
        self._event_buffer = []
        self._buffer_lock = threading.Lock()
        self._session_data = {}
        
    def _setup_logging(self):
        """Setup structured logging"""
        self.logger = logging.getLogger("audit")
        self.logger.setLevel(logging.INFO)
        
        # Remove existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # File handler for audit logs
        audit_file = self.log_dir / "audit.jsonl"
        file_handler = logging.FileHandler(audit_file)
        file_handler.setLevel(logging.INFO)
        
        # Security events handler
        security_file = self.log_dir / "security.jsonl"
        security_handler = logging.FileHandler(security_file)
        security_handler.setLevel(logging.WARNING)
        
        # Console handler for development
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        
        # JSON formatter
        formatter = logging.Formatter('%(message)s')
        file_handler.setFormatter(formatter)
        security_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.security_logger = logging.getLogger("security")
        self.security_logger.addHandler(security_handler)
        self.security_logger.addHandler(console_handler)
    
    def _generate_event_id(self) -> str:
        """Generate unique event ID"""
        return str(uuid.uuid4())
    
    def _hash_result(self, result: Any) -> str:
        """Generate hash of result data for integrity checking"""
        result_str = json.dumps(result, sort_keys=True, default=str)
        return hashlib.sha256(result_str.encode()).hexdigest()[:16]
    
    def create_session(self, user_id: str = None, source_ip: str = None, 
                      user_agent: str = None) -> str:
        """Create a new audit session"""
        session_id = str(uuid.uuid4())
        self._session_data[session_id] = {
            "user_id": user_id,
            "source_ip": source_ip,
            "user_agent": user_agent,
            "created_at": datetime.now(timezone.utc),
            "tool_count": 0,
            "last_activity": datetime.now(timezone.utc)
        }
        
        self.log_event(
            event_type=EventType.SYSTEM_EVENT,
            severity=Severity.LOW,
            session_id=session_id,
            additional_data={"action": "session_created"}
        )
        
        return session_id
    
    def log_event(self, event_type: EventType, severity: Severity,
                  session_id: str = None, user_id: str = None,
                  tool_name: str = None, parameters: Dict[str, Any] = None,
                  result: Any = None, execution_time_ms: float = 0,
                  error_message: str = None, additional_data: Dict[str, Any] = None):
        """Log an audit event"""
        
        # Get session data if available
        session_info = self._session_data.get(session_id, {})
        
        # Create event
        event = AuditEvent(
            event_id=self._generate_event_id(),
            timestamp=datetime.now(timezone.utc),
            event_type=event_type,
            severity=severity,
            user_id=user_id or session_info.get("user_id"),
            session_id=session_id,
            tool_name=tool_name,
            parameters=parameters or {},
            result_hash=self._hash_result(result) if result else None,
            execution_time_ms=execution_time_ms,
            source_ip=session_info.get("source_ip"),
            user_agent=session_info.get("user_agent"),
            error_message=error_message,
            additional_data=additional_data or {}
        )
        
        # Update session data
        if session_id and session_id in self._session_data:
            self._session_data[session_id]["last_activity"] = event.timestamp
            if tool_name:
                self._session_data[session_id]["tool_count"] += 1
        
        # Convert to JSON
        event_json = json.dumps(asdict(event), default=str, ensure_ascii=False)
        
        # Log to appropriate logger
        if severity in [Severity.HIGH, Severity.CRITICAL] or event_type == EventType.SECURITY_VIOLATION:
            self.security_logger.warning(event_json)
        else:
            self.logger.info(event_json)
        
        # Buffer for real-time analysis
        with self._buffer_lock:
            self._event_buffer.append(event)
            if len(self._event_buffer) > 1000:  # Keep last 1000 events
                self._event_buffer = self._event_buffer[-1000:]
    
    @contextmanager
    def tool_execution_context(self, tool_name: str, parameters: Dict[str, Any],
                              session_id: str = None):
        """Context manager for tracking tool execution"""
        start_time = time.time()
        result = None
        error = None
        
        try:
            yield
        except Exception as e:
            error = str(e)
            raise
        finally:
            execution_time = (time.time() - start_time) * 1000
            
            severity = Severity.LOW
            event_type = EventType.TOOL_EXECUTION
            
            if error:
                severity = Severity.MEDIUM
                event_type = EventType.ERROR
            elif execution_time > 30000:  # > 30 seconds
                severity = Severity.MEDIUM
                additional_data = {"slow_query": True}
            
            self.log_event(
                event_type=event_type,
                severity=severity,
                session_id=session_id,
                tool_name=tool_name,
                parameters=parameters,
                execution_time_ms=execution_time,
                error_message=error,
                additional_data={"slow_query": execution_time > 30000}
            )
    
    def log_security_violation(self, violation_type: str, details: str,
                             session_id: str = None, severity: Severity = Severity.HIGH):
        """Log security violation"""
        self.log_event(
            event_type=EventType.SECURITY_VIOLATION,
            severity=severity,
            session_id=session_id,
            additional_data={
                "violation_type": violation_type,
                "details": details
            }
        )
    
    def log_rate_limit_exceeded(self, limit_type: str, current_rate: int,
                                threshold: int, session_id: str = None):
        """Log rate limit exceeded event"""
        self.log_event(
            event_type=EventType.RATE_LIMIT_EXCEEDED,
            severity=Severity.MEDIUM,
            session_id=session_id,
            additional_data={
                "limit_type": limit_type,
                "current_rate": current_rate,
                "threshold": threshold
            }
        )

    def log_action(self, user_id: str, action: str, resource: str, result: str,
                   session_id: str = None, **kwargs):
        """Compatibility method for simple action logging"""
        event_type = EventType.TOOL_EXECUTION
        severity = Severity.LOW if result == "success" else Severity.MEDIUM
        
        self.log_event(
            event_type=event_type,
            severity=severity,
            user_id=user_id,
            session_id=session_id,
            tool_name=action,
            parameters={"resource": resource, **kwargs},
            additional_data={
                "result": result,
                "action": action,
                "resource": resource
            }
        )

    def get_recent_events(self, count: int = 100, 
                         event_type: EventType = None) -> List[AuditEvent]:
        """Get recent events from buffer"""
        with self._buffer_lock:
            events = self._event_buffer.copy()
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        return sorted(events, key=lambda x: x.timestamp, reverse=True)[:count]
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get summary of session activity"""
        session = self._session_data.get(session_id)
        if not session:
            return {"error": "Session not found"}
        
        # Get events for this session
        session_events = [e for e in self._event_buffer if e.session_id == session_id]
        
        tools_used = list(set(e.tool_name for e in session_events if e.tool_name))
        errors = [e for e in session_events if e.event_type == EventType.ERROR]
        
        return {
            "session_id": session_id,
            "user_id": session.get("user_id"),
            "created_at": session["created_at"],
            "last_activity": session["last_activity"],
            "tool_count": session["tool_count"],
            "tools_used": tools_used,
            "error_count": len(errors),
            "total_events": len(session_events)
        }
    
    def generate_compliance_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate compliance report for date range"""
        # This would typically read from log files for a full report
        # Here we'll use buffer data for demonstration
        
        relevant_events = [
            e for e in self._event_buffer
            if start_date <= e.timestamp <= end_date
        ]
        
        tool_usage = {}
        for event in relevant_events:
            if event.tool_name:
                tool_usage[event.tool_name] = tool_usage.get(event.tool_name, 0) + 1
        
        security_events = [e for e in relevant_events if e.event_type == EventType.SECURITY_VIOLATION]
        error_events = [e for e in relevant_events if e.event_type == EventType.ERROR]
        
        return {
            "report_period": {
                "start": start_date,
                "end": end_date
            },
            "summary": {
                "total_events": len(relevant_events),
                "tool_executions": len([e for e in relevant_events if e.event_type == EventType.TOOL_EXECUTION]),
                "security_violations": len(security_events),
                "errors": len(error_events),
                "unique_users": len(set(e.user_id for e in relevant_events if e.user_id))
            },
            "tool_usage": tool_usage,
            "security_violations": [
                {
                    "timestamp": e.timestamp,
                    "severity": e.severity.value,
                    "details": e.additional_data
                }
                for e in security_events
            ],
            "top_errors": [
                {
                    "error": e.error_message,
                    "tool": e.tool_name,
                    "timestamp": e.timestamp
                }
                for e in error_events[:10]
            ]
        }


# Global audit logger instance
_audit_logger = None


def get_audit_logger() -> AuditLogger:
    """Get global audit logger instance"""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger


# Convenience functions
def log_tool_execution(tool_name: str, parameters: Dict[str, Any],
                      execution_time_ms: float, session_id: str = None,
                      result: Any = None, error: str = None):
    """Log tool execution"""
    logger = get_audit_logger()
    
    event_type = EventType.ERROR if error else EventType.TOOL_EXECUTION
    severity = Severity.MEDIUM if error else Severity.LOW
    
    logger.log_event(
        event_type=event_type,
        severity=severity,
        session_id=session_id,
        tool_name=tool_name,
        parameters=parameters,
        result=result,
        execution_time_ms=execution_time_ms,
        error_message=error
    )


def log_security_violation(violation_type: str, details: str, 
                          session_id: str = None):
    """Log security violation"""
    logger = get_audit_logger()
    logger.log_security_violation(violation_type, details, session_id)


def create_audit_session(user_id: str = None) -> str:
    """Create new audit session"""
    logger = get_audit_logger()
    return logger.create_session(user_id=user_id)


if __name__ == "__main__":
    # Demo usage
    logger = AuditLogger()
    
    # Create session
    session_id = logger.create_session(user_id="demo_user")
    
    # Log some events
    with logger.tool_execution_context("system_info", {}, session_id):
        time.sleep(0.1)  # Simulate execution
    
    logger.log_security_violation("unauthorized_query", "Attempted to access restricted table", session_id)
    
    # Get recent events
    recent = logger.get_recent_events(10)
    print("Recent events:")
    for event in recent:
        print(f"  {event.timestamp}: {event.event_type.value} - {event.tool_name}")
    
    # Session summary
    summary = logger.get_session_summary(session_id)
    print(f"\nSession summary: {json.dumps(summary, indent=2, default=str)}")
    
    # Compliance report
    from datetime import datetime, timedelta
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(hours=1)
    
    report = logger.generate_compliance_report(start_date, end_date)
    print(f"\nCompliance report: {json.dumps(report, indent=2, default=str)}")