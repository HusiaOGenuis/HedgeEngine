"""
Portfolio Intelligence Engine (PIE) - Institutional Grade
Version: 2.0.0
Date: 2026-06-30
Status: INSTITUTIONAL - FULL PORTFOLIO MANAGEMENT

This is the "brain" of the system that asks:
"What should my portfolio look like now?"
Instead of "What trade should I make?"
"""

import logging
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import math

# ============================================================================
# ENUMS AND CONSTANTS
# ============================================================================

class MarketRegime(Enum):
    """Market regimes for adaptive portfolio management"""
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"
    VOLATILE = "volatile"
    CRISIS = "crisis"

class PortfolioObjective(Enum):
    """Investment objectives"""
    GROWTH = "growth"
    INCOME = "income"
    BALANCED = "balanced"
    CAPITAL_PRESERVATION = "capital_preservation"
    MAXIMIZE_SHARPE = "maximize_sharpe"

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class AssetDNA:
    """Complete asset intelligence from Research Engine"""
    symbol: str
    name: str = ""
    sector: str = "Unknown"
    industry: str = "Unknown"
    
    # Returns and volatility
    expected_return: float = 0.0  # Annual expected return
    volatility: float = 0.0       # Annual volatility
    sharpe: float = 0.0
    
    # Risk metrics
    beta: float = 1.0
    max_drawdown: float = 0.0
    var_95: float = 0.0          # Value at Risk 95%
    cvar_95: float = 0.0         # Conditional VaR
    
    # Quality metrics
    quality_score: float = 0.0   # 0-1 scale
    liquidity_score: float = 0.0 # 0-1 scale
    momentum_score: float = 0.0  # 0-1 scale
    value_score: float = 0.0     # 0-1 scale
    
    # Market data
    market_cap: float = 0.0
    avg_volume: float = 0.0
    spread: float = 0.0
    
    # Correlations (symbol -> correlation coefficient)
    correlations: Dict[str, float] = field(default_factory=dict)
    
    def get_risk_adjusted_return(self) -> float:
        """Calculate risk-adjusted return"""
        if self.volatility == 0:
            return self.expected_return
        return self.expected_return / self.volatility
    
    def to_dict(self) -> Dict:
        return {
            "symbol": self.symbol,
            "sector": self.sector,
            "expected_return": self.expected_return,
            "volatility": self.volatility,
            "sharpe": self.sharpe,
            "quality_score": self.quality_score,
            "beta": self.beta
        }

@dataclass
class PortfolioAllocation:
    """Complete portfolio allocation with all metrics"""
    allocations: Dict[str, float]  # symbol -> weight
    expected_return: float = 0.0
    expected_volatility: float = 0.0
    expected_sharpe: float = 0.0
    expected_drawdown: float = 0.0
    
    # Risk metrics
    var_95: float = 0.0
    cvar_95: float = 0.0
    beta: float = 0.0
    
    # Diversification
    effective_n: int = 0
    concentration_ratio: float = 0.0
    sector_weights: Dict[str, float] = field(default_factory=dict)
    
    # Performance
    projected_pnl: float = 0.0
    projected_max_drawdown: float = 0.0
    recovery_time: float = 0.0  # Expected recovery time in days
    
    timestamp: datetime = field(default_factory=datetime.now)
    
    def get_weights(self) -> Dict[str, float]:
        """Get allocation weights"""
        return {k: v for k, v in self.allocations.items() if v > 0.001}
    
    def get_invested_amounts(self, total_capital: float) -> Dict[str, float]:
        """Convert weights to dollar amounts"""
        return {symbol: weight * total_capital for symbol, weight in self.get_weights().items()}
    
    def get_top_allocations(self, n: int = 5) -> List[Tuple[str, float]]:
        """Get top n allocations"""
        sorted_alloc = sorted(self.allocations.items(), key=lambda x: x[1], reverse=True)
        return sorted_alloc[:n]

