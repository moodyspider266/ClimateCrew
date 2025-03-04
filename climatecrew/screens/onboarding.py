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

class OnboardingScreen(Screen):
    def __init__(self, **kwargs):
        super(OnboardingScreen, self).__init__(**kwargs)
        self.name = 'onboarding'
        
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
        subtitle = Label(text='Let\'s complete your profile to get started',
                       font_size=dp(16),
                       color=get_color_from_hex(COLORS['secondary_text'] + 'ff'),
                       pos_hint={'center_x': 0.5, 'center_y': 0.78},
                       halign='center')
        subtitle.bind(size=subtitle.setter('text_size'))
        layout.add_widget(subtitle)
        
        # Form layout
        form_layout = BoxLayout(orientation='vertical',
                              spacing=dp(15),
                              padding=[dp(20), dp(0)],
                              pos_hint={'center_x': 0.5, 'center_y': 0.5},
                              size_hint=(0.9, 0.5))
        
        # Profile fields (adding just a few from the design)
        name_input = TextInput(hint_text='Name',
                             multiline=False,
                             size_hint=(1, None),
                             height=dp(40),
                             background_color=get_color_from_hex(COLORS['white'] + 'ff'),
                             cursor_color=get_color_from_hex(COLORS['primary'] + 'ff'),
                             padding=[dp(10), dp(10), 0, 0])
        form_layout.add_widget(name_input)
        
        # City field with icon (simplified)
        city_layout = BoxLayout(orientation='horizontal', 
                              size_hint=(1, None),
                              height=dp(40))
        
        city_input = TextInput(hint_text='City',
                             multiline=False,
                             background_color=get_color_from_hex(COLORS['white'] + 'ff'),
                             cursor_color=get_color_from_hex(COLORS['primary'] + 'ff'),
                             padding=[dp(10), dp(10), 0, 0])
        
        city_icon = Button(text='📍',  # Using emoji as placeholder
                         size_hint=(0.1, 1),
                         background_color=get_color_from_hex(COLORS['white'] + 'ff'))
        
        city_layout.add_widget(city_input)
        city_layout.add_widget(city_icon)
        form_layout.add_widget(city_layout)
        
        # Country field with icon (simplified)
        country_layout = BoxLayout(orientation='horizontal', 
                                 size_hint=(1, None),
                                 height=dp(40))
        
        country_input = TextInput(hint_text='Country',
                                multiline=False,
                                background_color=get_color_from_hex(COLORS['white'] + 'ff'),
                                cursor_color=get_color_from_hex(COLORS['primary'] + 'ff'),
                                padding=[dp(10), dp(10), 0, 0])
        
        country_icon = Button(text='🌍',  # Using emoji as placeholder
                            size_hint=(0.1, 1),
                            background_color=get_color_from_hex(COLORS['white'] + 'ff'))
        
        country_layout.add_widget(country_input)
        country_layout.add_widget(country_icon)
        form_layout.add_widget(country_layout)
        
        # Areas of interest dropdown (simplified)
        interests_layout = BoxLayout(orientation='horizontal', 
                                   size_hint=(1, None),
                                   height=dp(40))
        
        interests_input = TextInput(hint_text='Areas of Interest',
                                  multiline=False,
                                  background_color=get_color_from_hex(COLORS['white'] + 'ff'),
                                  cursor_color=get_color_from_hex(COLORS['primary'] + 'ff'),
                                  padding=[dp(10), dp(10), 0, 0])
        
        dropdown_icon = Button(text='▼',
                             size_hint=(0.1, 1),
                             background_color=get_color_from_hex(COLORS['white'] + 'ff'))
        
        interests_layout.add_widget(interests_input)
        interests_layout.add_widget(dropdown_icon)
        form_layout.add_widget(interests_layout)
        
        # Continue button
        continue_btn = Button(text='Continue',
                            background_color=get_color_from_hex(COLORS['primary'] + 'ff'),
                            color=get_color_from_hex(COLORS['white'] + 'ff'),
                            size_hint=(1, None),
                            height=dp(40),
                            font_size=dp(16))
        continue_btn.bind(on_press=self.continue_to_home)
        form_layout.add_widget(continue_btn)
        
        layout.add_widget(form_layout)
        
        # Skip option
        skip_btn = Button(text='Skip',
                        background_color=get_color_from_hex(COLORS['background'] + '00'),
                        color=get_color_from_hex(COLORS['primary'] + 'ff'),
                        size_hint=(0.2, 0.05),
                        pos_hint={'right': 0.95, 'top': 0.95})
        skip_btn.bind(on_press=self.skip_to_home)
        layout.add_widget(skip_btn)
        
        self.add_widget(layout)
    
    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
    
    def continue_to_home(self, instance):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'home'
    
    def skip_to_home(self, instance):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'home'
