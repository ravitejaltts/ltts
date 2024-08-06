# Readme

## Setup

```sh
poetry run pip3 install dbus-python
poetry run pip3 install requests
poetry run sudo apt install libgirepository1.0-dev gcc libcairo2-dev pkg-config python3-dev gir1.2-gtk-3.0
poetry run pip3 install pycairo
poetry run pip3 install PyGObject
```

## Execution

```sh
poetry run python3 app.py
```

If the SmartRV backend is running (see [readme](https://dev.azure.com/WGO-Web-Development/_git/SmartRV?path=/README.md&_a=preview)), you can make requests to the API with the [standard message encoding](https://dev.azure.com/WGO-Web-Development/Owners%20App/_wiki/wikis/Owners-App.wiki/549/BLE-Messages).

For example, 010013002f6170692f6C69676874696E672f7A6f6E65730000 will request GET /api/lighting/zones.
**Note:** This only works for GET rquests currently.