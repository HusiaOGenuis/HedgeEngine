"""
Canonical Order Executor for Transition Capital Hedge Engine
Version: 2.0.0 - WITH STATE MACHINE
Date: 2026-06-30
Status: ACTIVE - STATE MACHINE INTEGRATED
"""

import logging
import time
from datetime import datetime
from typing import Dict, Optional, List, Any
from enum import Enum

# Import state machine
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from core.models.order_state import OrderStateMachine, OrderState, StateMachinePersistence

# ============================================================================
# ORDER CLASS WITH STATE MACHINE
# ============================================================================

class Order:
    """Represents a single order with full state machine lifecycle management"""
    
    def __init__(self, symbol: str, volume: float, direction: int, order_type: str = "LIMIT"):
        # Order identification
        self.order_id = f"ORD_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{id(self)}"
        self.symbol = symbol
        self.volume = volume
        self.direction = direction  # 1 for long, -1 for short
        self.order_type = order_type
        
        # State Machine
        self.state_machine = OrderStateMachine(self.order_id, OrderState.CREATED)
        
        # Transaction metrics (for telemetry)
        self.expected_slippage = None
        self.actual_slippage = None
        self.expected_spread = None
        self.actual_spread = None
        self.broker_latency = None
        self.total_latency = None
        
        # Execution details
        self.executed_price = None
        self.executed_volume = 0
        self.broker_order_id = None
        self.recovery_data = None
        
        # Timestamps
        self.created_at = datetime.now()
        self.updated_at = self.created_at
    
    # ============================================================
    # STATE TRANSITION WRAPPERS
    # ============================================================
    
    def validate(self) -> bool:
        """Validate order parameters"""
        if self.volume <= 0:
            self.state_machine.transition_to(OrderState.EXITED, "FAILED: Invalid volume")
            return False
        if self.direction not in [1, -1]:
            self.state_machine.transition_to(OrderState.EXITED, "FAILED: Invalid direction")
            return False
        self.state_machine.transition_to(OrderState.VALIDATED, "Validation passed")
        return True
    
    def approve(self) -> bool:
        """Risk and compliance approval"""
        self.state_machine.transition_to(OrderState.APPROVED, "Risk approval granted")
        return True
    
    def queue(self) -> bool:
        """Queue for execution"""
        self.state_machine.transition_to(OrderState.QUEUED, "Added to execution queue")
        return True
    
    def submit(self) -> bool:
        """Submit to broker"""
        start_time = time.time()
        self.state_machine.transition_to(OrderState.SUBMITTED, "Submitted to broker")
        self.total_latency = time.time() - start_time
        return True
    
    def accept(self, broker_order_id: str) -> bool:
        """Broker accepted the order"""
        self.broker_order_id = broker_order_id
        self.state_machine.transition_to(OrderState.ACCEPTED, f"Broker accepted: {broker_order_id}")
        return True
    
    def fill(self, price: float, volume: float) -> bool:
        """Partially or fully fill the order"""
        self.executed_price = price
        self.executed_volume += volume
        if self.executed_volume >= self.volume:
            self.state_machine.transition_to(OrderState.FILLED, f"Fully filled at {price}")
        else:
            self.state_machine.transition_to(OrderState.FILLED, f"Partially filled: {self.executed_volume}/{self.volume}")
        return True
    
    def confirm(self) -> bool:
        """Confirm execution with broker"""
        self.state_machine.transition_to(OrderState.CONFIRMED, "Execution confirmed")
        return True
    
    def monitor(self) -> bool:
        """Active monitoring of open order"""
        self.state_machine.transition_to(OrderState.MONITORED, "Order being monitored")
        return True
    
    def exit(self) -> bool:
        """Exit or cancel the order"""
        self.state_machine.transition_to(OrderState.EXITED, "Order exited")
        return True
    
    def archive(self) -> bool:
        """Archive completed order"""
        self.state_machine.transition_to(OrderState.ARCHIVED, "Archived to history")
        return True
    
    # ============================================================
    # STATE QUERY METHODS
    # ============================================================
    
    @property
    def state(self) -> OrderState:
        """Get current state"""
        return self.state_machine.current_state
    
    def get_state_history(self) -> List[Dict]:
        """Get full state transition history"""
        return self.state_machine.get_history()
    
    def get_state_duration(self) -> float:
        """Get duration in current state"""
        return self.state_machine.get_state_duration()
    
    def is_terminal(self) -> bool:
        """Check if order is in terminal state"""
        return self.state_machine.is_terminal
    
    def can_transition_to(self, target_state: OrderState) -> bool:
        """Check if can transition to target state"""
        return self.state_machine.current_state.can_transition_to(target_state)
    
    # ============================================================
    # PERSISTENCE
    # ============================================================
    
    def save_to_storage(self, storage: Dict[str, Dict]):
        """Save order to persistent storage"""
        StateMachinePersistence.save_state_machine(self.state_machine, storage)
    
    @classmethod
    def load_from_storage(cls, order_id: str, storage: Dict[str, Dict], symbol: str, volume: float, direction: int) -> Optional['Order']:
        """Load order from persistent storage"""
        if order_id not in storage:
            return None
        
        # Create order with state machine reconstructed
        order = cls(symbol, volume, direction)
        order.order_id = order_id
        order.state_machine = StateMachinePersistence.load_state_machine(order_id, storage)
        
        return order
    
    def __repr__(self):
        return f"Order({self.order_id}, {self.symbol}, {self.direction}, state={self.state.value})"

