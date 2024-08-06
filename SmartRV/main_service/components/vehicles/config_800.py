'''Defines that modules to load in the HAL.
Some of which are shared like sw_features, and some may be specific.

TODO: We are aiming to reduce the need for custom files by using specific
components.
'''

# TODO: Update to use 800 specific code where needed
# NOTE: Aiming to not have 800 specific code but components that are specific
# to the 800 as needed
HAL_CATEGORIES_800 = {
    "climate":
        "modules.hardware._500.hw_climate",
    "electrical":
        "modules.hardware._500.hw_electrical",
    "energy":
        "modules.hardware._500.hw_energy",
    "lighting":
        "modules.hardware._500.hw_lighting",
    # TODO: Do we need an 800 specific vehicle ?
    "vehicle":
        "modules.hardware._500.hw_vehicle",
    "watersystems":
        "modules.hardware._500.hw_watersystems",
    "connectivity":
        "modules.hardware.cradlepoint.hw_connectivity",
    # "movables":
    #     "modules.hardware.hw_movables",
    "system":
        "modules.hardware.hw_system",
    'features':
        'modules.sw_features'
}
