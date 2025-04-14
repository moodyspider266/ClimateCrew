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
from kivy.clock import Clock

# Color scheme based on your Figma design
COLORS = {
    'background': '#e3f8ee',
    'primary': '#446e49',
    'text': '#333333',
    'secondary_text': '#666666',
    'white': '#ffffff'
}


class RegistrationScreen(Screen):
    def __init__(self, db_helper, **kwargs):
        super(RegistrationScreen, self).__init__(**kwargs)
        self.name = 'register'
        self.db_helper = db_helper

        layout = FloatLayout()
        with layout.canvas.before:
            Color(rgba=get_color_from_hex(COLORS['background'] + 'ff'))
            self.rect = Rectangle(size=layout.size, pos=layout.pos)
        layout.bind(size=self._update_rect, pos=self._update_rect)

        # Title
        title = Label(text='Create Account',
                      font_size=dp(24),
                      color=get_color_from_hex(COLORS['primary'] + 'ff'),
                      pos_hint={'center_x': 0.5, 'center_y': 0.85},
                      bold=True)
        layout.add_widget(title)

        # Form layout
        form_layout = BoxLayout(orientation='vertical',
                                spacing=dp(15),
                                padding=[dp(20), dp(0)],
                                pos_hint={'center_x': 0.5, 'center_y': 0.55},
                                size_hint=(0.9, 0.5))

        # Username field
        self.username_input = TextInput(hint_text='username',
                                        multiline=False,
                                        size_hint=(1, None),
                                        height=dp(40),
                                        background_color=get_color_from_hex(
                                            COLORS['white'] + 'ff'),
                                        cursor_color=get_color_from_hex(
                                            COLORS['primary'] + 'ff'),
                                        padding=[dp(10), dp(10), 0, 0])
        form_layout.add_widget(self.username_input)

        # Email field
        self.email_input = TextInput(hint_text='email',
                                     multiline=False,
                                     size_hint=(1, None),
                                     height=dp(40),
                                     background_color=get_color_from_hex(
                                         COLORS['white'] + 'ff'),
                                     cursor_color=get_color_from_hex(
                                         COLORS['primary'] + 'ff'),
                                     padding=[dp(10), dp(10), 0, 0])
        form_layout.add_widget(self.email_input)

        # Password field
        self.password_input = TextInput(hint_text='password',
                                        multiline=False,
                                        password=True,
                                        size_hint=(1, None),
                                        height=dp(40),
                                        background_color=get_color_from_hex(
                                            COLORS['white'] + 'ff'),
                                        cursor_color=get_color_from_hex(
                                            COLORS['primary'] + 'ff'),
                                        padding=[dp(10), dp(10), 0, 0])
        form_layout.add_widget(self.password_input)

        # Confirm Password field
        self.confirm_input = TextInput(hint_text='confirm_password',
                                       multiline=False,
                                       password=True,
                                       size_hint=(1, None),
                                       height=dp(40),
                                       background_color=get_color_from_hex(
                                           COLORS['white'] + 'ff'),
                                       cursor_color=get_color_from_hex(
                                           COLORS['primary'] + 'ff'),
                                       padding=[dp(10), dp(10), 0, 0])
        form_layout.add_widget(self.confirm_input)

        self.message = Label(text="", color=(1, 0, 0, 1))
        form_layout.add_widget(self.message)

        # Sign up button
        signup_btn = Button(text='Sign Up',
                            background_color=get_color_from_hex(
                                COLORS['primary'] + 'ff'),
                            color=get_color_from_hex(COLORS['white'] + 'ff'),
                            size_hint=(1, None),
                            height=dp(40),
                            font_size=dp(16))
        signup_btn.bind(on_press=self.sign_up)
        form_layout.add_widget(signup_btn)

        layout.add_widget(form_layout)

        # Social login options
        social_layout = BoxLayout(orientation='horizontal',
                                  spacing=dp(20),
                                  pos_hint={'center_x': 0.5, 'center_y': 0.25},
                                  size_hint=(0.6, 0.05))

        layout.add_widget(social_layout)

        # Back button
        back_btn = Button(text='Back',
                          background_color=get_color_from_hex(
                              COLORS['background'] + '00'),
                          color=get_color_from_hex(COLORS['primary'] + 'ff'),
                          size_hint=(0.2, 0.05),
                          pos_hint={'x': 0.05, 'top': 0.95})
        back_btn.bind(on_press=self.go_back)
        layout.add_widget(back_btn)

        self.add_widget(layout)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def sign_up(self, instance=None):
        # Would connect to your user registration system
        # For now, navigate to onboarding screen
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        email = self.email_input.text.strip()
        confirm_password = self.confirm_input.text.strip()
        print(
            f"Username : {username} \n Password : {password} \n Email : {email} \n Confirm_Password : {confirm_password}")

        if not username or not password or not email:
            self.message.text = 'Please enter all required details'
            self.message.color = (1, 0, 0, 1)
            return

        if password != confirm_password:
            self.message.text = 'Password and Confirm Password should be the same'
            return

        response = self.db_helper.register_user(username, password, email)
        print("Response :", response)
        if response == True:
            user_data = self.db_helper.authenticate_user(username, password)
            if user_data:
                user_id = user_data[0]
                # Store user_id in app
                App.get_running_app().set_user_id(user_id)
                # Initialize user task
                self.db_helper.initialize_user_task(user_id)
                self.message.text = 'Registration Successful!'
                self.message.color = (0, 1, 0, 1)
                Clock.schedule_once(self.navigate_to_onboarding, 3)
        else:
            self.message.text = 'Username or email already exists'
            self.message.color = (1, 0, 0, 1)

    def navigate_to_onboarding(self, dt):
        # Ensure db_helper has a cursor to query the database
        conn = self.db_helper.connect()  # Now connect() returns a valid connection
        if conn is None:
            print("Database connection failed!")
            return  # Prevent further execution

        cursor = conn.cursor()  # Now this won't cause an error

        cursor.execute('SELECT id FROM users WHERE username = ?',
                       (self.username_input.text.strip(),))
        user_data = cursor.fetchone()

        if user_data:
            user_id = user_data[0]
            print(f"User Registered with ID: {user_id}")  # Debugging
            # App.get_running_app().set_user_id(user_id)
            self.manager.get_screen('onboarding').set_user_id(user_id)
            self.manager.transition = SlideTransition(direction='left')
            self.manager.current = 'onboarding'
        else:
            print("Error: User not found in the database after registration.")

        cursor.close()
        conn.close()

    def goto_login(self, instance):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'login'

    def go_back(self, instance):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'welcome'
