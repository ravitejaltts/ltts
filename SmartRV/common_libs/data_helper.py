def remove_empty_elements(d):
    """recursively remove empty lists, empty dicts, or None elements from a dictionary"""
    # def empty(x):
    #     return x is None or x == {} or x == [] or x == ""

    def empty(x):
        return x is None

    if not isinstance(d, (dict, list)):
        return d
    elif isinstance(d, list):
        return [v for v in (remove_empty_elements(v) for v in d) if not empty(v)]
    else:
        return {k: v for k, v in ((k, remove_empty_elements(v)) for k, v in d.items()) if not empty(v)}



if __name__ == '__main__':
    x = {
        "mode": None,
        "alerts": [],
        "test": {
            "too": "123",
            "better": ""
        },
        "empty": {
            "empty2": None
        }
    }

    print(remove_empty_elements(x))
