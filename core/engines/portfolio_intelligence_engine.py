"""
Portfolio Intelligence Engine (PIE) - Foundational Layer
Version: 1.0.0
Date: 2026-06-30
Status: FOUNDATIONAL - READY FOR EXPANSION

The PIE decides what the firm should own and in what proportions.
This is the institutional layer that transforms the system from
"what trade?" to "what should my portfolio look like now?"
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, field
import math

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class AssetDNA:
    """Asset characteristics from the Research Engine"""
    symbol: str
    expected_value: float
    volatility: float
    correlation_matrix: Dict[str, float] = field(default_factory=dict)
    quality_score: float = 0.0
    sector: str = "Unknown"
    market_cap: float = 0.0
    
    def __repr__(self):
        return f"AssetDNA({self.symbol}, EV={self.expected_value:.2f}, Vol={self.volatility:.2f})"

@dataclass
class PortfolioTarget:
    """Target portfolio composition from PIE"""
    allocations: Dict[str, float]  # symbol -> target weight
    expected_return: float = 0.0
    expected_volatility: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    
    def get_weights(self) -> Dict[str, float]:
        """Get the target weights"""
        return self.allocations
    
    def get_invested_amounts(self, total_capital: float) -> Dict[str, float]:
        """Convert weights to dollar amounts"""
        return {symbol: weight * total_capital for symbol, weight in self.allocations.items()}

@dataclass
class PortfolioConstraints:
    """Constraints for portfolio optimization"""
    max_position_weight: float = 0.20  # 20% max per position
    max_sector_weight: float = 0.40    # 40% max per sector
    min_cash: float = 0.05             # 5% minimum cash
    max_leverage: float = 1.0          # No leverage
    max_correlation: float = 0.70      # Max correlation between any two assets
    min_assets: int = 5                # Minimum number of assets

# ============================================================================
# PORTFOLIO INTELLIGENCE ENGINE
# ============================================================================

class PortfolioIntelligenceEngine:
    """
    Portfolio Intelligence Engine (PIE)
    
    Decides what the portfolio should look like based on:
    - Asset DNA (from Research Engine)
    - Portfolio constraints
    - Current positions
    - Market regime
    - Risk preferences
    """
    
    def __init__(self, constraints: Optional[PortfolioConstraints] = None):
        self.constraints = constraints or PortfolioConstraints()
        self.asset_dna: Dict[str, AssetDNA] = {}
        self.portfolio_history: List[PortfolioTarget] = []
        self.current_target: Optional[PortfolioTarget] = None
        self.last_optimization = None
        
        logging.info("PortfolioIntelligenceEngine initialized with constraints:")
        logging.info(f"  Max position weight: {self.constraints.max_position_weight:.1%}")
        logging.info(f"  Max sector weight: {self.constraints.max_sector_weight:.1%}")
        logging.info(f"  Min cash: {self.constraints.min_cash:.1%}")
    
    # ============================================================
    # ASSET DNA MANAGEMENT
    # ============================================================
    
    def add_asset(self, dna: AssetDNA):
        """Add or update asset DNA"""
        self.asset_dna[dna.symbol] = dna
        logging.debug(f"Added asset: {dna}")
    
    def add_assets(self, assets: List[AssetDNA]):
        """Add multiple assets"""
        for asset in assets:
            self.add_asset(asset)
    
    def get_asset(self, symbol: str) -> Optional[AssetDNA]:
        """Get asset DNA by symbol"""
        return self.asset_dna.get(symbol)
    
    def get_all_assets(self) -> List[AssetDNA]:
        """Get all assets"""
        return list(self.asset_dna.values())
    
    # ============================================================
    # PORTFOLIO OPTIMIZATION
    # ============================================================
    
    def optimize_portfolio(self, 
                          available_capital: float,
                          current_positions: Optional[Dict[str, float]] = None,
                          market_regime: str = "neutral") -> PortfolioTarget:
        """
        Optimize portfolio allocation based on current assets and constraints
        
        Args:
            available_capital: Total capital to allocate
            current_positions: Current positions {symbol: volume}
            market_regime: Current market regime (neutral, bullish, bearish)
        
        Returns:
            PortfolioTarget with target allocations
        """
        current_positions = current_positions or {}
        
        # Filter assets
        eligible_assets = self._filter_eligible_assets(market_regime)
        
        if not eligible_assets:
            logging.warning("No eligible assets found for optimization")
            return PortfolioTarget(allocations={})
        
        # Calculate scores
        scored_assets = self._score_assets(eligible_assets)
        
        # Apply constraints
        constrained_allocations = self._apply_constraints(scored_assets)
        
        # Adjust for current positions (rebalancing)
        final_allocations = self._adjust_for_rebalancing(
            constrained_allocations, 
            current_positions,
            available_capital
        )
        
        # Calculate portfolio metrics
        expected_return = self._calculate_expected_return(final_allocations)
        expected_volatility = self._calculate_expected_volatility(final_allocations)
        sharpe = expected_return / expected_volatility if expected_volatility > 0 else 0
        
        # Create target
        target = PortfolioTarget(
            allocations=final_allocations,
            expected_return=expected_return,
            expected_volatility=expected_volatility,
            sharpe_ratio=sharpe,
            max_drawdown=self._estimate_max_drawdown(final_allocations)
        )
        
        self.current_target = target
        self.portfolio_history.append(target)
        self.last_optimization = datetime.now()
        
        logging.info(f"Portfolio optimized: {len(final_allocations)} assets, Sharpe: {sharpe:.2f}")
        logging.debug(f"Target: {final_allocations}")
        
        return target
    
    # ============================================================
    # INTERNAL OPTIMIZATION METHODS
    # ============================================================
    
    def _filter_eligible_assets(self, market_regime: str) -> List[AssetDNA]:
        """Filter assets based on market regime and quality"""
        eligible = []
        for dna in self.asset_dna.values():
            # Quality filter
            if dna.quality_score < 0.3:
                continue
            
            # Regime-based filtering
            if market_regime == "bearish" and dna.volatility > 0.4:
                continue
                
            eligible.append(dna)
        
        return sorted(eligible, key=lambda x: x.expected_value, reverse=True)
    
    def _score_assets(self, assets: List[AssetDNA]) -> List[Tuple[AssetDNA, float]]:
        """
        Score assets based on risk-adjusted expected value
        
        Returns:
            List of (AssetDNA, score) tuples sorted by score
        """
        scored = []
        for dna in assets:
            # Risk-adjusted score
            if dna.volatility > 0:
                score = dna.expected_value / dna.volatility
            else:
                score = dna.expected_value
            
            # Quality bonus
            score *= (1 + dna.quality_score * 0.5)
            
            scored.append((dna, score))
        
        return sorted(scored, key=lambda x: x[1], reverse=True)
    
    def _apply_constraints(self, scored_assets: List[Tuple[AssetDNA, float]]) -> Dict[str, float]:
        """
        Apply portfolio constraints to allocations
        
        Returns:
            Dict of symbol -> target weight
        """
        if not scored_assets:
            return {}
        
        # Start with equal weights
        n_assets = min(len(scored_assets), 10)  # Limit to top 10
        initial_weight = (1 - self.constraints.min_cash) / n_assets
        
        allocations = {}
        sector_weights = {}
        
        for dna, _ in scored_assets[:n_assets]:
            weight = initial_weight
            
            # Cap per position
            weight = min(weight, self.constraints.max_position_weight)
            
            # Sector cap
            sector = dna.sector
            if sector not in sector_weights:
                sector_weights[sector] = 0
            sector_weights[sector] += weight
            
            if sector_weights[sector] > self.constraints.max_sector_weight:
                # Reduce weight to meet sector cap
                overage = sector_weights[sector] - self.constraints.max_sector_weight
                weight -= overage
            
            allocations[dna.symbol] = max(0.01, weight)  # Minimum 1%
        
        # Normalize
        total = sum(allocations.values())
        for symbol in allocations:
            allocations[symbol] = allocations[symbol] / total * (1 - self.constraints.min_cash)
        
        # Add cash
        allocations["CASH"] = self.constraints.min_cash
        
        return allocations
    
    def _adjust_for_rebalancing(self, 
                               target_allocations: Dict[str, float],
                               current_positions: Dict[str, float],
                               available_capital: float) -> Dict[str, float]:
        """
        Adjust target allocations based on current positions
        to minimize trading costs
        """
        # If no current positions, return target as-is
        if not current_positions:
            return target_allocations
        
        # Calculate current weights
        current_weights = {}
        for symbol, volume in current_positions.items():
            # Get price (in production, get from market data)
            price = 100.0  # Placeholder
            value = volume * price
            current_weights[symbol] = value / available_capital
        
        # Blend current with target (smooth rebalancing)
        blending_factor = 0.5  # 50% adjustment toward target
        adjusted = {}
        
        for symbol, target_weight in target_allocations.items():
            current_weight = current_weights.get(symbol, 0)
            adjusted[symbol] = current_weight + blending_factor * (target_weight - current_weight)
        
        # Handle new assets not in current portfolio
        for symbol, weight in target_allocations.items():
            if symbol not in adjusted:
                adjusted[symbol] = weight * blending_factor
        
        return adjusted
    
    def _calculate_expected_return(self, allocations: Dict[str, float]) -> float:
        """Calculate expected portfolio return"""
        total_return = 0
        for symbol, weight in allocations.items():
            if symbol == "CASH":
                total_return += weight * 0.02  # 2% cash return
            elif symbol in self.asset_dna:
                total_return += weight * self.asset_dna[symbol].expected_value
        
        return total_return
    
    def _calculate_expected_volatility(self, allocations: Dict[str, float]) -> float:
        """Calculate expected portfolio volatility"""
        # Simple approximation
        total_vol = 0
        for symbol, weight in allocations.items():
            if symbol == "CASH":
                continue
            elif symbol in self.asset_dna:
                total_vol += (weight * self.asset_dna[symbol].volatility) ** 2
        
        return math.sqrt(total_vol) if total_vol > 0 else 0
    
    def _estimate_max_drawdown(self, allocations: Dict[str, float]) -> float:
        """Estimate maximum portfolio drawdown"""
        # Simple approximation: 2x volatility
        vol = self._calculate_expected_volatility(allocations)
        return vol * 2
    
    # ============================================================
    # REBALANCING LOGIC
    # ============================================================
    
    def get_rebalance_signals(self, 
                             target: PortfolioTarget,
                             current_positions: Dict[str, float],
                             available_capital: float) -> Dict[str, Dict[str, Any]]:
        """
        Generate rebalance signals based on target vs current positions
        
        Returns:
            Dict of signals: {symbol: {action: 'BUY'/'SELL'/'HOLD', volume: float}}
        """
        signals = {}
        
        # Calculate current weights
        current_weights = {}
        for symbol, volume in current_positions.items():
            price = 100.0  # Placeholder
            value = volume * price
            current_weights[symbol] = value / available_capital
        
        # Compare to target
        for symbol, target_weight in target.allocations.items():
            current_weight = current_weights.get(symbol, 0)
            diff = target_weight - current_weight
            
            if abs(diff) < 0.005:  # 0.5% threshold
                signals[symbol] = {"action": "HOLD", "volume": 0}
            elif diff > 0:
                # Need to buy
                target_value = target_weight * available_capital
                current_value = current_weight * available_capital
                volume = (target_value - current_value) / 100.0  # Price placeholder
                signals[symbol] = {"action": "BUY", "volume": volume}
            else:
                # Need to sell
                target_value = target_weight * available_capital
                current_value = current_weight * available_capital
                volume = (current_value - target_value) / 100.0
                signals[symbol] = {"action": "SELL", "volume": volume}
        
        return signals
    
    # ============================================================
    # REPORTING
    # ============================================================
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of current portfolio state"""
        return {
            "assets_under_management": len(self.asset_dna),
            "current_target": self.current_target.allocations if self.current_target else {},
            "expected_return": self.current_target.expected_return if self.current_target else 0,
            "expected_volatility": self.current_target.expected_volatility if self.current_target else 0,
            "sharpe_ratio": self.current_target.sharpe_ratio if self.current_target else 0,
            "last_optimization": self.last_optimization.isoformat() if self.last_optimization else None,
            "optimization_count": len(self.portfolio_history)
        }
    
    def get_recommendation(self) -> str:
        """Get human-readable recommendation"""
        if not self.current_target:
            return "No portfolio target set"
        
        top_allocations = sorted(
            self.current_target.allocations.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        recommendation = f"Recommended allocations:\n"
        for symbol, weight in top_allocations:
            if symbol != "CASH":
                recommendation += f"  {symbol}: {weight:.1%}\n"
        recommendation += f"  Cash: {self.current_target.allocations.get('CASH', 0):.1%}\n"
        recommendation += f"Expected Sharpe: {self.current_target.sharpe_ratio:.2f}"
        
        return recommendation

# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("=" * 70)
    print("TESTING PORTFOLIO INTELLIGENCE ENGINE")
    print("=" * 70)
    
    # Create PIE
    pie = PortfolioIntelligenceEngine()
    
    # Add assets
    assets = [
        AssetDNA("AAPL", 0.15, 0.25, quality_score=0.8, sector="Tech"),
        AssetDNA("GOOGL", 0.12, 0.28, quality_score=0.85, sector="Tech"),
        AssetDNA("MSFT", 0.14, 0.22, quality_score=0.9, sector="Tech"),
        AssetDNA("AMZN", 0.18, 0.35, quality_score=0.75, sector="Consumer"),
        AssetDNA("META", 0.10, 0.30, quality_score=0.7, sector="Tech"),
        AssetDNA("JPM", 0.08, 0.20, quality_score=0.6, sector="Financial"),
        AssetDNA("GS", 0.09, 0.22, quality_score=0.55, sector="Financial"),
        AssetDNA("BRK.B", 0.07, 0.18, quality_score=0.65, sector="Financial"),
    ]
    pie.add_assets(assets)
    
    print(f"\nAssets under management: {len(pie.asset_dna)}")
    
    # Optimize portfolio
    print("\nOptimizing portfolio...")
    target = pie.optimize_portfolio(available_capital=100000)
    
    print(f"Target allocations:")
    for symbol, weight in sorted(target.allocations.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {symbol}: {weight:.1%}")
    
    print(f"\nExpected return: {target.expected_return:.2%}")
    print(f"Expected volatility: {target.expected_volatility:.2%}")
    print(f"Sharpe ratio: {target.sharpe_ratio:.2f}")
    
    # Get recommendation
    print(f"\nRecommendation:")
    print(pie.get_recommendation())
    
    # Test rebalance signals
    print("\nTesting rebalance signals...")
    current_positions = {"AAPL": 50, "GOOGL": 30}
    signals = pie.get_rebalance_signals(target, current_positions, 100000)
    print(f"Generated {len(signals)} signals:")
    for symbol, signal in signals.items():
        if signal["action"] != "HOLD":
            print(f"  {symbol}: {signal['action']} {signal['volume']:.2f}")
    
    print("\n" + "=" * 70)
    print("PORTFOLIO INTELLIGENCE ENGINE TEST COMPLETE")
    print("=" * 70)
