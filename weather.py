import tkinter as tk
from tkinter import messagebox, simpledialog
import os
from pathlib import Path

try:
    import requests
except ImportError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests

def get_weather():
    # Get city name from the input field
    city = city_entry.get().strip()
    
    if not city:
        messagebox.showerror("Error", "Please enter a city name!")
        return
    
    # Get API key from environment, local file, or prompt the user
    api_key = os.getenv("df3a7a31b2ba57c0370d78ffcdfad360")
    key_file = Path.home() / ".weather_api_key"
    if not api_key and key_file.exists():
        try:
            api_key = key_file.read_text(encoding="utf-8").strip()
        except Exception:
            api_key = None

    if not api_key:
        api_key = simpledialog.askstring("API Key", "Enter OpenWeatherMap API key (or set OPENWEATHER_API_KEY env var):")
        if not api_key:
            messagebox.showerror("API Key Missing", "No API key provided. Set OPENWEATHER_API_KEY environment variable or enter a key.")
            return

        # Offer to save the API key locally for convenience
        try:
            if messagebox.askyesno("Save API Key", "Save this API key to a local file for future use?"):
                key_file.write_text(api_key, encoding="utf-8")
        except Exception:
            # Non-fatal; continue without saving
            pass
    
    # URL to fetch data from (use HTTPS)
    base_url = "https://api.openweathermap.org/data/2.5/weather?"
    
    # Complete url with city and api key (units=metric gives Celsius)
    complete_url = f"{base_url}q={city}&appid={api_key}&units=metric"
    
    try:
        # Request data from the server
        response = requests.get(complete_url, timeout=10)

        # Safely parse JSON response
        try:
            data = response.json()
        except ValueError:
            messagebox.showerror("API Error", "Received invalid JSON from the weather service.")
            return

        # Some APIs return numeric or string 'cod' values; normalize
        cod = data.get("cod", response.status_code)
        try:
            cod = int(cod)
        except Exception:
            cod = response.status_code

        # Handle non-success codes
        if cod != 200:
            api_msg = data.get("message", "Unexpected API error.")
            if cod == 401:
                messagebox.showerror("API Key Error", f"Authentication failed: {api_msg}")
            elif cod == 404:
                messagebox.showerror("Error", f"City not found: {api_msg}")
            else:
                messagebox.showerror("API Error", f"{api_msg}")
            return

        # Success: extract weather info
        main_data = data.get("main")
        weather_list = data.get("weather")
        if not main_data or not weather_list:
            messagebox.showerror("API Error", "Incomplete API response.")
            return

        weather_data = weather_list[0]
        temp = main_data.get("temp")
        humidity = main_data.get("humidity")
        description = weather_data.get("description", "")

        # Update the result label
        result_text = (f"Temperature: {temp}°C\n"
                       f"Humidity: {humidity}%\n"
                       f"Condition: {description.capitalize()}")
        result_label.config(text=result_text)
    
    except requests.exceptions.ConnectionError:
        messagebox.showerror("Connection Error", "No internet connection!\nPlease check your network and try again.")
    except requests.exceptions.Timeout:
        messagebox.showerror("Timeout Error", "Request timed out!\nServer is taking too long to respond.")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Network Error", f"Network error occurred:\n{e}")
    except KeyError:
        messagebox.showerror("API Error", "Invalid API response. The API key may be invalid or expired.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred:\n{e}")

# --- GUI Setup ---
root = tk.Tk()
root.title("Weather App")
root.geometry("350x400")
root.config(bg="#f0f0f0")

# Heading
title_label = tk.Label(root, text="Weather App", font=("Helvetica", 20, "bold"), bg="#f0f0f0")
title_label.pack(pady=20)

# Input Field
city_entry = tk.Entry(root, font=("Helvetica", 14), width=20)
city_entry.pack(pady=10)

# Search Button
search_button = tk.Button(root, text="Check Weather", font=("Helvetica", 12), command=get_weather)
search_button.pack(pady=10)

# Display Result
result_label = tk.Label(root, text="", font=("Helvetica", 14), bg="#f0f0f0", justify="left")
result_label.pack(pady=30)

# Start the app
root.mainloop()
