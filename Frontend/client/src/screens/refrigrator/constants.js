export const REFRIDGERATOR_TITLE = "Refrigerator";
export const REFRIDGERATOR_DEFAULT_TEMP = "--";
export const REFRIDGERATOR_TEMPERATURE_UNIT = "°F";

export const REFRIDGERATOR_TOP_LINE = "Average Temp --";
export const REFRIDGERATOR_SUB_TEXT = "Current Temp";
export const REFRIDGERATOR_BUTTON_DEFAULT = "See Full History";

export const refData = {
  overview: {
    title: "Refrigeration",

    settings: {
      href: "/ui/refrigerator/settings",

      type: "GET",
    },

    bottom_widget_refrigerator: {
      title: "FRIDGE",

      text: 36,

      sidetext: "°F",

      subtext: "Inside Range",

      alert: false,
    },

    bottom_widget_freezer: {
      title: "FREEZER",

      text: 32,

      sidetext: "°F",

      subtext: "Inside Range",

      alert: false,
    },
  },

  controls: {
    refrigerator_current_history: {
      title: "Refrigerator Temperature History",

      subtext: "2023-11-01",

      refrigerator_data: [
        {
          event: 9400,

          value: "36° F",

          text: "36° F",

          time: "02:37 PM",

          timestamp: 1698863847.5782156,

          alert: false,
        },
        {
          event: 9400,

          value: "36° F",

          text: "36° F",

          time: "02:37 PM",

          timestamp: 1698863847.5782156,

          alert: false,
        },
        {
          event: 9400,

          value: "36° F",

          text: "36° F",

          time: "02:37 PM",

          timestamp: 1698863847.5782156,

          alert: false,
        },
        {
          event: 9400,

          value: "36° F",

          text: "36° F",

          time: "02:37 PM",

          timestamp: 1698863847.5782156,

          alert: false,
        },
        {
          event: 9400,

          value: "36° F",

          text: "36° F",

          time: "02:37 PM",

          timestamp: 1698863847.5782156,

          alert: false,
        },
        {
          event: 9400,

          value: "36° F",

          text: "36° F",

          time: "02:37 PM",

          timestamp: 1698863847.5782156,

          alert: false,
        },
        {
          event: 9400,

          value: "36° F",

          text: "36° F",

          time: "02:37 PM",

          timestamp: 1698863847.5782156,

          alert: false,
        },
        {
          event: 9400,

          value: "36° F",

          text: "36° F",

          time: "02:37 PM",

          timestamp: 1698863847.5782156,

          alert: false,
        },

        {
          event: 50006,

          value: "39° F",

          text: "39° F",

          time: "02:36 PM",

          timestamp: 1698863817.325948,

          alert: true,
        },

        {
          event: 50006,

          value: "34° F",

          text: "34° F",

          time: "02:36 PM",

          timestamp: 1698863795.5558784,

          alert: true,
        },
      ],

      refrigerator_full_history: {
        title: "See Refrigerator History",

        type: "button",

        PRESS: {
          type: "navigate",

          action: {
            href: "/ui/refrigerator/fullhistory",

            type: "PUT",

            params: {
              applianceType: "refrigerator",

              date: "2023-11-01",
            },
          },
        },
      },
    },

    freezer_current_history: {
      title: "Freezer Temperature History",

      subtext: "Wednesday, 2023-11-01",

      freezer_data: [
        {
          event: 9400,

          value: "32° F",

          text: "32° F",

          time: "02:37 PM",

          timestamp: 1698863849.8339553,

          alert: false,
        },
        {
          event: 9400,

          value: "32° F",

          text: "32° F",

          time: "02:37 PM",

          timestamp: 1698863849.8339553,

          alert: false,
        },
        {
          event: 9400,

          value: "32° F",

          text: "32° F",

          time: "02:37 PM",

          timestamp: 1698863849.8339553,

          alert: false,
        },
        {
          event: 9400,

          value: "32° F",

          text: "32° F",

          time: "02:37 PM",

          timestamp: 1698863849.8339553,

          alert: false,
        },
        {
          event: 9400,

          value: "32° F",

          text: "32° F",

          time: "02:37 PM",

          timestamp: 1698863849.8339553,

          alert: false,
        },
        {
          event: 9400,

          value: "32° F",

          text: "32° F",

          time: "02:37 PM",

          timestamp: 1698863849.8339553,

          alert: false,
        },
        {
          event: 9400,

          value: "32° F",

          text: "32° F",

          time: "02:37 PM",

          timestamp: 1698863849.8339553,

          alert: false,
        },
        {
          event: 9400,

          value: "32° F",

          text: "32° F",

          time: "02:37 PM",

          timestamp: 1698863849.8339553,

          alert: false,
        },
        {
          event: 9400,

          value: "32° F",

          text: "32° F",

          time: "02:37 PM",

          timestamp: 1698863849.8339553,

          alert: false,
        },
        {
          event: 9400,

          value: "32° F",

          text: "32° F",

          time: "02:37 PM",

          timestamp: 1698863849.8339553,

          alert: false,
        },
        {
          event: 9400,

          value: "32° F",

          text: "32° F",

          time: "02:37 PM",

          timestamp: 1698863849.8339553,

          alert: false,
        },
        {
          event: 9400,

          value: "32° F",

          text: "32° F",

          time: "02:37 PM",

          timestamp: 1698863849.8339553,

          alert: false,
        },

        {
          event: 9400,

          value: "28° F",

          text: "28° F",

          time: "02:36 PM",

          timestamp: 1698863819.3471575,

          alert: false,
        },

        {
          event: 9400,

          value: "32° F",

          text: "32° F",

          time: "02:36 PM",

          timestamp: 1698863798.0277445,

          alert: false,
        },
      ],

      freezer_full_history: {
        title: "See Freezer History",

        type: "button",

        PRESS: {
          type: "navigate",

          action: {
            href: "/ui/refrigerator/freezer/fullhistory",

            type: "PUT",

            params: {
              applianceType: "freezer",

              date: "2023-11-01",
            },
          },
        },
      },
    },
  },
};

