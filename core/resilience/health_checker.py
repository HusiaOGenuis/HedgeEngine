"""
Production-Grade Health Check System
Version: 1.0.0
Date: 2026-06-30
Status: PRODUCTION - HEALTH MONITORING

Provides:
- Component health checks
- Dependency checks
- Performance monitoring
- Alert generation
- Status reporting
"""

import logging
import time
import threading
import json
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path

# ============================================================================
# HEALTH ENUMS
# ============================================================================

class HealthStatus(Enum):
    """Health status levels"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

# ============================================================================
# HEALTH DATA STRUCTURES
# ============================================================================

@dataclass
class ComponentHealth:
    """Health status of a component"""
    component_name: str
    status: HealthStatus
    message: str
    last_check: datetime
    details: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "component": self.component_name,
            "status": self.status.value,
            "message": self.message,
            "last_check": self.last_check.isoformat(),
            "details": self.details,
            "dependencies": self.dependencies
        }

@dataclass
class HealthReport:
    """Complete health report"""
    timestamp: datetime
    overall_status: HealthStatus
    components: List[ComponentHealth]
    alerts: List[Dict]
    uptime_seconds: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "overall_status": self.overall_status.value,
            "components": [c.to_dict() for c in self.components],
            "alerts": self.alerts,
            "uptime_seconds": self.uptime_seconds,
            "metadata": self.metadata
        }

# ============================================================================
# HEALTH CHECKER
# ============================================================================

class HealthChecker:
    """
    Production-grade health check system
    
    Features:
    - Registered health checks
    - Automated monitoring
    - Alert generation
    - Status reporting
    - Dependency tracking
    """
    
    def __init__(self, 
                 check_interval: int = 30,  # seconds
                 alert_webhook: Optional[str] = None,
                 alert_email: Optional[str] = None):
        
        self.check_interval = check_interval
        self.alert_webhook = alert_webhook
        self.alert_email = alert_email
        
        # Registered checks
        self.checks: Dict[str, Callable[[], ComponentHealth]] = {}
        
        # Current status
        self.component_status: Dict[str, ComponentHealth] = {}
        self.overall_status: HealthStatus = HealthStatus.UNKNOWN
        
        # Alerts
        self.alerts: List[Dict] = []
        self.alert_thresholds = {
            AlertLevel.ERROR: 1,      # 1 error triggers alert
            AlertLevel.CRITICAL: 1,   # 1 critical triggers alert
            AlertLevel.WARNING: 3,    # 3 warnings trigger alert
        }
        
        # Statistics
        self.check_count = 0
        self.failure_count = 0
        self.start_time = datetime.now()
        self.last_check_time: Optional[datetime] = None
        
        # Background checker
        self.is_running = True
        self._start_background_checker()
        
        logging.info(f"HealthChecker initialized (Interval: {check_interval}s)")
    
    # ============================================================
    # CHECK REGISTRATION
    # ============================================================
    
    def register_check(self, 
                       name: str, 
                       check_func: Callable[[], ComponentHealth],
                       dependencies: List[str] = None):
        """Register a health check"""
        self.checks[name] = check_func
        logging.debug(f"Registered health check: {name}")
    
    def register_standard_checks(self):
        """Register standard system checks"""
        # System check
        self.register_check("system", self._check_system)
        
        # Disk check
        self.register_check("disk", self._check_disk)
        
        # Memory check
        self.register_check("memory", self._check_memory)
        
        # Process check
        self.register_check("process", self._check_process)
        
        logging.info("Registered standard health checks")
    
    # ============================================================
    # STANDARD CHECKS
    # ============================================================
    
    def _check_system(self) -> ComponentHealth:
        """Check system health"""
        try:
            import psutil
            load_avg = psutil.getloadavg()
            status = HealthStatus.HEALTHY
            message = "System running normally"
            
            if load_avg[0] > 2.0:
                status = HealthStatus.DEGRADED
                message = f"High load average: {load_avg[0]:.2f}"
            elif load_avg[0] > 4.0:
                status = HealthStatus.UNHEALTHY
                message = f"Critical load average: {load_avg[0]:.2f}"
            
            return ComponentHealth(
                component_name="system",
                status=status,
                message=message,
                last_check=datetime.now(),
                details={"load_avg": load_avg}
            )
        except Exception as e:
            return ComponentHealth(
                component_name="system",
                status=HealthStatus.UNHEALTHY,
                message=f"Failed to check system: {e}",
                last_check=datetime.now()
            )
    
    def _check_disk(self) -> ComponentHealth:
        """Check disk health"""
        try:
            import psutil
            disk = psutil.disk_usage('/')
            usage_percent = disk.percent
            
            status = HealthStatus.HEALTHY
            message = f"Disk usage: {usage_percent:.1f}%"
            
            if usage_percent > 85:
                status = HealthStatus.DEGRADED
                message = f"High disk usage: {usage_percent:.1f}%"
            elif usage_percent > 95:
                status = HealthStatus.UNHEALTHY
                message = f"Critical disk usage: {usage_percent:.1f}%"
            
            return ComponentHealth(
                component_name="disk",
                status=status,
                message=message,
                last_check=datetime.now(),
                details={"usage_percent": usage_percent}
            )
        except Exception as e:
            return ComponentHealth(
                component_name="disk",
                status=HealthStatus.UNHEALTHY,
                message=f"Failed to check disk: {e}",
                last_check=datetime.now()
            )
    
    def _check_memory(self) -> ComponentHealth:
        """Check memory health"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            usage_percent = memory.percent
            
            status = HealthStatus.HEALTHY
            message = f"Memory usage: {usage_percent:.1f}%"
            
            if usage_percent > 80:
                status = HealthStatus.DEGRADED
                message = f"High memory usage: {usage_percent:.1f}%"
            elif usage_percent > 90:
                status = HealthStatus.UNHEALTHY
                message = f"Critical memory usage: {usage_percent:.1f}%"
            
            return ComponentHealth(
                component_name="memory",
                status=status,
                message=message,
                last_check=datetime.now(),
                details={"usage_percent": usage_percent, "available_mb": memory.available / 1024 / 1024}
            )
        except Exception as e:
            return ComponentHealth(
                component_name="memory",
                status=HealthStatus.UNHEALTHY,
                message=f"Failed to check memory: {e}",
                last_check=datetime.now()
            )
    
    def _check_process(self) -> ComponentHealth:
        """Check process health"""
        try:
            import psutil
            process = psutil.Process()
            cpu_percent = process.cpu_percent(interval=0.1)
            memory_mb = process.memory_info().rss / 1024 / 1024
            
            status = HealthStatus.HEALTHY
            message = f"Process running: CPU {cpu_percent:.1f}%, Memory {memory_mb:.1f}MB"
            
            if cpu_percent > 80:
                status = HealthStatus.DEGRADED
                message = f"High CPU usage: {cpu_percent:.1f}%"
            elif memory_mb > 1000:
                status = HealthStatus.DEGRADED
                message = f"High memory usage: {memory_mb:.1f}MB"
            
            return ComponentHealth(
                component_name="process",
                status=status,
                message=message,
                last_check=datetime.now(),
                details={"cpu_percent": cpu_percent, "memory_mb": memory_mb}
            )
        except Exception as e:
            return ComponentHealth(
                component_name="process",
                status=HealthStatus.UNHEALTHY,
                message=f"Failed to check process: {e}",
                last_check=datetime.now()
            )
    
    # ============================================================
    # CUSTOM CHECK HELPERS
    # ============================================================
    
    def create_component_check(self, 
                               component_name: str,
                               is_healthy: bool,
                               message: str,
                               details: Dict = None) -> ComponentHealth:
        """Create a component health check result"""
        return ComponentHealth(
            component_name=component_name,
            status=HealthStatus.HEALTHY if is_healthy else HealthStatus.UNHEALTHY,
            message=message,
            last_check=datetime.now(),
            details=details or {}
        )
    
    # ============================================================
    # CHECK EXECUTION
    # ============================================================
    
    def run_checks(self) -> HealthReport:
        """Run all registered health checks"""
        self.check_count += 1
        self.last_check_time = datetime.now()
        
        component_statuses = []
        alerts = []
        unhealthy_count = 0
        
        for name, check_func in self.checks.items():
            try:
                result = check_func()
                component_statuses.append(result)
                self.component_status[name] = result
                
                if result.status == HealthStatus.UNHEALTHY:
                    unhealthy_count += 1
                    alerts.append({
                        "level": AlertLevel.ERROR.value,
                        "component": name,
                        "message": result.message,
                        "timestamp": datetime.now().isoformat()
                    })
                elif result.status == HealthStatus.DEGRADED:
                    alerts.append({
                        "level": AlertLevel.WARNING.value,
                        "component": name,
                        "message": result.message,
                        "timestamp": datetime.now().isoformat()
                    })
            except Exception as e:
                self.failure_count += 1
                error_result = ComponentHealth(
                    component_name=name,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Check failed: {e}",
                    last_check=datetime.now()
                )
                component_statuses.append(error_result)
                self.component_status[name] = error_result
                alerts.append({
                    "level": AlertLevel.CRITICAL.value,
                    "component": name,
                    "message": f"Check execution failed: {e}",
                    "timestamp": datetime.now().isoformat()
                })
                unhealthy_count += 1
        
        # Determine overall status
        if unhealthy_count > 0:
            overall_status = HealthStatus.UNHEALTHY
        elif any(s.status == HealthStatus.DEGRADED for s in component_statuses):
            overall_status = HealthStatus.DEGRADED
        else:
            overall_status = HealthStatus.HEALTHY
        
        self.overall_status = overall_status
        
        # Trigger alerts
        self._process_alerts(alerts)
        
        # Create report
        report = HealthReport(
            timestamp=datetime.now(),
            overall_status=overall_status,
            components=component_statuses,
            alerts=alerts,
            uptime_seconds=(datetime.now() - self.start_time).total_seconds(),
            metadata={
                "check_count": self.check_count,
                "failure_count": self.failure_count,
                "component_count": len(self.checks)
            }
        )
        
        # Log status
        logging.info(f"Health check completed: {overall_status.value} ({len(component_statuses)} components)")
        
        return report
    
    def _process_alerts(self, alerts: List[Dict]):
        """Process alerts based on thresholds"""
        if not alerts:
            return
        
        # Group alerts by level
        for level in AlertLevel:
            level_alerts = [a for a in alerts if a["level"] == level.value]
            if len(level_alerts) >= self.alert_thresholds.get(level, 5):
                self._send_alert(level.value, level_alerts)
    
    def _send_alert(self, level: str, alerts: List[Dict]):
        """Send alert notification"""
        logging.warning(f"ALERT [{level.upper()}]: {len(alerts)} alerts triggered")
        for alert in alerts:
            logging.warning(f"  {alert['component']}: {alert['message']}")
        
        # Webhook alert
        if self.alert_webhook:
            try:
                import requests
                requests.post(self.alert_webhook, json={"alerts": alerts})
            except:
                pass
        
        # Email alert
        if self.alert_email:
            try:
                # Implement email sending
                pass
            except:
                pass
    
    # ============================================================
    # BACKGROUND CHECKER
    # ============================================================
    
    def _start_background_checker(self):
        """Start background health checker"""
        def checker():
            while self.is_running:
                try:
                    self.run_checks()
                    time.sleep(self.check_interval)
                except Exception as e:
                    logging.error(f"Health checker error: {e}")
                    time.sleep(self.check_interval)
        
        thread = threading.Thread(target=checker, daemon=True)
        thread.start()
    
    # ============================================================
    # REPORTING
    # ============================================================
    
    def get_status(self) -> Dict[str, Any]:
        """Get current health status"""
        return {
            "overall_status": self.overall_status.value,
            "components": {name: status.to_dict() for name, status in self.component_status.items()},
            "check_count": self.check_count,
            "failure_count": self.failure_count,
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
            "last_check": self.last_check_time.isoformat() if self.last_check_time else None,
            "alerts": self.alerts[-10:]  # Last 10 alerts
        }
    
    def get_health_report(self) -> Dict[str, Any]:
        """Get full health report"""
        report = self.run_checks()
        return report.to_dict()
    
    def shutdown(self):
        """Shutdown health checker"""
        self.is_running = False
        logging.info("HealthChecker shutdown complete")

# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("\n" + "=" * 70)
    print("HEALTH CHECKER TEST")
    print("=" * 70)
    
    # Create health checker
    checker = HealthChecker(check_interval=5)
    
    # Register standard checks
    checker.register_standard_checks()
    
    # Register custom check
    def check_portfolio():
        return checker.create_component_check(
            "portfolio",
            True,
            "Portfolio is healthy",
            {"positions": 5, "value": 100000}
        )
    checker.register_check("portfolio", check_portfolio)
    
    # Run initial check
    print("\n🩺 Running health check...")
    report = checker.run_checks()
    
    # Show results
    print(f"\nOverall Status: {report.overall_status.value.upper()}")
    print(f"Components: {len(report.components)}")
    for comp in report.components:
        status_emoji = "✅" if comp.status == HealthStatus.HEALTHY else "⚠️" if comp.status == HealthStatus.DEGRADED else "❌"
        print(f"  {status_emoji} {comp.component_name}: {comp.status.value} - {comp.message}")
    
    # Get status
    print("\n📊 Status Summary:")
    status = checker.get_status()
    print(json.dumps(status, indent=2))
    
    # Wait for background checks
    print("\n⏳ Waiting for background checks...")
    time.sleep(3)
    
    # Clean up
    checker.shutdown()
    
    print("\n" + "=" * 70)
    print("HEALTH CHECKER TEST COMPLETE")
    print("=" * 70)
