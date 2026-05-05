from dataclasses import is_dataclass, asdict
from typing import TypeVar

T = TypeVar("T")


class Mapper:
    @staticmethod
    def to_entity(model, entity_cls: type[T]) -> T:
        """Convert SQLAlchemy model to entity (dataclass)."""
        if is_dataclass(model) and not isinstance(model, type):
            data = asdict(model)
        else:
            data = {k: v for k, v in vars(model).items() if not k.startswith("_")}
        return entity_cls(**data)

    @staticmethod
    def to_model(entity, model_cls: type[T]) -> T:
        """Convert entity (dataclass) to SQLAlchemy model."""
        return model_cls(**asdict(entity))
