"""Deterministic arithmetic only. Assumptions are supplied, never inferred."""
from __future__ import annotations
from typing import Any, Callable
from functools import wraps
from .validation import DataError, number, require, sequence

def checked(value: Any, name: str, minimum: float | None = None, maximum: float | None = None) -> float:
    result = number(value, name)
    if minimum is not None:
        require(result >= minimum, f"{name} below minimum {minimum}")
    if maximum is not None:
        require(result <= maximum, f"{name} above maximum {maximum}")
    return result

def fraction(value: Any, name: str) -> float:
    return checked(value, name, 0, 1)

def positive(value: Any, name: str) -> float:
    result = number(value, name)
    require(result > 0, f"{name} must be positive")
    return result

def series(value: Any, name: str) -> list[float]:
    values = sequence(value, name, True)
    require(len(values) <= 1000, f"{name} too long for the illustrative annual-period helper")
    return [number(item, name) for item in values]

def operation(units: dict[str, str], output_unit: str) -> Callable:
    def decorate(func: Callable) -> Callable:
        @wraps(func)
        def finite_operation(*args, **kwargs):
            result = func(*args, **kwargs)
            def inspect(value):
                if isinstance(value, float): number(value, "calculation result")
                elif isinstance(value, dict):
                    for item in value.values(): inspect(item)
                elif isinstance(value, (list, tuple)):
                    for item in value: inspect(item)
            inspect(result)
            return result
        finite_operation.argument_units = units
        finite_operation.output_unit = output_unit
        return finite_operation
    return decorate

@operation({"cashflows": "$money", "annual_discount": "decimal"}, "$money")
def npv(cashflows: list[float], annual_discount: float) -> float:
    """Periodic NPV; cashflows[0] is at time zero, then annual periods."""
    amounts = series(cashflows, "cashflows")
    rate = number(annual_discount, "annual_discount")
    require(rate > -1, "discount rate must exceed -100%")
    try:
        result = sum(cf / (1 + rate) ** t for t, cf in enumerate(amounts))
    except (OverflowError, ZeroDivisionError) as exc:
        raise DataError("discount factors outside supported finite range") from exc
    return number(result, "NPV result")

@operation({"cash_available": "$money", "debt_service": "$money"}, "multiple")
def dscr(cash_available: float, debt_service: float) -> float:
    return number(cash_available, "cash_available") / positive(debt_service, "debt_service")

@operation({"value": "$input_unit", "factor": "conversion_factor"}, "$output_unit")
def scale(value: float, factor: float) -> float:
    """Explicit arithmetic conversion; external unit semantics need human review."""
    return number(value, "value") * positive(factor, "factor")

@operation({"initial_dirty_price": "$money", "exit_dirty_price": "$money", "cash_income": "$money", "funding_cost": "$money", "transaction_cost": "$money"}, "decimal_return")
def holding_period_return(initial_dirty_price: float, exit_dirty_price: float, cash_income: float,
                          funding_cost: float, transaction_cost: float) -> float:
    initial = positive(initial_dirty_price, "initial_dirty_price")
    end = checked(exit_dirty_price, "exit_dirty_price", 0)
    income = number(cash_income, "cash_income")
    funding = number(funding_cost, "funding_cost")
    costs = checked(transaction_cost, "transaction_cost", 0)
    return (end - initial + income - funding - costs) / initial

COMMON_OPERATIONS = {f.__name__: f for f in (npv, dscr, scale, holding_period_return)}
