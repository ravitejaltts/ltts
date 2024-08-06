from ble import (
    Service,
)


class GenericService(Service):
    def __init__(self, bus, index, UUID):
        Service.__init__(self, bus, index, UUID, True)

        self.UUID = UUID
