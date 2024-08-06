# Component Property Rules

## mode / onOff / setMode
If a component only supports a simple operation for on off, the property shall be mode with the two options EventValues.OFF and EventValues.ON.

```
{"mode": 0|1}
```

If a component supports more modes but does not have a superseding onOff that overrides the mode selection it shall use mode as well

```
{
    "mode": 0|525|526
}
```

If a component has a superseding onOff such e.g. the Thermostat which, when in off does not support a mode shall use both properties mode and onOff

```
{
    "onOff": 0|1,
    "mode": 525|526
}
```

Ultimately, if a component has an onOff switch, subsequent modes that the user can request and an actual mode the sytem operates in, then it shall use onOff, mode and setMode. Thermostat is an example which allows the user to turn it off overall using onOff, set a desired mode such as AUTO, HEAT, COOL, ..., in setMode and the system will report its actual mode in mode.

```
{
    "onOff": 0|1,
    "setMode": 525|526|527,
    "mode": 0
}
```
