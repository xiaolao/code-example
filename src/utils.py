import json
import gzip
import base64
import decimal

from functools import partialmethod

from boto3.dynamodb.types import TypeDeserializer, Binary


def partial_class(cls, *arg, **kwargs):

    class NewCls(cls):
        __init__ = partialmethod(cls.__init__, *arg, **kwargs)

    return NewCls


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            if obj.as_tuple().exponent < 0:
                return float(obj)
            return int(obj)
        elif isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


class Deserializer(TypeDeserializer):

    def _deserialize_b(self, value: str):
        if isinstance(value, str):
            return Binary(base64.decodebytes(value.encode()))
        return Binary(value)


deserializer = Deserializer()


def deserialize(dynamodb_values):
    if isinstance(dynamodb_values, dict):
        return {k: deserializer.deserialize(v) for k, v in dynamodb_values.items()}
    elif isinstance(dynamodb_values, list):
        return [deserializer.deserialize(value) for value in dynamodb_values]
    else:
        return deserializer.deserialize(dynamodb_values)


def decompress(image: dict):
    for k, v in image.items():
        if isinstance(v, Binary):
            image[k] = gzip.decompress(v.value).decode()
    return image
