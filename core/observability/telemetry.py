"""
Production-Grade Telemetry System
Version: 1.0.0
Date: 2026-06-30
Status: PRODUCTION - COMPLETE OBSERVABILITY

Captures:
- Order lifecycle events
- Performance metrics
- System health
- Latency tracking
- Error logging
- Audit trails
"""

import logging
import json
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
import threading
from queue import Queue, Empty
import csv
import os

# ============================================================================
# TELEMETRY DATA STRUCTURES
# ============================================================================

class TelemetryLevel(Enum):
    """Telemetry verbosity levels"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class OrderTelemetry:
    """Complete order telemetry payload"""
    # Order identification
    order_id: str
    symbol: str
    direction: int
    volume: float
    order_type: str
    
    # Timing
    timestamp: str
    latency_ms: float
    broker_latency_ms: float
    total_latency_ms: float
    
    # Execution
    expected_slippage: float
    actual_slippage: float
    expected_spread: float
    actual_spread: float
    executed_price: float
    executed_volume: float
    
    # Context
    market_regime: str
    signal_id: str
    capital_id: str
    decision_id: str
    portfolio_id: str
    
    # State
    state: str
    broker_order_id: str
    
    # Additional
    transition_count: int
    error_message: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class PerformanceTelemetry:
    """Performance metrics telemetry"""
    timestamp: str
    component: str
    operation: str
    duration_ms: float
    success: bool
    memory_usage_mb: float
    cpu_usage_percent: float
    error: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class SystemHealthTelemetry:
    """System health telemetry"""
    timestamp: str
    status: str  # healthy, degraded, unhealthy
    uptime_seconds: float
    active_orders: int
    total_orders: int
    memory_usage_mb: float
    cpu_usage_percent: float
    disk_usage_percent: float
    active_threads: int
    error_count: int
    
    def to_dict(self) -> Dict:
        return asdict(self)

# ============================================================================
# TELEMETRY COLLECTOR
# ============================================================================

class TelemetryCollector:
    """
    Production-grade telemetry collector
    
    Features:
    - Structured logging
    - Multiple outputs (console, file, JSON)
    - Batching for performance
    - Async processing
    - Filtering by level
    """
    
    def __init__(self, 
                 app_name: str = "HedgeEngine",
                 log_level: TelemetryLevel = TelemetryLevel.INFO,
                 enable_console: bool = True,
                 enable_file: bool = True,
                 log_dir: str = "logs",
                 batch_size: int = 100,
                 flush_interval: int = 5):
        
        self.app_name = app_name
        self.log_level = log_level
        self.enable_console = enable_console
        self.enable_file = enable_file
        self.log_dir = Path(log_dir)
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        
        # Create log directory
        if enable_file:
            self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup file handlers
        self.order_log_file = self.log_dir / f"orders_{datetime.now().strftime('%Y%m%d')}.log"
        self.performance_log_file = self.log_dir / f"performance_{datetime.now().strftime('%Y%m%d')}.log"
        self.health_log_file = self.log_dir / f"health_{datetime.now().strftime('%Y%m%d')}.log"
        self.error_log_file = self.log_dir / f"errors_{datetime.now().strftime('%Y%m%d')}.log"
        
        # Batch queue
        self.queue = Queue()
        self.is_running = True
        
        # Statistics
        self.total_events = 0
        self.error_count = 0
        self.warning_count = 0
        
        # Start background processor
        self._start_processor()
        
        logging.info(f"TelemetryCollector initialized (Level: {log_level.value})")
        logging.info(f"Log directory: {self.log_dir.absolute()}")
    
    # ============================================================
    # CORE LOGGING METHODS
    # ============================================================
    
    def log_order_event(self, order_data: OrderTelemetry):
        """Log an order lifecycle event"""
        self._log_event("order", order_data.to_dict(), TelemetryLevel.INFO)
    
    def log_performance(self, performance_data: PerformanceTelemetry):
        """Log performance metrics"""
        self._log_event("performance", performance_data.to_dict(), TelemetryLevel.DEBUG)
    
    def log_health(self, health_data: SystemHealthTelemetry):
        """Log system health metrics"""
        self._log_event("health", health_data.to_dict(), TelemetryLevel.INFO)
    
    def log_error(self, error_message: str, context: Dict = None, level: TelemetryLevel = TelemetryLevel.ERROR):
        """Log an error event"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "error": error_message,
            "context": context or {},
            "level": level.value
        }
        self.error_count += 1
        self._log_event("error", event, level)
        
        # Also write to error log immediately
        self._write_immediate(self.error_log_file, event)
    
    def log_warning(self, warning_message: str, context: Dict = None):
        """Log a warning event"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "warning": warning_message,
            "context": context or {},
            "level": "warning"
        }
        self.warning_count += 1
        self._log_event("warning", event, TelemetryLevel.WARNING)
    
    # ============================================================
    # INTERNAL METHODS
    # ============================================================
    
    def _log_event(self, event_type: str, data: Dict, level: TelemetryLevel):
        """Internal method to queue an event"""
        # Check log level
        if self._should_skip(level):
            return
        
        # Add common fields
        event = {
            "event_type": event_type,
            "app": self.app_name,
            "level": level.value,
            **data
        }
        
        self.total_events += 1
        
        # Send to console immediately for important events
        if self.enable_console and level in [TelemetryLevel.ERROR, TelemetryLevel.CRITICAL]:
            self._write_console(event)
        
        # Queue for batch processing
        self.queue.put(event)
        
        # Trigger flush if batch is full
        if self.queue.qsize() >= self.batch_size:
            self._flush_events()
    
    def _should_skip(self, level: TelemetryLevel) -> bool:
        """Check if event should be skipped based on log level"""
        level_order = [TelemetryLevel.DEBUG, TelemetryLevel.INFO, 
                      TelemetryLevel.WARNING, TelemetryLevel.ERROR, 
                      TelemetryLevel.CRITICAL]
        current_index = level_order.index(self.log_level)
        event_index = level_order.index(level)
        return event_index < current_index
    
    def _start_processor(self):
        """Start background event processor"""
        def processor():
            while self.is_running:
                try:
                    # Process events in batches
                    events = []
                    for _ in range(self.batch_size):
                        event = self.queue.get(timeout=self.flush_interval)
                        events.append(event)
                    
                    if events:
                        self._process_batch(events)
                except Empty:
                    # Flush any remaining events
                    self._flush_events()
                except Exception as e:
                    logging.error(f"Telemetry processor error: {e}")
        
        thread = threading.Thread(target=processor, daemon=True)
        thread.start()
    
    def _process_batch(self, events: List[Dict]):
        """Process a batch of events"""
        if not events:
            return
        
        # Group by event type for efficient writing
        grouped = {}
        for event in events:
            event_type = event.get("event_type", "unknown")
            if event_type not in grouped:
                grouped[event_type] = []
            grouped[event_type].append(event)
        
        # Write each group
        for event_type, batch in grouped.items():
            if event_type == "order":
                self._write_order_batch(batch)
            elif event_type == "performance":
                self._write_performance_batch(batch)
            elif event_type == "health":
                self._write_health_batch(batch)
            elif event_type in ["error", "warning"]:
                self._write_immediate(self.error_log_file, batch)
    
    def _flush_events(self):
        """Force flush all queued events"""
        events = []
        while not self.queue.empty():
            try:
                events.append(self.queue.get_nowait())
            except Empty:
                break
        
        if events:
            self._process_batch(events)
    
    # ============================================================
    # OUTPUT WRITERS
    # ============================================================
    
    def _write_console(self, event: Dict):
        """Write to console"""
        level = event.get("level", "info")
        event_type = event.get("event_type", "unknown")
        
        # Color codes
        colors = {
            "error": "\033[91m",
            "warning": "\033[93m",
            "info": "\033[92m",
            "debug": "\033[94m",
            "critical": "\033[91m\033[1m"
        }
        reset = "\033[0m"
        
        color = colors.get(level, "")
        prefix = f"{color}[{level.upper()}]{reset}"
        
        if level in ["error", "critical"]:
            print(f"{prefix} [{event_type}] {event.get('error', event.get('message', ''))}")
        else:
            print(f"{prefix} [{event_type}] {json.dumps(event, indent=2)}")
    
    def _write_order_batch(self, orders: List[Dict]):
        """Write order telemetry to CSV"""
        if not orders:
            return
        
        # Write as JSON lines for easy parsing
        with open(self.order_log_file, 'a') as f:
            for order in orders:
                f.write(json.dumps(order) + '\n')
    
    def _write_performance_batch(self, metrics: List[Dict]):
        """Write performance telemetry to CSV"""
        if not metrics:
            return
        
        with open(self.performance_log_file, 'a') as f:
            for metric in metrics:
                f.write(json.dumps(metric) + '\n')
    
    def _write_health_batch(self, health_data: List[Dict]):
        """Write health telemetry to CSV"""
        if not health_data:
            return
        
        with open(self.health_log_file, 'a') as f:
            for data in health_data:
                f.write(json.dumps(data) + '\n')
    
    def _write_immediate(self, filepath: Path, data: Any):
        """Write data immediately to file"""
        if isinstance(data, list):
            with open(filepath, 'a') as f:
                for item in data:
                    f.write(json.dumps(item) + '\n')
        else:
            with open(filepath, 'a') as f:
                f.write(json.dumps(data) + '\n')
    
    # ============================================================
    # QUERY METHODS
    # ============================================================
    
    def get_stats(self) -> Dict[str, Any]:
        """Get telemetry statistics"""
        return {
            "total_events": self.total_events,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "queue_size": self.queue.qsize(),
            "log_level": self.log_level.value,
            "log_dir": str(self.log_dir)
        }
    
    def get_recent_errors(self, count: int = 10) -> List[Dict]:
        """Get recent errors"""
        if not self.error_log_file.exists():
            return []
        
        errors = []
        with open(self.error_log_file, 'r') as f:
            lines = f.readlines()
            for line in lines[-count:]:
                try:
                    errors.append(json.loads(line))
                except:
                    pass
        return errors
    
    def get_orders_today(self) -> int:
        """Get number of orders today"""
        if not self.order_log_file.exists():
            return 0
        
        with open(self.order_log_file, 'r') as f:
            return sum(1 for _ in f)
    
    def shutdown(self):
        """Shutdown telemetry collector"""
        self.is_running = False
        self._flush_events()
        logging.info("TelemetryCollector shutdown complete")

# ============================================================================
# OBSERVABILITY CONTEXT
# ============================================================================

class ObservabilityContext:
    """
    Context manager for observability
    
    Tracks:
    - Operation duration
    - Success/failure
    - Context data
    - Performance metrics
    """
    
    def __init__(self, 
                 collector: TelemetryCollector,
                 component: str,
                 operation: str,
                 context_data: Optional[Dict] = None):
        
        self.collector = collector
        self.component = component
        self.operation = operation
        self.context_data = context_data or {}
        self.start_time = None
        self.start_memory = None
        self.success = False
        self.error = None
    
    def __enter__(self):
        self.start_time = time.time()
        self.start_memory = self._get_memory_usage()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = (time.time() - self.start_time) * 1000
        end_memory = self._get_memory_usage()
        
        if exc_val:
            self.error = str(exc_val)
            self.success = False
            self.collector.log_error(self.error, self.context_data)
        else:
            self.success = True
        
        # Log performance
        perf = PerformanceTelemetry(
            timestamp=datetime.now().isoformat(),
            component=self.component,
            operation=self.operation,
            duration_ms=duration_ms,
            success=self.success,
            memory_usage_mb=end_memory - self.start_memory,
            cpu_usage_percent=self._get_cpu_usage(),
            error=self.error or ""
        )
        self.collector.log_performance(perf)
        
        # Log errors if any
        if not self.success:
            logging.error(f"Operation failed: {self.component}.{self.operation} - {self.error}")
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            import psutil
            return psutil.Process().memory_info().rss / 1024 / 1024
        except:
            return 0.0
    
    def _get_cpu_usage(self) -> float:
        """Get current CPU usage percent"""
        try:
            import psutil
            return psutil.cpu_percent(interval=0.1)
        except:
            return 0.0

# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("TELEMETRY SYSTEM TEST")
    print("=" * 70)
    
    # Create collector
    collector = TelemetryCollector(
        app_name="HedgeEngine",
        log_level=TelemetryLevel.INFO,
        enable_console=True,
        enable_file=True,
        batch_size=5,
        flush_interval=2
    )
    
    # Test order telemetry
    print("\n📊 Logging order telemetry...")
    order = OrderTelemetry(
        order_id="ORD_001",
        symbol="AAPL",
        direction=1,
        volume=100,
        order_type="LIMIT",
        timestamp=datetime.now().isoformat(),
        latency_ms=50.5,
        broker_latency_ms=25.3,
        total_latency_ms=75.8,
        expected_slippage=0.01,
        actual_slippage=0.015,
        expected_spread=0.02,
        actual_spread=0.025,
        executed_price=150.50,
        executed_volume=100,
        market_regime="neutral",
        signal_id="SIG_001",
        capital_id="CAP_001",
        decision_id="DEC_001",
        portfolio_id="PORT_001",
        state="FILLED",
        broker_order_id="BRK_001",
        transition_count=11
    )
    collector.log_order_event(order)
    
    # Test performance telemetry
    print("\n⚡ Logging performance telemetry...")
    perf = PerformanceTelemetry(
        timestamp=datetime.now().isoformat(),
        component="OrderExecutor",
        operation="place_order",
        duration_ms=45.2,
        success=True,
        memory_usage_mb=125.5,
        cpu_usage_percent=15.2
    )
    collector.log_performance(perf)
    
    # Test health telemetry
    print("\n💚 Logging health telemetry...")
    health = SystemHealthTelemetry(
        timestamp=datetime.now().isoformat(),
        status="healthy",
        uptime_seconds=3600,
        active_orders=5,
        total_orders=100,
        memory_usage_mb=128.5,
        cpu_usage_percent=12.3,
        disk_usage_percent=45.6,
        active_threads=8,
        error_count=0
    )
    collector.log_health(health)
    
    # Test error logging
    print("\n❌ Logging error...")
    collector.log_error("Test error message", {"context": "testing"})
    
    # Test warning logging
    print("\n⚠️ Logging warning...")
    collector.log_warning("Test warning message", {"context": "testing"})
    
    # Test observability context
    print("\n⏱️ Testing observability context...")
    with ObservabilityContext(collector, "TestComponent", "test_operation", {"test": "data"}):
        time.sleep(0.1)
    
    # Flush and show stats
    collector._flush_events()
    print("\n📊 Telemetry Stats:")
    stats = collector.get_stats()
    print(json.dumps(stats, indent=2))
    
    collector.shutdown()
    
    print("\n" + "=" * 70)
    print("TELEMETRY TEST COMPLETE")
    print("=" * 70)
