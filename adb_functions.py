from ppadb.client import Client as AdbClient

from uuid import uuid4

import json

# Default is "127.0.0.1" and 5037
client = AdbClient(host="127.0.0.1", port=5037)
print(client.version())


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

    return props


def search_files(device_serial, directory, file_pattern):
    device = get_device(device_serial)
    if device is None:
        return "Device not found"
    results = device.shell(f"find {directory} -name '{file_pattern}'")

    # Remove any patterns of the form: find: './proc/17/task/17/net/stat/nf_conntrack': Permission denied
    results = results.split("\n")
    results = [result for result in results if "Permission denied" not in result]
    return "\n".join(results)


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


# def list_installed_apps(device_serial):
#     device = get_device(device_serial)
#     if device is None:
#         return "Device not found"
#     return device.shell("pm list packages")


# def save_report_output(output_path, report_name, report_output):
#     with open(f"{output_path}/{report_name}", "w") as fp:
#         fp.write(report_output)
#     return f"Report saved to {output_path}"
