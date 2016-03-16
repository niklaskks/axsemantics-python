#!/usr/bin/env python3
"""
This is an example script demonstrating the usage of the axsemantics API client.
Please use the configuration section below to customize behaviour and proceed
at your own risk.

This script will upload data found in an excel file to a given content project.
It expects the excel file name as command line parameter.

Take care to include an 'name' and a 'uid' field in either your data or the
MAPPING dict if you want to create the Objects.

Required dependencies:
    - axsemantics
    - pandas
    - xlrd
"""
import json
import re
import sys

import axsemantics
import pandas as pd

# mapping helper functions
def splitdata(field, key, row_separator, value_separator):
    data = {}
    try:
        pairs = field.split(row_separator)
    except AttributeError:
        return data

    for pair in pairs:
        key, value = pair.split(value_separator)
        key = normalize_key(key)
        data[key] = value.strip()
    return data


def splitlist(field, key, separator):
    data = [element.strip() for element in field.split(separator)]
    return {key: data}


# IMPORT_UNCONFIGURED: Boolean
#  - True: columns not defined in MAPPING will be camel-cased and imported
#  - False: only columns in MAPPING will be imported
IMPORT_UNCONFIGURED = True

# MAPPING: dict
#  - {"column name": "datafield name"}: map a column name to a different data field name
#  - {"column name": [function, params]}: map a column name to a parsing method (returning a dict)
#    the mapping function will be passed the parameters 'field' and 'key' aswell as everything in
#    the params dict
MAPPING = {
    'MPID': 'uid',
    'Title English': 'name',
    'Sizes': [splitlist, {'separator': '~'}],
    'Specification': [splitdata, {'row_separator': '~',
                                  'value_separator': ':'}]
}

# EXPORT: Boolean
#  - True: save things as json instead of creating them
#  - False: create things in API
EXPORT = True

# AXSEMANTICS_*: values to use with the axsemantics library
AXSEMANTICS_USER = 'user@example.com'
AXSEMANTICS_PASSWORD = 'securepassword'
AXSEMANTICS_CONTENT_PROJECT = 4004


def normalize_key(key):
    key = key.strip()
    key = re.sub(r'A-Za-z0-9_', '', key)
    key = key.title()
    return key.replace(' ', '')


def _parse_row(row):
    data = {}

    for xslx_key in row.keys():
        xslx_value = row[xslx_key]

        if xslx_key in MAPPING:
            mapped_key = MAPPING[xslx_key]
            if isinstance(mapped_key, str):
                data[mapped_key] = xslx_value

            elif isinstance(mapped_key, list):
                data.update(mapped_key[0](field=xslx_value, key=xslx_key, **mapped_key[1]))

        elif IMPORT_UNCONFIGURED:
            data[normalize_key(xslx_key)] = xslx_value
    return data


if __name__ == '__main__':
    try:
        xslx = pd.ExcelFile(sys.argv[-1])
    except FileNotFoundError:
        sys.exit('Could not find .xslx file {}.'.format(sys.argv[-1]))

    data = []
    sheet = xslx.parse(0)
    # replace float with value `nan` with none
    sheet_with_none = sheet.where((pd.notnull(sheet)), None)

    for index, row in sheet_with_none.iterrows():
        data.append(_parse_row(row))

    if EXPORT is True:
        json_name = re.sub(r'.xslx', '.json', sys.argv[-1])
        with open(json_name, 'w') as f:
            json.dump(data, f)
    else:
        axsemantics.login(AXSEMANTICS_USER, AXSEMANTICS_PASSWORD)
        things = []
        for pure_data in data:
            thing = axsemantics.Thing(
                uid=pure_data['uid'],
                name=pure_data['name'],
                cp_id=AXSEMANTICS_CONTENT_PROJECT,
                pure_data=pure_data,
            ).create()
            things.append(thing)
