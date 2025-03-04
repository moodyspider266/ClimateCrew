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

class WelcomeScreen(Screen):
    def __init__(self, **kwargs):
        super(WelcomeScreen, self).__init__(**kwargs)
        self.name = 'welcome'
        
        layout = FloatLayout()
        with layout.canvas.before:
            Color(rgba=get_color_from_hex(COLORS['background'] + 'ff'))
            self.rect = Rectangle(size=layout.size, pos=layout.pos)
        layout.bind(size=self._update_rect, pos=self._update_rect)
        
        # Logo and title
        logo_layout = BoxLayout(orientation='vertical', 
                              pos_hint={'center_x': 0.5, 'center_y': 0.65},
                              size_hint=(0.7, 0.4))
        
        logo = Image(source='assets/logo.png', size_hint=(1, 0.7))
        logo_layout.add_widget(logo)
        
        title = Label(text='ClimateCrew', 
                    font_size=dp(24), 
                    color=get_color_from_hex(COLORS['primary'] + 'ff'),
                    bold=True,
                    size_hint=(1, 0.15))
        logo_layout.add_widget(title)
        
        subtitle = Label(text='Join the Cause',
                       font_size=dp(16),
                       color=get_color_from_hex(COLORS['secondary_text'] + 'ff'),
                       size_hint=(1, 0.15))
        logo_layout.add_widget(subtitle)
        
        layout.add_widget(logo_layout)
        
        # Buttons
        btn_layout = BoxLayout(orientation='horizontal', 
                             spacing=dp(10),
                             padding=dp(20),
                             pos_hint={'center_x': 0.5, 'center_y': 0.25},
                             size_hint=(0.8, 0.08))
        
        login_btn = Button(text='Login',
                         background_color=get_color_from_hex(COLORS['primary'] + 'ff'),
                         color=get_color_from_hex(COLORS['white'] + 'ff'),
                         size_hint=(0.5, 1),
                         font_size=dp(16))
        login_btn.bind(on_press=self.go_to_login)
        
        register_btn = Button(text='Register',
                            background_color=get_color_from_hex(COLORS['white'] + 'ff'),
                            color=get_color_from_hex(COLORS['primary'] + 'ff'),
                            size_hint=(0.5, 1),
                            font_size=dp(16))
        register_btn.bind(on_press=self.go_to_register)
        
        btn_layout.add_widget(login_btn)
        btn_layout.add_widget(register_btn)
        layout.add_widget(btn_layout)
        
        self.add_widget(layout)
    
    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
    
    def go_to_login(self, instance):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'login'
    
    def go_to_register(self, instance):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'register'