# UI Service

## Purpose
The UI service is primary responsible to provide static files as needed and to host the APIs that are required to assemble a dynamic and working UI.
TBD is the responsibility on the API to trigger actual functions to the system and read values back.


## Open Issues
1. Define the scope of this service
2. Device server sided update methods, either HTTP polling, Websockets long polling or Server Side Events
3. Define more open issues


## Installing for testing
1. Install Python 3.x (subversion currently 3.8, but check the developer overview page)
2. Install poetry

        pip3 install poetry

3. Install dependencies (in UI_Service folder)

        poetry install

4. Run UI Service locally

        poetry run uvicorn main_service:application

    or for active development (set up to automatically reload on change)

        poetry run python3 wgo_main_service.py



Navigate to http://localhost:8000/docs for swagger documentation or http://localhost:8000 for the static service of the actual UI


## Issues
Please report any issues to the SmartRV team
