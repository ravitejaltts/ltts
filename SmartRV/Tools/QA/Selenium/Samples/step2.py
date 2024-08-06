import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.touch_actions import TouchActions
from selenium.webdriver.chrome.options import Options

# This might help setting up chrome to be as close as possible to the HMI
# https://chromium.googlesource.com/chromium/src/+/167a7f5e03f8b9bd297d2663ec35affa0edd5076/third_party/WebKit/Source/devtools/front_end/emulated_devices/module.json
mobile_emulation = {
    "deviceMetrics": {
        "width": 1280, 
        "height": 800, 
        "pixelRatio": 0.5 
    },
}

chrome_options = Options()
chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
# chrome_options.add_experimental_option('w3c', False)

driver = webdriver.Chrome(options = chrome_options)
# driver = webdriver.Chrome()
driver.set_window_size(1280, 800)

driver.get("http://localhost:8000")


# TODO: Figure out how this works due to W3C issues, cannot immediately understand if these features are dropped in favor of W3C mode or if just another mode of working with it is required
# touch_actions = TouchActions(driver)
# TODO: Figure out how to use ActionChains to swipe left and right
actions = ActionChains(driver)

# INFO: The selection here is way to specific to be useful, need to work with Uday to provide meaningful IDs/Name/Attributes that do not change often
current_temp = driver.find_element_by_class_name("temp_mainTemp__bdVdg")
# print(current_temp)
# print(dir(current_temp))
# print(current_temp.text)
# INFO: Python way of confirming an expected value, will fail the code if not
assert "72" == current_temp.text

temp_down = driver.find_element_by_class_name("temp_controlButtons__5W8PH")
temp_down.click()
time.sleep(1)
temp_down.click()
input('ENTER to continue')
temp_down.click()

assert "69" == current_temp.text

input('ENTER to continue')

temp_up = driver.find_element_by_xpath("/html/body/div/div/div[2]/div[2]/div[2]/div[2]/div/div[3]/button[2]")
# print(temp_up)
# print(dir(temp_up))
temp_up.click()
temp_up.click()


assert "71" == current_temp.text

input('ENTER to continue')

for i in range(50):
    temp_up.click()
    assert int(current_temp.text) == (71 + i + 1)

input('ENTER to continue')
arrow = driver.find_element_by_xpath('/html/body/div/div/div[3]')
arrow.click()

input('ENTER to continue')

# Check for elements expected
time.sleep(1)

back = driver.find_element_by_xpath('/html/body/div/div/div[1]/button')
back.click()

# Check that we are back on the home screen

input('ENTER to close')

driver.close()