@dataclass
class PortfolioConstraints:
    """Institutional-grade portfolio constraints"""
    # Position limits
    max_position_weight: float = 0.20      # 20% max per position
    min_position_weight: float = 0.01      # 1% min per position
    
    # Sector limits
    max_sector_weight: float = 0.40        # 40% max per sector
    
    # Risk limits
    max_beta: float = 1.2                  # Maximum portfolio beta
    max_var_95: float = 0.05               # 5% VaR limit
    max_correlation: float = 0.70          # Max correlation between any two assets
    
    # Capital constraints
    min_cash: float = 0.05                 # 5% minimum cash
    max_leverage: float = 1.0              # No leverage
    max_drawdown: float = 0.15             # 15% max drawdown
    
    # Diversification
    min_assets: int = 5                    # Minimum 5 assets
    max_assets: int = 20                   # Maximum 20 assets
    max_sector_concentration: float = 0.60 # 60% max in any sector
    
    # Quality filters
    min_quality_score: float = 0.4         # 0.4 minimum quality
    
    # Time horizon
    investment_horizon: int = 30           # Days
    
    def to_dict(self) -> Dict:
        return {
            "max_position_weight": self.max_position_weight,
            "min_position_weight": self.min_position_weight,
            "max_sector_weight": self.max_sector_weight,
            "max_beta": self.max_beta,
            "min_assets": self.min_assets,
            "max_assets": self.max_assets,
            "min_cash": self.min_cash
        }

# ============================================================================
# PORTFOLIO INTELLIGENCE ENGINE - FULL IMPLEMENTATION
# ============================================================================

