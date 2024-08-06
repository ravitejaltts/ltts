set PYTHONPATH=%PYTHONPATH%;"C:\Users\vlnp1.DESKTOP-2R1FRU3\OneDrive\Documents\winnebago6-2\SmartRV"

cd main_service
pip3 install poetry
poetry install

poetry run python wgo_main_service.py
