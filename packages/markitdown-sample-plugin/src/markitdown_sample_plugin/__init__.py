# SPDX-FileCopyrightText: 2024-present Syed Ariful Islam Emon <syedarifulislamemon201093@gmail.com>
#
# SPDX-License-Identifier: MIT

from ._plugin import __plugin_interface_version__, register_converters, RtfConverter
from .__about__ import __version__

__all__ = [
    "__version__",
    "__plugin_interface_version__",
    "register_converters",
    "RtfConverter",
]
