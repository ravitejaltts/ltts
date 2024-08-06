echo %1

pip3 install poetry

REM Build Frontend
call build_frontend.bat

IF [%1]==["run"] GOTO RUN ELSE GOTO END

:RUN
ECHO "Running build"
cd ..\..\build
launch_local.bat

:END
ECHO "Build END"