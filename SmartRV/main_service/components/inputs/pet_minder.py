pet_alerts = {
    "PM1": {
        "Severity": "High",
        "Notification Trigger": "Rx: Winnebago Connect has lost connection with the RV.",
        "Location": "Push, Dashboard",
        "Headline": "Lost RV Connection",
        "Temp Status": "*Last Known Temp*",
        "Short Description": "We're having trouble connecting to your RV.",
    },
    "PM2": {
        "Severity": "High",
        "Notification Trigger": "R11: Temperature is unknown, there's a sensor error.",
        "Location": "Push, Dashboard",
        "Headline": "Temperature Sensor Error",
        "Temp Status": "Current temp cannot be displayed.",
        "Short Description": "There is an error with the temperature sensor and current RV inside temp cannot be displayed.",
    },
    "PM4": {
        "Severity": "Mid",
        "Notification Trigger": "R11: Temperature is BELOW set range. Heat is OFF.",
        "Location": "Push, Dashboard",
        "Headline": "Inside Temp is Below Pet Range",
        "Temp Status": "Your RV temp is below Pet Comfort range: {temp}",
        "Short Description": "Please consider turning the heat on in your coach.",
    },
    "PM5": {
        "Severity": "Mid",
        "Notification Trigger": "R11: Temperature is BELOW set range. Heat is ON, thermostat set too low.",
        "Location": "Push, Dashboard",
        "Headline": "Inside Temp is Below Pet Range",
        "Temp Status": "Your RV temp is below Pet Comfort range: {temp}",
        "Short Description": "Your heat is set too low. Please consider raising the heating temp in your coach.",
    },
    "PM6": {
        "Severity": "High",
        "Notification Trigger": "R11: Temperature is BELOW set range, there is an error..",
        "Location": "Push, Dashboard",
        "Headline": "Furnace Isn't Responding",
        "Temp Status": "Your RV temp is below Pet Comfort range:{temp}",
        "Short Description": "The furnace power output control fuse is blown. Please try restarting your system.",
    },
    "PM7": {
        "Severity": "High",
        "Notification Trigger": "R11: Temperature is BELOW set range, WinnConnect cannot communicate with Climate Control.",
        "Location": "Push, Dashboard",
        "Headline": "Climate Control Cannot Be Reached",
        "Temp Status": "Your RV temp is below Pet Comfort range: {temp}",
        "Short Description": "The climate control system cannot be reached due to xyz.",
    },
    "PM8": {
        "Severity": "High",
        "Notification Trigger": "R11:Temperature is BELOW set range, the outside temperature is too severe.",
        "Location": "Push, Dashboard",
        "Headline": "Inside Temp is Below Pet Range",
        "Temp Status": "Your RV temp is below Pet Comfort range: {temp}",
        "Short Description": "Please consider turning the heat on in your coach.",
    },
    "PM10": {
        "Severity": "Mid",
        "Notification Trigger": "R11: Temperature is ABOVE set range, AC is OFF.",
        "Location": "Push, Dashboard",
        "Headline": "Inside Temp is Above Pet Range",
        "Temp Status": "Your RV temp is above Pet Comfort range: {temp}",
        "Short Description": "Please consider turning the air conditioning on in your coach.",
    },
    "PM11": {
        "Severity": "Mid",
        "Notification Trigger": "R11: Temperature is ABOVE set range, AC is on, thermostat set too high..",
        "Location": "Push, Dashboard",
        "Headline": "Inside Temp is Above Pet Range",
        "Temp Status": "Your RV temp is above Pet Comfort range: {temp}",
        "Short Description": "Your AC is set too high. Please consider lowering the cooling temp in your coach..",
    },
    "PM12": {
        "Severity": "High",
        "Notification Trigger": "R11: Temperature is ABOVE set range, there is an error..",
        "Location": "Push, Dashboard",
        "Headline": "Air Conditioner Isn't Responding",
        "Temp Status": "Your RV temp is above Pet Comfort range: {temp}",
        "Short Description": "Winnebago Connect lost communication with the Air Conditioner. Please try restarting your system.",
    },
    "PM13": {
        "Severity": "High",
        "Notification Trigger": "R11: Temperature is ABOVE set range, WinnConnect cannot communicate with Climate Control.",
        "Location": "Push, Dashboard",
        "Headline": "Climate Control Cannot Be Reached",
        "Temp Status": "Your RV temp is above Pet Comfort range: {temp}",
        "Short Description": "The climate control system cannot be reached due to xyz.",
    },
    "PM14": {
        "Severity": "High",
        "Notification Trigger": "R11:Temperature is ABOVE set range, the outside temperature is too severe.",
        "Location": "Push, Dashboard",
        "Headline": "Inside Temp is Above Pet Range",
        "Temp Status": "Your RV temp is above Pet Comfort range: {temp}",
        "Short Description": "The temperature outside is very high, please consider lowering the cooling temp in your coach.",
    },
    "PM16": {
        "Severity": "Low",
        "Notification Trigger": "Rx: RV Ignition is on, AGS has been disabled.",
        "Location": "Push, Dashboard",
        "Headline": "RV Ignition is On",
        "Temp Status": "Your RV temp is within Pet Comfort range: {temp}",
        "Short Description": "The AGS has been disabled and your ignition has been turned on.",
    },
    "PM17": {
        "Severity": "Low",
        "Notification Trigger": "Rx: Quiet Hours are engaged, AGS cannot turn on.",
        "Location": "Push, Dashboard",
        "Headline": "Quiet Hours Are Active",
        "Temp Status": "{temp}",
        "Short Description": "During Quiet Hours your generator will not run.",
    },
    "PM19": {
        "Notification Trigger": "R14: Shore Power Restored",
        "Location": "Push",
        "Headline": "Update: Shore Power Is Active",
        "Temp Status": "None",
        "Short Description": "None",
    },
    "PM20": {
        "Notification Trigger": "R18: System has started the generator.",
        "Location": "Push",
        "Headline": "Update: The Generator Has Started",
        "Temp Status": "None",
        "Short Description": "None",
    },
    "PM21": {
        "Severity": "Mid/High",
        "Notification Trigger": "R20: Out of fuel",
        "Location": "Push, Dashboard",
        "Headline": "Fuel Empty. Battery Has XX% Remaining",
        "Temp Status": "{temp}",
        "Short Description": "Your RV battery is low and cannot be charged because the fuel tank is empty.",
    },
    "PM22": {
        "Notification Trigger": "R22: Power source switched from shore to battery.",
        "Location": "Push",
        "Headline": "Update: Power Source now on Battery.",
        "Temp Status": "None",
        "Short Description": "None",
    },
    "PM23": {
        "Severity": "Mid/High",
        "Notification Trigger": "R23: Generator has stopped.",
        "Location": "Push, Dashboard",
        "Headline": "Generator Has Stopped Low Fuel",
        "Temp Status": "{temp}",
        "Short Description": "Battery is at XX%. Please return to your RV soon.",
    },
    "PM24": {
        "Severity": "Mid/High",
        "Notification Trigger": "R23: Generator has stopped.",
        "Location": "Push, Dashboard",
        "Headline": "Generator Has Stopped Quiet Hours",
        "Temp Status": "{temp}",
        "Short Description": "Quiet hours are in effect until 00:00AM. AGS will not start the generator during this time.",
    },
    "PM25": {
        "Severity": "Mid/High",
        "Notification Trigger": "R25: Battery is low, AGS is off.",
        "Location": "Push, Dashboard",
        "Headline": "RV Battery is Low. Battery Has 15% Remaining",
        "Temp Status": "{temp}",
        "Short Description": "Your RV battery is low and needs to charge. Please turn on the generator or enable AGS.",
    },
    "PM26": {
        "Notification Trigger": "R27: Battery is charged",
        "Location": "Push",
        "Headline": "Battery is Fully Charged",
        "Temp Status": "None",
        "Short Description": "None",
    },
    "PM27": {
        "Notification Trigger": "R25: Battery is low, AGS on, Generator cannot start",
        "Location": "Push, Dashboard",
        "Headline": "Battery is Low, Generator OFF",
        "Temp Status": "{temp}",
        "Short Description": "The generator has tried to start but is experiencing an error.",
    },
}
