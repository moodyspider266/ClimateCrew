from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.core.text import LabelBase

LabelBase.register(name="Roboto", fn_regular="assets/fonts/Roboto-VariableFont_wdth,wght.ttf")

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
        
        # Logo & Title Section
        logo_layout = BoxLayout(orientation='vertical',
                        pos_hint={'center_x': 0.5, 'center_y': 0.6},  
                        size_hint=(1.5, None),
                        height=dp(250),  
                        spacing=dp(10))

        
        logo = Image(source='assets/logo.png', 
             size_hint=(None, None),  # Disable automatic resizing
             size=(dp(120), dp(120)),
             pos_hint={'center_x': 0.5})  # Increase size manually
        logo_layout.add_widget(logo)
        
        title = Label(text='ClimateCrew', 
                      font_size=dp(28),
                      font_name='Roboto',
                      color=get_color_from_hex(COLORS['primary'] + 'ff'),
                      bold=True)
        logo_layout.add_widget(title)
        
        subtitle = Label(text='Join. Act. Inspire.',
                         font_size=dp(16),
                         font_name='Roboto',
                         color=get_color_from_hex(COLORS['primary'] + 'ff'))
        logo_layout.add_widget(subtitle)
        
        layout.add_widget(logo_layout)
        
        # Buttons Section
        btn_layout = BoxLayout(orientation='horizontal',
                               spacing=dp(15),
                               padding=dp(20),
                               pos_hint={'center_x': 0.5, 'center_y': 0.25},
                               size_hint=(0.8, 0.12))
        
        login_btn = Button(text='Login',
                           background_color=get_color_from_hex(COLORS['primary'] + 'ff'),
                           color=get_color_from_hex(COLORS['white'] + 'ff'),
                           size_hint=(0.5, 1),
                           font_size=dp(18),
                        #    size=(dp(120), dp(50)), 
                           padding=(dp(15), dp(10)),
                           font_name='Roboto',
                           halign='center',
                           valign='middle', 
                           bold=True)
        login_btn.bind(on_press=self.go_to_login)
        
        register_btn = Button(text='Register',
                              background_normal='',
                              background_color=(1,1,1,1),
                              color=get_color_from_hex(COLORS['primary'] + 'ff'),
                              size_hint=(0.5, 1),
                              font_size=dp(18),
                              font_name='Roboto',
                              bold=True)
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