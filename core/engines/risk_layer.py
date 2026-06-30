"""
Institutional Risk Layer - Complete Risk Management
Version: 2.0.0
Date: 2026-06-30
Status: INSTITUTIONAL - COMPREHENSIVE RISK MANAGEMENT

Integrates:
- Portfolio Risk
- Sector Risk
- Correlation Risk
- Volatility Scaling
- Dynamic Risk
- Drawdown Scaling
- Capital State
- Regime Risk
"""

import logging
import math
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import numpy as np

# ============================================================================
# RISK ENUMS
# ============================================================================

class RiskLevel(Enum):
    """Risk level categories"""
    MINIMAL = "minimal"      # 0-10% risk
    LOW = "low"              # 10-25% risk
    MODERATE = "moderate"    # 25-50% risk
    HIGH = "high"            # 50-75% risk
    EXTREME = "extreme"      # 75-100% risk

class DrawdownStatus(Enum):
    """Drawdown status"""
    NORMAL = "normal"
    WARNING = "warning"
    DRAWDOWN = "drawdown"
    CRISIS = "crisis"

# ============================================================================
# RISK DATA STRUCTURES
# ============================================================================

@dataclass
class RiskMetrics:
    """Complete risk metrics for portfolio"""
    # Portfolio risk
    total_risk: float = 0.0
    systematic_risk: float = 0.0
    idiosyncratic_risk: float = 0.0
    
    # Position risk
    position_risks: Dict[str, float] = field(default_factory=dict)
    concentration_risk: float = 0.0
    correlation_risk: float = 0.0
    
    # Sector risk
    sector_risks: Dict[str, float] = field(default_factory=dict)
    max_sector_risk: float = 0.0
    
    # Drawdown risk
    current_drawdown: float = 0.0
    max_drawdown: float = 0.0
    drawdown_status: DrawdownStatus = DrawdownStatus.NORMAL
    
    # Tail risk
    var_95: float = 0.0
    var_99: float = 0.0
    cvar_95: float = 0.0
    expected_shortfall: float = 0.0
    
    # Risk ratios
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    calmar_ratio: float = 0.0
    
    # Volatility
    current_volatility: float = 0.0
    historical_volatility: float = 0.0
    volatility_scaling: float = 1.0
    
    # Capital risk
    capital_at_risk: float = 0.0
    risk_of_ruin: float = 0.0
    
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            "total_risk": self.total_risk,
            "current_drawdown": self.current_drawdown,
            "var_95": self.var_95,
            "sharpe_ratio": self.sharpe_ratio,
            "drawdown_status": self.drawdown_status.value
        }

@dataclass
class RiskLimits:
    """Institutional risk limits"""
    # Portfolio limits
    max_total_risk: float = 0.15      # 15% max total risk
    max_var_95: float = 0.05          # 5% VaR limit
    
    # Position limits
    max_position_risk: float = 0.03   # 3% risk per position
    max_concentration: float = 0.20   # 20% max concentration
    
    # Sector limits
    max_sector_risk: float = 0.05     # 5% risk per sector
    
    # Drawdown limits
    max_drawdown: float = 0.20        # 20% max drawdown
    drawdown_warning: float = 0.10    # 10% warning level
    drawdown_stop: float = 0.15       # 15% stop level
    
    # Capital risk
    max_capital_at_risk: float = 0.10 # 10% capital at risk
    max_risk_of_ruin: float = 0.01    # 1% risk of ruin
    
    # Volatility limits
    volatility_ceiling: float = 0.30  # 30% max volatility
    volatility_floor: float = 0.05    # 5% min volatility
    
    def to_dict(self) -> Dict:
        return {
            "max_total_risk": self.max_total_risk,
            "max_drawdown": self.max_drawdown,
            "max_var_95": self.max_var_95,
            "max_position_risk": self.max_position_risk,
            "max_concentration": self.max_concentration
        }

# ============================================================================
# RISK LAYER - COMPLETE IMPLEMENTATION
# ============================================================================