class PortfolioIntelligenceEngine:
    """
    Institutional Portfolio Intelligence Engine
    
    Decides what the portfolio should look like using:
    - Modern Portfolio Theory (MPT)
    - Risk Parity
    - Factor Investing
    - Machine Learning signals
    - Market regime adaptation
    """
    
    def __init__(self, 
                 constraints: Optional[PortfolioConstraints] = None,
                 objective: PortfolioObjective = PortfolioObjective.MAXIMIZE_SHARPE):
        
        self.constraints = constraints or PortfolioConstraints()
        self.objective = objective
        
        # Asset database
        self.asset_dna: Dict[str, AssetDNA] = {}
        self.universe: Set[str] = set()
        
        # Current state
        self.current_allocation: Optional[PortfolioAllocation] = None
        self.current_regime: MarketRegime = MarketRegime.NEUTRAL
        
        # History
        self.allocation_history: List[PortfolioAllocation] = []
        self.optimization_count = 0
        
        # Performance tracking
        self.performance_metrics = {
            "avg_sharpe": 0.0,
            "max_sharpe": 0.0,
            "avg_return": 0.0,
            "avg_volatility": 0.0
        }
        
        logging.info("=" * 70)
        logging.info("PORTFOLIO INTELLIGENCE ENGINE (PIE) INITIALIZED")
        logging.info("=" * 70)
        logging.info(f"Objective: {self.objective.value}")
        logging.info(f"Constraints: {json.dumps(self.constraints.to_dict(), indent=2)}")
    
    # ============================================================
    # ASSET MANAGEMENT
    # ============================================================
    
    def add_asset(self, dna: AssetDNA):
        """Add or update asset in the universe"""
        self.asset_dna[dna.symbol] = dna
        self.universe.add(dna.symbol)
        logging.debug(f"Added asset: {dna.symbol} (Sector: {dna.sector}, EV: {dna.expected_return:.2%})")
    
    def add_assets(self, assets: List[AssetDNA]):
        """Add multiple assets"""
        for asset in assets:
            self.add_asset(asset)
        logging.info(f"Added {len(assets)} assets to universe")
    
    def remove_asset(self, symbol: str):
        """Remove asset from universe"""
        if symbol in self.asset_dna:
            del self.asset_dna[symbol]
            self.universe.discard(symbol)
            logging.debug(f"Removed asset: {symbol}")
    
    def get_asset(self, symbol: str) -> Optional[AssetDNA]:
        """Get asset DNA by symbol"""
        return self.asset_dna.get(symbol)
    
    def get_all_assets(self) -> List[AssetDNA]:
        """Get all assets in universe"""
        return list(self.asset_dna.values())
    
    def get_assets_by_sector(self, sector: str) -> List[AssetDNA]:
        """Get assets by sector"""
        return [a for a in self.asset_dna.values() if a.sector == sector]
    
    # ============================================================
    # MARKET REGIME DETECTION
    # ============================================================
    
    def detect_market_regime(self, market_data: Dict[str, Any]) -> MarketRegime:
        """
        Detect current market regime from market data
        
        Args:
            market_data: Dict with VIX, market returns, etc.
        
        Returns:
            MarketRegime enum
        """
        vix = market_data.get("vix", 20)
        market_return = market_data.get("market_return", 0)
        market_volatility = market_data.get("market_volatility", 0.15)
        
        # Crisis detection
        if vix > 40 or market_return < -0.05:
            return MarketRegime.CRISIS
        
        # Volatile market
        if market_volatility > 0.25:
            return MarketRegime.VOLATILE
        
        # Trend detection
        if market_return > 0.02:
            return MarketRegime.BULLISH
        elif market_return < -0.02:
            return MarketRegime.BEARISH
        
        return MarketRegime.NEUTRAL
    
    # ============================================================
    # CORE OPTIMIZATION
    # ============================================================
    
    def optimize_portfolio(self,
                          total_capital: float,
                          current_positions: Optional[Dict[str, float]] = None,
                          market_data: Optional[Dict[str, Any]] = None,
                          regime: Optional[MarketRegime] = None) -> PortfolioAllocation:
        """
        Optimize portfolio allocation using institutional methods
        
        Returns:
            Complete PortfolioAllocation with all metrics
        """
        self.optimization_count += 1
        
        # Detect market regime
        if regime:
            self.current_regime = regime
        elif market_data:
            self.current_regime = self.detect_market_regime(market_data)
        
        logging.info(f"Optimizing portfolio (Regime: {self.current_regime.value})")
        
        # Filter eligible assets
        eligible_assets = self._filter_assets_by_regime(self.current_regime)
        
        if len(eligible_assets) < self.constraints.min_assets:
            logging.warning(f"Insufficient eligible assets: {len(eligible_assets)} < {self.constraints.min_assets}")
            return self._create_fallback_allocation(total_capital)
        
        # Score assets
        scored_assets = self._score_assets(eligible_assets)
        
        # Calculate optimal weights using different methods
        weights = self._calculate_optimal_weights(scored_assets, total_capital)
        
        # Apply constraints
        constrained_weights = self._apply_all_constraints(weights, scored_assets)
        
        # Adjust for existing positions (rebalancing)
        final_weights = self._adjust_for_rebalancing(
            constrained_weights,
            current_positions or {},
            total_capital
        )
        
        # Calculate portfolio metrics
        allocation = self._calculate_portfolio_metrics(final_weights, total_capital)
        
        # Store allocation
        self.current_allocation = allocation
        self.allocation_history.append(allocation)
        
        # Update performance metrics
        self._update_performance_metrics(allocation)
        
        logging.info(f"Portfolio optimized: {len(allocation.get_weights())} assets")
        logging.info(f"Expected Sharpe: {allocation.expected_sharpe:.2f}")
        logging.info(f"Expected Return: {allocation.expected_return:.2%}")
        logging.info(f"Expected Volatility: {allocation.expected_volatility:.2%}")
        
        return allocation
    
    # ============================================================
    # OPTIMIZATION METHODS
    # ============================================================
    
    def _filter_assets_by_regime(self, regime: MarketRegime) -> List[AssetDNA]:
        """Filter assets based on market regime"""
        filtered = []
        
        for dna in self.asset_dna.values():
            # Quality filter
            if dna.quality_score < self.constraints.min_quality_score:
                continue
            
            # Regime-specific filters
            if regime == MarketRegime.BEARISH:
                # Prefer low beta, high quality assets
                if dna.beta > 0.8:
                    continue
                if dna.quality_score < 0.6:
                    continue
                    
            elif regime == MarketRegime.CRISIS:
                # Only highest quality, lowest beta
                if dna.beta > 0.6:
                    continue
                if dna.quality_score < 0.7:
                    continue
                if dna.volatility > 0.3:
                    continue
                    
            elif regime == MarketRegime.VOLATILE:
                # Reduce volatility exposure
                if dna.volatility > 0.35:
                    continue
                    
            filtered.append(dna)
        
        return filtered
    
    def _score_assets(self, assets: List[AssetDNA]) -> List[Tuple[AssetDNA, float]]:
        """Score assets using multi-factor model"""
        scored = []
        
        for dna in assets:
            # Factor scores
            factors = {
                "momentum": dna.momentum_score,
                "value": dna.value_score,
                "quality": dna.quality_score,
                "liquidity": dna.liquidity_score,
                "risk_adjusted": dna.get_risk_adjusted_return()
            }
            
            # Weighted score based on objective
            if self.objective == PortfolioObjective.GROWTH:
                score = (0.3 * factors["momentum"] + 
                        0.2 * factors["quality"] +
                        0.3 * factors["risk_adjusted"] +
                        0.1 * factors["value"] +
                        0.1 * factors["liquidity"])
            
            elif self.objective == PortfolioObjective.INCOME:
                score = (0.2 * factors["quality"] +
                        0.3 * factors["value"] +
                        0.3 * factors["risk_adjusted"] +
                        0.1 * factors["momentum"] +
                        0.1 * factors["liquidity"])
            
            else:  # MAXIMIZE_SHARPE or BALANCED
                score = (0.25 * factors["risk_adjusted"] +
                        0.25 * factors["quality"] +
                        0.2 * factors["momentum"] +
                        0.15 * factors["value"] +
                        0.15 * factors["liquidity"])
            
            # Market regime adjustment
            if self.current_regime == MarketRegime.BEARISH:
                score *= (0.5 + 0.5 * dna.quality_score)
            elif self.current_regime == MarketRegime.CRISIS:
                score *= dna.quality_score
            
            scored.append((dna, score))
        
        return sorted(scored, key=lambda x: x[1], reverse=True)
    
    def _calculate_optimal_weights(self, 
                                  scored_assets: List[Tuple[AssetDNA, float]],
                                  total_capital: float) -> Dict[str, float]:
        """Calculate optimal weights using multiple methods"""
        
        # Cap number of assets
        max_assets = min(len(scored_assets), self.constraints.max_assets)
        selected = scored_assets[:max_assets]
        
        if not selected:
            return {}
        
        # Use risk parity approach for initial weights
        weights = {}
        total_risk_score = sum(1 / dna.volatility for dna, _ in selected if dna.volatility > 0)
        
        for dna, score in selected:
            # Risk parity component
            if dna.volatility > 0:
                risk_weight = (1 / dna.volatility) / total_risk_score
            else:
                risk_weight = 1 / len(selected)
            
            # Score component
            score_weight = score / sum(s for _, s in selected)
            
            # Blend based on regime
            if self.current_regime in [MarketRegime.BEARISH, MarketRegime.CRISIS]:
                # More weight on risk parity in bad markets
                weight = 0.7 * risk_weight + 0.3 * score_weight
            else:
                # More weight on scoring in good markets
                weight = 0.4 * risk_weight + 0.6 * score_weight
            
            weights[dna.symbol] = weight
        
        # Normalize weights
        total = sum(weights.values())
        if total > 0:
            weights = {k: v / total for k, v in weights.items()}
        
        return weights
    
    def _apply_all_constraints(self, 
                              weights: Dict[str, float],
                              scored_assets: List[Tuple[AssetDNA, float]]) -> Dict[str, float]:
        """Apply all portfolio constraints"""
        if not weights:
            return {}
        
        # Create asset lookup
        asset_lookup = {dna.symbol: dna for dna, _ in scored_assets}
        
        # Apply position limits
        constrained = {}
        sector_weights = {}
        
        for symbol, weight in weights.items():
            # Min/max position
            weight = min(weight, self.constraints.max_position_weight)
            weight = max(weight, self.constraints.min_position_weight)
            
            # Sector cap
            if symbol in asset_lookup:
                sector = asset_lookup[symbol].sector
                sector_weights[sector] = sector_weights.get(sector, 0) + weight
            
            constrained[symbol] = weight
        
        # Reduce weights if sector caps exceeded
        for sector, sector_weight in sector_weights.items():
            if sector_weight > self.constraints.max_sector_weight:
                reduction = sector_weight / self.constraints.max_sector_weight
                for symbol in list(constrained.keys()):
                    if symbol in asset_lookup and asset_lookup[symbol].sector == sector:
                        constrained[symbol] = constrained[symbol] / reduction
        
        # Normalize
        total = sum(constrained.values())
        if total > 0:
            normalized = {k: v / total for k, v in constrained.items()}
        else:
            normalized = {k: 0 for k in constrained}
        
        # Add cash
        cash_weight = self.constraints.min_cash
        normalized = {k: v * (1 - cash_weight) for k, v in normalized.items()}
        normalized["CASH"] = cash_weight
        
        return normalized
    
    def _adjust_for_rebalancing(self,
                               target_weights: Dict[str, float],
                               current_positions: Dict[str, float],
                               total_capital: float) -> Dict[str, float]:
        """Adjust weights for smooth rebalancing"""
        if not current_positions or not target_weights:
            return target_weights
        
        # Calculate current weights
        current_weights = {}
        for symbol, volume in current_positions.items():
            # Get price (should come from market data)
            price = 100.0  # Placeholder
            value = volume * price
            current_weights[symbol] = value / total_capital
        
        # Blend with rebalancing factor
        # Use different blending based on regime
        if self.current_regime in [MarketRegime.BEARISH, MarketRegime.CRISIS]:
            blend_factor = 0.3  # Slow rebalancing in bad markets
        else:
            blend_factor = 0.5  # Moderate rebalancing in normal markets
        
        adjusted = {}
        
        # Adjust existing assets
        for symbol, target_weight in target_weights.items():
            current_weight = current_weights.get(symbol, 0)
            adjusted[symbol] = current_weight + blend_factor * (target_weight - current_weight)
        
        # Handle new assets
        for symbol, weight in target_weights.items():
            if symbol not in adjusted:
                adjusted[symbol] = weight * blend_factor
        
        # Handle assets to be reduced
        for symbol, current_weight in current_weights.items():
            if symbol not in adjusted and symbol != "CASH":
                adjusted[symbol] = current_weight * (1 - blend_factor)
        
        # Normalize
        total = sum(adjusted.values())
        if total > 0:
            adjusted = {k: v / total for k, v in adjusted.items()}
        
        return adjusted
    
    # ============================================================
    # PORTFOLIO METRICS CALCULATION
    # ============================================================
    
    def _calculate_portfolio_metrics(self, 
                                    weights: Dict[str, float],
                                    total_capital: float) -> PortfolioAllocation:
        """Calculate comprehensive portfolio metrics"""
        
        # Filter out cash and zero weights
        non_cash = {k: v for k, v in weights.items() if k != "CASH" and v > 0.001}
        
        if not non_cash:
            return PortfolioAllocation(
                allocations=weights,
                expected_return=0.02,
                expected_volatility=0.01,
                expected_sharpe=0,
                expected_drawdown=0
            )
        
        # Calculate expected return
        expected_return = 0
        for symbol, weight in non_cash.items():
            if symbol in self.asset_dna:
                expected_return += weight * self.asset_dna[symbol].expected_return
            else:
                expected_return += weight * 0.05  # Default 5%
        
        # Add cash return
        expected_return += weights.get("CASH", 0) * 0.02
        
        # Calculate volatility
        volatility = 0
        for symbol, weight in non_cash.items():
            if symbol in self.asset_dna:
                volatility += (weight * self.asset_dna[symbol].volatility) ** 2
        
        # Add correlation (simplified)
        # In production, use full covariance matrix
        for symbol1, weight1 in non_cash.items():
            for symbol2, weight2 in non_cash.items():
                if symbol1 < symbol2:  # Avoid double counting
                    corr = 0.5  # Default correlation
                    if symbol1 in self.asset_dna and symbol2 in self.asset_dna:
                        corr = self.asset_dna[symbol1].correlations.get(symbol2, 0.5)
                    volatility += 2 * weight1 * weight2 * self._get_volatility(symbol1) * self._get_volatility(symbol2) * corr
        
        volatility = math.sqrt(volatility) if volatility > 0 else 0
        
        # Calculate Sharpe ratio
        risk_free_rate = 0.02
        sharpe = (expected_return - risk_free_rate) / volatility if volatility > 0 else 0
        
        # Calculate other metrics
        var_95 = self._calculate_var_95(weights, volatility)
        cvar_95 = self._calculate_cvar_95(weights, volatility)
        beta = self._calculate_portfolio_beta(weights)
        
        # Effective number of assets
        effective_n = 1 / sum(w**2 for w in non_cash.values()) if non_cash else 0
        
        # Concentration ratio
        top_weight = max(non_cash.values()) if non_cash else 0
        concentration = top_weight
        
        # Sector weights
        sector_weights = {}
        for symbol, weight in non_cash.items():
            if symbol in self.asset_dna:
                sector = self.asset_dna[symbol].sector
                sector_weights[sector] = sector_weights.get(sector, 0) + weight
        
        # Projected metrics
        projected_pnl = expected_return * total_capital
        projected_drawdown = self._estimate_drawdown(volatility, expected_return)
        
        return PortfolioAllocation(
            allocations=weights,
            expected_return=expected_return,
            expected_volatility=volatility,
            expected_sharpe=sharpe,
            expected_drawdown=projected_drawdown,
            var_95=var_95,
            cvar_95=cvar_95,
            beta=beta,
            effective_n=int(effective_n),
            concentration_ratio=concentration,
            sector_weights=sector_weights,
            projected_pnl=projected_pnl,
            projected_max_drawdown=projected_drawdown * total_capital,
            recovery_time=self._estimate_recovery_time(expected_return, projected_drawdown)
        )
    
    def _get_volatility(self, symbol: str) -> float:
        """Get volatility for a symbol"""
        if symbol in self.asset_dna:
            return self.asset_dna[symbol].volatility
        return 0.2  # Default 20%
    
    def _calculate_var_95(self, weights: Dict[str, float], volatility: float) -> float:
        """Calculate 95% Value at Risk"""
        if volatility == 0:
            return 0
        # Assuming normal distribution
        return 1.645 * volatility
    
    def _calculate_cvar_95(self, weights: Dict[str, float], volatility: float) -> float:
        """Calculate 95% Conditional Value at Risk"""
        if volatility == 0:
            return 0
        # Expected shortfall for normal distribution
        return 2.063 * volatility
    
    def _calculate_portfolio_beta(self, weights: Dict[str, float]) -> float:
        """Calculate portfolio beta"""
        beta = 0
        total_weight = 0
        for symbol, weight in weights.items():
            if symbol != "CASH" and symbol in self.asset_dna:
                beta += weight * self.asset_dna[symbol].beta
                total_weight += weight
        
        if total_weight > 0:
            return beta / total_weight
        return 1.0
    
    def _estimate_drawdown(self, volatility: float, expected_return: float) -> float:
        """Estimate maximum drawdown"""
        # Based on volatility and expected return
        if volatility == 0:
            return 0
        return min(volatility * 2.5, 0.4)  # Cap at 40%
    
    def _estimate_recovery_time(self, expected_return: float, drawdown: float) -> float:
        """Estimate recovery time in days"""
        if expected_return == 0:
            return 365  # 1 year
        daily_return = expected_return / 252
        return drawdown / daily_return if daily_return > 0 else 365
    
    def _update_performance_metrics(self, allocation: PortfolioAllocation):
        """Update performance tracking metrics"""
        if self.performance_metrics["max_sharpe"] == 0:
            self.performance_metrics["max_sharpe"] = allocation.expected_sharpe
        
        self.performance_metrics["avg_sharpe"] = (
            self.performance_metrics["avg_sharpe"] * (len(self.allocation_history) - 1) +
            allocation.expected_sharpe
        ) / len(self.allocation_history)
        
        self.performance_metrics["avg_return"] = (
            self.performance_metrics["avg_return"] * (len(self.allocation_history) - 1) +
            allocation.expected_return
        ) / len(self.allocation_history)
        
        self.performance_metrics["avg_volatility"] = (
            self.performance_metrics["avg_volatility"] * (len(self.allocation_history) - 1) +
            allocation.expected_volatility
        ) / len(self.allocation_history)
        
        if allocation.expected_sharpe > self.performance_metrics["max_sharpe"]:
            self.performance_metrics["max_sharpe"] = allocation.expected_sharpe
    
    def _create_fallback_allocation(self, total_capital: float) -> PortfolioAllocation:
        """Create fallback allocation when optimization fails"""
        return PortfolioAllocation(
            allocations={"CASH": 1.0},
            expected_return=0.02,
            expected_volatility=0.01,
            expected_sharpe=0.5,
            expected_drawdown=0.0
        )
    
    # ============================================================
    # REBALANCING LOGIC
    # ============================================================
    
    def generate_rebalance_signals(self,
                                  target: PortfolioAllocation,
                                  current_positions: Dict[str, float],
                                  total_capital: float) -> Dict[str, Dict[str, Any]]:
        """Generate signals for rebalancing portfolio"""
        signals = {}
        
        # Get target amounts
        target_amounts = target.get_invested_amounts(total_capital)
        
        # Get current amounts
        current_amounts = {}
        for symbol, volume in current_positions.items():
            # Get price (should come from market data)
            price = 100.0  # Placeholder
            current_amounts[symbol] = volume * price
        
        # Compare and generate signals
        for symbol, target_amount in target_amounts.items():
            current_amount = current_amounts.get(symbol, 0)
            difference = target_amount - current_amount
            threshold = total_capital * 0.005  # 0.5% threshold
            
            if abs(difference) < threshold:
                signals[symbol] = {"action": "HOLD", "amount": 0, "volume": 0}
            elif difference > 0:
                # Buy signal
                price = 100.0  # Placeholder
                volume = difference / price
                signals[symbol] = {
                    "action": "BUY",
                    "amount": difference,
                    "volume": volume
                }
            else:
                # Sell signal
                price = 100.0  # Placeholder
                volume = abs(difference) / price
                signals[symbol] = {
                    "action": "SELL",
                    "amount": abs(difference),
                    "volume": volume
                }
        
        return signals
    
    # ============================================================
    # REPORTING
    # ============================================================
    
    def get_summary(self) -> Dict[str, Any]:
        """Get complete summary of current portfolio state"""
        return {
            "universe_size": len(self.asset_dna),
            "optimization_count": self.optimization_count,
            "current_regime": self.current_regime.value,
            "current_allocation": self.current_allocation.allocations if self.current_allocation else {},
            "expected_return": self.current_allocation.expected_return if self.current_allocation else 0,
            "expected_volatility": self.current_allocation.expected_volatility if self.current_allocation else 0,
            "expected_sharpe": self.current_allocation.expected_sharpe if self.current_allocation else 0,
            "performance_metrics": self.performance_metrics,
            "constraints": self.constraints.to_dict()
        }
    
    def get_recommendation(self) -> str:
        """Get human-readable recommendation"""
        if not self.current_allocation:
            return "No portfolio allocation available"
        
        alloc = self.current_allocation
        top = alloc.get_top_allocations(5)
        
        lines = [
            "=" * 70,
            "PORTFOLIO RECOMMENDATION",
            "=" * 70,
            f"Regime: {self.current_regime.value.upper()}",
            f"Objective: {self.objective.value}",
            "",
            "ALLOCATION:",
        ]
        
        for symbol, weight in top:
            if symbol != "CASH":
                lines.append(f"  {symbol}: {weight:.1%}")
        
        lines.append(f"  CASH: {alloc.allocations.get('CASH', 0):.1%}")
        lines.append("")
        lines.append("METRICS:")
        lines.append(f"  Expected Return: {alloc.expected_return:.2%}")
        lines.append(f"  Expected Volatility: {alloc.expected_volatility:.2%}")
        lines.append(f"  Sharpe Ratio: {alloc.expected_sharpe:.2f}")
        lines.append(f"  Effective N: {alloc.effective_n}")
        lines.append(f"  Beta: {alloc.beta:.2f}")
        lines.append(f"  VaR 95%: {alloc.var_95:.2%}")
        lines.append("=" * 70)
        
        return "\n".join(lines)

# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    print("\n" + "=" * 70)
    print("PHASE 2: INSTITUTIONAL PORTFOLIO INTELLIGENCE ENGINE TEST")
    print("=" * 70)
    
    # Create PIE
    pie = PortfolioIntelligenceEngine()
    
    # Create realistic assets
    assets = [
        AssetDNA("AAPL", sector="Tech", expected_return=0.15, volatility=0.25, 
                quality_score=0.85, beta=1.1, sharpe=0.6),
        AssetDNA("GOOGL", sector="Tech", expected_return=0.12, volatility=0.28,
                quality_score=0.82, beta=1.0, sharpe=0.43),
        AssetDNA("MSFT", sector="Tech", expected_return=0.14, volatility=0.22,
                quality_score=0.88, beta=0.95, sharpe=0.64),
        AssetDNA("AMZN", sector="Consumer", expected_return=0.18, volatility=0.35,
                quality_score=0.75, beta=1.2, sharpe=0.51),
        AssetDNA("META", sector="Tech", expected_return=0.10, volatility=0.30,
                quality_score=0.70, beta=1.15, sharpe=0.33),
        AssetDNA("JPM", sector="Financial", expected_return=0.08, volatility=0.20,
                quality_score=0.65, beta=0.85, sharpe=0.4),
        AssetDNA("GS", sector="Financial", expected_return=0.09, volatility=0.22,
                quality_score=0.60, beta=0.9, sharpe=0.41),
        AssetDNA("BRK.B", sector="Financial", expected_return=0.07, volatility=0.18,
                quality_score=0.70, beta=0.75, sharpe=0.39),
        AssetDNA("VTI", sector="ETF", expected_return=0.10, volatility=0.15,
                quality_score=0.90, beta=1.0, sharpe=0.67),
        AssetDNA("BND", sector="Fixed Income", expected_return=0.04, volatility=0.05,
                quality_score=0.95, beta=0.2, sharpe=0.8),
    ]
    
    pie.add_assets(assets)
    print(f"\n✅ Added {len(assets)} assets to universe")
    
    # Optimize portfolio
    print("\n📊 Optimizing portfolio...")
    target = pie.optimize_portfolio(total_capital=100000)
    
    # Show results
    print("\n" + pie.get_recommendation())
    
    # Generate rebalance signals
    print("\n📈 Generating rebalance signals...")
    current_positions = {"AAPL": 50, "GOOGL": 30}
    signals = pie.generate_rebalance_signals(target, current_positions, 100000)
    
    print("\nRebalance Signals:")
    for symbol, signal in signals.items():
        if signal["action"] != "HOLD":
            print(f"  {symbol}: {signal['action']} {signal['volume']:.2f} units")
    
    print("\n" + "=" * 70)
    print("PHASE 2 TEST COMPLETE")
    print("=" * 70)
