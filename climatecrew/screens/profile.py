from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.graphics import Color, Rectangle

# Constants
COLORS = {
    'background': '#e3f8ee',
    'primary': '#446e49',
    'text': '#333333',
    'secondary_text': '#666666',
    'white': '#ffffff',
    'camera_blue': '#03A9F4'
}

class ProfileScreen(Screen):
    def __init__(self, **kwargs):
        super(ProfileScreen, self).__init__(**kwargs)
        self.name = 'profile'
        
        main_layout = FloatLayout()
        with main_layout.canvas.before:
            Color(rgba=get_color_from_hex(COLORS['background'] + 'ff'))
            self.rect = Rectangle(size=main_layout.size, pos=main_layout.pos)
        main_layout.bind(size=self._update_rect, pos=self._update_rect)
        
        # Header with back button and title
        header = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 0.08),
            pos_hint={'top': 1}
        )
        
        # Back button
        back_btn = Button(
            text='←',
            font_size=dp(24),
            background_color=(0, 0, 0, 0),
            color=get_color_from_hex(COLORS['text'] + 'ff'),
            size_hint=(0.1, 1)
        )
        back_btn.bind(on_press=self.go_back)
        header.add_widget(back_btn)
        
        # Title
        title = Label(
            text='Fill your Profile',
            font_size=dp(20),
            color=get_color_from_hex(COLORS['text'] + 'ff'),
            size_hint=(0.8, 1)
        )
        header.add_widget(title)
        
        # Spacer
        header.add_widget(BoxLayout(size_hint=(0.1, 1)))
        
        main_layout.add_widget(header)
        
        # Content ScrollView with profile form
        content = BoxLayout(
            orientation='vertical',
            size_hint=(1, 0.82),
            pos_hint={'top': 0.92},
            padding=[dp(20), dp(10)]
        )
        
        # Profile picture section
        profile_pic_layout = BoxLayout(
            orientation='vertical',
            size_hint=(1, 0.25),
            spacing=dp(5)
        )
        
        # Profile picture container
        pic_container = FloatLayout(
            size_hint=(None, None),
            size=(dp(120), dp(120)),
            pos_hint={'center_x': 0.5}
        )
        
        # Profile picture
        profile_pic = Image(
            source='assets/profile_placeholder.png',
            size_hint=(1, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        pic_container.add_widget(profile_pic)
        
        # Camera button
        camera_btn = Button(
            text='📷',
            font_size=dp(20),
            background_color=get_color_from_hex(COLORS['camera_blue'] + 'ff'),
            color=get_color_from_hex(COLORS['white'] + 'ff'),
            size_hint=(None, None),
            size=(dp(30), dp(30)),
            pos_hint={'right': 1, 'y': 0}
        )
        pic_container.add_widget(camera_btn)
        
        profile_pic_layout.add_widget(pic_container)
        content.add_widget(profile_pic_layout)
        
        # Form fields
        form_layout = GridLayout(
            cols=1,
            spacing=dp(10),
            size_hint=(1, 0.75)
        )
        
        # Username
        username_label = Label(
            text='Username',
            font_size=dp(14),
            color=get_color_from_hex(COLORS['text'] + 'ff'),
            halign='left',
            size_hint=(1, None),
            height=dp(20),
            text_size=(None, None)
        )
        form_layout.add_widget(username_label)
        
        username_input = TextInput(
            text='moodyspider266',
            multiline=False,
            size_hint=(1, None),
            height=dp(40),
            background_color=get_color_from_hex(COLORS['white'] + 'ff'),
            cursor_color=get_color_from_hex(COLORS['primary'] + 'ff'),
            padding=[dp(10), dp(10), 0, 0]
        )
        form_layout.add_widget(username_input)
        
        # Full Name
        fullname_label = Label(
            text='Full Name',
            font_size=dp(14),
            color=get_color_from_hex(COLORS['text'] + 'ff'),
            halign='left',
            size_hint=(1, None),
            height=dp(20),
            text_size=(None, None)
        )
        form_layout.add_widget(fullname_label)
        
        fullname_input = TextInput(
            text='Kushi Alve',
            multiline=False,
            size_hint=(1, None),
            height=dp(40),
            background_color=get_color_from_hex(COLORS['white'] + 'ff'),
            cursor_color=get_color_from_hex(COLORS['primary'] + 'ff'),
            padding=[dp(10), dp(10), 0, 0]
        )
        form_layout.add_widget(fullname_input)
        
        # Email Address
        email_label = Label(
            text='Email Address*',
            font_size=dp(14),
            color=get_color_from_hex(COLORS['text'] + 'ff'),
            halign='left',
            size_hint=(1, None),
            height=dp(20),
            text_size=(None, None)
        )
        form_layout.add_widget(email_label)
        
        email_input = TextInput(
            text='kushialve007@gmail.com',
            multiline=False,
            size_hint=(1, None),
            height=dp(40),
            background_color=get_color_from_hex(COLORS['white'] + 'ff'),
            cursor_color=get_color_from_hex(COLORS['primary'] + 'ff'),
            padding=[dp(10), dp(10), 0, 0]
        )
        form_layout.add_widget(email_input)
        
        # Phone Number
        phone_label = Label(
            text='Phone Number*',
            font_size=dp(14),
            color=get_color_from_hex(COLORS['text'] + 'ff'),
            halign='left',
            size_hint=(1, None),
            height=dp(20),
            text_size=(None, None)
        )
        form_layout.add_widget(phone_label)
        
        phone_input = TextInput(
            text='+91-99874-57425',
            multiline=False,
            size_hint=(1, None),
            height=dp(40),
            background_color=get_color_from_hex(COLORS['white'] + 'ff'),
            cursor_color=get_color_from_hex(COLORS['primary'] + 'ff'),
            padding=[dp(10), dp(10), 0, 0]
        )
        form_layout.add_widget(phone_input)
        
        # City
        city_label = Label(
            text='City*',
            font_size=dp(14),
            color=get_color_from_hex(COLORS['text'] + 'ff'),
            halign='left',
            size_hint=(1, None),
            height=dp(20),
            text_size=(None, None)
        )
        form_layout.add_widget(city_label)
        
        city_input = TextInput(
            text='Mumbai',
            multiline=False,
            size_hint=(1, None),
            height=dp(40),
            background_color=get_color_from_hex(COLORS['white'] + 'ff'),
            cursor_color=get_color_from_hex(COLORS['primary'] + 'ff'),
            padding=[dp(10), dp(10), 0, 0]
        )
        form_layout.add_widget(city_input)
        
        # Country
        country_label = Label(
            text='Country*',
            font_size=dp(14),
            color=get_color_from_hex(COLORS['text'] + 'ff'),
            halign='left',
            size_hint=(1, None),
            height=dp(20),
            text_size=(None, None)
        )
        form_layout.add_widget(country_label)
        
        country_input = TextInput(
            text='India',
            multiline=False,
            size_hint=(1, None),
            height=dp(40),
            background_color=get_color_from_hex(COLORS['white'] + 'ff'),
            cursor_color=get_color_from_hex(COLORS['primary'] + 'ff'),
            padding=[dp(10), dp(10), 0, 0]
        )
        form_layout.add_widget(country_input)
        
        # Occupation
        occupation_label = Label(
            text='Occupation*',
            font_size=dp(14),
            color=get_color_from_hex(COLORS['text'] + 'ff'),
            halign='left',
            size_hint=(1, None),
            height=dp(20),
            text_size=(None, None)
        )
        form_layout.add_widget(occupation_label)
        
        occupation_input = TextInput(
            text='Student',
            multiline=False,
            size_hint=(1, None),
            height=dp(40),
            background_color=get_color_from_hex(COLORS['white'] + 'ff'),
            cursor_color=get_color_from_hex(COLORS['primary'] + 'ff'),
            padding=[dp(10), dp(10), 0, 0]
        )
        form_layout.add_widget(occupation_input)
        
        # Save button
        save_btn = Button(
            text='Save Changes',
            font_size=dp(16),
            background_color=get_color_from_hex(COLORS['primary'] + 'ff'),
            color=get_color_from_hex(COLORS['white'] + 'ff'),
            size_hint=(1, None),
            height=dp(50),
            pos_hint={'center_x': 0.5}
        )
        save_btn.bind(on_press=self.save_profile)
        form_layout.add_widget(save_btn)
        
        content.add_widget(form_layout)
        main_layout.add_widget(content)
        
        # Bottom navigation bar
        nav_bar = GridLayout(
            cols=4,
            size_hint=(1, 0.1),
            pos_hint={'bottom': 1}
        )
        
        with nav_bar.canvas.before:
            Color(rgba=get_color_from_hex(COLORS['primary'] + 'ff'))
            self.nav_rect = Rectangle(size=nav_bar.size, pos=nav_bar.pos)
        nav_bar.bind(size=self._update_nav_rect, pos=self._update_nav_rect)
        
        # Home button
        home_btn = BoxLayout(orientation='vertical')
        home_icon = Button(
            text='⌂',
            font_size=dp(24),
            background_color=(0, 0, 0, 0),
            color=get_color_from_hex(COLORS['white'] + 'ff'),
            size_hint=(1, 0.7)
        )
        home_icon.bind(on_press=self.go_to_home)
        home_label = Label(
            text='Home',
            font_size=dp(12),
            color=get_color_from_hex(COLORS['white'] + 'ff'),
            size_hint=(1, 0.3)
        )
        home_btn.add_widget(home_icon)
        home_btn.add_widget(home_label)
        nav_bar.add_widget(home_btn)
        
        # Map button
        map_btn = BoxLayout(orientation='vertical')
        map_icon = Button(
            text='◎',
            font_size=dp(24),
            background_color=(0, 0, 0, 0),
            color=get_color_from_hex(COLORS['white'] + 'ff'),
            size_hint=(1, 0.7)
        )
        map_icon.bind(on_press=self.go_to_map)
        map_label = Label(
            text='Map',
            font_size=dp(12),
            color=get_color_from_hex(COLORS['white'] + 'ff'),
            size_hint=(1, 0.3)
        )
        map_btn.add_widget(map_icon)
        map_btn.add_widget(map_label)
        nav_bar.add_widget(map_btn)
        
        # Social button
        social_btn = BoxLayout(orientation='vertical')
        social_icon = Button(
            text='⚇',
            font_size=dp(24),
            background_color=(0, 0, 0, 0),
            color=get_color_from_hex(COLORS['white'] + 'ff'),
            size_hint=(1, 0.7)
        )
        social_icon.bind(on_press=self.go_to_social)
        social_label = Label(
            text='Social',
            font_size=dp(12),
            color=get_color_from_hex(COLORS['white'] + 'ff'),
            size_hint=(1, 0.3)
        )
        social_btn.add_widget(social_icon)
        social_btn.add_widget(social_label)
        nav_bar.add_widget(social_btn)
        
        # News button
        news_btn = BoxLayout(orientation='vertical')
        news_icon = Button(
            text='≡',
            font_size=dp(24),
            background_color=(0, 0, 0, 0),
            color=get_color_from_hex(COLORS['white'] + 'ff'),
            size_hint=(1, 0.7)
        )
        news_icon.bind(on_press=self.go_to_news)
        news_label = Label(
            text='News',
            font_size=dp(12),
            color=get_color_from_hex(COLORS['white'] + 'ff'),
            size_hint=(1, 0.3)
        )
        news_btn.add_widget(news_icon)
        news_btn.add_widget(news_label)
        nav_bar.add_widget(news_btn)
        
        main_layout.add_widget(nav_bar)
        
        self.add_widget(main_layout)
    
    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
    
    def _update_nav_rect(self, instance, value):
        self

    def go_back(self, instance):
        self.manager.transition.direction = 'left'
        self.manager.current = 'home'

    def save_profile(self, instance):
        self
        #yet to implement saving changes to profile.

    def go_to_map(self, instance):
        self.manager.transition.direction = 'left'
        self.manager.current = 'map'
    
    def go_to_social(self, instance):
        self.manager.transition.direction = 'left'
        self.manager.current = 'social'
    
    def go_to_news(self, instance):
        self.manager.transition.direction = 'left'
        self.manager.current = 'news'

    def go_to_home(self, instance):
        self.manager.transition.direction = 'left'
        self.manager.current = 'home'