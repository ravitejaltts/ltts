# Functional Control Panel


## Assumptions
- Each widget only knows one action / API call !
- Widgets are provided in a big list and can be filtered by category
- Overview page will provide a list of categories to filter

## Decisions
- Levels go away
- categories is a list of title, category, name under overview key
    - null is specifal as it should remove the filter
- Shorten name for Functional Control Panel (Dom)
- Change Icon for FCP


## Questions
- Do we want to use state key to put the things affected by API like we do in other places ?


## TODO
- Figure out how to generate the content needed based on the model definition
     - Get Circuits as defined in hw_electrical
     - Get list of system functions that are same (reboot etc.)
     - Get list of functions that might be specific to the HMI (brightness)
     - Get list of other HW elements from HW layer and map widget type somewhere (JSON?)
