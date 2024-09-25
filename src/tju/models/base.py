from typing import ClassVar, Generic, List, Type, TypeVar

from marshmallow import Schema

from tju.exceptions import DataError


class Result:
    Schema: ClassVar[Type["Schema"]] = Schema


T_Result = TypeVar("T_Result", bound=Result)


class QueryResult(Generic[T_Result]): ...


class Results(List[T_Result]):
    _item: Type[T_Result]

    def __init__(self):
        super().__init__()

    def load(self, data: list):
        schema = self._item.Schema(many=True)
        results = schema.load(data)
        if results is None:
            raise DataError("Failed to load data")
        self.extend(results)
