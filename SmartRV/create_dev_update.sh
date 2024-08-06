#/bin/bash
# TODO: Back up storage folder

# Run Pytests
source ./venv/bin/activate

# MAIN SERVICE
cd main_service
pytest | tee pytest_report.log
# TODO: Check test results for failure

cd ..

# IOT Service

# Generate Templates
cd main_service/components
python3 generate_templates.py
cd ../..

# Make a build
cd setup
./build_all_dom.sh

# TODO: Return storage folder
