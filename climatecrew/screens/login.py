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


class LoginScreen(Screen):
    def __init__(self, db_helper, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        self.db_helper = db_helper
        self.name = 'login'
        self.user_id = None

        layout = FloatLayout()
        with layout.canvas.before:
            Color(rgba=get_color_from_hex(COLORS['background'] + 'ff'))
            self.rect = Rectangle(size=layout.size, pos=layout.pos)
        layout.bind(size=self._update_rect, pos=self._update_rect)

        # Title
        title = Label(text='Login',
                      font_size=dp(24),
                      color=get_color_from_hex(COLORS['primary'] + 'ff'),
                      pos_hint={'center_x': 0.5, 'center_y': 0.85},
                      bold=True)
        layout.add_widget(title)

        # Form layout
        form_layout = BoxLayout(orientation='vertical',
                                spacing=dp(15),
                                padding=[dp(20), dp(0)],
                                pos_hint={'center_x': 0.5, 'center_y': 0.6},
                                size_hint=(0.9, 0.4))

        # Username field
        self.username_input = TextInput(hint_text='Username',
                                        multiline=False,
                                        size_hint=(1, None),
                                        height=dp(40),
                                        background_color=get_color_from_hex(
                                            COLORS['white'] + 'ff'),
                                        cursor_color=get_color_from_hex(
                                            COLORS['primary'] + 'ff'),
                                        padding=[dp(10), dp(10), 0, 0])
        form_layout.add_widget(self.username_input)

        # Password field
        self.password_input = TextInput(hint_text='Password',
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

        self.message = Label(text="", color=(1, 0, 0, 1))
        form_layout.add_widget(self.message)

        # Sign in button
        signin_btn = Button(text='Sign In',
                            background_color=get_color_from_hex(
                                COLORS['primary'] + 'ff'),
                            color=get_color_from_hex(COLORS['white'] + 'ff'),
                            size_hint=(1, None),
                            height=dp(40),
                            font_size=dp(16))
        signin_btn.bind(on_press=self.sign_in)
        form_layout.add_widget(signin_btn)

        # "Don't have an account" text and register link
        account_label = Label(text="Don't have an account?",
                              font_size=dp(14),
                              color=get_color_from_hex(
                                  COLORS['secondary_text'] + 'ff'),
                              size_hint=(1, None),
                              height=dp(30),
                              halign='center')
        account_label.bind(on_touch_down=self.navigate_to_register)
        form_layout.add_widget(account_label)

        layout.add_widget(form_layout)

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

    def sign_in(self, instance):
        # Would connect to your authentication system
        # For now, navigate to home screen
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        print(f"Username : {username} \nPassword : {password}")

        if not username or not password:
            self.message.text = 'Please enter username and password.'
            self.message.color = (1, 0, 0, 1)
            return

        user_data = self.db_helper.authenticate_user(username, password)

        if user_data:  # If authentication is successful
            user_id = user_data[0]  # Assuming first element is user_id
            print(f"Successfully logged in. User ID: {user_id}")

            # Set user_id in the app
            app = App.get_running_app()
            app.set_user_id(user_id)

            # Show success animation
            self.message.text = "Login successful!"
            self.message.color = (0, 1, 0, 1)

            # Delay navigation to home
            Clock.schedule_once(self.navigate_to_home, 1)
        else:
            # Show error and stay on login screen
            self.message.text = 'Invalid username or password.'
            self.message.color = (1, 0, 0, 1)

    # Example code to navigate from login to profile (add this to your login screen)
    def on_login_success(self, user_id):
        # Set user ID in profile screen
        self.manager.get_screen('profile').set_user_id(user_id)
        self.manager.get_screen('home').set_user_id(user_id)
        self.manager.get_screen('news').set_user_id(user_id)
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'home'

    def navigate_to_home(self, dt):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'home'

    def forgot_password(self, instance, touch):
        if instance.collide_point(touch.x, touch.y):
            # Would implement password recovery
            print("Password recovery")

    def go_back(self, instance):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'welcome'

    def navigate_to_register(self, instance, touch):
        # Ensures it was actually clicked
        if instance.collide_point(*touch.pos):
            self.manager.transition = SlideTransition(direction='right')
            self.manager.current = 'register'
