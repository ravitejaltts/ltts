import os
import sys
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

sys.path.append(os.path.abspath("./.."))
sys.path.append(os.path.abspath("."))

# from fastapi.testclient import TestClient
# from iot_service.wgo_iot_service import app
from common_libs.models.common import LogEvent

from common_libs.models.common import KeyValue, RVEvents, EventValues

import signal
import pytest


from conftest import client


# Combine api calls to save startup times
def test_put_endpoints(client):
    print("skipping IOT put /vin for now. Too much happens.")

    print("skipping IOT put /ota_start for now. Too much happens.")

    print("IOT put /telemetry/events")

    event_test = LogEvent(
        # timestamp=time.time(),
        event=RVEvents.AIR_CONDITIONER_COMPRESSOR_MODE_CHANGE,
        instance=1,
        value=EventValues.ON
    )
    response = client.put("/telemetry/event", data=json.dumps(event_test, default=vars),)
    assert response.status_code == 200
    print(response.json(), "\n")
    assert response.json() != {}

