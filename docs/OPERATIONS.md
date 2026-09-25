# Executable operation catalogue

Every operation requires supplied assumptions/provenance. No market or issuer data are inferred.

## `activity_intensity_bridge`
```python
activity_intensity_bridge(activity0: 'float', intensity0: 'float', activity1: 'float', intensity1: 'float') -> 'dict'
```
See source code and domain methodology for assumptions.

Input units: `{"activity0": "activity_units", "intensity0": "tCO2e_per_activity", "activity1": "activity_units", "intensity1": "tCO2e_per_activity"}`. Output unit/type: `emissions_decomposition`.

## `capex_alignment_bounds`
```python
capex_alignment_bounds(verified_aligned_capex: 'float', unassessed_capex: 'float', total_capex: 'float') -> 'dict'
```
See source code and domain methodology for assumptions.

Input units: `{"verified_aligned_capex": "$money", "unassessed_capex": "$money", "total_capex": "$money"}`. Output unit/type: `capex_bounds`.

## `dscr`
```python
dscr(cash_available: 'float', debt_service: 'float') -> 'float'
```
See source code and domain methodology for assumptions.

Input units: `{"cash_available": "$money", "debt_service": "$money"}`. Output unit/type: `multiple`.

## `funding_gap`
```python
funding_gap(required_investment: 'float', committed_funding: 'float') -> 'float'
```
See source code and domain methodology for assumptions.

Input units: `{"required_investment": "$money", "committed_funding": "$money"}`. Output unit/type: `$money`.

## `holding_period_return`
```python
holding_period_return(initial_dirty_price: 'float', exit_dirty_price: 'float', cash_income: 'float', funding_cost: 'float', transaction_cost: 'float') -> 'float'
```
See source code and domain methodology for assumptions.

Input units: `{"initial_dirty_price": "$money", "exit_dirty_price": "$money", "cash_income": "$money", "funding_cost": "$money", "transaction_cost": "$money"}`. Output unit/type: `decimal_return`.

## `npv`
```python
npv(cashflows: 'list[float]', annual_discount: 'float') -> 'float'
```
Periodic NPV; cashflows[0] is at time zero, then annual periods.

Input units: `{"cashflows": "$money", "annual_discount": "decimal"}`. Output unit/type: `$money`.

## `scale`
```python
scale(value: 'float', factor: 'float') -> 'float'
```
Explicit arithmetic conversion; external unit semantics need human review.

Input units: `{"value": "$input_unit", "factor": "conversion_factor"}`. Output unit/type: `$output_unit`.

## `target_path`
```python
target_path(base_emissions: 'float', target_emissions: 'float', base_year: 'int', target_year: 'int', observation_year: 'int', observed_emissions: 'float') -> 'dict'
```
See source code and domain methodology for assumptions.

Input units: `{"base_emissions": "tCO2e", "target_emissions": "tCO2e", "base_year": "year", "target_year": "year", "observation_year": "year", "observed_emissions": "tCO2e"}`. Output unit/type: `target_progress`.
