import pyautogui
import time

def auto_typer():
    print("You have 3 seconds to click on Notepad!")
    time.sleep(3)
    pyautogui.write("Hello! I am typing this automatically!", interval=0.05)
    pyautogui.press("enter")
    pyautogui.write("Python is amazing!", interval=0.05)

auto_typer()