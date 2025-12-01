#!/usr/bin/env python3
"""
security_policy.py

Comprehensive security policy engine for OSQuery MCP server.
Implements access control, query validation, and security monitoring.

Features:
- Role-based access control (RBAC)
- Query whitelisting/blacklisting
- SQL injection detection
- Data exfiltration prevention
- Compliance enforcement
"""

import re
import json
import hashlib
from typing import Dict, Any, List, Optional, Set, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class AccessLevel(Enum):
    NONE = "none"
    READ = "read"
    LIMITED = "limited"
    FULL = "full"
    ADMIN = "admin"


class PolicyViolationType(Enum):
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    FORBIDDEN_QUERY = "forbidden_query"
    SQL_INJECTION = "sql_injection"
    DATA_EXFILTRATION = "data_exfiltration"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    SUSPICIOUS_PATTERN = "suspicious_pattern"


@dataclass
class SecurityRole:
    name: str
    access_level: AccessLevel
    allowed_tools: Set[str] = field(default_factory=set)
    allowed_tables: Set[str] = field(default_factory=set)
    forbidden_tables: Set[str] = field(default_factory=set)
    max_query_complexity: int = 100
    max_result_rows: int = 1000
    can_use_custom_queries: bool = False
    query_patterns: List[str] = field(default_factory=list)  # Allowed regex patterns


@dataclass
class SecurityPolicy:
    name: str
    description: str
    roles: Dict[str, SecurityRole]
    global_forbidden_patterns: List[str]
    global_required_patterns: List[str]
    compliance_requirements: Dict[str, Any]


@dataclass
class PolicyViolation:
    violation_type: PolicyViolationType
    severity: str  # "low", "medium", "high", "critical"
    message: str
    context: Dict[str, Any]
    recommended_action: str


