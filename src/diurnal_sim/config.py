from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Mapping, Literal


LulcCode = Literal["RESI", "COMB", "COMI", "INDU", "INST", "RECR", "NCNU"]


LulcCodes: Mapping[str, str] = {
    "RESI": "Residential",
    "COMB": "Commercial-NonIT",
    "COMI": "Commercial-IT",
    "INDU": "Industrial",
    "INST": "Institutional",
    "RECR": "Recreation",
    "NCNU": "NotClassified",
}


EmploymentDistribution: Mapping[str, float] = {
    "self_employed_own": 0.1313,
    "self_employed_helper": 0.0264,
    "regular_salaried": 0.1933,
    "casual_labour": 0.0425,
    "unemployed": 0.0206,
    "homemakers_elderly": 0.3792,
    "students_children": 0.2067,
}


@dataclass(frozen=True)
class WorkSchedule:
    """A work schedule distribution for a destination building category."""

    days: Literal["ALL", "MON-FRI", "MON-SAT"]
    start_mean: float
    start_std: float
    start_min: float
    start_max: float
    end_mean: float
    end_std: float
    end_min: float
    end_max: float


WorkSchedules: Dict[str, WorkSchedule] = {
    "COMI": WorkSchedule(
        days="MON-FRI",
        start_mean=8.0,
        start_std=0.67,
        start_min=6.0,
        start_max=10.0,
        end_mean=18.0,
        end_std=1.0,
        end_min=16.0,
        end_max=22.0,
    ),
    "COMB": WorkSchedule(
        days="ALL",
        start_mean=9.5,
        start_std=0.5,
        start_min=8.0,
        start_max=11.0,
        end_mean=22.0,
        end_std=0.67,
        end_min=21.0,
        end_max=23.0,
    ),
    "INDU": WorkSchedule(
        days="MON-SAT",
        start_mean=8.0,
        start_std=0.67,
        start_min=6.0,
        start_max=10.0,
        end_mean=17.0,
        end_std=1.0,
        end_min=15.0,
        end_max=19.0,
    ),
    "INST": WorkSchedule(
        days="MON-FRI",
        start_mean=8.5,
        start_std=0.5,
        start_min=7.0,
        start_max=9.5,
        end_mean=16.0,
        end_std=0.67,
        end_min=14.0,
        end_max=18.0,
    ),
    "RECR": WorkSchedule(
        days="ALL",
        start_mean=10.0,
        start_std=1.0,
        start_min=8.0,
        start_max=12.0,
        end_mean=21.0,
        end_std=1.0,
        end_min=18.0,
        end_max=23.0,
    ),
}


def is_working_day(day_of_week: str, schedule_type: str) -> bool:
    """Return True if `day_of_week` is a working day for schedule_type."""
    sched = WorkSchedules.get(schedule_type)
    if sched is None:
        return False

    if sched.days == "ALL":
        return True
    if sched.days == "MON-FRI":
        return day_of_week not in {"Saturday", "Sunday"}
    if sched.days == "MON-SAT":
        return day_of_week != "Sunday"
    return False
