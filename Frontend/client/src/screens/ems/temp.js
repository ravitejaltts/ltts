export const data = {
  title: "Energy Management",
  items: [
    {
      title: "Source",
      name: "EnergySourceColumn",
      subtext: "{watts}W",
      actions: ["action_default"],
      action_default: {
        type: "navigate",
        action: {
          href: "/home/ems/sources",
        },
      },
      state: {
        watts: 0,
      },
      active: 0,
      widgets: [
        {
          name: "EmsSolarWidget",
          title: "SOLAR",
          subtext: "--",
          subtext_unit: "W",
          type: "Info",
          state: {
            onOff: false,
          },
          actions: null,
          active: false,
        },
        {
          name: "EmsShoreWidget",
          title: "SHORE",
          subtext: "--",
          subtext_unit: "W",
          type: "Info",
          state: {
            onOff: false,
          },
          actions: null,
          active: false,
        },
        {
          name: "EmsGeneratorWidget",
          title: "LP GENERATOR",
          subtext: 0,
          subtext_unit: "W",
          type: "Simple",
          state: {
            onOff: 0,
          },
          actions: ["action_default"],
          action_default: {
            type: "navigate",
            action: {
              href: "/home/ui/generator",
            },
          },
          switches: [
            {
              title: "Start",
              type: "DEADMAN",
              intervalMs: null,
              holdDelayMs: 1000,
              enabled: true,
              option_param: "mode",
              actions: {
                PRESS: null,
                HOLD: {
                  type: "api_call",
                  action: {
                    href: "/api/energy/ge/1/state",
                    type: "PUT",
                    param: {
                      $mode: 537,
                    },
                  },
                },
                RELEASE: null,
              },
            },
          ],
          active: 0,
        },
      ],
    },
    {
      title: "Battery",
      name: "EnergyBatteryColumn",
      subtext: "{soc} Charge Left",
      actions: ["action_default"],
      action_default: {
        type: "navigate",
        action: {
          href: "/home/ems/battery",
        },
      },
      state: {
        soc: "0%",
      },
      active: 1,
      widgets: [
        {
          name: "EmsBatteryMainWidget",
          title: null,
          type: "BatteryMain",
          BatteryMain: {
            value: 80,
            value_unit: "%",
            battery_low: true,
            battery_warning: false,
            remaining_high: "-- ",
            remaining_low: "-- ",
            text_high: "h",
            text_low: "m",
            subtext: "--",
          },
          state: {
            value: 0,
            value_unit: "%",
            battery_low: true,
            battery_warning: false,
            remaining_high: "-- ",
            remaining_low: "-- ",
            text_high: "h",
            text_low: "m",
            subtext: "--",
          },
        },
        {
          name: "EmsInverterWidget",
          title: "INVERTER XANTREX",
          subtext: "",
          type: "InverterEMSWidget",
          state: {
            onOff: 0,
            load: 0,
            overld: false,
            overldTimer: 0,
            maxLoad: 2000,
          },
          actions: ["action_default"],
          action_default: {
            type: "api_call",
            action: {
              href: "/api/energy/ei/1/state",
              type: "PUT",
              params: {
                $onOff: "int",
              },
            },
          },
          active: 0,
          inverterLoadText: "{load}W",
          inverterCapacityText: "of {maxLoad}W",
        },
      ],
    },
    {
      title: "Usage",
      name: "EnergyUsageColumn",
      subtext: "{watts}W",
      actions: ["action_default"],
      action_default: {
        type: "navigate",
        action: {
          href: "/home/ems/usage",
        },
      },
      state: {
        watts: 0,
      },
      active: null,
      widgets: [
        {
          name: "EmsUsageWidget",
          title: "USAGE",
          type: "UsageMain",
          UsageMain: {
            usage_level: 0,
            usage_unit: "kW",
            charge_level: 0,
            charge_unit: "kW",
            active: 0,
          },
        },
        {
          name: "EmsConsumerWidget",
          title: null,
          type: "Consumers",
          Consumers: [],
        },
      ],
    },
  ],
};
