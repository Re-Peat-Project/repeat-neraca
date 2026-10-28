"""Groundwater model of a peat KHG: the 2D Boussinesq solver and the peat tables (storage and transmissivity against water table depth)."""
from .solver import PEAT_TABLES, TROPICAL_SETS, PeatTable, solve

__all__ = ["PEAT_TABLES", "TROPICAL_SETS", "PeatTable", "solve"]