export const refSettings = {
  title: "Refrigerator Settings",

  configuration: [
    {
      title: null,

      items: [
        {
          title: "Fridge Temp Alert",

          selected_text: "on",

          type: "Simple",

          Simple: {
            onOff: 1,
          },

          actions: ["action_default"],

          action_default: {
            type: "api_call",

            action: {
              href: "/api/climate/refrigerator/settings/alert",

              type: "PUT",

              params: {
                $onOff: "int",
              },
            },
          },
        },

        {
          title: "Temp Range",

          items: [
            {
              title: "upper limit",

              value: 34,

              type: "Upper_Limit",

              actions: ["change_upper_limit"],

              change_upper_limit: {
                type: "api_call",

                action: {
                  href: "/api/climate/refrigerator/settings/temprange",

                  type: "PUT",

                  params: {
                    $fdg_upper_limit: "float",

                    $fdg_lower_limit: "float",
                  },
                },
              },
            },

            {
              title: "lower limit",

              value: 34,

              type: "Lower_Limit",

              actions: ["change_lower_limit"],

              change_lower_limit: {
                type: "api_call",

                action: {
                  href: "/api/climate/refrigerator/settings/temprange",

                  type: "PUT",

                  params: {
                    $upper_limit: "float",

                    $lower_limit: "float",
                  },
                },
              },
            },
          ],
        },

        {
          title: "restore default",

          actions: ["action_default"],

          action_default: {
            type: "api_call",

            action: {
              href: "/api/climate/refrigerator/settings/restoredefault",

              type: "PUT",
            },
          },
        },
      ],
    },

    {
      title: null,

      items: [
        {
          title: "Freezer Temp Alert",

          selected_text: "on",

          type: "Simple",

          Simple: {
            onOff: 1,
          },

          actions: ["action_default"],

          action_default: {
            type: "api_call",

            action: {
              href: "/api/climate/refrigerator/freezer/settings/alert",

              type: "PUT",

              params: {
                $onOff: "int",
              },
            },
          },
        },

        {
          title: "Temp Range",

          items: [
            {
              title: "upper limit",

              value: 38,

              type: "Upper_Limit",

              actions: ["change_upper_limit"],

              change_upper_limit: {
                type: "api_call",

                action: {
                  href: "/api/climate/refrigerator/freezer/settings/temprange",

                  type: "PUT",

                  params: {
                    $upper_limit: "float",

                    $lower_limit: "float",
                  },
                },
              },
            },

            {
              title: "lower limit",

              value: 38,

              type: "Lower_Limit",

              actions: ["change_lower_limit"],

              change_lower_limit: {
                type: "api_call",

                action: {
                  href: "/api/climate/refrigerator/freezer/settings/temprange",

                  type: "PUT",

                  params: {
                    $fdg_upper_limit: "float",

                    $fdg_lower_limit: "float",
                  },
                },
              },
            },
          ],
        },

        {
          title: "restore default",

          actions: ["action_default"],

          action_default: {
            type: "api_call",

            action: {
              href: "/api/climate/refrigerator/freezer/settings/restoredefault",

              type: "PUT",
            },
          },
        },
      ],
    },
  ],

  information: [
    {
      title: "MANUFACTURER INFORMATION",

      items: [
        {
          title: "Refrigerator",

          sections: [
            {
              title: "FRIDGE",

              items: [
                {
                  key: "Manufacturer",

                  value: "",
                },

                {
                  key: "Product Model",

                  value: "",
                },

                {
                  key: "Part#",

                  value: "",
                },
              ],
            },

            {
              title: "SENSOR",

              items: [
                {
                  key: "Manufacturer",

                  value: "KiB",
                },

                {
                  key: "Product Model",

                  value: "Some Model",
                },
              ],
            },
          ],
        },

        {
          title: "Refrigerator",

          sections: [
            {
              title: "FRIDGE",

              items: [
                {
                  key: "Manufacturer",

                  value: "",
                },

                {
                  key: "Product Model",

                  value: "",
                },

                {
                  key: "Part#",

                  value: "",
                },
              ],
            },

            {
              title: "SENSOR",

              items: [
                {
                  key: "Manufacturer",

                  value: "KiB",
                },

                {
                  key: "Product Model",

                  value: "Some Model",
                },
              ],
            },
          ],
        },
      ],
    },
  ],

  notification: [],
};
