# Copyright (c) 2023 - 2025, AG2ai, Inc., AG2ai open-source projects maintainers and core contributors
#
# SPDX-License-Identifier: Apache-2.0
import logging
from functools import wraps
from typing import Callable

from pydantic import BaseModel

logger = logging.getLogger(__name__)


def deprecated_by(new_class: type[BaseModel]) -> Callable[[type[BaseModel]], Callable[..., BaseModel] :]:
    def decorator(old_class: type[BaseModel]) -> Callable[..., BaseModel]:
        @wraps(old_class.__init__)
        def wrapper(*args, **kwargs) -> BaseModel:
            logger.warning(
                f"{old_class.__name__} is deprecated by {new_class.__name__}. Please import it from {new_class.__module__} and use it instead."
            )
            return new_class(*args, **kwargs)

        return wrapper

    return decorator