class RiskLayer:
    """
    Institutional Risk Layer
    
    Provides comprehensive risk management including:
    - Portfolio risk aggregation
    - Position and sector risk monitoring
    - Drawdown management
    - Dynamic risk scaling
    - Correlation risk
    - Regime-based risk adjustment
    """
    
    def __init__(self, limits: Optional[RiskLimits] = None):
        self.limits = limits or RiskLimits()
        self.current_metrics: Optional[RiskMetrics] = None
        self.risk_history: List[RiskMetrics] = []
        
        # Drawdown tracking
        self.peak_equity: float = 0.0
        self.current_drawdown: float = 0.0
        self.max_drawdown_observed: float = 0.0
        
        # Volatility tracking
        self.volatility_history: List[float] = []
        self.volatility_ewma: float = 0.15  # Start with 15%
        
        # Risk events
        self.risk_events: List[Dict] = []
        self.risk_level: RiskLevel = RiskLevel.MODERATE
        
        # Correlation matrix
        self.correlation_matrix: Dict[str, Dict[str, float]] = {}
        
        logging.info("=" * 70)
        logging.info("RISK LAYER INITIALIZED")
        logging.info("=" * 70)
        logging.info(f"Risk Limits: {json.dumps(self.limits.to_dict(), indent=2)}")
    
    # ============================================================
    # CORE RISK CALCULATION
    # ============================================================
    
    def calculate_risk(self,
                      positions: Dict[str, float],  # symbol -> value
                      returns: Dict[str, float],     # symbol -> return
                      asset_volatilities: Dict[str, float],
                      asset_correlations: Dict[str, Dict[str, float]]) -> RiskMetrics:
        """Calculate comprehensive portfolio risk"""
        
        total_value = sum(positions.values())
        if total_value == 0:
            return RiskMetrics()
        
        # Calculate position weights
        weights = {symbol: value / total_value for symbol, value in positions.items()}
        
        # ============================================================
        # 1. PORTFOLIO RISK
        # ============================================================
        
        # Systematic risk (market risk)
        beta = 1.0  # Placeholder - should come from market data
        market_volatility = 0.15  # Placeholder
        systematic_risk = beta * market_volatility
        
        # Idiosyncratic risk
        weighted_volatility = sum(weights.get(sym, 0) * asset_volatilities.get(sym, 0.2) 
                                 for sym in positions.keys())
        idiosyncratic_risk = weighted_volatility * 0.5  # Simplified
        
        # Total risk
        total_risk = math.sqrt(systematic_risk**2 + idiosyncratic_risk**2)
        
        # ============================================================
        # 2. POSITION RISK
        # ============================================================
        
        position_risks = {}
        for symbol, weight in weights.items():
            vol = asset_volatilities.get(symbol, 0.2)
            position_risks[symbol] = weight * vol
        
        # Concentration risk
        top_weight = max(weights.values()) if weights else 0
        concentration_risk = top_weight * 2  # Scaled concentration risk
        
        # ============================================================
        # 3. SECTOR RISK
        # ============================================================
        
        sector_risks = {}
        for symbol, weight in weights.items():
            sector = "Unknown"  # Should come from asset data
            sector_risks[sector] = sector_risks.get(sector, 0) + weight
        
        # ============================================================
        # 4. CORRELATION RISK
        # ============================================================
        
        correlation_risk = 0
        if len(positions) > 1:
            avg_correlation = 0.5  # Default
            # Calculate average correlation
            correlations = []
            symbols = list(positions.keys())
            for i in range(len(symbols)):
                for j in range(i + 1, len(symbols)):
                    corr = asset_correlations.get(symbols[i], {}).get(symbols[j], 0.5)
                    correlations.append(corr)
            if correlations:
                avg_correlation = sum(correlations) / len(correlations)
            correlation_risk = avg_correlation * total_risk
        
        # ============================================================
        # 5. VAR AND TAIL RISK
        # ============================================================
        
        # Value at Risk (assume normal distribution)
        z_95 = 1.645
        z_99 = 2.326
        var_95 = z_95 * total_risk
        var_99 = z_99 * total_risk
        
        # Conditional VaR (Expected Shortfall)
        cvar_95 = 2.063 * total_risk  # For normal distribution
        
        # ============================================================
        # 6. VOLATILITY METRICS
        # ============================================================
        
        # Update volatility tracking
        self.volatility_history.append(total_risk)
        if len(self.volatility_history) > 100:
            self.volatility_history = self.volatility_history[-100:]
        
        # EWMA volatility
        if self.volatility_ewma:
            lambda_ewma = 0.94  # Standard EWMA decay factor
            self.volatility_ewma = lambda_ewma * self.volatility_ewma + (1 - lambda_ewma) * total_risk
        else:
            self.volatility_ewma = total_risk
        
        # Volatility scaling
        baseline_vol = 0.15
        volatility_scaling = baseline_vol / max(self.volatility_ewma, 0.01)
        
        # ============================================================
        # 7. DRAWDOWN
        # ============================================================
        
        # Update drawdown tracking
        total_return = sum(weights.get(sym, 0) * returns.get(sym, 0) for sym in positions.keys())
        self._update_drawdown(total_return, total_value)
        
        # ============================================================
        # 8. RISK RATIOS
        # ============================================================
        
        # Sharpe ratio
        risk_free_rate = 0.02
        average_return = total_return / 252  # Daily to annual conversion
        sharpe_ratio = (average_return - risk_free_rate) / total_risk if total_risk > 0 else 0
        
        # Sortino ratio (downside risk only)
        sortino_ratio = (average_return - risk_free_rate) / (total_risk * 0.7) if total_risk > 0 else 0
        
        # Calmar ratio
        calmar_ratio = average_return / self.max_drawdown_observed if self.max_drawdown_observed > 0 else 0
        
        # ============================================================
        # 9. CAPITAL RISK
        # ============================================================
        
        capital_at_risk = total_risk * total_value
        risk_of_ruin = math.exp(-2 * average_return / total_risk) if total_risk > 0 else 0
        
        # ============================================================
        # CREATE RISK METRICS
        # ============================================================
        
        metrics = RiskMetrics(
            total_risk=total_risk,
            systematic_risk=systematic_risk,
            idiosyncratic_risk=idiosyncratic_risk,
            position_risks=position_risks,
            concentration_risk=concentration_risk,
            correlation_risk=correlation_risk,
            sector_risks=sector_risks,
            max_sector_risk=max(sector_risks.values()) if sector_risks else 0,
            current_drawdown=self.current_drawdown,
            max_drawdown=self.max_drawdown_observed,
            drawdown_status=self._get_drawdown_status(),
            var_95=var_95,
            var_99=var_99,
            cvar_95=cvar_95,
            expected_shortfall=cvar_95,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            calmar_ratio=calmar_ratio,
            current_volatility=total_risk,
            historical_volatility=self.volatility_ewma,
            volatility_scaling=volatility_scaling,
            capital_at_risk=capital_at_risk,
            risk_of_ruin=risk_of_ruin
        )
        
        # Store and update
        self.current_metrics = metrics
        self.risk_history.append(metrics)
        
        # Update risk level
        self.risk_level = self._calculate_risk_level(metrics)
        
        # Check for violations
        self._check_risk_limits(metrics)
        
        return metrics
    
    # ============================================================
    # DRAWDOWN MANAGEMENT
    # ============================================================
    
    def _update_drawdown(self, daily_return: float, current_equity: float):
        """Update drawdown tracking"""
        # Update peak equity
        if current_equity > self.peak_equity:
            self.peak_equity = current_equity
        
        # Calculate current drawdown
        if self.peak_equity > 0:
            self.current_drawdown = (self.peak_equity - current_equity) / self.peak_equity
        else:
            self.current_drawdown = 0
        
        # Update max drawdown
        if self.current_drawdown > self.max_drawdown_observed:
            self.max_drawdown_observed = self.current_drawdown
    
    def _get_drawdown_status(self) -> DrawdownStatus:
        """Get current drawdown status"""
        if self.current_drawdown >= self.limits.drawdown_stop:
            return DrawdownStatus.CRISIS
        elif self.current_drawdown >= self.limits.drawdown_warning:
            return DrawdownStatus.DRAWDOWN
        elif self.current_drawdown >= self.limits.drawdown_warning * 0.5:
            return DrawdownStatus.WARNING
        return DrawdownStatus.NORMAL
    
    # ============================================================
    # RISK LEVEL CALCULATION
    # ============================================================
    
    def _calculate_risk_level(self, metrics: RiskMetrics) -> RiskLevel:
        """Calculate overall risk level"""
        # Multiple factors
        risk_factors = {
            "total_risk": metrics.total_risk / self.limits.max_total_risk,
            "var_95": metrics.var_95 / self.limits.max_var_95,
            "drawdown": metrics.current_drawdown / self.limits.max_drawdown,
            "concentration": metrics.concentration_risk / self.limits.max_concentration
        }
        
        # Average risk factor (weighted)
        weights = {"total_risk": 0.4, "var_95": 0.3, "drawdown": 0.2, "concentration": 0.1}
        risk_score = sum(risk_factors[k] * weights[k] for k in risk_factors)
        
        # Map to risk level
        if risk_score < 0.25:
            return RiskLevel.MINIMAL
        elif risk_score < 0.50:
            return RiskLevel.LOW
        elif risk_score < 0.75:
            return RiskLevel.MODERATE
        elif risk_score < 0.90:
            return RiskLevel.HIGH
        else:
            return RiskLevel.EXTREME
    
    # ============================================================
    # RISK LIMIT CHECKS
    # ============================================================
    
    def _check_risk_limits(self, metrics: RiskMetrics):
        """Check if risk limits are exceeded"""
        violations = []
        
        # Check each limit
        checks = [
            ("total_risk", metrics.total_risk, self.limits.max_total_risk),
            ("var_95", metrics.var_95, self.limits.max_var_95),
            ("drawdown", metrics.current_drawdown, self.limits.max_drawdown),
            ("concentration", metrics.concentration_risk, self.limits.max_concentration)
        ]
        
        for name, value, limit in checks:
            if value > limit:
                violations.append({
                    "type": name,
                    "value": value,
                    "limit": limit,
                    "excess": (value - limit) / limit * 100
                })
        
        if violations:
            logging.warning(f"Risk limit violations: {json.dumps(violations, indent=2)}")
            # Store risk event
            self.risk_events.append({
                "timestamp": datetime.now().isoformat(),
                "violations": violations,
                "metrics": metrics.to_dict()
            })
            
            # Trigger alerts based on severity
            for violation in violations:
                if violation["excess"] > 20:
                    logging.error(f"SEVERE: {violation['type']} exceeded by {violation['excess']:.1f}%")
                elif violation["excess"] > 10:
                    logging.warning(f"WARNING: {violation['type']} exceeded by {violation['excess']:.1f}%")
    
    # ============================================================
    # RISK ADJUSTMENT
    # ============================================================
    
    def calculate_position_size_adjustment(self, 
                                         symbol: str,
                                         base_size: float,
                                         risk_metrics: RiskMetrics) -> float:
        """Adjust position size based on current risk"""
        if symbol not in risk_metrics.position_risks:
            return base_size
        
        # Risk scaling factor
        position_risk = risk_metrics.position_risks[symbol]
        if position_risk == 0:
            return base_size
        
        # Calculate adjustment factor
        # Lower risk -> higher allocation, higher risk -> lower allocation
        target_risk_per_position = 0.02  # 2% risk per position
        adjustment = target_risk_per_position / position_risk
        adjustment = min(max(adjustment, 0.5), 2.0)  # Cap between 0.5x and 2x
        
        # Apply drawdown adjustment
        if risk_metrics.drawdown_status == DrawdownStatus.CRISIS:
            adjustment *= 0.5
        elif risk_metrics.drawdown_status == DrawdownStatus.DRAWDOWN:
            adjustment *= 0.7
        
        # Apply risk level adjustment
        if self.risk_level == RiskLevel.EXTREME:
            adjustment *= 0.5
        elif self.risk_level == RiskLevel.HIGH:
            adjustment *= 0.75
        
        return base_size * adjustment
    
    def get_risk_adjusted_weights(self, 
                                 weights: Dict[str, float],
                                 risk_metrics: RiskMetrics) -> Dict[str, float]:
        """Get risk-adjusted weights for portfolio"""
        if not weights or not risk_metrics:
            return weights
        
        adjusted = {}
        total_risk_weight = 0
        
        for symbol, weight in weights.items():
            if symbol in risk_metrics.position_risks:
                risk = risk_metrics.position_risks[symbol]
                if risk > 0:
                    # Inverse risk weighting
                    adjusted_weight = weight * (1 / risk)
                    adjusted[symbol] = adjusted_weight
                    total_risk_weight += adjusted_weight
        
        # Normalize
        if total_risk_weight > 0:
            adjusted = {k: v / total_risk_weight for k, v in adjusted.items()}
        
        return adjusted
    
    # ============================================================
    # REGIME RISK ADJUSTMENT
    # ============================================================
    
    def apply_regime_adjustment(self,
                               metrics: RiskMetrics,
                               regime: str) -> Dict[str, float]:
        """Apply risk adjustments based on market regime"""
        adjustments = {
            "bullish": {"position_multiplier": 1.2, "risk_multiplier": 1.0},
            "bearish": {"position_multiplier": 0.7, "risk_multiplier": 0.8},
            "volatile": {"position_multiplier": 0.6, "risk_multiplier": 0.7},
            "crisis": {"position_multiplier": 0.3, "risk_multiplier": 0.5},
            "neutral": {"position_multiplier": 1.0, "risk_multiplier": 1.0}
        }
        
        adj = adjustments.get(regime, adjustments["neutral"])
        
        return {
            "position_size_multiplier": adj["position_multiplier"],
            "risk_cap_multiplier": adj["risk_multiplier"],
            "risk_level": self.risk_level.value
        }
    
    # ============================================================
    # RISK REPORTING
    # ============================================================
    
    def get_risk_summary(self) -> Dict[str, Any]:
        """Get complete risk summary"""
        if not self.current_metrics:
            return {"status": "No risk data available"}
        
        return {
            "current_risk_level": self.risk_level.value,
            "drawdown_status": self.current_metrics.drawdown_status.value,
            "current_drawdown": self.current_metrics.current_drawdown,
            "max_drawdown": self.current_metrics.max_drawdown,
            "total_risk": self.current_metrics.total_risk,
            "var_95": self.current_metrics.var_95,
            "sharpe_ratio": self.current_metrics.sharpe_ratio,
            "capital_at_risk": self.current_metrics.capital_at_risk,
            "risk_of_ruin": self.current_metrics.risk_of_ruin,
            "volatility_scaling": self.current_metrics.volatility_scaling,
            "risk_events_count": len(self.risk_events),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_risk_report(self) -> str:
        """Get human-readable risk report"""
        if not self.current_metrics:
            return "No risk data available"
        
        m = self.current_metrics
        
        lines = [
            "=" * 70,
            "RISK REPORT",
            "=" * 70,
            f"Risk Level: {self.risk_level.value.upper()}",
            f"Drawdown Status: {m.drawdown_status.value.upper()}",
            "",
            "PORTFOLIO RISK:",
            f"  Total Risk: {m.total_risk:.2%}",
            f"  Systematic: {m.systematic_risk:.2%}",
            f"  Idiosyncratic: {m.idiosyncratic_risk:.2%}",
            "",
            "TAIL RISK:",
            f"  VaR 95%: {m.var_95:.2%}",
            f"  VaR 99%: {m.var_99:.2%}",
            f"  CVaR 95%: {m.cvar_95:.2%}",
            "",
            "DRAWDOWN:",
            f"  Current: {m.current_drawdown:.2%}",
            f"  Maximum: {m.max_drawdown:.2%}",
            "",
            "RISK RATIOS:",
            f"  Sharpe: {m.sharpe_ratio:.2f}",
            f"  Sortino: {m.sortino_ratio:.2f}",
            f"  Calmar: {m.calmar_ratio:.2f}",
            "",
            "CAPITAL RISK:",
            f"  Capital at Risk: ${m.capital_at_risk:,.2f}",
            f"  Risk of Ruin: {m.risk_of_ruin:.2%}",
            "=" * 70
        ]
        
        return "\n".join(lines)

# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    import json
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    print("\n" + "=" * 70)
    print("RISK LAYER TEST")
    print("=" * 70)
    
    # Create risk layer
    risk_layer = RiskLayer()
    
    # Test positions
    positions = {"AAPL": 50000, "GOOGL": 30000, "MSFT": 20000}
    returns = {"AAPL": 0.001, "GOOGL": 0.002, "MSFT": -0.001}
    volatilities = {"AAPL": 0.25, "GOOGL": 0.28, "MSFT": 0.22}
    correlations = {
        "AAPL": {"GOOGL": 0.6, "MSFT": 0.7},
        "GOOGL": {"AAPL": 0.6, "MSFT": 0.5},
        "MSFT": {"AAPL": 0.7, "GOOGL": 0.5}
    }
    
    print("\n📊 Calculating risk metrics...")
    metrics = risk_layer.calculate_risk(positions, returns, volatilities, correlations)
    
    # Print report
    print("\n" + risk_layer.get_risk_report())
    
    # Test risk adjustment
    print("\n📈 Testing risk-adjusted weights...")
    weights = {"AAPL": 0.5, "GOOGL": 0.3, "MSFT": 0.2}
    adjusted = risk_layer.get_risk_adjusted_weights(weights, metrics)
    print(f"Original weights: {weights}")
    print(f"Adjusted weights: {adjusted}")
    
    # Test regime adjustment
    print("\n🌍 Testing regime adjustments...")
    for regime in ["bullish", "bearish", "crisis"]:
        adj = risk_layer.apply_regime_adjustment(metrics, regime)
        print(f"  {regime}: position_multiplier={adj['position_size_multiplier']}")
    
    print("\n" + "=" * 70)
    print("RISK LAYER TEST COMPLETE")
    print("=" * 70)
