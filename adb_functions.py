from ppadb.client import Client as AdbClient

from uuid import uuid4

import json

# Default is "127.0.0.1" and 5037
client = AdbClient(host="127.0.0.1", port=5037)


def get_device(device_serial):
    devices = client.devices()

    for device in devices:
        if device.serial == device_serial:
            return device
    return None


def list_devices():
    devices = client.devices()
    return [device.serial for device in devices]


def get_device_battery_level(device_serial):
    device = get_device(device_serial)
    if device is None:
        return None
    return f"{device.get_battery_level()}%"


def get_device_info(device_serial, output_folder_path):
    device = get_device(device_serial)
    if device is None:
        return "Device not found"

    # Write the json output of this device to an output file
    result = device.get_properties()

    # Device info unique name
    output_path = (
        f"{output_folder_path}/DeviceInfo-{device_serial}-{str(uuid4())[0:4]}.json"
    )

    with open(output_path, "w") as fp:
        json.dump(result, fp)

    # Some interesting properties
    props = [
        {
            "name": "ro.build.fingerprint",
            "description": "Complete build fingerprint, including brand, device name, version, and build number, crucial for identifying software version and build.",
        },
        {
            "name": "ro.product.model",
            "description": "Indicates the model of the device, essential for compatibility checks, software updates, or repair purposes.",
        },
        {
            "name": "ro.build.version.release",
            "description": "Shows the version of the Android OS installed, important for app compatibility and understanding security features.",
        },
        {
            "name": "ro.crypto.state",
            "description": "Indicates if the device's storage is encrypted, crucial for data security and forensics.",
        },
        {
            "name": "ro.hardware",
            "description": "Provides information about the hardware platform, useful for understanding device capabilities and performance.",
        },
        {
            "name": "ro.secure",
            "description": "Shows if the device is running in secure mode, important for understanding security posture and root access considerations.",
        },
        {
            "name": "ro.boot.serialno",
            "description": "The serial number of the device, unique to each unit, crucial for tracking, warranty, or identification in case of theft or loss.",
        },
        {
            "name": "ro.product.locale",
            "description": "Indicates the default locale setting, useful for understanding the intended market or user preferences.",
        },
        {
            "name": "persist.sys.timezone",
            "description": "Shows the device's set timezone, relevant in forensic investigation for location settings or user preferences.",
        },
        {
            "name": "ro.build.version.security_patch",
            "description": "Date of the last security patch applied, critical for understanding the security level and vulnerability to known exploits.",
        },
    ]

    # Filter the properties to only include the ones we care about, then return the name, description, and value
    props = [
        {
            "name": prop["name"],
            "description": prop["description"],
            "value": result.get(prop["name"]),
        }
        for prop in props
    ]

    return str(props) + f"Successfully saved to {output_path}."


def search_files(device_serial, output_folder_path, directory, file_pattern):
    device = get_device(device_serial)
    if device is None:
        return "Device not found"
    results = device.shell(f"find {directory} -name '{file_pattern}'")

    # Remove any patterns of the form: find: './proc/17/task/17/net/stat/nf_conntrack': Permission denied
    results = results.split("\n")
    results = [result for result in results if "Permission denied" not in result]
    raw_results = "\n".join(results)

    # Write the raw output to a file
    output_path = (
        f"{output_folder_path}/SearchFiles-{device_serial}-{str(uuid4())[0:4]}.txt"
    )
    with open(output_path, "w") as fp:
        fp.write(raw_results)

    return raw_results + f"Successfully saved to {output_path}."


def capture_screenshot(device_serial, output_folder_path):
    device = get_device(device_serial)
    if device is None:
        return "Device not found"
    device.screencap()

    # Screenshot unique name
    output_path = f"{output_folder_path}/Screenshot-{uuid4()}.png"

    with open(output_path, "wb") as fp:
        fp.write(device.read_screencap())
    return f"Screenshot saved to {output_path}"


def list_installed_apps(device_serial, output_folder_path):
    """
    Output list of installed apps to a file

    Return a consolidated and cleaned list for the chatbot to use
    """

    device = get_device(device_serial)
    if device is None:
        return "Device not found"

    raw_output = device.shell("pm list packages -f")

    # Write the raw output to a file
    output_path = (
        f"{output_folder_path}/InstalledApps-{device_serial}-{str(uuid4())[0:4]}.txt"
    )
    with open(output_path, "w") as fp:
        fp.write(raw_output)

    clean_output = device.shell("pm list packages")

    apps = clean_output.replace("package:com.", "").split("\n")

    extra_text = ""
    app_text = " ".join(apps)

    if len(app_text) > 8000:
        app_text = app_text[0:8000]
        extra_text = f"This list is not comprehensive and some were left out."

    return (
        app_text
        + extra_text
        + f"There are {len(apps)} apps installed on this device."
        + f"Successfully saved to {output_path}."
    )


def get_wifi_networks_connected(device_serial):
    device = get_device(device_serial)
    if device is None:
        return "Device not found"

    # This will also work -> adb shell cat /data/misc/wifi/WifiConfigStore.xml
    return device.shell("dumpsys wifi | grep -E '^\\s*SSID:'")


def get_call_logs(device_serial):
    device = get_device(device_serial)
    if device is None:
        return "Device not found"

    return device.shell("content query --uri content://call_log/calls")


def get_running_processes(device_serial, output_folder_path):
    device = get_device(device_serial)
    if device is None:
        return "Device not found"

    raw_output = device.shell("ps -A")

    # Write the raw output to a file
    output_path = (
        f"{output_folder_path}/RunningProcesses-{device_serial}-{str(uuid4())[0:4]}.txt"
    )
    with open(output_path, "w") as fp:
        fp.write(raw_output)

    all_lines = raw_output.split("\n")[1:]

    output_lines = []
    for line in all_lines:
        cleaned_line = [r for r in line.split(" ") if r]
        if len(cleaned_line) > 1 and cleaned_line[0] != "root":
            output_lines.append(f"{cleaned_line[-1]}")

    extra_text = ""
    final_output = "\n".join(output_lines)
    if len(final_output) > 500:
        final_output = final_output[0:500]
        extra_text = f"This list is not comprehensive and some were left out."

    return final_output + extra_text + f"Successfully saved to {output_path}."


def get_device_location(device_serial):
    device = get_device(device_serial)
    if device is None:
        return "Device not found"

    return device.shell("dumpsys location")
