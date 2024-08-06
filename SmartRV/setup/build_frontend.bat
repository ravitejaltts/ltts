REM Package and clean Python services
poetry run python package_build.py ..\..\build
cd ..\..\

REM Build Frontend
cd Frontend\client

npm run build

xcopy /E "build" "..\..\build\main_service\base_static\"
