from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type

from adb_functions import (
    list_devices,
    get_device_battery_level,
    get_device_info,
    search_files,
    list_installed_apps,
    get_running_processes,
)


def get_tool_metadata_from_name(tool_name: str):
    """
    Useful chat messages that help inform the user how information was gathered using adb
    """
    if tool_name == "get_device_battery_level_tool":
        return """
---
Additional Info:\n
- Bot Action: Get Device Battery Level
- Info: This action uses the adb command `adb shell dumpsys battery` to get the battery level of the device.
"""
    elif tool_name == "get_device_info_tool":
        return """
---
Additional Info:\n
- Bot Action: Get Device Info
- Info: This action uses the adb command `adb shell getprop` to get the device info.
"""
    elif tool_name == "list_installed_apps_tool":
        return """
---
Additional Info:\n
- Bot Action: Get Installed Applications
- Info: This action uses the adb command `adb shell pm list packages` to get the list of installed apps on the device.
"""
    elif tool_name == "search_device_files_tool":
        return """
---
Additional Info:\n
- Bot Action: Search Device Files
- Info: This action uses the adb command `adb shell find {directory} pattern -name {file_pattern}` to search the device for files that match a specific pattern.
"""
    elif tool_name == "list_running_processes_tool":
        return """
---
Additional Info:\n
- Bot Action: List Running Processes
- Info: This action uses the adb command `adb shell ps -A` to list all the processes currently running on the device.
"""


class SerialInput(BaseModel):
    serial_number: str = Field(description="Device serial number")


class SerialAndOutputFolderInput(BaseModel):
    serial_number: str = Field(description="Device serial number")
    output_folder: str = Field(description="Absolute path to output folder")


class SearchInput(BaseModel):
    serial_number: str = Field(description="Device serial number")
    output_folder: str = Field(description="Absolute path to output folder")
    directory: str = Field(
        description="Directory to search, needs to be an absolute path or '.' if you want to search current directory"
    )
    file_pattern: str = Field(
        description="File regex pattern to search for, i.e. *.txt"
    )


class ListDevicesTool(BaseTool):
    name = "list_devices_tool"
    description = """
        for listing the available android devices connected to your computer
        """
    args_schema: Type[BaseModel] = None

    def _run(self, tool_input: str = None):
        return list_devices()

    def _arun(self):
        raise NotImplementedError("list_devices_tool does not support async")


class GetDeviceBatteryLevelTool(BaseTool):
    name = "get_device_battery_level_tool"
    description = """
        for getting the battery level of a device
        """
    args_schema: Type[BaseModel] = SerialInput

    def _run(self, serial_number: str = None):
        return get_device_battery_level(serial_number)

    def _arun(self):
        raise NotImplementedError(
            "get_device_battery_level_tool does not support async"
        )


class GetDeviceInfoTool(BaseTool):
    name = "get_device_info_tool"
    description = """
        for getting simple info about the device. Saves the full output to the output_folder, but will return some useful info. Mention that you saved it in your response.
        """
    args_schema: Type[BaseModel] = SerialAndOutputFolderInput

    def _run(self, serial_number: str, output_folder: str):
        return get_device_info(serial_number, output_folder)

    def _arun(self):
        raise NotImplementedError("get_device_info_tool does not support async")


class SearchDeviceFilesTool(BaseTool):
    name = "search_device_files_tool"
    description = """
        for searching the device for files that match a specific pattern i.e. *.txt
        """
    args_schema: Type[BaseModel] = SearchInput

    def _run(
        self, serial_number: str, output_folder: str, directory: str, file_pattern: str
    ):
        return search_files(serial_number, output_folder, directory, file_pattern)

    def _arun(self):
        raise NotImplementedError("search_device_files_tool does not support async")


class ListInstalledAppsTool(BaseTool):
    name = "list_installed_apps_tool"
    description = """
        for listing the apps that are currently installed on the device
        """
    args_schema: Type[BaseModel] = SerialAndOutputFolderInput

    def _run(self, serial_number: str, output_folder: str):
        return list_installed_apps(serial_number, output_folder)

    def _arun(self):
        raise NotImplementedError("list_installed_apps_tool does not support async")


class ListRunningProcessesTool(BaseTool):
    name = "list_running_processes_tool"
    description = """
        for listing the processes currently running on this device
        """
    args_schema: Type[BaseModel] = SerialAndOutputFolderInput

    def _run(self, serial_number: str, output_folder: str):
        return get_running_processes(serial_number, output_folder)

    def _arun(self):
        raise NotImplementedError("list_running_processes_tool does not support async")
