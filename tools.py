import os
import subprocess
import webbrowser
import pyautogui
import pywhatkit
import psutil
import pyperclip
import ollama
from PIL import Image

# --- Desktop Automation & Tools ---

def open_website(url: str) -> str:
    """Opens a specified website in the default web browser."""
    try:
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
        webbrowser.open(url)
        return f"Opening {url}, boss."
    except Exception as e:
        return f"Failed to open website: {e}"

def play_youtube(topic: str) -> str:
    """Searches and plays a video on YouTube based on the given topic."""
    try:
        pywhatkit.playonyt(topic)
        return f"Playing {topic} on YouTube, boss."
    except Exception as e:
        return f"Failed to play YouTube video: {e}"

def set_volume(level: int) -> str:
    """Sets the system volume to a percentage level between 0 and 100."""
    try:
        level = max(0, min(100, level))
        for _ in range(50):
            pyautogui.press('volumedown')
        steps = int(level / 2)
        for _ in range(steps):
            pyautogui.press('volumeup')
        return f"Volume set to approximately {level} percent, boss."
    except Exception as e:
        return f"Failed to set volume: {e}"

def volume_up() -> str:
    """Increases system volume."""
    try:
        for _ in range(5):
            pyautogui.press('volumeup')
        return "Increased volume, boss."
    except Exception as e:
        return f"Failed to increase volume: {e}"

def volume_down() -> str:
    """Decreases system volume."""
    try:
        for _ in range(5):
            pyautogui.press('volumedown')
        return "Decreased volume, boss."
    except Exception as e:
        return f"Failed to decrease volume: {e}"

def toggle_play_pause() -> str:
    """Toggles media play/pause on Windows."""
    try:
        pyautogui.press('playpause')
        return "Toggled play pause, boss."
    except Exception as e:
        return f"Failed to toggle play pause: {e}"

def toggle_full_screen() -> str:
    """Toggles full screen mode on active window (YouTube/Browser/Media)."""
    try:
        pyautogui.press('f')
        return "Toggled full screen, boss."
    except Exception as e:
        return f"Failed to toggle full screen: {e}"

def take_screenshot() -> str:
    """Captures a screenshot of the current screen and saves it locally."""
    try:
        screenshots_dir = os.path.join(os.getcwd(), "screenshots")
        os.makedirs(screenshots_dir, exist_ok=True)
        filename = f"screenshot_{os.urandom(4).hex()}.png"
        filepath = os.path.join(screenshots_dir, filename)
        
        image = pyautogui.screenshot()
        image.save(filepath)
        return f"Screenshot saved successfully at {filepath}, boss."
    except Exception as e:
        return f"Failed to take screenshot: {e}"

def analyze_screen(prompt: str = "Describe what is currently visible on the screen in detail.") -> str:
    """Captures a screenshot and analyzes screen contents using llava."""
    try:
        screenshots_dir = os.path.join(os.getcwd(), "screenshots")
        os.makedirs(screenshots_dir, exist_ok=True)
        filepath = os.path.join(screenshots_dir, "temp_vision.png")
        
        image = pyautogui.screenshot()
        image.save(filepath)

        res = ollama.chat(
            model="llava",
            messages=[{
                'role': 'user',
                'content': prompt,
                'images': [filepath]
            }]
        )
        return res['message']['content']
    except Exception as e:
        return f"Screen vision analysis failed. Error: {e}"

def read_clipboard() -> str:
    """Reads text content currently saved on the system clipboard."""
    try:
        content = pyperclip.paste()
        if not content.strip():
            return "The clipboard is currently empty, boss."
        return f"Clipboard text: {content}"
    except Exception as e:
        return f"Failed to read clipboard: {e}"

def copy_to_clipboard(text: str) -> str:
    """Copies specified text to the system clipboard."""
    try:
        pyperclip.copy(text)
        return "Text copied to clipboard, boss."
    except Exception as e:
        return f"Failed to copy to clipboard: {e}"

