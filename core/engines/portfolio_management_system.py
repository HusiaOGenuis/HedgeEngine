"""
Phase 2 Integration Module - PIE + Risk Layer
Connects Portfolio Intelligence Engine with Risk Layer
"""

import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# Add the project root to path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Now import using absolute paths
from core.engines.portfolio_intelligence_engine import (
    PortfolioIntelligenceEngine, 
    AssetDNA, 
    PortfolioAllocation,
    PortfolioConstraints,
    PortfolioObjective,
    MarketRegime
)
from core.engines.risk_layer import RiskLayer, RiskMetrics, RiskLimits

class PortfolioManagementSystem:
    """
    Integrated Portfolio Management System
    
    Combines:
    - Portfolio Intelligence Engine (PIE) for allocation
    - Risk Layer for comprehensive risk management
    - Execution Engine for trade execution
    """
    
    def __init__(self,
                 initial_capital: float = 100000.0,
                 pie_constraints: Optional[PortfolioConstraints] = None,
                 risk_limits: Optional[RiskLimits] = None,
                 objective: PortfolioObjective = PortfolioObjective.MAXIMIZE_SHARPE):
        
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        
        # Initialize components
        self.pie = PortfolioIntelligenceEngine(
            constraints=pie_constraints or PortfolioConstraints(),
            objective=objective
        )
        
        self.risk = RiskLayer(limits=risk_limits or RiskLimits())
        
        # State
        self.current_allocation: Optional[PortfolioAllocation] = None
        self.current_risk_metrics: Optional[RiskMetrics] = None
        self.positions: Dict[str, float] = {}
        self.asset_data: Dict[str, Dict] = {}
        
        # History
        self.allocation_history: List[Dict] = []
        self.risk_history: List[Dict] = []
        
        logging.info("=" * 70)
        logging.info("PORTFOLIO MANAGEMENT SYSTEM INITIALIZED")
        logging.info("=" * 70)
        logging.info(f"Initial Capital: ${initial_capital:,.2f}")
        logging.info(f"Objective: {objective.value}")
    
    # ============================================================
    # ASSET MANAGEMENT
    # ============================================================
    
    def add_asset(self, symbol: str, dna: AssetDNA):
        """Add asset to the system"""
        self.pie.add_asset(dna)
        self.asset_data[symbol] = {
            "dna": dna,
            "current_price": 100.0,  # Placeholder
            "last_updated": datetime.now()
        }
        logging.debug(f"Added asset: {symbol}")
    
    def add_assets(self, assets: List[AssetDNA]):
        """Add multiple assets"""
        for asset in assets:
            self.add_asset(asset.symbol, asset)
        logging.info(f"Added {len(assets)} assets")
    
    def update_position(self, symbol: str, volume: float, price: float):
        """Update a position"""
        self.positions[symbol] = volume * price
        if symbol in self.asset_data:
            self.asset_data[symbol]["current_price"] = price
            self.asset_data[symbol]["last_updated"] = datetime.now()
    
    # ============================================================
    # CORE FUNCTIONALITY
    # ============================================================
    
    def analyze_and_allocate(self, 
                            market_data: Optional[Dict] = None) -> PortfolioAllocation:
        """
        Full portfolio analysis and allocation cycle
        
        1. Detect market regime
        2. Optimize portfolio
        3. Calculate risk
        4. Apply risk adjustments
        5. Generate signals
        """
        # Step 1: Detect regime
        if market_data:
            regime = self.pie.detect_market_regime(market_data)
        else:
            regime = MarketRegime.NEUTRAL
        
        logging.info(f"Current Regime: {regime.value}")
        
        # Step 2: Optimize portfolio
        allocation = self.pie.optimize_portfolio(
            total_capital=self.current_capital,
            current_positions=self.positions,
            market_data=market_data,
            regime=regime
        )
        self.current_allocation = allocation
        
        # Step 3: Calculate risk
        returns = self._get_asset_returns()
        volatilities = self._get_asset_volatilities()
        correlations = self._get_asset_correlations()
        
        risk_metrics = self.risk.calculate_risk(
            positions=self.positions,
            returns=returns,
            asset_volatilities=volatilities,
            asset_correlations=correlations
        )
        self.current_risk_metrics = risk_metrics
        
        # Step 4: Apply risk adjustments
        risk_adjusted_weights = self.risk.get_risk_adjusted_weights(
            allocation.get_weights(),
            risk_metrics
        )
        
        # Step 5: Generate signals
        signals = self.pie.generate_rebalance_signals(
            allocation,
            self.positions,
            self.current_capital
        )
        
        # Store history
        self.allocation_history.append({
            "timestamp": datetime.now().isoformat(),
            "allocation": allocation.allocations,
            "regime": regime.value,
            "signals": signals
        })
        
        self.risk_history.append({
            "timestamp": datetime.now().isoformat(),
            "metrics": risk_metrics.to_dict()
        })
        
        return allocation
    
    def get_rebalance_signals(self) -> Dict[str, Dict[str, Any]]:
        """Get rebalance signals based on current allocation"""
        if not self.current_allocation:
            return {}
        
        return self.pie.generate_rebalance_signals(
            self.current_allocation,
            self.positions,
            self.current_capital
        )
    
    # ============================================================
    # RISK MANAGEMENT
    # ============================================================
    
    def check_risk_limits(self) -> Dict[str, Any]:
        """Check if any risk limits are exceeded"""
        if not self.current_risk_metrics:
            return {"status": "No risk data available"}
        
        violations = []
        
        # Check limits
        limits = self.risk.limits
        metrics = self.current_risk_metrics
        
        checks = [
            ("total_risk", metrics.total_risk, limits.max_total_risk),
            ("drawdown", metrics.current_drawdown, limits.max_drawdown),
            ("var_95", metrics.var_95, limits.max_var_95)
        ]
        
        for name, value, limit in checks:
            if value > limit:
                violations.append({
                    "type": name,
                    "value": value,
                    "limit": limit,
                    "excess_percent": (value - limit) / limit * 100
                })
        
        return {
            "status": "VIOLATION" if violations else "OK",
            "violations": violations,
            "risk_level": self.risk.risk_level.value,
            "drawdown_status": metrics.drawdown_status.value
        }
    
    def get_risk_adjustment(self) -> Dict[str, float]:
        """Get risk adjustment factors"""
        if not self.current_risk_metrics:
            return {"multiplier": 1.0, "reason": "No risk data"}
        
        # Calculate adjustment based on risk level
        risk_level = self.risk.risk_level
        drawdown_status = self.current_risk_metrics.drawdown_status
        
        if drawdown_status.value == "crisis":
            return {"multiplier": 0.3, "reason": "Crisis drawdown"}
        elif drawdown_status.value == "drawdown":
            return {"multiplier": 0.6, "reason": "Significant drawdown"}
        elif risk_level.value == "extreme":
            return {"multiplier": 0.5, "reason": "Extreme risk level"}
        elif risk_level.value == "high":
            return {"multiplier": 0.7, "reason": "High risk level"}
        elif risk_level.value == "moderate":
            return {"multiplier": 0.9, "reason": "Moderate risk"}
        else:
            return {"multiplier": 1.0, "reason": "Normal risk"}
    
    # ============================================================
    # HELPER METHODS
    # ============================================================
    
    def _get_asset_returns(self) -> Dict[str, float]:
        """Get returns for all assets"""
        returns = {}
        for symbol in self.positions:
            # In production, get actual returns
            returns[symbol] = 0.001  # Placeholder
        return returns
    
    def _get_asset_volatilities(self) -> Dict[str, float]:
        """Get volatilities for all assets"""
        volatilities = {}
        for symbol in self.positions:
            if symbol in self.asset_data:
                volatilities[symbol] = self.asset_data[symbol]["dna"].volatility
            else:
                volatilities[symbol] = 0.20  # Default volatility
        return volatilities
    
    def _get_asset_correlations(self) -> Dict[str, Dict[str, float]]:
        """Get correlations between assets"""
        # In production, use actual correlation matrix
        return {}
    
    # ============================================================
    # REPORTING
    # ============================================================
    
    def get_full_status(self) -> Dict[str, Any]:
        """Get complete system status"""
        return {
            "capital": {
                "initial": self.initial_capital,
                "current": self.current_capital,
                "change": self.current_capital - self.initial_capital
            },
            "portfolio": {
                "allocation": self.current_allocation.allocations if self.current_allocation else {},
                "expected_return": self.current_allocation.expected_return if self.current_allocation else 0,
                "expected_sharpe": self.current_allocation.expected_sharpe if self.current_allocation else 0
            },
            "risk": self.current_risk_metrics.to_dict() if self.current_risk_metrics else {},
            "risk_summary": self.risk.get_risk_summary(),
            "positions": self.positions,
            "asset_count": len(self.asset_data)
        }
    
    def get_management_report(self) -> str:
        """Get human-readable management report"""
        lines = [
            "=" * 70,
            "PORTFOLIO MANAGEMENT REPORT",
            "=" * 70,
            f"Capital: ${self.current_capital:,.2f}",
            "",
            "ALLOCATION:",
        ]
        
        if self.current_allocation:
            top = self.current_allocation.get_top_allocations(5)
            for symbol, weight in top:
                lines.append(f"  {symbol}: {weight:.1%}")
        
        lines.append("")
        lines.append("RISK STATUS:")
        
        if self.current_risk_metrics:
            m = self.current_risk_metrics
            lines.append(f"  Total Risk: {m.total_risk:.2%}")
            lines.append(f"  Drawdown: {m.current_drawdown:.2%}")
            lines.append(f"  VaR 95%: {m.var_95:.2%}")
            lines.append(f"  Risk Level: {self.risk.risk_level.value.upper()}")
        
        # Risk adjustment
        adjustment = self.get_risk_adjustment()
        lines.append("")
        lines.append(f"RISK ADJUSTMENT: {adjustment['multiplier']:.1f}x ({adjustment['reason']})")
        
        # Risk limits check
        check = self.check_risk_limits()
        lines.append("")
        lines.append(f"LIMIT STATUS: {check['status']}")
        
        lines.append("=" * 70)
        
        return "\n".join(lines)

# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    print("\n" + "=" * 70)
    print("PORTFOLIO MANAGEMENT SYSTEM TEST")
    print("=" * 70)
    
    # Create system
    system = PortfolioManagementSystem(initial_capital=100000)
    
    # Add assets
    assets = [
        AssetDNA("AAPL", sector="Tech", expected_return=0.15, volatility=0.25, quality_score=0.85, beta=1.1),
        AssetDNA("GOOGL", sector="Tech", expected_return=0.12, volatility=0.28, quality_score=0.82, beta=1.0),
        AssetDNA("MSFT", sector="Tech", expected_return=0.14, volatility=0.22, quality_score=0.88, beta=0.95),
        AssetDNA("AMZN", sector="Consumer", expected_return=0.18, volatility=0.35, quality_score=0.75, beta=1.2),
        AssetDNA("JPM", sector="Financial", expected_return=0.08, volatility=0.20, quality_score=0.65, beta=0.85),
    ]
    system.add_assets(assets)
    
    print(f"\n✅ Added {len(assets)} assets")
    
    # Run analysis
    print("\n📊 Running portfolio analysis...")
    allocation = system.analyze_and_allocate()
    
    # Show report
    print("\n" + system.get_management_report())
    
    # Show rebalance signals
    print("\n📈 Rebalance Signals:")
    signals = system.get_rebalance_signals()
    for symbol, signal in signals.items():
        if signal["action"] != "HOLD":
            print(f"  {symbol}: {signal['action']} {signal['volume']:.2f} units")
    
    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)
