"""Groundwater model of a peat KHG.

  solver    2D Boussinesq solver and peat tables (storage and transmissivity against water table depth); also used by repeat-pump
  grid      a real KHG (boundary, DTM, peat depth, canals, stations) on a metric grid
  forcing   daily rain and evaporation of the KHG
  lumped    tier 1: one KHG-level water table
  spatial   tier 2: the solver run daily over the KHG grid
  validate  comparison with the SiTMAT stations
"""
from .solver import PEAT_TABLES, TROPICAL_SETS, PeatTable, solve

__all__ = ["PEAT_TABLES", "TROPICAL_SETS", "PeatTable", "solve"]
