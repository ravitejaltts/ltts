from copy import deepcopy

from pydantic import BaseModel


# TODO: Discover the defined floorplans dynamically instead of through import
from .vanilla import model_definition as VANILLA
from .vanilla import config_definition as Config_VANILLA

from ._500_XM524T import model_definition as _WM524T
from ._500_XM524T import config_definition as Config_WM524T

from ._500_XM524T import alternate_model_definition as _IM524T
from ._500_XM524T import alternate_config_definition as Config_IM524T

from ._500_XM524R import model_definition as _WM524R
from ._500_XM524R import config_definition as Config_WM524R

from ._500_XM524R import alternate_model_definition as _IM524R
from ._500_XM524R import alternate_config_definition as Config_IM524R

from ._500_XM524D import model_definition as _WM524D
from ._500_XM524D import config_definition as Config_WM524D

from ._500_XM524D import alternate_model_definition as _IM524D
from ._500_XM524D import alternate_config_definition as Config_IM524D

# from ._500_WM524NP import model_definition as _WM524NP

from ._800_848XX import model_definition as _BF848
from ._800_848XX import config_definition as Config_BF848

from ._800_W44R import model_definition as _W44R
from ._800_W44R import config_definition as Config_W44R

# ROBO500
from ._X500_XR524D import model_definition as _XR524D
from ._X500_XR524D import config_definition as Config_XR524D

# MOCK
from ._X500_MOCK import model_definition as MOCK
from ._X500_MOCK import config_definition as Config_MOCK


MODELS = [
    VANILLA,

    _WM524T,
    _IM524T,

    _WM524R,
    _IM524R,

    _WM524D,
    _IM524D,

    # _WM524NP,
    _BF848,

    _W44R,

    # ROBO500
    _XR524D,

    # MOCK All component floorplan
    MOCK
]


derivative_models = []
# Inject new revision and model years
# Some of the revisions are not true and would have to be revised later
# print(MODELS)
for model in MODELS:
    print('Creating derivative Model', model.get('floorPlan'))
    generator_fields = model.get('generator_fields')
    print('\t', 'Generator Fields', generator_fields)
    if generator_fields:
        model_years = generator_fields.get('modelYears', {})
        for model_year, fields in model_years.items():
            # Get the last digit of the year 2024 -> 4
            year = model_year[-1]

            for rev_id in fields.get('revisions', []):
                new_model = deepcopy(model)
                series_model = new_model['seriesModel']
                new_model['seriesModel'] = series_model[:5] + str(year) + str(rev_id)
                new_model['filters']['modelYears'] = [model_year]

                new_model['id'] = '{}.{}.{}'.format(
                    new_model.get('deviceType'),
                    new_model.get('seriesModel'),
                    new_model.get('floorPlan')
                )
                drop_fields = []
                for key, value in new_model.items():
                    if key.startswith('generator_'):
                        drop_fields.append(key)

                for key in drop_fields:
                    del new_model[key]

                derivative_models.append(new_model)
    else:
        print('No derivative models found', model.get('floorPlan'))


MODELS.extend(derivative_models)

[print(x.get('seriesModel'), x.get('floorPlan')) for x in MODELS]


MODEL_DICT = {
    "VANILLA": VANILLA,

    "WM524T": _WM524T,
    "IM524T": _IM524T,

    "WM524R": _WM524R,
    "IM524R": _IM524R,

    "WM524D": _WM524D,
    "IM524D": _IM524D,

    "DOMCOACH": _BF848,
    "XR524R": _XR524D,

    "W44R": _W44R,

    "MOCK": MOCK,
}


CONFIGS = [
    Config_VANILLA,
    Config_WM524T,
    Config_IM524T,
    Config_WM524R,
    Config_IM524R,
    Config_WM524D,
    Config_IM524D,
    Config_BF848,
    Config_W44R,
    # ROBO500,
    Config_XR524D,
    Config_MOCK,
]


class componentGroup(BaseModel):
    pass



if __name__ == '__main__':
    pass
