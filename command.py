from datetime import datetime
import os
import math
import random
import platform
import sys
import time

# Utility Commands
def get_date():
    """Return the current date."""
    return datetime.now().strftime("%Y-%m-%d")

def get_time():
    """Return the current time."""
    return datetime.now().strftime("%H:%M:%S")

def get_day():
    """Return the current day."""
    return datetime.now().strftime("%A")

def sleep_for_seconds():
    """Pause for 2 seconds (example of time.sleep)."""
    time.sleep(2)
    return "I paused for 2 seconds!"

def get_system_info():
    """Return basic system information."""
    return f"System: {platform.system()}, Version: {platform.version()}, Processor: {platform.processor()}"

def get_python_version():
    """Return the current Python version."""
    return sys.version

# File System Commands
def get_current_directory():
    """Return the current working directory."""
    return os.getcwd()

def list_files():
    """Return a list of files in the current directory."""
    return ", ".join(os.listdir("."))

# Math Commands
def calculate_square_root():
    """Return the square root of a random number."""
    number = random.randint(1, 100)
    return f"The square root of {number} is {math.sqrt(number):.2f}"

def calculate_factorial():
    """Return the factorial of a random number."""
    number = random.randint(1, 10)
    return f"The factorial of {number} is {math.factorial(number)}"

def generate_random_number():
    """Generate a random number between 1 and 100."""
    return f"Your random number is: {random.randint(1, 100)}"

def calculate_power():
    """Calculate power of two random numbers."""
    base = random.randint(1, 10)
    exponent = random.randint(1, 5)
    return f"{base} raised to the power of {exponent} is {math.pow(base, exponent):.2f}"

# String Commands
def reverse_string():
    """Return a reversed string of 'Python'."""
    text = "Python"
    return f"The reverse of '{text}' is '{text[::-1]}'"

def convert_to_uppercase():
    """Convert 'hello world' to uppercase."""
    text = "hello world"
    return f"'{text}' in uppercase is '{text.upper()}'"

# Command dictionary
commands = {
    # Utilities
    "date": get_date,
    "time": get_time,
    "day": get_day,
    "system info": get_system_info,
    "python version": get_python_version,
    "pause": sleep_for_seconds,

    # File System
    "current directory": get_current_directory,
    "list files": list_files,

    # Math
    "square root": calculate_square_root,
    "factorial": calculate_factorial,
    "random number": generate_random_number,
    "power": calculate_power,

    # Strings
    "reverse string": reverse_string,
    "uppercase": convert_to_uppercase
}
