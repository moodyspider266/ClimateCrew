from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image, AsyncImage
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.network.urlrequest import UrlRequest
from kivy.properties import ListProperty, NumericProperty
from kivy.clock import Clock
from kivymd.uix.button import MDFloatingActionButton, MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
import json
import webbrowser


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


class NewsScreen(Screen):
    news_items = ListProperty([])
    current_index = NumericProperty(0)

    def __init__(self, **kwargs):
        super(NewsScreen, self).__init__(**kwargs)
        self.name = 'news'

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

        # Title in the middle
        title_label = MDLabel(
            text="Climate News",
            halign="center",
            font_style="H6",
            theme_text_color="Custom",
            text_color=get_color_from_hex(COLORS['white'] + 'ff'),
            size_hint=(0.8, 1)
        )
        header.add_widget(title_label)

        # Profile button - changed from image to icon button
        profile_btn = MDIconButton(
            icon='account-circle',
            pos_hint={'center_y': 0.5},
            icon_size=dp(24),
            theme_text_color="Custom",
            text_color=get_color_from_hex(COLORS['white'] + 'ff'),
            size_hint=(0.1, 1)
        )
        profile_btn.bind(on_press=self.go_to_profile)
        header.add_widget(profile_btn)
        main_layout.add_widget(header)

        # Previous News Arrow (just below header)
        prev_arrow = MDIconButton(
            icon="arrow-up-bold",
            pos_hint={'center_x': 0.5, 'top': 0.92},
            icon_size=dp(36),  # Changed from user_font_size to icon_size
            theme_text_color="Custom",
            text_color=get_color_from_hex(COLORS['primary'] + 'ff')
        )
        prev_arrow.bind(on_press=self.show_previous_news)
        main_layout.add_widget(prev_arrow)

        # Content area for news display
        self.content_area = FloatLayout(
            size_hint=(1, 0.74),
            pos_hint={'top': 0.90, 'center_x': 0.5}
        )

        # News card container
        self.news_container = ScrollView(
            size_hint=(0.95, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            do_scroll_x=False,
            do_scroll_y=True
        )

        # Bind scrolling to navigation
        self.news_container.bind(scroll_y=self.on_scroll)

        # Create layout for news content
        self.news_layout = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(800),
            spacing=dp(15),
            padding=[dp(10), dp(10)]
        )

        # Empty news card (will be populated later)
        self.news_card = MDCard(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(700),
            radius=[dp(15)],
            elevation=4,
            padding=[dp(20), dp(20)]
        )

        # Loading indicator
        loading_box = BoxLayout(
            orientation='vertical',
            size_hint=(1, 1),
            spacing=dp(20),
            padding=[dp(20), dp(100)]
        )
        loading_label = MDLabel(
            text="Loading Climate News...",
            halign="center",
            font_style="H5"
        )
        loading_box.add_widget(loading_label)
        self.news_card.add_widget(loading_box)

        self.news_layout.add_widget(self.news_card)
        self.news_container.add_widget(self.news_layout)
        self.content_area.add_widget(self.news_container)

        main_layout.add_widget(self.content_area)

        # Next News Arrow (just above navbar)
        next_arrow = MDIconButton(
            icon="arrow-down-bold",
            pos_hint={'center_x': 0.5, 'y': 0.1},
            icon_size=dp(36),  # Changed from user_font_size to icon_size
            theme_text_color="Custom",
            text_color=get_color_from_hex(COLORS['primary'] + 'ff')
        )
        next_arrow.bind(on_press=self.show_next_news)
        main_layout.add_widget(next_arrow)

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
        home_icon.bind(on_press=self.go_to_home)
        home_btn.add_widget(home_icon)
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
        nav_bar.add_widget(social_btn)

        # News button (active)
        news_btn = BoxLayout(orientation='vertical')
        news_icon = MDFloatingActionButton(
            icon='newspaper',
            font_size=dp(24),
            md_bg_color=(1, 1, 1, 1),  # White background for active icon
            text_color=(68/255, 110/255, 73/255, 1),  # Primary color for icon
            size_hint=(1, 0.7)
        )
        news_btn.add_widget(news_icon)
        nav_bar.add_widget(news_btn)

        main_layout.add_widget(nav_bar)
        self.add_widget(main_layout)

    def on_enter(self):
        """Called when the screen is entered - fetch news data"""
        self.fetch_news()

    def fetch_news(self):
        """Fetch climate news from API"""
        url = "http://localhost:5000/api/climate-news?count=15"
        UrlRequest(
            url,
            on_success=self.on_news_success,
            on_error=self.on_news_error,
            on_failure=self.on_news_error,
            req_headers={'Content-Type': 'application/json'}
        )

    def on_news_success(self, request, result):
        """Handle successful news API response"""
        self.news_items = result.get('articles', [])
        if self.news_items:
            self.current_index = 0
            self.display_current_news()
        else:
            self.display_error("No news articles available.")

    def on_news_error(self, request, error):
        """Handle news API error"""
        print(f"News API Error: {error}")
        print(f"Request: {request}")
        self.display_error(f"Could not load news: {error}")

    def display_error(self, message):
        """Display error message in the news card"""
        self.news_card.clear_widgets()
        error_label = MDLabel(
            text=message,
            halign="center",
            font_style="Body1",
            theme_text_color="Error"
        )
        self.news_card.add_widget(error_label)

    def display_current_news(self):
        """Display the current news item"""
        self.news_card.clear_widgets()

        if not self.news_items or self.current_index >= len(self.news_items):
            self.display_error("No news articles available.")
            return

        news = self.news_items[self.current_index]

        # Create vertical layout for news content
        content_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(15),
            size_hint=(1, 1)
        )

        # Title
        title = MDLabel(
            text=news['title'],
            font_style="H5",
            theme_text_color="Primary",
            halign="left",
            size_hint_y=None,
            height=dp(80)
        )
        content_layout.add_widget(title)

        # Image if available
        if news.get('image'):
            try:
                img = AsyncImage(
                    source=news['image'],
                    size_hint=(1, None),
                    height=dp(200),
                    allow_stretch=True,
                    keep_ratio=True
                )
                content_layout.add_widget(img)
            except:
                pass

        # Content
        content = MDLabel(
            text=news['summary'],
            theme_text_color="Secondary",
            font_style="Body1",
            halign="left",
            size_hint_y=None,
            height=dp(300)
        )
        content_layout.add_widget(content)

        # # Source link button
        # source_layout = BoxLayout(
        #     orientation='horizontal',
        #     size_hint=(1, None),
        #     height=dp(50)
        # )

        # source_label = MDLabel(
        #     text=f"Source: {news['source_name']}",
        #     theme_text_color="Secondary",
        #     size_hint=(0.6, 1)
        # )
        # source_layout.add_widget(source_label)

        # view_btn = Button(
        #     text="Read More",
        #     background_color=get_color_from_hex(COLORS['primary'] + 'ff'),
        #     size_hint=(0.4, 1)
        # )
        # view_btn.bind(
        #     on_press=lambda x: self.open_source_url(news['source_url']))
        # source_layout.add_widget(view_btn)

        # content_layout.add_widget(source_layout)

        # News counter
        counter_label = MDLabel(
            text=f"Article {self.current_index + 1} of {len(self.news_items)}",
            theme_text_color="Hint",
            halign="center",
            size_hint_y=None,
            height=dp(30)
        )
        content_layout.add_widget(counter_label)

        self.news_card.add_widget(content_layout)

    def show_next_news(self, instance=None):
        """Show the next news article"""
        if self.news_items and self.current_index < len(self.news_items) - 1:
            self.current_index += 1
            self.display_current_news()
            self.news_container.scroll_y = 1  # Reset scroll position

    def show_previous_news(self, instance=None):
        """Show the previous news article"""
        if self.news_items and self.current_index > 0:
            self.current_index -= 1
            self.display_current_news()
            self.news_container.scroll_y = 1  # Reset scroll position

    def on_scroll(self, instance, value):
        """Handle scrolling to navigate between news items"""
        # When scrolled to the bottom
        if value <= 0.1:
            Clock.schedule_once(lambda dt: self.show_next_news(), 0.3)

        # When scrolled to the top
        elif value >= 0.9 and self.news_container.scroll_y >= 0.98:
            Clock.schedule_once(lambda dt: self.show_previous_news(), 0.3)

    def open_source_url(self, url):
        """Open the source URL in the browser"""
        webbrowser.open(url)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def _update_header_rect(self, instance, value):
        self.header_rect.pos = instance.pos
        self.header_rect.size = instance.size

    def _update_nav_rect(self, instance, value):
        self.nav_rect.pos = instance.pos
        self.nav_rect.size = instance.size

    def go_to_home(self, instance):
        self.manager.transition.direction = 'right'
        # Assuming your home screen is named 'dashboard'
        self.manager.current = 'home'

    def go_to_profile(self, instance):
        self.manager.transition.direction = 'left'
        self.manager.current = 'profile'

    def go_to_map(self, instance):
        self.manager.transition.direction = 'left'
        self.manager.current = 'map'

    def go_to_social(self, instance):
        self.manager.transition.direction = 'left'
        self.manager.current = 'social'
