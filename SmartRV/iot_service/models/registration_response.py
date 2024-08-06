from iot_service.utils import Utils
from urllib.parse import urlparse
class RegistrationResponse:
    """Represents the response received from the platform's PATCH registration endpoint"""

    success: bool
    """Whether or not the request to the platform was successful"""

    message: str
    """Error message when request was not successful"""

    request_id: str
    """Internal ID of the http request"""

    errors: str
    """List of errors if applicable"""

    device_id: str
    """Device Identifier"""

    device_type: str
    """Determined Device Type based on VIN"""

    serial_number: str
    """Determined Device Serial Number based on VIN"""

    certificate: str
    """The device's x.509 certificate"""

    dps_host: str
    """DPS Host url used in provisioning"""

    dps_scope: str
    """DPS Scope ID used in provisioning"""

    csr_required: str
    """Whether or not a CSR is required to retrieve a device's certificate"""

    attributes: dict
    """Tags/Attributes associated with the device"""

    floor_plan: str
    """Attribute to Determined Floorplan Options based on VIN"""

    series_model: str
    """Attribute to Determined Floorplan Options based on VIN"""

    option_codes: str
    """Attribute to Determined Floorplan Options based on VIN"""

    transfer: str
    '''Is the platform asking us to transfer?'''

    transfer_path: str
    '''Did we get a request to move environments?'''

    transfer_expires: str
    '''Is this a temp path?'''

    installation_cert: str
    '''Did we receive a environment cert?'''

    installation_cert_name: str
    '''Did we receive a environment cert?'''

    def __init__(self, obj: dict):
        self.success = obj.get('success', None)
        self.message = obj.get('message', None)
        self.request_id = obj.get('requestId', None)
        self.errors = obj.get('errors', None)
        self.device_id = obj.get('deviceId', None)
        self.device_type = obj.get('deviceType', None)
        self.serial_number = obj.get('serialNumber', None)
        self.certificate = obj.get('cert', None)
        self.dps_host = obj.get('dpsHost', None)
        self.dps_scope = obj.get('dpsScope', None)
        self.csr_required = obj.get("csrRequired", None)
        self.attributes = obj.get("attributes", obj.get("attrs", None))
        if self.attributes is not None:
            self.series_model = self.attributes.get("seriesModel", "")
            self.floor_plan = self.attributes.get("floorPlan", "")
            self.option_codes = self.attributes.get("optionCodes", "")
            self.model_year = self.attributes.get("modelYear", "")
        else:
            self.series_model = ""
            self.floor_plan = ""
            self.option_codes = ""
            self.model_year = ""
        self.transfer = obj.get("transfer", None)
        if self.transfer is not None:
            self.transfer_path = self.transfer.get("path", "")
            self.transfer_expires = self.transfer.get("expires", None)
        else:
            self.transfer_path = ""
            self.transfer_expires = None
        self.installation_cert = obj.get("installationCert", None)
        if self.installation_cert is not None:
            if self.transfer_path != "":
                parsed_url = urlparse(self.transfer_path)
                self.installation_cert_name = parsed_url.hostname.split('.')[0] + '-env.newraw'
                Utils.put_secret(self.installation_cert_name, self.installation_cert)
            else:
                self.installation_cert_name = ""
        else:
            self.installation_cert_name = ""

    def __dict__(self):
        return {
            "success": self.success,
            "message": self.message,
            "requestId": self.request_id,
            "errors": self.errors,
            "deviceId": self.device_id,
            "deviceType": self.device_type,
            "serialNumber": self.serial_number,
            "dpsHost": self.dps_host,
            "dpsScope": self.dps_scope,
            "csrRequired": self.csr_required,
            "seriesModel": self.series_model,
            "floorPlan": self.floor_plan,
            "optionCodes": self.option_codes,
            "attributes": self.attributes,
            "transfer_path": self.transfer_path,
            "transfer_expires": self.transfer_expires,
            "installation_cert": self.installation_cert_name,
        }
