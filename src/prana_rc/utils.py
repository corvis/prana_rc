#    Prana RC
#    Copyright (C) 2020 Dmitry Berezovsky
#
#    prana is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    prana is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from typing import Optional, TypeVar, Type, Any

__all__ = ("none_throws", "safe_cast")


_T = TypeVar("_T")


def none_throws(optional: Optional[_T], message: str = "Unexpected `None`") -> _T:
    """Convert an optional to its value. Raises an `AssertionError` if the
    value is `None`"""
    if optional is None:
        raise AssertionError(message)
    return optional


def safe_cast(new_type: Type[_T], value: Any) -> _T:
    """safe_cast will change the type checker's inference of x if it was
    already a subtype of what we are casting to, and error otherwise."""
    return value  # type: ignore[no-any-return]


# ===================================
