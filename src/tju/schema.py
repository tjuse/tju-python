from __future__ import annotations

from dataclasses import field

from marshmallow import Schema, post_dump
from marshmallow.fields import Field


class LoadDumpSchema(Schema):
    def on_bind_field(self, field_name: str, field_obj: Field) -> None:
        field_obj.data_key = field_obj.data_key or field_name

    # @pre_load
    # def rename_keys(self, data, **kwargs):
    #     for field_name, field in self.fields.items():
    #         print(field_name, field.data_key)
    #         if field.data_key:
    #             data[field_name] = data.pop(field.data_key)
    #     return data

    @post_dump
    def restore_keys(self, data, **kwargs):
        for field_name, _field in self.fields.items():
            if _field.data_key:
                data[field_name] = data.pop(_field.data_key)
        return data


def mfield(default=None, *, data_key: str | None = None, **kwargs):
    """field with metadata"""
    for k in ["data_key"]:
        if locals().get(k) is not None:
            kwargs[k] = locals().get(k)
    return field(default=default, metadata=kwargs)
