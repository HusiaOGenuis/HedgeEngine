"""
Order State Machine for Transition Capital Hedge Engine
Version: 1.0.1 - Fixed None handling
Date: 2026-06-30
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

# ============================================================================
# ORDER STATE ENUM - Complete Lifecycle
# ============================================================================

class OrderState(Enum):
    """Defines the complete lifecycle of an order with transitions"""
    CREATED = "CREATED"
    VALIDATED = "VALIDATED"
    APPROVED = "APPROVED"
    QUEUED = "QUEUED"
    SUBMITTED = "SUBMITTED"
    ACCEPTED = "ACCEPTED"
    FILLED = "FILLED"
    CONFIRMED = "CONFIRMED"
    MONITORED = "MONITORED"
    EXITED = "EXITED"
    ARCHIVED = "ARCHIVED"
    
    @classmethod
    def get_transition_rules(cls) -> Dict['OrderState', List['OrderState']]:
        """Define valid state transitions"""
        return {
            cls.CREATED: [cls.VALIDATED, cls.EXITED],
            cls.VALIDATED: [cls.APPROVED, cls.EXITED],
            cls.APPROVED: [cls.QUEUED, cls.EXITED],
            cls.QUEUED: [cls.SUBMITTED, cls.EXITED],
            cls.SUBMITTED: [cls.ACCEPTED, cls.EXITED],
            cls.ACCEPTED: [cls.FILLED, cls.EXITED],
            cls.FILLED: [cls.CONFIRMED, cls.EXITED],
            cls.CONFIRMED: [cls.MONITORED, cls.ARCHIVED],
            cls.MONITORED: [cls.ARCHIVED, cls.EXITED],
            cls.EXITED: [cls.ARCHIVED],
            cls.ARCHIVED: []  # Terminal state
        }
    
    def can_transition_to(self, target: 'OrderState') -> bool:
        """Check if transition to target state is valid"""
        rules = self.get_transition_rules()
        return target in rules.get(self, [])

# ============================================================================
# STATE TRANSITION RECORD - FIXED
# ============================================================================

class StateTransition:
    """Records a single state transition with full context"""
    
    def __init__(self, from_state: Optional[OrderState], to_state: OrderState, reason: str, metadata: Optional[Dict] = None):
        self.from_state = from_state
        self.to_state = to_state
        self.reason = reason
        self.timestamp = datetime.now()
        self.metadata = metadata or {}
        self.transition_id = f"TRANS_{self.timestamp.strftime('%Y%m%d_%H%M%S')}_{id(self)}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization - FIXED None handling"""
        return {
            "transition_id": self.transition_id,
            "from_state": self.from_state.value if self.from_state else None,  # FIXED: Handle None
            "to_state": self.to_state.value,
            "reason": self.reason,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }
    
    def __repr__(self):
        from_state_str = self.from_state.value if self.from_state else "INITIAL"
        return f"Transition({from_state_str} -> {self.to_state.value}, reason={self.reason})"

# ============================================================================
# ORDER STATE MACHINE - Core Implementation
# ============================================================================

class OrderStateMachine:
    """State machine for managing order lifecycle with persistence support"""
    
    def __init__(self, order_id: str, initial_state: OrderState = OrderState.CREATED):
        self.order_id = order_id
        self.current_state = initial_state
        self.transitions: List[StateTransition] = []
        self.created_at = datetime.now()
        self.updated_at = self.created_at
        self.is_terminal = False
        
        # Record initial state
        self._record_transition(None, initial_state, "Order initialized")
        logging.debug(f"StateMachine initialized for {order_id} at {initial_state.value}")
    
    def transition_to(self, target_state: OrderState, reason: str, metadata: Optional[Dict] = None) -> bool:
        """Attempt to transition to a new state"""
        if self.is_terminal:
            logging.warning(f"Order {self.order_id} is terminal. Cannot transition from {self.current_state.value}")
            return False
        
        if not self.current_state.can_transition_to(target_state):
            logging.error(f"Invalid transition from {self.current_state.value} to {target_state.value} for {self.order_id}")
            return False
        
        old_state = self.current_state
        self._record_transition(old_state, target_state, reason, metadata)
        self.current_state = target_state
        self.updated_at = datetime.now()
        
        if target_state in [OrderState.ARCHIVED, OrderState.EXITED]:
            self.is_terminal = True
        
        logging.info(f"Order {self.order_id}: {old_state.value} -> {target_state.value} ({reason})")
        return True
    
    def _record_transition(self, from_state: Optional[OrderState], to_state: OrderState, reason: str, metadata: Optional[Dict] = None):
        """Internal method to record a transition"""
        transition = StateTransition(from_state, to_state, reason, metadata)
        self.transitions.append(transition)
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get full transition history"""
        return [t.to_dict() for t in self.transitions]
    
    def get_last_transition(self) -> Optional[StateTransition]:
        """Get the most recent transition"""
        return self.transitions[-1] if self.transitions else None
    
    def get_state_duration(self) -> float:
        """Get duration in current state in seconds"""
        return (datetime.now() - self.updated_at).total_seconds()
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize state machine for persistence"""
        return {
            "order_id": self.order_id,
            "current_state": self.current_state.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "is_terminal": self.is_terminal,
            "transitions": self.get_history(),
            "total_transitions": len(self.transitions)
        }
    
    def __repr__(self):
        return f"StateMachine({self.order_id}, {self.current_state.value}, transitions={len(self.transitions)})"

# ============================================================================
# PERSISTENCE SUPPORT
# ============================================================================

class StateMachinePersistence:
    """Handle saving and loading state machines"""
    
    @staticmethod
    def save_state_machine(state_machine: OrderStateMachine, storage: Dict[str, Dict]):
        """Save state machine to storage"""
        storage[state_machine.order_id] = state_machine.to_dict()
        logging.debug(f"Saved state machine for {state_machine.order_id}")
    
    @staticmethod
    def load_state_machine(order_id: str, storage: Dict[str, Dict]) -> Optional[OrderStateMachine]:
        """Load state machine from storage"""
        if order_id not in storage:
            return None
        
        data = storage[order_id]
        state_machine = OrderStateMachine(order_id, OrderState(data["current_state"]))
        state_machine.created_at = datetime.fromisoformat(data["created_at"])
        state_machine.updated_at = datetime.fromisoformat(data["updated_at"])
        state_machine.is_terminal = data["is_terminal"]
        
        # Clear the initial transition and reconstruct from data
        state_machine.transitions = []
        for t in data["transitions"]:
            from_state = OrderState(t["from_state"]) if t["from_state"] else None
            to_state = OrderState(t["to_state"])
            transition = StateTransition(from_state, to_state, t["reason"], t["metadata"])
            transition.timestamp = datetime.fromisoformat(t["timestamp"])
            state_machine.transitions.append(transition)
        
        logging.info(f"Loaded state machine for {order_id}")
        return state_machine

# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Testing State Machine with None handling fix...")
    sm = OrderStateMachine("TEST_001")
    sm.transition_to(OrderState.VALIDATED, "Test")
    history = sm.get_history()
    print(f"History: {history}")
    print("✅ State Machine working correctly!")
