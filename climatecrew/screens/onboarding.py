from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
import sqlite3

# Color scheme based on your Figma design
COLORS = {
    'background': '#e3f8ee',
    'primary': '#446e49',
    'text': '#333333',
    'secondary_text': '#666666',
    'white': '#ffffff'
}


class OnboardingScreen(Screen):
    def __init__(self, **kwargs):
        super(OnboardingScreen, self).__init__(**kwargs)
        self.name = 'onboarding'
        self.user_id = None
        self.db_path = "user_auth.db"  # Update with your actual DB path

        layout = FloatLayout()
        with layout.canvas.before:
            Color(rgba=get_color_from_hex(COLORS['background'] + 'ff'))
            self.rect = Rectangle(size=layout.size, pos=layout.pos)
        layout.bind(size=self._update_rect, pos=self._update_rect)

        # Title
        title = Label(text='Welcome to\nClimateCrew!',
                      font_size=dp(24),
                      color=get_color_from_hex(COLORS['primary'] + 'ff'),
                      pos_hint={'center_x': 0.5, 'center_y': 0.85},
                      halign='center',
                      valign='middle',
                      bold=True)
        title.bind(size=title.setter('text_size'))
        layout.add_widget(title)

        # Subtitle
        subtitle = Label(text="Let's complete your profile to get started",
                         font_size=dp(16),
                         color=get_color_from_hex(
                             COLORS['secondary_text'] + 'ff'),
                         pos_hint={'center_x': 0.5, 'center_y': 0.78},
                         halign='center')
        subtitle.bind(size=subtitle.setter('text_size'))
        layout.add_widget(subtitle)

        # Form layout
        form_layout = BoxLayout(orientation='vertical',
                                spacing=dp(15),
                                padding=[dp(20), dp(0)],
                                # Adjusted position
                                pos_hint={'center_x': 0.5, 'center_y': 0.45},
                                size_hint=(0.9, 0.6))  # Made taller for more fields

        # Full Name field
        self.full_name_input = TextInput(
            hint_text='Full Name',
            multiline=False,
            size_hint=(1, None),
            height=dp(40),
            background_color=get_color_from_hex(COLORS['white'] + 'ff'),
            cursor_color=get_color_from_hex(COLORS['primary'] + 'ff'),
            padding=[dp(10), dp(10), 0, 0]
        )
        form_layout.add_widget(self.full_name_input)

        # Contact field
        self.contact_input = TextInput(
            hint_text='Contact Number',
            multiline=False,
            size_hint=(1, None),
            height=dp(40),
            background_color=get_color_from_hex(COLORS['white'] + 'ff'),
            cursor_color=get_color_from_hex(COLORS['primary'] + 'ff'),
            padding=[dp(10), dp(10), 0, 0]
        )
        form_layout.add_widget(self.contact_input)

        # City field with icon
        city_layout = BoxLayout(orientation='horizontal',
                                size_hint=(1, None),
                                height=dp(40))

        self.city_input = TextInput(
            hint_text='City',
            multiline=False,
            background_color=get_color_from_hex(COLORS['white'] + 'ff'),
            cursor_color=get_color_from_hex(COLORS['primary'] + 'ff'),
            padding=[dp(10), dp(10), 0, 0]
        )

        city_icon = Button(
            text='📍',  # Using emoji as placeholder
            size_hint=(0.1, 1),
            background_color=get_color_from_hex(COLORS['white'] + 'ff')
        )

        city_layout.add_widget(self.city_input)
        city_layout.add_widget(city_icon)
        form_layout.add_widget(city_layout)

        # Country field with icon
        country_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(40)
        )

        self.country_input = TextInput(
            hint_text='Country',
            multiline=False,
            background_color=get_color_from_hex(COLORS['white'] + 'ff'),
            cursor_color=get_color_from_hex(COLORS['primary'] + 'ff'),
            padding=[dp(10), dp(10), 0, 0]
        )

        country_icon = Button(
            text='🌍',  # Using emoji as placeholder
            size_hint=(0.1, 1),
            background_color=get_color_from_hex(COLORS['white'] + 'ff')
        )

        country_layout.add_widget(self.country_input)
        country_layout.add_widget(country_icon)
        form_layout.add_widget(country_layout)

        # Occupation field
        self.occupation_input = TextInput(
            hint_text='Occupation',
            multiline=False,
            size_hint=(1, None),
            height=dp(40),
            background_color=get_color_from_hex(COLORS['white'] + 'ff'),
            cursor_color=get_color_from_hex(COLORS['primary'] + 'ff'),
            padding=[dp(10), dp(10), 0, 0]
        )
        form_layout.add_widget(self.occupation_input)

        # Continue button
        continue_btn = Button(
            text='Continue',
            background_color=get_color_from_hex(COLORS['primary'] + 'ff'),
            color=get_color_from_hex(COLORS['white'] + 'ff'),
            size_hint=(1, None),
            height=dp(40),
            font_size=dp(16)
        )
        continue_btn.bind(on_press=self.continue_to_home)
        form_layout.add_widget(continue_btn)

        # Status message
        self.status_label = Label(
            text="",
            color=(1, 0, 0, 1),  # Red for errors
            size_hint=(1, None),
            height=dp(30),
            halign='center'
        )
        form_layout.add_widget(self.status_label)

        layout.add_widget(form_layout)

        self.add_widget(layout)

    def set_user_id(self, user_id):
        self.user_id = user_id
        print(f"Received user_id: {self.user_id}")  # Debugging

        # Store user_id at app level for other screens
        App.get_running_app().set_user_id(user_id)

    def save_user_profile(self):
        if self.user_id is None:
            self.status_label.text = "Error: No user_id found!"
            print("Error: No user_id found!")  # Prevent saving without user_id
            return False

        try:
            # Connect to database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # First, get username and email from users table
            cursor.execute(
                'SELECT username, email FROM users WHERE id = ?', (self.user_id,))
            user_data = cursor.fetchone()

            if not user_data:
                self.status_label.text = "Error: User not found in database!"
                print(
                    f"Error: User with ID {self.user_id} not found in database!")
                conn.close()
                return False

            username, email = user_data

            # Check if user already has a profile
            cursor.execute(
                'SELECT user_id FROM user_profiles WHERE user_id = ?', (self.user_id,))
            existing_profile = cursor.fetchone()

            if existing_profile:
                # Update existing profile
                cursor.execute('''
                    UPDATE user_profiles 
                    SET full_name = ?, username = ?, email = ?, contact = ?, 
                        city = ?, country = ?, occupation = ?
                    WHERE user_id = ?
                ''', (
                    self.full_name_input.text.strip(),
                    username,
                    email,
                    self.contact_input.text.strip(),
                    self.city_input.text.strip(),
                    self.country_input.text.strip(),
                    self.occupation_input.text.strip(),
                    self.user_id
                ))
            else:
                # Insert new profile
                cursor.execute('''
                    INSERT INTO user_profiles 
                    (user_id, full_name, username, email, contact, city, country, occupation)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    self.user_id,
                    self.full_name_input.text.strip(),
                    username,
                    email,
                    self.contact_input.text.strip(),
                    self.city_input.text.strip(),
                    self.country_input.text.strip(),
                    self.occupation_input.text.strip()
                ))

            conn.commit()
            conn.close()

            print(f"User Profile Saved for ID: {self.user_id}")
            return True

        except Exception as e:
            self.status_label.text = f"Error saving profile: {str(e)}"
            print(f"Error saving user profile: {e}")
            if 'conn' in locals() and conn:
                conn.close()
            return False

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def continue_to_home(self, instance):
        if self.save_user_profile():
            # Pass the user_id to home screen
            home_screen = self.manager.get_screen('home')
            if hasattr(home_screen, 'set_user_id'):
                home_screen.set_user_id(self.user_id)

            # Transition to home screen
            self.manager.transition = SlideTransition(direction='left')
            self.manager.current = 'home'
        else:
            # Profile save failed, show error (already handled in save_user_profile)
            pass
