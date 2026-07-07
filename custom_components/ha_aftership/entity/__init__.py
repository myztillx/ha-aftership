"""
Entity package for ha_aftership.

Architecture:
    All platform entities inherit from (PlatformEntity, AftershipEntity).
    MRO order matters — platform-specific class first, then the integration base.
    Entities read data from coordinator.data and NEVER call the API client directly.
    Unique IDs follow the pattern: {entry_id}_{description.key}

See entity/base.py for the AftershipEntity base class.
"""

from .base import AftershipEntity

__all__ = ["AftershipEntity"]
