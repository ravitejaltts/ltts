import csv
import os
import sys


def read_component_types(path):
    '''Component tab from export as CSV
    https://winnebagoind.sharepoint.com/:x:/r/sites/CustomerDigitalStrategy/_layouts/15/doc2.aspx?sourcedoc=%7B002181d0-765c-4451-95ad-cc0615c68e02%7D&action=edit&activeCell=%27Data%20Elements%20848%27!D78&wdinitialsession=57ab61fe-2a9f-41c6-aab1-46e739c4f225&wdrldsc=7&wdrldc=1&wdrldr=AccessTokenExpiredWarning%2CRefreshingExpiredAccessT&cid=6db4f7a0-f373-4d0d-a7be-04f6b523e05d&clickparams=eyJBcHBOYW1lIjoiVGVhbXMtRGVza3RvcCIsIkFwcFZlcnNpb24iOiIyOC8yMzAyMDUwMTQyMSIsIkhhc0ZlZGVyYXRlZFVzZXIiOnRydWV9
    '''
    try:
        csv_data_file = open(path, 'r')
    except FileNotFoundError as err:
        print(err)
        return {}
    except Exception as err:
        print(err)
        return {}
    
    component_types = {}
    csv_handle = csv.DictReader(csv_data_file)
    for row in csv_handle:
        category = row['Category']
        code = row.get('\ufeffCode')

        if category in component_types:
            component_types[category][code] = row
        else:
            component_types[category] = {
                code: row
            }
    
    code_map = {}
    for k, v in component_types.items():
        for _k, _v in v.items():
            code_map[_k] = k

    return component_types, code_map


def read_vehicle_data(path, type_map={}):
    try:
        csv_data_file = open(path, 'r')
    except FileNotFoundError as err:
        print(err)
        return {}
    except Exception as err:
        print(err)
        return {}
    
    vehicle_data = {}
    csv_handle = csv.DictReader(csv_data_file)

    for i, row in enumerate(csv_handle):
        if row['\ufeffComponentType'] == '':
            break
        print(
            i, 
            row['\ufeffComponentType'], 
            row['Code'], 
            type_map.get(row['\ufeffComponentType']), 
            row['API Property']
        )

    return vehicle_data




if __name__ == '__main__':
    componentTypes, typeMap = read_component_types(_env.data_file_path('component_types.csv'))
    print(typeMap)
    vehicle_data = read_vehicle_data(_env.data_file_path('848.csv'), type_map=typeMap)
    # print(vehicle_data)
