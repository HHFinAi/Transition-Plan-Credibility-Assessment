"""Transparent target/progress arithmetic; no scientifically calibrated success score."""
from __future__ import annotations
from .maths import COMMON_OPERATIONS, checked, fraction, number, operation, positive, require

@operation({'base_emissions':'tCO2e','target_emissions':'tCO2e','base_year':'year','target_year':'year','observation_year':'year','observed_emissions':'tCO2e'},'target_progress')
def target_path(base_emissions: float,target_emissions: float,base_year: int,target_year: int,
                observation_year: int,observed_emissions: float) -> dict:
    b=positive(base_emissions,'base_emissions');t=checked(target_emissions,'target_emissions',0,b)
    for y in (base_year,target_year,observation_year): require(type(y) is int and 1900<=y<=2200,'invalid year')
    require(base_year<target_year and base_year<=observation_year<=target_year,'invalid year ordering')
    o=checked(observed_emissions,'observed_emissions',0)
    # A zero endpoint has no finite positive exponential path; require a separate schedule.
    require(t>0,'zero target needs an explicit non-exponential pathway')
    ratio=(t/b)**(1/(target_year-base_year))
    expected=b*ratio**(observation_year-base_year)
    return {'required_compound_annual_reduction':1-ratio,'illustrative_path_emissions':expected,
            'gap_tco2e':o-expected,'observed_reduction_fraction':1-o/b,
            'path_is_scenario_not_science_alignment':True}

@operation({'activity0':'activity_units','intensity0':'tCO2e_per_activity','activity1':'activity_units','intensity1':'tCO2e_per_activity'},'emissions_decomposition')
def activity_intensity_bridge(activity0: float,intensity0: float,activity1: float,intensity1: float) -> dict:
    a0=checked(activity0,'activity0',0);a1=checked(activity1,'activity1',0)
    i0=checked(intensity0,'intensity0',0);i1=checked(intensity1,'intensity1',0)
    ae=(a1-a0)*(i0+i1)/2;ie=(i1-i0)*(a0+a1)/2
    return {'start_emissions':a0*i0,'end_emissions':a1*i1,'activity_effect':ae,'intensity_effect':ie,'delta':ae+ie}

@operation({'verified_aligned_capex':'$money','unassessed_capex':'$money','total_capex':'$money'},'capex_bounds')
def capex_alignment_bounds(verified_aligned_capex: float,unassessed_capex: float,total_capex: float) -> dict:
    a=checked(verified_aligned_capex,'verified_aligned_capex',0);u=checked(unassessed_capex,'unassessed_capex',0);t=positive(total_capex,'total_capex')
    require(a+u<=t+1e-9,'capex categories exceed total')
    return {'confirmed_aligned_fraction':a/t,'maximum_if_unknown_aligns':(a+u)/t,'assessed_fraction':1-u/t}

@operation({'required_investment':'$money','committed_funding':'$money'},'$money')
def funding_gap(required_investment: float,committed_funding: float) -> float:
    return max(0,checked(required_investment,'required_investment',0)-checked(committed_funding,'committed_funding',0))
OPERATIONS=dict(COMMON_OPERATIONS)
OPERATIONS.update({f.__name__:f for f in (target_path,activity_intensity_bridge,capex_alignment_bounds,funding_gap)})