def open_app(app_name: str) -> str:
    """Launches common desktop applications by name."""
    app_lower = app_name.lower()
    try:
        if "notepad" in app_lower:
            subprocess.Popen(["notepad.exe"])
        elif "calculator" in app_lower or "calc" in app_lower:
            subprocess.Popen(["calc.exe"])
        elif "cmd" in app_lower or "command prompt" in app_lower or "terminal" in app_lower:
            subprocess.Popen(["cmd.exe"])
        elif "code" in app_lower or "vscode" in app_lower or "vs code" in app_lower:
            os.system("code")
        else:
            pyautogui.press('win')
            pyautogui.sleep(0.5)
            pyautogui.write(app_name)
            pyautogui.sleep(0.5)
            pyautogui.press('enter')
        return f"Opening {app_name}, boss."
    except Exception as e:
        return f"Failed to open application {app_name}: {e}"

def close_active_window() -> str:
    """Closes the currently focused active application window."""
    try:
        pyautogui.hotkey('alt', 'f4')
        return "Closed the active window, boss."
    except Exception as e:
        return f"Failed to close active window: {e}"

def minimize_all_windows(*args, **kwargs) -> str:
    """Minimizes all open windows to reveal the desktop."""
    try:
        pyautogui.hotkey('win', 'd')
        return "Minimized all windows, boss."
    except Exception as e:
        return f"Failed to minimize windows: {e}"

def system_power_control(action: str) -> str:
    """Executes Windows system power operations: shutdown, restart, or lock."""
    action_lower = action.lower()
    try:
        if "shutdown" in action_lower:
            os.system("shutdown /s /t 5")
            return "System shutting down in 5 seconds, boss."
        elif "restart" in action_lower:
            os.system("shutdown /r /t 5")
            return "System restarting in 5 seconds, boss."
        elif "lock" in action_lower:
            os.system("rundll32.exe user32.dll,LockWorkStation")
            return "Locking system workstation, boss."
        else:
            return f"Unknown power action requested: {action}"
    except Exception as e:
        return f"Failed to execute system power control: {e}"

def scroll_page(direction: str = "down") -> str:
    """Scrolls the web browser or active window up or down."""
    try:
        screenWidth, screenHeight = pyautogui.size()
        pyautogui.click(int(screenWidth * 0.3), int(screenHeight * 0.5))
        pyautogui.sleep(0.2)
        
        if direction.lower() in ["up", "top"]:
            pyautogui.scroll(800)
            return "Scrolled up, boss."
        else:
            pyautogui.scroll(-800)
            return "Scrolled down, boss."
    except Exception as e:
        return f"Failed to scroll: {e}"

def skip_youtube_ad() -> str:
    """Focuses YouTube video player and navigates Tab focus to trigger the Skip Ad button."""
    try:
        screenWidth, screenHeight = pyautogui.size()
        pyautogui.click(int(screenWidth * 0.4), int(screenHeight * 0.4))
        pyautogui.sleep(0.2)
        
        for _ in range(4):
            pyautogui.press('tab')
            pyautogui.sleep(0.05)
        
        pyautogui.press('enter')
        return "Attempted to skip YouTube ad, boss."
    except Exception as e:
        return f"Failed to skip YouTube ad: {e}"

# Master Tool Registry
tools_list = [
    open_website,
    play_youtube,
    set_volume,
    volume_up,
    volume_down,
    toggle_play_pause,
    toggle_full_screen,
    take_screenshot,
    analyze_screen,
    read_clipboard,
    copy_to_clipboard,
    open_app,
    close_active_window,
    minimize_all_windows,
    system_power_control,
    scroll_page,
    skip_youtube_ad
]

tools_map = {
    "open_website": open_website,
    "play_youtube": play_youtube,
    "set_volume": set_volume,
    "volume_up": volume_up,
    "volume_down": volume_down,
    "toggle_play_pause": toggle_play_pause,
    "toggle_full_screen": toggle_full_screen,
    "take_screenshot": take_screenshot,
    "analyze_screen": analyze_screen,
    "read_clipboard": read_clipboard,
    "copy_to_clipboard": copy_to_clipboard,
    "open_app": open_app,
    "close_active_window": close_active_window,
    "minimize_all_windows": minimize_all_windows,
    "scroll_page": scroll_page,
    "skip_youtube_ad": skip_youtube_ad,
    "minimize_window": minimize_all_windows,
    "minimize": minimize_all_windows
}