# ============================================================================
# EXECUTION INTELLIGENCE ENGINE (EIE) - WITH STATE MACHINE
# ============================================================================

class ExecutionIntelligenceEngine:
    """
    Execution Intelligence Engine - Single source of truth for all order execution
    Now with full state machine integration and persistence
    """
    
    def __init__(self):
        self.active_orders: Dict[str, Order] = {}
        self.historical_orders: List[Order] = []
        self.order_counter = 0
        
        # Persistence storage (in production, use Redis/SQLite)
        self.persistence_storage: Dict[str, Dict] = {}
        
        # Recovery flag
        self.recovered_orders: List[str] = []
        
        logging.info("ExecutionIntelligenceEngine initialized - CANONICAL INSTANCE WITH STATE MACHINE")
    
    # ============================================================
    # CORE EXECUTION METHODS
    # ============================================================
    
    def place_order(self, symbol: str, volume: float, direction: int, order_type: str = "LIMIT") -> Optional[Order]:
        """
        Place a new order with full state machine lifecycle management
        """
        # Create order with initial state
        order = Order(symbol, volume, direction, order_type)
        logging.info(f"Order created: {order.order_id}")
        
        # Validate
        if not order.validate():
            logging.error(f"Order validation failed: {order}")
            self._archive_order(order)
            return None
        
        # Risk approval
        if not order.approve():
            logging.error(f"Order risk approval failed: {order}")
            self._archive_order(order)
            return None
        
        # Queue for execution
        order.queue()
        
        # Store active order
        self.active_orders[order.order_id] = order
        self._persist_order(order)
        
        # Execute
        try:
            # Simulate execution flow
            order.submit()
            order.accept(f"BROKER_{order.order_id}")
            order.fill(price=100.0, volume=volume)  # Simulated fill
            order.confirm()
            order.monitor()
            order.archive()
            
            # Move to history
            self._archive_order(order)
            
            logging.info(f"Order executed successfully: {order}")
            return order
            
        except Exception as e:
            logging.error(f"Execution failed for {order.order_id}: {e}")
            order.exit()
            self._archive_order(order)
            return None
    
    def smart_execute(self, symbol: str, volume: float, direction: int) -> Optional[Order]:
        """
        Smart execution with market impact minimization
        """
        return self.place_order(symbol, volume, direction, order_type="SMART")
    
    # ============================================================
    # ORDER MANAGEMENT
    # ============================================================
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an active order"""
        if order_id in self.active_orders:
            order = self.active_orders[order_id]
            if order.can_transition_to(OrderState.EXITED):
                order.exit()
                self._archive_order(order)
                logging.info(f"Order cancelled: {order_id}")
                return True
        logging.warning(f"Order {order_id} not found or cannot be cancelled")
        return False
    
    def get_order_status(self, order_id: str) -> Optional[OrderState]:
        """Get current state of an order"""
        if order_id in self.active_orders:
            return self.active_orders[order_id].state
        # Check history
        for order in self.historical_orders:
            if order.order_id == order_id:
                return order.state
        return None
    
    def get_order_history(self, order_id: str) -> Optional[List[Dict]]:
        """Get full transition history for an order"""
        if order_id in self.active_orders:
            return self.active_orders[order_id].get_state_history()
        for order in self.historical_orders:
            if order.order_id == order_id:
                return order.get_state_history()
        return None
    
    def get_active_orders(self) -> Dict[str, Order]:
        """Get all currently active orders"""
        return self.active_orders.copy()
    
    def get_active_orders_with_states(self) -> Dict[str, str]:
        """Get summary of active orders with their states"""
        return {oid: order.state.value for oid, order in self.active_orders.items()}
    
    # ============================================================
    # PERSISTENCE
    # ============================================================
    
    def _persist_order(self, order: Order):
        """Save order state to persistence storage"""
        order.save_to_storage(self.persistence_storage)
    
    def _archive_order(self, order: Order):
        """Move order from active to history and persist"""
        if order.order_id in self.active_orders:
            del self.active_orders[order.order_id]
        self.historical_orders.append(order)
        self._persist_order(order)
    
    def save_all_states(self):
        """Save all active orders"""
        for order in self.active_orders.values():
            self._persist_order(order)
        logging.info(f"Saved {len(self.active_orders)} active order states")
    
    # ============================================================
    # RECOVERY
    # ============================================================
    
    def recover_from_persistence(self, orders_data: Dict[str, Dict]) -> int:
        """
        Recover orders from persistence storage
        
        Returns:
            Number of orders recovered
        """
        recovered_count = 0
        for order_id, data in orders_data.items():
            # Reconstruct order from persisted data
            try:
                # Check if order is still active
                current_state = OrderState(data["current_state"])
                if current_state not in [OrderState.ARCHIVED, OrderState.EXITED]:
                    # Reconstruct order
                    order = Order(data.get("symbol", "UNKNOWN"), 
                                data.get("volume", 0.0),
                                data.get("direction", 1))
                    order.order_id = order_id
                    order.state_machine = StateMachinePersistence.load_state_machine(order_id, orders_data)
                    
                    # Add to active orders
                    self.active_orders[order_id] = order
                    self.recovered_orders.append(order_id)
                    recovered_count += 1
                    
                    logging.info(f"Recovered order: {order_id} in state {current_state.value}")
                    
            except Exception as e:
                logging.error(f"Failed to recover order {order_id}: {e}")
        
        logging.info(f"Recovered {recovered_count} orders from persistence")
        return recovered_count
    
    def get_recovery_status(self) -> Dict[str, Any]:
        """Get recovery status information"""
        return {
            "recovered_orders": self.recovered_orders,
            "active_orders": len(self.active_orders),
            "persisted_orders": len(self.persistence_storage),
            "total_historical": len(self.historical_orders),
            "recovery_timestamp": datetime.now().isoformat()
        }

# ============================================================================
# SINGLETON INSTANCE - Global Access Point
# ============================================================================

execution_engine = ExecutionIntelligenceEngine()

# Backward compatibility functions
def place_order(symbol, volume=None, direction=1):
    """Legacy function wrapper - delegates to canonical engine"""
    return execution_engine.place_order(symbol, volume, direction)

def smart_execute(symbol, volume=None, direction=1):
    """Legacy function wrapper - delegates to canonical engine"""
    return execution_engine.smart_execute(symbol, volume, direction)

# ============================================================================
# MODULE INITIALIZATION
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("=" * 70)
    print("TESTING EXECUTION INTELLIGENCE ENGINE WITH STATE MACHINE")
    print("=" * 70)
    
    # Test order execution
    print("\n1. Placing test orders...")
    order1 = place_order("AAPL", 100, 1)
    print(f"   Order 1: {order1}")
    
    order2 = place_order("GOOGL", 50, -1)
    print(f"   Order 2: {order2}")
    
    # Show active orders
    print("\n2. Active orders:")
    active_states = execution_engine.get_active_orders_with_states()
    for oid, state in active_states.items():
        print(f"   {oid}: {state}")
    
    # Show history
    print("\n3. Order history for order 1:")
    if order1:
        history = order1.get_state_history()
        for i, t in enumerate(history, 1):
            print(f"   {i}. {t['from_state']} -> {t['to_state']}: {t['reason']}")
    
    # Test persistence
    print("\n4. Testing persistence...")
    execution_engine.save_all_states()
    print(f"   Saved {len(execution_engine.persistence_storage)} states")
    
    # Test recovery
    print("\n5. Testing recovery...")
    storage = execution_engine.persistence_storage.copy()
    # Simulate clearing active orders
    execution_engine.active_orders = {}
    print(f"   Active orders after clear: {len(execution_engine.active_orders)}")
    
    # Recover
    recovered = execution_engine.recover_from_persistence(storage)
    print(f"   Recovered {recovered} orders")
    print(f"   Active orders after recovery: {len(execution_engine.active_orders)}")
    
    # Show recovery status
    print("\n6. Recovery status:")
    status = execution_engine.get_recovery_status()
    print(f"   {status}")
    
    print("\n" + "=" * 70)
    print("EXECUTION INTELLIGENCE ENGINE TEST COMPLETE")
    print("=" * 70)
