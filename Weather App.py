#CODE OF THE WEATHER APP

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import pyodbc
import re
import requests

class WeatherData:
    def __init__(self, api_key):
        self.api_key = api_key

    def get_weather(self, city, country):
        base_url = "http://api.openweathermap.org/data/2.5/forecast"
        params = {
            "q": f"{city},{country}",
            "appid": self.api_key,
        }

        response = requests.get(base_url, params=params)

        if response.status_code == 200:
            data = response.json()

            # Extract detailed weather information for each hour
            weather_info = []
            for entry in data["list"]:
                timestamp = entry["dt_txt"]
                temperature_kelvin = entry["main"]["temp"]
                humidity = entry["main"]["humidity"]
                weather_info.append({
                    "timestamp": timestamp,
                    "temperature": temperature_kelvin - 273.15,  # Convert temperature to Celsius
                    "humidity": humidity,
                })

            return weather_info
        else:
            print("Failed to fetch weather data")
            return None

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SkyLite")
        self.conn = None
        self.cursor = None
        self.weather_data = WeatherData(api_key="43eb05793b6a386d26843865430e321a")

        self.setup_database()
        self.current_frame = None  # Track the current frame

        # Set the initial window size
        self.root.geometry("600x450")

        # Set the background color for the root window
        self.root.configure(bg="lightblue")

        self.create_login_ui()

    def setup_database(self):
        # Database connection configuration (replace with your server and database)
        server = 'AC-PC\\SQLEXPRESS'
        database = 'MyWeatherAppDB'

        # Use Trusted Connection for Windows Authentication
        try:
            self.conn = pyodbc.connect(f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;')
            self.cursor = self.conn.cursor()
        except pyodbc.Error as e:
            print(f"Database connection error: {e}")
            self.root.destroy()

    def create_frame(self):
        if self.current_frame:
            self.current_frame.destroy()
        frame = ttk.Frame(self.root)
        frame.grid(row=0, column=0, padx=100, pady=50, sticky="nsew")  # Adjust padx and pady for centering
        self.current_frame = frame
        return frame

    def create_login_ui(self):
        frame = self.create_frame()

        style = ttk.Style()
        style.configure("TButton", padding=(10, 5))
        style.configure("TFrame", background="lightblue")  # Set background color

        label_username = ttk.Label(frame, text="Username:")
        label_password = ttk.Label(frame, text="Password")
        self.username_entry = ttk.Entry(frame)
        self.password_entry = ttk.Entry(frame, show="*")
        login_button = ttk.Button(frame, text="Login", command=self.login)
        signup_button = ttk.Button(frame, text="Sign Up", command=self.create_signup_ui)
        forgot_password_button = ttk.Button(frame, text="Forgot Password", command=self.create_forgot_password_ui)
        self.error_label = ttk.Label(frame, text="", foreground="red")
        self.welcome_label = ttk.Label(frame, text="")

        label_username.grid(row=0, column=0, padx=10, pady=5, sticky='w')
        label_password.grid(row=1, column=0, padx=10, pady=5, sticky='w')
        self.username_entry.grid(row=0, column=1, padx=10, pady=5)
        self.password_entry.grid(row=1, column=1, padx=10, pady=5)
        login_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        signup_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        forgot_password_button.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        self.error_label.grid(row=5, column=0, columnspan=2, padx=10, pady=5)
        self.welcome_label.grid(row=6, column=0, columnspan=2, padx=10, pady=5)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

    def login(self):
        entered_username = self.username_entry.get()
        entered_password = self.password_entry.get()

        if not entered_username or not entered_password:
            self.welcome_label.config(text="PLEASE ENTER CREDENTIALS")
            return

        query = "SELECT * FROM Users WHERE Username = ? AND Password = ?"
        self.cursor.execute(query, (entered_username, entered_password))
        user = self.cursor.fetchone()

        if user:
            self.error_label.config(text="")
            self.welcome_label.config(text=f"Welcome, {entered_username}")

            # Call the method to get and display weather data
            self.get_and_display_weather_ui()

        else:
            self.welcome_label.config(text="")
            self.error_label.config(text="Invalid username or password")

    def create_signup_ui(self):
        frame = self.create_frame()

        style = ttk.Style()
        style.configure("TButton", padding=(10, 5))
        style.configure("TFrame", background="lightblue")  # Set background color

        label_username = ttk.Label(frame, text="Username:")
        label_fullname = ttk.Label(frame, text="Full Name:")
        label_mobile = ttk.Label(frame, text="Mobile No:")
        label_email = ttk.Label(frame, text="Email:")
        label_password = ttk.Label(frame, text="Password:")
        label_confirm_password = ttk.Label(frame, text="Confirm Password:")

        self.username_entry_signup = ttk.Entry(frame)
        self.fullname_entry = ttk.Entry(frame)
        self.mobile_entry = ttk.Entry(frame)
        self.email_entry = ttk.Entry(frame)
        self.password_entry = ttk.Entry(frame, show="*")
        self.confirm_password_entry = ttk.Entry(frame, show="*")

        signup_button = ttk.Button(frame, text="Submit", command=self.register_user)
        back_button = ttk.Button(frame, text="Back", command=self.create_login_ui)
        self.error_label_signup = ttk.Label(frame, text="", foreground="red")

        label_username.grid(row=0, column=0, padx=10, pady=5, sticky='w')
        label_fullname.grid(row=1, column=0, padx=10, pady=5, sticky='w')
        label_mobile.grid(row=2, column=0, padx=10, pady=5, sticky='w')
        label_email.grid(row=3, column=0, padx=10, pady=5, sticky='w')
        label_password.grid(row=4, column=0, padx=10, pady=5, sticky='w')
        label_confirm_password.grid(row=5, column=0, padx=10, pady=5, sticky='w')

        self.username_entry_signup.grid(row=0, column=1, padx=10, pady=5)
        self.fullname_entry.grid(row=1, column=1, padx=10, pady=5)
        self.mobile_entry.grid(row=2, column=1, padx=10, pady=5)
        self.email_entry.grid(row=3, column=1, padx=10, pady=5)
        self.password_entry.grid(row=4, column=1, padx=10, pady=5)
        self.confirm_password_entry.grid(row=5, column=1, padx=10, pady=5)

        signup_button.grid(row=6, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        back_button.grid(row=7, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        self.error_label_signup.grid(row=8, column=0, columnspan=2, padx=10, pady=5)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

    def register_user(self):
        entered_username = self.username_entry_signup.get()
        entered_fullname = self.fullname_entry.get()
        entered_mobile = self.mobile_entry.get()
        entered_email = self.email_entry.get()
        entered_password = self.password_entry.get()
        entered_confirm_password = self.confirm_password_entry.get()

        if not entered_username or not entered_fullname or not entered_mobile or not entered_email or not entered_password or not entered_confirm_password:
            self.error_label_signup.config(text="PLEASE ENTER CREDENTIALS")
            return

        if entered_password != entered_confirm_password:
            self.error_label_signup.config(text="Passwords do not match")
            return

        # Check if mobile number is exactly 10 digits
        if not re.match(r"^\d{10}$", entered_mobile):
            self.error_label_signup.config(text="Mobile number must have exactly 10 digits")
            return

        # Check if the email is in the correct format
        if not re.match(r"[^@]+@[^@]+\.[^@]+", entered_email):
            self.error_label_signup.config(text="Invalid email format")
            return

        # Check if Full Name contains only alphabets
        if not re.match(r"^[A-Za-z\s]+$", entered_fullname):
            self.error_label_signup.config(text="Full Name can only contain alphabets and spaces")
            return

        # Check if mobile number or email is already registered
        query = "SELECT * FROM Users WHERE Mobile = ? OR Email = ?"
        self.cursor.execute(query, (entered_mobile, entered_email))
        existing_user = self.cursor.fetchone()

        if existing_user:
            self.error_label_signup.config(text="Mobile number or email is already registered")
            return

        # Check if the username is already taken
        query = "SELECT * FROM Users WHERE Username = ?"
        self.cursor.execute(query, (entered_username,))
        existing_username = self.cursor.fetchone()

        if existing_username:
            self.error_label_signup.config(text="Username is already taken")
            return

        # If no conflicts found, proceed with registration
        try:
            query = "INSERT INTO Users (Username, FullName, Mobile, Email, Password) VALUES (?, ?, ?, ?, ?)"
            self.cursor.execute(query, (entered_username, entered_fullname, entered_mobile, entered_email, entered_password))
            self.conn.commit()
            self.error_label_signup.config(text="Registration successful")
        except Exception as e:
            self.error_label_signup.config(text="Error: " + str(e))

    def create_forgot_password_ui(self):
        frame = self.create_frame()

        style = ttk.Style()
        style.configure("TButton", padding=(10, 5))
        style.configure("TFrame", background="lightblue")  # Set background color

        label_username = ttk.Label(frame, text="Username:")
        label_fullname = ttk.Label(frame, text="Full Name:")
        label_mobile = ttk.Label(frame, text="Mobile No:")
        label_email = ttk.Label(frame, text="Email:")

        self.username_entry = ttk.Entry(frame)
        self.fullname_entry = ttk.Entry(frame)
        self.mobile_entry = ttk.Entry(frame)
        self.email_entry = ttk.Entry(frame)

        verify_button = ttk.Button(frame, text="Verify", command=self.verify_user)
        back_button = ttk.Button(frame, text="Back", command=self.create_login_ui)
        self.error_label_forgot = ttk.Label(frame, text="", foreground="red")

        label_username.grid(row=0, column=0, padx=10, pady=5, sticky='w')
        label_fullname.grid(row=1, column=0, padx=10, pady=5, sticky='w')
        label_mobile.grid(row=2, column=0, padx=10, pady=5, sticky='w')
        label_email.grid(row=3, column=0, padx=10, pady=5, sticky='w')

        self.username_entry.grid(row=0, column=1, padx=10, pady=5)
        self.fullname_entry.grid(row=1, column=1, padx=10, pady=5)
        self.mobile_entry.grid(row=2, column=1, padx=10, pady=5)
        self.email_entry.grid(row=3, column=1, padx=10, pady=5)

        verify_button.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        back_button.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        self.error_label_forgot.grid(row=6, column=0, columnspan=2, padx=10, pady=5)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

    def verify_user(self):
        entered_username = self.username_entry.get()
        entered_fullname = self.fullname_entry.get()
        entered_mobile = self.mobile_entry.get()
        entered_email = self.email_entry.get()

        if not entered_username or not entered_fullname or not entered_mobile or not entered_email:
            self.error_label_forgot.config(text="PLEASE ENTER CREDENTIALS")
            return

        query = "SELECT * FROM Users WHERE Username = ? AND FullName = ? AND Mobile = ? AND Email = ?"
        self.cursor.execute(query, (entered_username, entered_fullname, entered_mobile, entered_email))
        user = self.cursor.fetchone()

        if user:
            self.error_label_forgot.config(text="")
            self.create_reset_password_ui(entered_username)  # Pass the username to reset password UI
        else:
            self.error_label_forgot.config(text="Details entered are incorrect")

    def create_reset_password_ui(self, username):
        frame = self.create_frame()

        style = ttk.Style()
        style.configure("TButton", padding=(10, 5))
        style.configure("TFrame", background="lightblue")  # Set background color

        label_new_password = ttk.Label(frame, text="New Password:")
        label_confirm_password = ttk.Label(frame, text="Confirm Password:")

        self.new_password_entry = ttk.Entry(frame, show="*")
        self.confirm_new_password_entry = ttk.Entry(frame, show="*")

        reset_password_button = ttk.Button(frame, text="Reset Password", command=lambda: self.reset_password(username))
        back_button = ttk.Button(frame, text="Back", command=self.create_login_ui)
        self.error_label_reset = ttk.Label(frame, text="", foreground="red")

        label_new_password.grid(row=0, column=0, padx=10, pady=5, sticky='w')
        label_confirm_password.grid(row=1, column=0, padx=10, pady=5, sticky='w')

        self.new_password_entry.grid(row=0, column=1, padx=10, pady=5)
        self.confirm_new_password_entry.grid(row=1, column=1, padx=10, pady=5)

        reset_password_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        back_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        self.error_label_reset.grid(row=4, column=0, columnspan=2, padx=10, pady=5)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

    def reset_password(self, username):
        entered_new_password = self.new_password_entry.get()
        entered_confirm_new_password = self.confirm_new_password_entry.get()

        if not entered_new_password or not entered_confirm_new_password:
            self.error_label_reset.config(text="PLEASE ENTER NEW PASSWORD")
            return

        if entered_new_password != entered_confirm_new_password:
            self.error_label_reset.config(text="Passwords do not match")
            return

        # Update the password in the database
        query = "UPDATE Users SET Password = ? WHERE Username = ?"
        self.cursor.execute(query, (entered_new_password, username))
        self.conn.commit()

        self.error_label_reset.config(text="Password reset successful")

    def get_and_display_weather_ui(self):
        frame = self.create_frame()

        style = ttk.Style()
        style.configure("TButton", padding=(10, 5))
        style.configure("TFrame", background="lightblue")  # Set background color

        label_city = ttk.Label(frame, text="City:")
        label_country = ttk.Label(frame, text="Country:")
        self.city_entry = ttk.Entry(frame)
        self.country_entry = ttk.Entry(frame)
        get_weather_button = ttk.Button(frame, text="Get Weather", command=self.display_weather)
        back_button = ttk.Button(frame, text="Back", command=self.create_login_ui)
        self.weather_display_label = ttk.Label(frame, text="", font=('Helvetica', 10), wraplength=400)

        label_city.grid(row=0, column=0, padx=10, pady=5, sticky='w')
        label_country.grid(row=1, column=0, padx=10, pady=5, sticky='w')

        self.city_entry.grid(row=0, column=1, padx=10, pady=5)
        self.country_entry.grid(row=1, column=1, padx=10, pady=5)

        get_weather_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        get_weather_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        back_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        self.weather_display_label.grid(row=4, column=0, columnspan=2, padx=10, pady=5)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

    def display_weather(self):
        city = self.city_entry.get()
        country = self.country_entry.get()

        if not city or not country:
            self.weather_display_label.config(text="PLEASE ENTER CITY AND COUNTRY")
            return

        weather_info = self.weather_data.get_weather(city, country)

        if weather_info:
            # Display weather information
            display_text = "Weather Forecast:\n"
            for entry in weather_info:
                timestamp = entry["timestamp"]
                temperature = entry["temperature"]
                humidity = entry["humidity"]
                display_text += f"{timestamp}: Temperature: {temperature}°C, Humidity: {humidity}%\n"

            self.weather_display_label.config(text=display_text)
        else:
            self.weather_display_label.config(text="Failed to fetch weather data")

# Main code to run the application
root = tk.Tk()
app = WeatherApp(root)
root.mainloop()
