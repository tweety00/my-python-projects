<<<<<<< HEAD
import pyautogui
import time

def auto_typer():
    print("You have 3 seconds to click on Notepad!")
    time.sleep(3)
    pyautogui.write("Hello! I am typing this automatically!", interval=0.05)
    pyautogui.press("enter")
    pyautogui.write("Python is amazing!", interval=0.05)

=======
import pyautogui
import time

def auto_typer():
    print("You have 3 seconds to click on Notepad!")
    time.sleep(3)
    pyautogui.write("Hello! I am typing this automatically!", interval=0.05)
    pyautogui.press("enter")
    pyautogui.write("Python is amazing!", interval=0.05)

>>>>>>> 58956b795e70543a61d4f3119d118043286404b7
auto_typer()