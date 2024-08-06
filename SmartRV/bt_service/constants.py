from enum import Enum, auto

# from pydantic import BaseModel

class APIMethods(Enum):
    '''API Types for sending over BLE'''
    GET = 1
    HEAD = auto()
    POST = auto()
    PUT = auto()
    DELETE = auto()
    CONNECT = auto()
    OPTIONS = auto()
    TRACE = auto()
    PATCH = auto()


if __name__ == '__main__':
    import requests
    x = APIMethods(1)
    print(x, x.value)
    response = getattr(
            requests, x.name.lower()
        )('http://192.168.8.161:8000/ui/home')
    print(response.json())
