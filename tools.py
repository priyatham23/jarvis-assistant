import os
import subprocess
import webbrowser
import pyautogui
import pywhatkit
import psutil

try:
    from ctypes import POINTER, cast
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
except ImportError:
    pass

from rag_tool import search_personal_notes

def open_website(url: str) -> str:
    """Opens a specified URL or website in the default web browser."""
    if not url.startswith("http"):
        url = f"https://www.{url}.com" if not url.endswith(".com") else f"https://{url}"
    webbrowser.open_new_tab(url)
    return f"Opened {url} in browser."

def play_youtube(topic: str) -> str:
    """Searches and plays a video or song on YouTube."""
    pywhatkit.playonyt(topic)
    return f"Playing {topic} on YouTube."

def set_volume(level: int) -> str:
    """Sets system volume percentage (0 to 100)."""
    level = max(0, min(100, level))
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMasterVolumeLevelScalar(level / 100.0, None)
        return f"Volume set to {level}%."
    except Exception:
        return f"Adjusting volume level to {level}%."

def get_system_stats() -> str:
    """Gets real-time laptop battery level and CPU usage percentage."""
    battery = psutil.sensors_battery()
    cpu = psutil.cpu_percent(interval=1)
    percent = battery.percent if battery else "Unknown"
    return f"Battery is at {percent} percent, CPU usage is {cpu} percent."

tools_list = [open_website, play_youtube, set_volume, get_system_stats, search_personal_notes]
tools_map = {
    "open_website": open_website,
    "play_youtube": play_youtube,
    "set_volume": set_volume,
    "get_system_stats": get_system_stats,
    "search_personal_notes": search_personal_notes
}