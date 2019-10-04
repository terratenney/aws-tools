"""
Some utility functions for interacting with DynamoDB
"""
from decimal import Decimal
import json


def convert_data_for_dynamodb(data):
    """
    Convert data for DynamoDB limitations.

    :param data: a dictionary of arbitrary data
    :return: a dictionary with data cleaned up
    """
    # Handle float to decimal conversion for DynamoDB
    data = convert_floats_to_decimals(data)

    # Convert empty string to None
    data = convert_empty_string_to_none(data)

    return data


def convert_floats_to_decimals(data):
    """
    Convert floats into decimals that DynamoDB can handle.

    :param data: a dictionary of arbitrary data
    :return: a dictionary with any floats converted to Decimals
    """
    # See https://blog.ruanbekker.com/blog/2019/02/05/convert-float-to-decimal-data-types-for-boto3-dynamodb-using-python/
    return json.loads(json.dumps(data), parse_float=Decimal)


def convert_empty_string_to_none(data):
    """
    Nullify empty strings in `data`.

    :param data: arbitrary data
    :return: data contains no empty string
    """
    if isinstance(data, str) and data == "":
        data = None
    elif isinstance(data, dict):
        for key, value in data.items():
            data[key] = convert_empty_string_to_none(value)
    elif isinstance(data, list):
        for i in range(len(data)):
            data[i] = convert_empty_string_to_none(data[i])
    return data