class SecurityPolicyEngine:
    """Advanced security policy engine"""
    
    def __init__(self, policy_file: str = None):
        self.policies: Dict[str, SecurityPolicy] = {}
        self.user_roles: Dict[str, str] = {}  # user_id -> role_name
        
        # Default security policy
        self._create_default_policy()
        
        # Load custom policy if provided
        if policy_file and Path(policy_file).exists():
            self.load_policy_file(policy_file)
    
    def _create_default_policy(self):
        """Create default security policy with common roles"""
        
        # Define roles
        guest_role = SecurityRole(
            name="guest",
            access_level=AccessLevel.READ,
            allowed_tools={"system_info"},
            allowed_tables={"system_info", "os_version", "uptime"},
            max_query_complexity=10,
            max_result_rows=50,
            can_use_custom_queries=False
        )
        
        user_role = SecurityRole(
            name="user",
            access_level=AccessLevel.LIMITED,
            allowed_tools={"system_info", "processes", "users", "network_interfaces"},
            allowed_tables={
                "system_info", "os_version", "uptime", "processes", "users",
                "interface_details", "listening_ports"
            },
            forbidden_tables={"file", "hash", "yara"},
            max_query_complexity=50,
            max_result_rows=500,
            can_use_custom_queries=True,
            query_patterns=[
                r"SELECT .+ FROM (system_info|processes|users|interface_details)",
                r"SELECT .+ FROM processes WHERE .+ LIMIT \d+"
            ]
        )
        
        analyst_role = SecurityRole(
            name="analyst", 
            access_level=AccessLevel.FULL,
            allowed_tools={"system_info", "processes", "users", "network_interfaces", 
                         "network_connections", "custom_query"},
            allowed_tables={
                "system_info", "processes", "users", "interface_details",
                "listening_ports", "process_open_sockets", "file", "hash"
            },
            forbidden_tables={"yara", "kernel_modules"},
            max_query_complexity=200,
            max_result_rows=2000,
            can_use_custom_queries=True
        )
        
        admin_role = SecurityRole(
            name="admin",
            access_level=AccessLevel.ADMIN,
            allowed_tools=set(),  # Empty = all tools allowed
            allowed_tables=set(),  # Empty = all tables allowed 
            forbidden_tables=set(),
            max_query_complexity=1000,
            max_result_rows=10000,
            can_use_custom_queries=True
        )
        
        # Create default policy
        default_policy = SecurityPolicy(
            name="default",
            description="Default security policy with role-based access control",
            roles={
                "guest": guest_role,
                "user": user_role,
                "analyst": analyst_role,
                "admin": admin_role
            },
            global_forbidden_patterns=[
                # SQL injection patterns
                r"(\b(union|select|insert|update|delete|drop|create|alter)\b.*\b(union|select|insert|update|delete|drop|create|alter)\b)",
                r"(\b(or|and)\b\s*\d+\s*[=<>])",
                r"['\"];?\s*(\b(or|and|union|select)\b)",
                # File system access
                r"\bfile\b.*\bpath\b.*['\"]\/",
                # System manipulation
                r"\b(shutdown|reboot|kill|killall)\b",
                # Credential harvesting
                r"\b(password|passwd|shadow|credential)\b",
            ],
            global_required_patterns=[
                # Require LIMIT clause for potentially large tables
                r"SELECT .* FROM (processes|file|hash) .* LIMIT \d+"
            ],
            compliance_requirements={
                "audit_all_queries": True,
                "max_session_duration_hours": 8,
                "require_user_identification": True,
                "log_data_access": True
            }
        )
        
        self.policies["default"] = default_policy
    
    def assign_role(self, user_id: str, role_name: str, policy_name: str = "default"):
        """Assign role to user"""
        policy = self.policies.get(policy_name)
        if not policy:
            raise ValueError(f"Policy '{policy_name}' not found")
        
        if role_name not in policy.roles:
            raise ValueError(f"Role '{role_name}' not found in policy '{policy_name}'")
        
        self.user_roles[user_id] = f"{policy_name}:{role_name}"
    
    def get_user_role(self, user_id: str) -> Optional[SecurityRole]:
        """Get user's security role"""
        if user_id not in self.user_roles:
            return None
        
        policy_role = self.user_roles[user_id]
        policy_name, role_name = policy_role.split(":", 1)
        
        policy = self.policies.get(policy_name)
        if not policy:
            return None
        
        return policy.roles.get(role_name)
    
    def validate_tool_access(self, user_id: str, tool_name: str) -> List[PolicyViolation]:
        """Validate if user can access a specific tool"""
        violations = []
        role = self.get_user_role(user_id)
        
        if not role:
            violations.append(PolicyViolation(
                violation_type=PolicyViolationType.UNAUTHORIZED_ACCESS,
                severity="high",
                message=f"User {user_id} has no assigned role",
                context={"user_id": user_id, "tool_name": tool_name},
                recommended_action="Assign appropriate role to user"
            ))
            return violations
        
        # Check tool access
        if role.allowed_tools and tool_name not in role.allowed_tools:
            violations.append(PolicyViolation(
                violation_type=PolicyViolationType.UNAUTHORIZED_ACCESS,
                severity="medium",
                message=f"Tool '{tool_name}' not allowed for role '{role.name}'",
                context={"user_id": user_id, "tool_name": tool_name, "role": role.name},
                recommended_action="Use an allowed tool or request role upgrade"
            ))
        
        return violations
    
    def validate_custom_query(self, user_id: str, sql_query: str) -> List[PolicyViolation]:
        """Validate custom SQL query against security policies"""
        violations = []
        role = self.get_user_role(user_id)
        
        if not role:
            violations.append(PolicyViolation(
                violation_type=PolicyViolationType.UNAUTHORIZED_ACCESS,
                severity="high",
                message=f"User {user_id} has no assigned role",
                context={"user_id": user_id, "query": sql_query},
                recommended_action="Assign appropriate role to user"
            ))
            return violations
        
        # Check if custom queries are allowed
        if not role.can_use_custom_queries:
            violations.append(PolicyViolation(
                violation_type=PolicyViolationType.UNAUTHORIZED_ACCESS,
                severity="high",
                message=f"Custom queries not allowed for role '{role.name}'",
                context={"user_id": user_id, "role": role.name},
                recommended_action="Use predefined tools instead of custom queries"
            ))
            return violations
        
        # Normalize query for analysis
        normalized_query = sql_query.lower().strip()
        
        # Check global forbidden patterns
        policy = self._get_user_policy(user_id)
        if policy:
            for pattern in policy.global_forbidden_patterns:
                if re.search(pattern, normalized_query, re.IGNORECASE):
                    violations.append(PolicyViolation(
                        violation_type=PolicyViolationType.FORBIDDEN_QUERY,
                        severity="critical",
                        message=f"Query matches forbidden pattern: {pattern}",
                        context={"user_id": user_id, "query": sql_query, "pattern": pattern},
                        recommended_action="Modify query to avoid forbidden patterns"
                    ))
        
        # Check SQL injection patterns
        sql_injection_violations = self._detect_sql_injection(sql_query)
        violations.extend(sql_injection_violations)
        
        # Check table access
        table_violations = self._validate_table_access(user_id, sql_query)
        violations.extend(table_violations)
        
        # Check query complexity
        complexity_violations = self._validate_query_complexity(user_id, sql_query)
        violations.extend(complexity_violations)
        
        # Check result size limits
        limit_violations = self._validate_result_limits(user_id, sql_query)
        violations.extend(limit_violations)
        
        return violations
    
    def _get_user_policy(self, user_id: str) -> Optional[SecurityPolicy]:
        """Get the policy for a user"""
        if user_id not in self.user_roles:
            return None
        
        policy_name = self.user_roles[user_id].split(":", 1)[0]
        return self.policies.get(policy_name)
    
    def _detect_sql_injection(self, sql_query: str) -> List[PolicyViolation]:
        """Detect potential SQL injection attempts"""
        violations = []
        normalized = sql_query.lower().strip()
        
        # Common SQL injection patterns
        injection_patterns = [
            (r"['\"];?\s*(or|and)\s*['\"]?\w+['\"]?\s*[=<>]", "Boolean-based injection"),
            (r"union\s+(all\s+)?select", "Union-based injection"),
            (r";\s*(drop|delete|insert|update|create)", "Stacked queries"),
            (r"^\s*(drop|delete|insert|update|create|alter)\s+", "DDL/DML injection"),
            (r"(\/\*|\*\/|--|\#)", "Comment injection"),
            (r"(benchmark|sleep|waitfor|delay)\s*\(", "Time-based injection"),
            (r"(load_file|into\s+outfile|into\s+dumpfile)", "File operation injection"),
            (r"(exec|execute|sp_|xp_)", "Stored procedure injection"),
            (r"where\s+path\s*=\s*['\"][^'\"]*/(etc|usr|var|home)", "File system access injection"),
        ]
        
        for pattern, description in injection_patterns:
            if re.search(pattern, normalized):
                violations.append(PolicyViolation(
                    violation_type=PolicyViolationType.SQL_INJECTION,
                    severity="critical",
                    message=f"Potential SQL injection detected: {description}",
                    context={"query": sql_query, "pattern": pattern},
                    recommended_action="Sanitize query and use parameterized statements"
                ))
        
        return violations
    
    def _validate_table_access(self, user_id: str, sql_query: str) -> List[PolicyViolation]:
        """Validate table access in SQL query"""
        violations = []
        role = self.get_user_role(user_id)
        
        if not role:
            return violations
        
        # Extract table names from query (simplified)
        table_pattern = r"\bFROM\s+(\w+)"
        join_pattern = r"\bJOIN\s+(\w+)"
        
        tables = set()
        tables.update(re.findall(table_pattern, sql_query, re.IGNORECASE))
        tables.update(re.findall(join_pattern, sql_query, re.IGNORECASE))
        
        for table in tables:
            # Check forbidden tables
            if role.forbidden_tables and table in role.forbidden_tables:
                violations.append(PolicyViolation(
                    violation_type=PolicyViolationType.UNAUTHORIZED_ACCESS,
                    severity="high",
                    message=f"Access to table '{table}' is forbidden for role '{role.name}'",
                    context={"user_id": user_id, "table": table, "role": role.name},
                    recommended_action="Remove forbidden table from query"
                ))
            
            # Check allowed tables (if whitelist is defined)
            if role.allowed_tables and table not in role.allowed_tables:
                violations.append(PolicyViolation(
                    violation_type=PolicyViolationType.UNAUTHORIZED_ACCESS,
                    severity="medium",
                    message=f"Access to table '{table}' not allowed for role '{role.name}'",
                    context={"user_id": user_id, "table": table, "role": role.name},
                    recommended_action="Use only allowed tables or request permission"
                ))
        
        return violations
    
    def _validate_query_complexity(self, user_id: str, sql_query: str) -> List[PolicyViolation]:
        """Validate query complexity"""
        violations = []
        role = self.get_user_role(user_id)
        
        if not role:
            return violations
        
        # Simple complexity calculation
        complexity = 1
        normalized = sql_query.lower()
        
        # Add complexity for various SQL features
        complexity += len(re.findall(r'\bjoin\b', normalized)) * 5
        complexity += len(re.findall(r'\bgroup\s+by\b', normalized)) * 3
        complexity += len(re.findall(r'\border\s+by\b', normalized)) * 2
        complexity += len(re.findall(r'\bwhere\b', normalized)) * 2
        complexity += len(re.findall(r'\b(and|or)\b', normalized))
        
        # Penalize wildcard selects
        if re.search(r'SELECT\s+\*', sql_query, re.IGNORECASE):
            complexity += 5
        
        if complexity > role.max_query_complexity:
            violations.append(PolicyViolation(
                violation_type=PolicyViolationType.SUSPICIOUS_PATTERN,
                severity="medium",
                message=f"Query complexity ({complexity}) exceeds limit ({role.max_query_complexity})",
                context={"user_id": user_id, "complexity": complexity, "limit": role.max_query_complexity},
                recommended_action="Simplify query or request higher complexity limit"
            ))
        
        return violations
    
    def _validate_result_limits(self, user_id: str, sql_query: str) -> List[PolicyViolation]:
        """Validate result size limits"""
        violations = []
        role = self.get_user_role(user_id)
        
        if not role:
            return violations
        
        # Check for LIMIT clause
        limit_match = re.search(r'\bLIMIT\s+(\d+)', sql_query, re.IGNORECASE)
        
        if limit_match:
            limit_value = int(limit_match.group(1))
            if limit_value > role.max_result_rows:
                violations.append(PolicyViolation(
                    violation_type=PolicyViolationType.DATA_EXFILTRATION,
                    severity="medium",
                    message=f"LIMIT ({limit_value}) exceeds maximum ({role.max_result_rows})",
                    context={"user_id": user_id, "limit": limit_value, "max_limit": role.max_result_rows},
                    recommended_action=f"Reduce LIMIT to {role.max_result_rows} or less"
                ))
        else:
            # No LIMIT clause - might return too much data
            if self._query_potentially_large_table(sql_query):
                violations.append(PolicyViolation(
                    violation_type=PolicyViolationType.DATA_EXFILTRATION,
                    severity="medium",
                    message="Query on potentially large table without LIMIT clause",
                    context={"user_id": user_id, "query": sql_query},
                    recommended_action=f"Add LIMIT clause (max {role.max_result_rows})"
                ))
        
        return violations
    
    def _query_potentially_large_table(self, sql_query: str) -> bool:
        """Check if query targets potentially large tables"""
        large_tables = {"processes", "file", "hash", "process_open_sockets", "listening_ports"}
        
        for table in large_tables:
            if re.search(rf'\bFROM\s+{table}\b', sql_query, re.IGNORECASE):
                return True
        
        return False
    
    def validate_request(self, user_id: str, tool_name: str, 
                        parameters: Dict[str, Any] = None) -> List[PolicyViolation]:
        """Comprehensive request validation"""
        violations = []
        parameters = parameters or {}
        
        # Validate tool access
        tool_violations = self.validate_tool_access(user_id, tool_name)
        violations.extend(tool_violations)
        
        # Validate custom query if applicable
        if tool_name == "custom_query" and "sql" in parameters:
            query_violations = self.validate_custom_query(user_id, parameters["sql"])
            violations.extend(query_violations)
        
        return violations
    
    def get_user_permissions(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive permissions for a user"""
        role = self.get_user_role(user_id)
        
        if not role:
            return {
                "user_id": user_id,
                "role": None,
                "access_level": AccessLevel.NONE.value,
                "permissions": {}
            }
        
        return {
            "user_id": user_id,
            "role": role.name,
            "access_level": role.access_level.value,
            "permissions": {
                "allowed_tools": list(role.allowed_tools),
                "allowed_tables": list(role.allowed_tables),
                "forbidden_tables": list(role.forbidden_tables),
                "can_use_custom_queries": role.can_use_custom_queries,
                "max_query_complexity": role.max_query_complexity,
                "max_result_rows": role.max_result_rows
            }
        }
    
    def load_policy_file(self, filepath: str):
        """Load security policy from JSON file"""
        with open(filepath, 'r') as f:
            policy_data = json.load(f)
        
        # Parse and validate policy
        # Implementation would parse JSON into SecurityPolicy objects
        pass
    
    def save_policy_file(self, policy_name: str, filepath: str):
        """Save security policy to JSON file"""
        policy = self.policies.get(policy_name)
        if not policy:
            raise ValueError(f"Policy '{policy_name}' not found")
        
        # Convert to JSON
        # Implementation would serialize SecurityPolicy objects
        pass


# Global security policy engine
_security_policy = None


def get_security_policy() -> SecurityPolicyEngine:
    """Get global security policy engine"""
    global _security_policy
    if _security_policy is None:
        _security_policy = SecurityPolicyEngine()
    return _security_policy


# Convenience functions
def validate_user_request(user_id: str, tool_name: str, 
                         parameters: Dict[str, Any] = None) -> List[PolicyViolation]:
    """Validate user request against security policy"""
    policy_engine = get_security_policy()
    return policy_engine.validate_request(user_id, tool_name, parameters)


def assign_user_role(user_id: str, role_name: str):
    """Assign role to user"""
    policy_engine = get_security_policy()
    policy_engine.assign_role(user_id, role_name)


if __name__ == "__main__":
    # Demo usage
    engine = SecurityPolicyEngine()
    
    # Assign roles to users
    engine.assign_role("user1", "guest")
    engine.assign_role("user2", "user") 
    engine.assign_role("user3", "analyst")
    
    # Test validations
    test_cases = [
        ("user1", "system_info", {}),
        ("user1", "processes", {}),  # Should fail - not allowed
        ("user2", "custom_query", {"sql": "SELECT * FROM processes LIMIT 10"}),
        ("user3", "custom_query", {"sql": "SELECT * FROM file WHERE path LIKE '/etc/%'"}),
        ("user2", "custom_query", {"sql": "DROP TABLE processes"}),  # Should fail - injection
    ]
    
    print("Security Policy Validation Tests:")
    print("=" * 50)
    
    for user_id, tool_name, params in test_cases:
        violations = engine.validate_request(user_id, tool_name, params)
        
        print(f"\nUser: {user_id}, Tool: {tool_name}")
        if params:
            print(f"Params: {params}")
        
        if violations:
            print("❌ VIOLATIONS:")
            for violation in violations:
                print(f"  - {violation.violation_type.value}: {violation.message}")
        else:
            print("✅ ALLOWED")
    
    print(f"\n\nUser Permissions:")
    print("=" * 30)
    for user_id in ["user1", "user2", "user3"]:
        perms = engine.get_user_permissions(user_id)
        print(f"\n{user_id}: {perms['role']} ({perms['access_level']})")
        if perms['permissions']:
            print(f"  Tools: {perms['permissions']['allowed_tools']}")
            print(f"  Custom queries: {perms['permissions']['can_use_custom_queries']}")