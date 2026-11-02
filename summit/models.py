from dataclasses import dataclass
from datetime import date
from enum import IntEnum, StrEnum


class Priority(IntEnum):
    """Lower is more urgent, so `min()` picks the more serious of two priorities."""

    P0 = 0
    P1 = 1
    P2 = 2
    P3 = 3

    @property
    def label(self) -> str:
        return {0: "P0 safety emergency", 1: "P1 urgent", 2: "P2 soon", 3: "P3 routine"}[self]


class Pool(StrEnum):
    REGULAR = "regular"
    EMERGENCY = "emergency"
    MEMBER = "member"


class Membership(StrEnum):
    ACTIVE = "active"
    LAPSED = "lapsed"
    NONE = "none"


@dataclass
class Customer:
    id: int
    first_name: str
    last_name: str
    phone: str
    address: str
    zip: str
    county: str
    membership: Membership = Membership.NONE
    membership_expires: date | None = None

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


@dataclass
class Appointment:
    id: int
    customer_id: int
    county: str
    day: date
    window: str
    pool: Pool
    job_type: str
    priority: Priority
    service_address: str
    status: str
