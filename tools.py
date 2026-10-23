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
    """Captures a screenshot and analyzes screen contents using llama3.2-vision."""
    try:
        screenshots_dir = os.path.join(os.getcwd(), "screenshots")
        os.makedirs(screenshots_dir, exist_ok=True)
        filepath = os.path.join(screenshots_dir, "temp_vision.png")
        
        # Capture active screen
        image = pyautogui.screenshot()
        image.save(filepath)

        # Analyze image using Ollama vision model
        res = ollama.chat(
            model="llama3.2-vision",
            messages=[{
                'role': 'user',
                'content': prompt,
                'images': [filepath]
            }]
        )
        return res['message']['content']
    except Exception as e:
        return f"Screen vision analysis failed. Ensure llama3.2-vision is pulled via Ollama. Error: {e}"

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
        pyautogui.