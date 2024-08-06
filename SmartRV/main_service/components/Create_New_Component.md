# New Component that fits and existing category
- Find the fitting category: e.g. energy
    - /main_service/components/energy.py
- Check if it requires a new code (two letters)
    - Yes ->
        - Open '/common_libs/models/common.py'
        - Add to the CODE_TO_ATTR dictionary
        - Make sure they are unique, there cannot be duplicates
        - Add to 'COMP_TYPE_?' (Might not want this anymore)

    - Create a State and a Component (copy a small existing component)
        - State define the fields, their types and defaults, eventId and if they are a setting or not

    - Add new eventIDs to RVEvents /common_libs/models/common.py
    - Add new literals to EventValues /common_libs/models/common.py

    - Add the new component class (not the state) to `/main_service/components/generate_templates.py` COMPONENTS
    - Add pair of component and state to `/main_service/components/catalog.py` in `components`
        `(LoadShedding500, LoadSheddingState),`
    -Add new code (e.g. 'ls') to `/main_service/components/common.py` to `ComponentTypeEnum`
        `    ls = 'Load Shedding'`
        Take care of sorting it alphabetically

    - Generate components running `python3 generate_tempaltes.py`
    - Errors will be called out and suually are around omissions in the required schema, such as a description for a state property


# New Category


# Add to vehicle
- Make sure the component is already pert of the gneration as above
- Open the vehicle template that needs the components such as `XM524T`
- Make sure the component(s) needed are imported on top
- Go to the end of the components key of the main dictionary (if present) or in the section where it makes the most sense like Energy
- Add an instance of the model with
    - instance
    - attributes (name and description are mandatory)
    - relatedComponents if any
    - Optioncodes if any



# Upgrading a vehicle component



# Creating a new vehicle
