'''Defines that modules to load in the HAL.
Some of which are shared like sw_features, and some may be specific.

TODO: We are aiming to reduce the need for custom files by using specific
components.
'''

HAL_CATEGORIES_500 = {
    "climate":
        "modules.hardware._500.hw_climate",
    "electrical":
        "modules.hardware._500.hw_electrical",
    "energy":
        "modules.hardware._500.hw_energy",
    "lighting":
        "modules.hardware._500.hw_lighting",
    "vehicle":
        "modules.hardware._500.hw_vehicle",
    "watersystems":
        "modules.hardware._500.hw_watersystems",
    "connectivity":
        "modules.hardware.cradlepoint.hw_connectivity",
    "movables":
        "modules.hardware.hw_movables",
    "system":
        "modules.hardware.hw_system",
    'features':
        'modules.sw_features'
}
