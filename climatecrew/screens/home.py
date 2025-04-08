from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.graphics import Color, Rectangle
from kivymd.uix.button import MDFloatingActionButton
from kivymd.uix.label import MDLabel

# Color scheme based on your Figma design
COLORS = {
    'background': '#e3f8ee',
    'primary': '#446e49',
    'text': '#333333',
    'secondary_text': '#666666',
    'white': '#ffffff',
    'task_bg': '#446e49',
    'yellow': '#ffc107',
    'button_blue': '#2196F3'
}


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)
        self.name = 'home'

        main_layout = FloatLayout()
        with main_layout.canvas.before:
            Color(rgba=get_color_from_hex(COLORS['background'] + 'ff'))
            self.rect = Rectangle(size=main_layout.size, pos=main_layout.pos)
        main_layout.bind(size=self._update_rect, pos=self._update_rect)

        # Header with menu and profile photo
        header = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 0.08),
            pos_hint={'top': 1},
            padding=[dp(10), dp(10)]
        )

        with header.canvas.before:
            Color(rgba=get_color_from_hex(COLORS['primary'] + 'ff'))
            self.header_rect = Rectangle(size=header.size, pos=header.pos)
        header.bind(size=self._update_header_rect,
                    pos=self._update_header_rect)

        # Menu button
        menu_btn = MDFloatingActionButton(
            icon='menu',
            font_size=dp(24),
            md_bg_color=(68/255, 110/255, 73/255, 1),
            icon_color=get_color_from_hex(COLORS['white'] + 'ff'),
            size_hint=(0.1, 1)
        )
        header.add_widget(menu_btn)

        # Spacer
        header.add_widget(BoxLayout(size_hint=(0.8, 1)))

        # Profile photo button
        profile_btn = Button(
            background_normal='../assets/default_profile.png',
            background_down='../assets/default_profile.png',
            border=(0, 0, 0, 0),
            size_hint=(0.1, 1)
        )
        profile_btn.bind(on_press=self.go_to_profile)
        header.add_widget(profile_btn)

        main_layout.add_widget(header)

        # Content area
        content = BoxLayout(
            orientation='vertical',
            size_hint=(1, 0.82),
            pos_hint={'top': 0.92},
            padding=[dp(10), dp(5)]
        )

        # Leaderboard position
        leaderboard_btn = Button(
            text='🏆 Leaderboard Position : 5',
            font_size=dp(18),
            background_color=get_color_from_hex(COLORS['yellow'] + 'ff'),
            color=get_color_from_hex(COLORS['text'] + 'ff'),
            size_hint=(1, 0.08),
            pos_hint={'center_x': 0.5}
        )
        leaderboard_btn.bind(on_press=self.go_to_leaderboard)
        content.add_widget(leaderboard_btn)

        # Welcome message
        welcome_label = Label(
            text='Welcome Kushl!',
            font_size=dp(22),
            color=get_color_from_hex(COLORS['primary'] + 'ff'),
            halign='left',
            valign='middle',
            size_hint=(1, 0.08),
            text_size=(None, None)
        )
        content.add_widget(welcome_label)

        # Task heading
        task_heading = Label(
            text='Here is your task for today :',
            font_size=dp(18),
            color=get_color_from_hex(COLORS['text'] + 'ff'),
            halign='left',
            valign='middle',
            size_hint=(1, 0.08),
            text_size=(None, None)
        )
        content.add_widget(task_heading)

        # Task card
        task_card = FloatLayout(
            size_hint=(1, 0.4)
        )

        with task_card.canvas.before:
            Color(rgba=get_color_from_hex(COLORS['task_bg'] + 'ff'))
            self.task_rect = Rectangle(size=task_card.size, pos=task_card.pos)
        task_card.bind(size=self._update_task_rect, pos=self._update_task_rect)

        # Task description
        task_text = MDLabel(
            text='This weekend, your task is to volunteer for a local tree planting initiative in Mumbai. Find one happening near you (check with local NGOs or online). It\'s a great way to contribute to the city\'s green spaces!',
            font_size=dp(16),
            color=get_color_from_hex(COLORS['white'] + 'ff'),
            halign='left',
            valign='top',
            size_hint=(0.9, None),
            # height=dp(120),
            pos_hint={'center_x': 0.5, 'top': 0.95},
            # text_size=(dp(280), None)  # Set width constraint for text wrapping
        )
        # Bind the width of task_card to update text_size

        def update_text_size(instance, value):
            task_text.text_size = (instance.width * 0.9, None)
            task_text.texture_update()
            # After texture update, adjust height based on texture size
            task_text.height = task_text.texture_size[1]

        task_card.bind(width=update_text_size)
        task_card.add_widget(task_text)

        # Impact points
        points_btn = Button(
            text='+ 20 Impact Points',
            font_size=dp(16),
            background_color=get_color_from_hex(COLORS['yellow'] + 'ff'),
            color=get_color_from_hex(COLORS['text'] + 'ff'),
            size_hint=(0.5, 0.15),
            pos_hint={'center_x': 0.5, 'y': 0.05}
        )
        task_card.add_widget(points_btn)

        content.add_widget(task_card)

        # Task buttons
        task_buttons = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 0.1),
            spacing=dp(10),
            padding=[dp(0), dp(10)]
        )

        change_task_btn = Button(
            text='Change Task',
            font_size=dp(16),
            background_color=get_color_from_hex(
                COLORS['secondary_text'] + 'ff'),
            color=get_color_from_hex(COLORS['white'] + 'ff'),
            size_hint=(0.5, 1)
        )
        task_buttons.add_widget(change_task_btn)

        submit_task_btn = Button(
            text='Submit Task',
            font_size=dp(16),
            background_color=get_color_from_hex(COLORS['button_blue'] + 'ff'),
            color=get_color_from_hex(COLORS['white'] + 'ff'),
            size_hint=(0.5, 1)
        )
        task_buttons.add_widget(submit_task_btn)

        content.add_widget(task_buttons)

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
        home_icon = MDFloatingActionButton(
            icon='home',
            font_size=dp(24),
            md_bg_color=(68/255, 110/255, 73/255, 1),
            size_hint=(1, 0.7)
        )
        home_btn.add_widget(home_icon)
        # home_btn.add_widget(home_label)
        nav_bar.add_widget(home_btn)

        # Map button
        map_btn = BoxLayout(orientation='vertical')
        map_icon = MDFloatingActionButton(
            icon='map-marker',
            font_size=dp(24),
            md_bg_color=(68/255, 110/255, 73/255, 1),
            size_hint=(1, 0.7)
        )
        map_icon.bind(on_press=self.go_to_map)
        map_btn.add_widget(map_icon)
        # map_btn.add_widget(map_label)
        nav_bar.add_widget(map_btn)

        # Social button
        social_btn = BoxLayout(orientation='vertical')
        social_icon = MDFloatingActionButton(
            icon='account-group',
            font_size=dp(24),
            md_bg_color=(68/255, 110/255, 73/255, 1),
            size_hint=(1, 0.7)
        )
        social_icon.bind(on_press=self.go_to_social)
        social_btn.add_widget(social_icon)
        # social_btn.add_widget(social_label)
        nav_bar.add_widget(social_btn)

        # News button
        news_btn = BoxLayout(orientation='vertical')
        news_icon = MDFloatingActionButton(
            icon='newspaper',
            font_size=dp(24),
            md_bg_color=(68/255, 110/255, 73/255, 1),
            size_hint=(1, 0.7)
        )
        news_icon.bind(on_press=self.go_to_news)
        news_btn.add_widget(news_icon)
        # news_btn.add_widget(news_label)
        nav_bar.add_widget(news_btn)

        main_layout.add_widget(nav_bar)

        self.add_widget(main_layout)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def _update_header_rect(self, instance, value):
        self.header_rect.pos = instance.pos
        self.header_rect.size = instance.size

    def _update_task_rect(self, instance, value):
        self.task_rect.pos = instance.pos
        self.task_rect.size = instance.size

    def _update_nav_rect(self, instance, value):
        self.nav_rect.pos = instance.pos
        self.nav_rect.size = instance.size

    def go_to_profile(self, instance):
        self.manager.transition.direction = 'left'
        self.manager.get_screen('profile').set_user_id(self.user_id)
        self.manager.current = 'profile'

    def go_to_leaderboard(self, instance):
        self.manager.transition.direction = 'left'
        self.manager.current = 'leaderboard'

    def go_to_map(self, instance):
        self.manager.transition.direction = 'left'
        self.manager.current = 'map'

    def go_to_social(self, instance):
        self.manager.transition.direction = 'left'
        self.manager.current = 'social'

    def go_to_news(self, instance):
        self.manager.transition.direction = 'left'
        self.manager.current = 'news'
