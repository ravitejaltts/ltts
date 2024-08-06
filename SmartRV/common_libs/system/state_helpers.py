'''Helper function to process farfield special condition states.'''
from starlette.responses import JSONResponse


def check_special_states(component, in_state):
    '''Must be a list of dictionaries in special and the state as a dictionary passed in.'''
    match_found = False
    for special_state in component.attributes.get('special-states', []):
        state_found = True
        for prop, value in special_state.items():
            try:
                print(prop, '=', value, )
                print('incoming state', prop, '=', in_state[prop])
                if value != in_state[prop]:
                    state_found = False
                    break
            except KeyError:
                # Key Error but check other options
                pass
        if state_found is True:
            match_found = True
            break

    if match_found is False:
        return JSONResponse(
                status_code=403,
                content={"detail": "Farfield commanding not allowed for this component."}
            )
    else:
        return None

