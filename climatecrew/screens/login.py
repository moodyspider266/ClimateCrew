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
        username_input = TextInput(hint_text='Username',
                              multiline=False,
                              size_hint=(1, None),
                              height=dp(40),
                              background_color=get_color_from_hex(COLORS['white'] + 'ff'),
                              cursor_color=get_color_from_hex(COLORS['primary'] + 'ff'),
                              padding=[dp(10), dp(10), 0, 0])
        form_layout.add_widget(username_input)
        
        # Password field
        password_input = TextInput(hint_text='Password',
                                 multiline=False,
                                 password=True,
                                 size_hint=(1, None),
                                 height=dp(40),
                                 background_color=get_color_from_hex(COLORS['white'] + 'ff'),
                                 cursor_color=get_color_from_hex(COLORS['primary'] + 'ff'),
                                 padding=[dp(10), dp(10), 0, 0])
        form_layout.add_widget(password_input)
        
        # Forgot password link
        forgot_pw = Label(text='Forgot your password?',
                        font_size=dp(14),
                        color=get_color_from_hex(COLORS['secondary_text'] + 'ff'),
                        size_hint=(1, None),
                        height=dp(30),
                        halign='right')
        forgot_pw.bind(on_touch_down=self.forgot_password)
        form_layout.add_widget(forgot_pw)
        
        # Sign in button
        signin_btn = Button(text='Sign In',
                          background_color=get_color_from_hex(COLORS['primary'] + 'ff'),
                          color=get_color_from_hex(COLORS['white'] + 'ff'),
                          size_hint=(1, None),
                          height=dp(40),
                          font_size=dp(16))
        signin_btn.bind(on_press=self.sign_in)
        form_layout.add_widget(signin_btn)
        
        # "Don't have an account" text and register link
        account_label = Label(text="Don't have an account?",
                            font_size=dp(14),
                            color=get_color_from_hex(COLORS['secondary_text'] + 'ff'),
                            size_hint=(1, None),
                            height=dp(30),
                            halign='center')
        form_layout.add_widget(account_label)
        
        layout.add_widget(form_layout)
        
        # Social login options
        social_layout = BoxLayout(orientation='horizontal',
                                spacing=dp(20),
                                pos_hint={'center_x': 0.5, 'center_y': 0.28},
                                size_hint=(0.6, 0.05))
        
        # Social login icons (these would be replaced with actual icons)
        google_btn = Button(text='G',
                          background_color=get_color_from_hex(COLORS['white'] + 'ff'),
                          color=get_color_from_hex(COLORS['primary'] + 'ff'),
                          size_hint=(0.33, 1))
        
        facebook_btn = Button(text='F',
                            background_color=get_color_from_hex(COLORS['white'] + 'ff'),
                            color=get_color_from_hex(COLORS['primary'] + 'ff'),
                            size_hint=(0.33, 1))
        
        twitter_btn = Button(text='T',
                           background_color=get_color_from_hex(COLORS['white'] + 'ff'),
                           color=get_color_from_hex(COLORS['primary'] + 'ff'),
                           size_hint=(0.33, 1))
        
        social_layout.add_widget(google_btn)
        social_layout.add_widget(facebook_btn)
        social_layout.add_widget(twitter_btn)
        
        layout.add_widget(social_layout)
        
        # Back button
        back_btn = Button(text='Back',
                        background_color=get_color_from_hex(COLORS['background'] + '00'),
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
        username = self.username.text.strip()
        password = self.password.text.strip()
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'home'
    
    def forgot_password(self, instance, touch):
        if instance.collide_point(touch.x, touch.y):
            # Would implement password recovery
            print("Password recovery")
    
    def go_back(self, instance):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'welcome'