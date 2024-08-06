import os
import sys
import logging
from datetime import datetime

from copy import deepcopy

logger = logging.getLogger(__name__)

# from common_libs.models.common import RVEvents, EventValues

from main_service.components.movables import *
from main_service.components.lighting import *
from main_service.components.climate import *
from main_service.components.energy import *
from main_service.components.vehicle import *
from main_service.components.watersystems import *
from main_service.components.system import *
import main_service.components.generate_templates as generator

import pytest

# Component Schemas

# Trigger generation
# @pytest.fixture
# def generate():
#     # Generate files
#     with TestClient(app) as c:
#         yield c


def generate():
    base_path = os.path.abspath(sys.argv[0])
    print('Base Path', base_path)
    return generator.generate_all(
        base_path=base_path,
        write_to_data=False,
        create_folders=True
    )


@pytest.mark.skip('Not ready to make universally work, need to get schema pulled in from another place')
def test_validate_componentGroup_schema():
    '''Test to validate the componentGroup output adheres to the required schema.'''
    # Generate
    # Get folder
    # Get schema
    # Validate all files for adherance to the schema
    for folder in generate():
        result = generator.validate_schema(folder)
        print('folder', folder, 'result', result)
        assert result is False
