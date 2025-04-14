from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivymd.uix.button import MDFloatingActionButton, MDIconButton
from kivymd.uix.label import MDLabel
from kivy.clock import Clock
from kivy.app import App
from kivy_garden.mapview import MapView, MapMarker, MapMarkerPopup
from kivy.uix.popup import Popup
import tempfile
import os
from datetime import datetime

# You'll need to install the mapview component:
# pip install kivy_garden.mapview

# Color scheme
COLORS = {
    'background': '#e3f8ee',
    'primary': '#446e49',
    'text': '#333333',
    'secondary_text': '#666666',
    'white': '#ffffff',
    'task_bg': '#446e49',
    'yellow': '#ffc107',
    'button_blue': '#2196F3',
    'upvote': '#4CAF50'
}


class CustomMarker(MapMarkerPopup):
    """Custom map marker with additional post data"""

    def __init__(self, post_data, on_select_callback, **kwargs):
        self.post_data = post_data
        self.on_select_callback = on_select_callback

        # Extract lat/lon from post data
        lat = post_data[4]
        lon = post_data[5]

        # Initialize marker with custom properties for better visibility
        super(CustomMarker, self).__init__(
            lat=lat,
            lon=lon,
            source='atlas://data/images/defaulttheme/marker',  # This might need a better icon
            color=[1, 0.3, 0.3, 1],  # Red color for better visibility
            size_hint=(None, None),
            size=(dp(40), dp(40)),  # Larger size for better visibility
            **kwargs
        )

    def on_release(self):
        """Called when marker is tapped - directly show full post"""
        if self.on_select_callback:
            self.on_select_callback(self.post_data)


class PostPreviewPopup(Popup):
    """Small popup showing post preview when marker is clicked"""

    def __init__(self, post_data, on_view_full, **kwargs):
        super(PostPreviewPopup, self).__init__(**kwargs)
        self.post_data = post_data
        self.on_view_full = on_view_full
        self.title = "Climate Action Post"
        self.size_hint = (0.8, 0.4)
        self.background_color = get_color_from_hex(COLORS['white'] + 'dd')

        # Unpack post data
        post_id, user_id, task_text, image_data, lat, lon, location_text, description, date, upvotes = post_data

        # Create layout for popup content
        content = BoxLayout(orientation='vertical',
                            spacing=dp(10), padding=dp(10))

        # Location if available
        if location_text:
            loc_label = MDLabel(
                text=f"📍 {location_text}",
                theme_text_color="Custom",
                text_color=get_color_from_hex(COLORS['primary'] + 'ff'),
                font_style="Subtitle1",
                size_hint=(1, None),
                height=dp(30)
            )
            content.add_widget(loc_label)

        # Brief description preview
        preview_text = description[:100] + \
            "..." if len(description) > 100 else description
        desc_label = MDLabel(
            text=preview_text,
            theme_text_color="Custom",
            text_color=get_color_from_hex(COLORS['text'] + 'ff'),
            size_hint=(1, None),
            height=dp(60),
            halign="left"
        )
        content.add_widget(desc_label)

        # View full post button
        view_btn = Button(
            text="View Full Post",
            background_color=get_color_from_hex(COLORS['button_blue'] + 'ff'),
            color=get_color_from_hex(COLORS['white'] + 'ff'),
            size_hint=(0.8, None),
            height=dp(40),
            pos_hint={'center_x': 0.5}
        )
        view_btn.bind(on_press=self.view_full_post)
        content.add_widget(view_btn)

        self.content = content

    def view_full_post(self, instance):
        """Show the full post view"""
        self.dismiss()
        if self.on_view_full:
            self.on_view_full(self.post_data)


class MapScreen(Screen):
    def __init__(self, db_helper=None, **kwargs):
        super(MapScreen, self).__init__(**kwargs)
        self.name = 'map'
        self.db_helper = db_helper
        self.user_id = None
        self.posts = []
        self.current_post = None
        self.showing_map = True  # Track if map or post detail is showing

        # Main layout
        self.main_layout = FloatLayout()
        with self.main_layout.canvas.before:
            Color(rgba=get_color_from_hex(COLORS['background'] + 'ff'))
            self.rect = Rectangle(
                size=self.main_layout.size, pos=self.main_layout.pos)
        self.main_layout.bind(size=self._update_rect, pos=self._update_rect)

        # Header
        header = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 0.08),
            pos_hint={'top': 1},
            padding=[dp(10), dp(10)]
        )

        with header.canvas.before:
            Color(rgba=get_color_from_hex(COLORS['primary'] + 'ff'))
            self.header_rect = RoundedRectangle(
                size=header.size,
                pos=header.pos,
                radius=[0, 0, 0, dp(10)]  # Bottom corners rounded
            )
        header.bind(size=self._update_header_rect,
                    pos=self._update_header_rect)

        # Back button
        back_btn = MDIconButton(
            icon='arrow-left',
            pos_hint={'center_y': 0.5},
            theme_text_color="Custom",
            text_color=get_color_from_hex(COLORS['white'] + 'ff'),
            size_hint=(0.1, 1)
        )
        back_btn.bind(on_press=self.go_back)
        header.add_widget(back_btn)

        # Title
        self.title_label = MDLabel(
            text="Climate Action Map",
            halign="center",
            theme_text_color="Custom",
            text_color=get_color_from_hex(COLORS['white'] + 'ff'),
            font_style="H6",
            size_hint=(0.8, 1),
            pos_hint={'center_y': 0.5}
        )
        header.add_widget(self.title_label)

        # Refresh button
        refresh_btn = MDIconButton(
            icon='refresh',
            pos_hint={'center_y': 0.5},
            theme_text_color="Custom",
            text_color=get_color_from_hex(COLORS['white'] + 'ff'),
            size_hint=(0.1, 1)
        )
        refresh_btn.bind(on_press=self.load_map_markers)
        header.add_widget(refresh_btn)

        self.main_layout.add_widget(header)

        # Content area - will contain either map or post detail
        self.content_area = FloatLayout(
            size_hint=(1, 0.82),
            pos_hint={'top': 0.92}
        )

        # Create the map view
        self.map_view = MapView(
            lat=19.0760,  # Default center (somewhere in India)
            lon=72.8777,
            zoom=10,
            size_hint=(1, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        self.map_view.map_source.allow_zoom = True

        self.content_area.add_widget(self.map_view)

        # Post detail container (hidden initially)
        self.post_detail = BoxLayout(
            orientation='vertical',
            size_hint=(1, 1),
            opacity=0,
            disabled=True
        )

        # Post detail scrollview
        post_scroll = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=False,
            do_scroll_y=True
        )

        self.post_content = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            padding=[dp(15), dp(15)],
            spacing=dp(15)
        )
        self.post_content.bind(
            minimum_height=self.post_content.setter('height'))

        post_scroll.add_widget(self.post_content)
        self.post_detail.add_widget(post_scroll)

        self.content_area.add_widget(self.post_detail)

        self.main_layout.add_widget(self.content_area)

        # Bottom navigation bar
        nav_bar = GridLayout(
            cols=4,
            size_hint=(1, 0.1),
            pos_hint={'bottom': 1}
        )

        with nav_bar.canvas.before:
            Color(rgba=get_color_from_hex(COLORS['primary'] + 'ff'))
            self.nav_rect = RoundedRectangle(
                size=nav_bar.size,
                pos=nav_bar.pos,
                radius=[dp(10), dp(10), 0, 0]  # Top corners rounded
            )
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

        # Map button (active)
        map_btn = BoxLayout(orientation='vertical')
        map_icon = MDFloatingActionButton(
            icon='map-marker',
            font_size=dp(24),
            md_bg_color=(1, 0.8, 0, 1),  # Highlight active button
            size_hint=(1, 0.7)
        )
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
        nav_bar.add_widget(news_btn)

        self.main_layout.add_widget(nav_bar)

        self.add_widget(self.main_layout)

    # Add to on_enter method
    def on_enter(self):
        """Called when screen is entered"""
        from kivy.app import App

        # Get current user_id from app
        app = App.get_running_app()
        self.user_id = app.get_user_id()

        print(f"Map screen entered with user_id: {self.user_id}")

        # Print specific debug info
        print(
            f"Map initial center: {self.map_view.lat}, {self.map_view.lon}, zoom: {self.map_view.zoom}")

        # Load map markers
        self.load_map_markers()

        # Reset to map view if showing post detail
        self.show_map()

    # Update the load_map_markers method

    def load_map_markers(self, *args):
        """Load all posts with location data and create markers"""
        if not self.db_helper:
            return

        try:
            # Clear existing markers
            self.map_view.clear_markers()

            # Get all submissions from database
            self.posts = self.db_helper.get_user_submissions(limit=100)
            print(f"Retrieved {len(self.posts)} posts for map")

            # Create marker for each post with valid coordinates
            markers_added = 0
            min_lat, max_lat = 90, -90
            min_lon, max_lon = 180, -180

            for post in self.posts:
                post_id, user_id, task_text, image_data, lat, lon, location_text, description, date, upvotes = post

                # Skip posts without coordinates
                if lat is None or lon is None:
                    continue

                try:
                    # Convert to float
                    lat_float = float(lat)
                    lon_float = float(lon)

                    # Track bounds for map centering
                    min_lat = min(min_lat, lat_float)
                    max_lat = max(max_lat, lat_float)
                    min_lon = min(min_lon, lon_float)
                    max_lon = max(max_lon, lon_float)

                    # Create marker - skip the preview popup and go directly to post view
                    marker = CustomMarker(
                        post_data=post,
                        lat=lat_float,
                        lon=lon_float,
                        on_select_callback=self.show_post_detail  # Direct to full post view
                    )

                    self.map_view.add_marker(marker)
                    markers_added += 1

                except Exception as e:
                    print(f"Error adding marker for post {post_id}: {e}")

            print(f"Added {markers_added} markers to map")

            # Center map if markers were added
            if markers_added > 0:
                # Calculate center of all markers
                center_lat = (min_lat + max_lat) / 2
                center_lon = (min_lon + max_lon) / 2

                # Determine appropriate zoom level based on bounds
                lat_span = max_lat - min_lat
                lon_span = max_lon - min_lon

                # Center map and adjust zoom
                self.map_view.center_on(center_lat, center_lon)

                # Adjust zoom based on the geographic spread
                if lat_span > 0 or lon_span > 0:
                    # This will zoom out more for widely dispersed markers
                    max_span = max(lat_span, lon_span)
                    # Adjust algorithm as needed
                    zoom = min(15, max(9, int(10 - max_span * 10)))
                    self.map_view.zoom = zoom

        except Exception as e:
            print(f"Error loading map markers: {e}")

    def show_post_preview(self, post_data):
        """Show a preview popup for a post when marker is clicked"""
        preview = PostPreviewPopup(
            post_data=post_data,
            on_view_full=self.show_post_detail
        )
        preview.open()

    def show_post_detail(self, post_data):
        """Display full post detail view"""
        self.current_post = post_data

        # Update title
        self.title_label.text = "Post Detail"

        # Clear existing content
        self.post_content.clear_widgets()

        # Unpack post data
        post_id, user_id, task_text, image_data, lat, lon, location_text, description, submission_date, upvotes = post_data

        # Get username from database
        user_profile = self.db_helper.get_user_profile(user_id)
        username = user_profile[2] if user_profile else f"User {user_id}"

        # Header with username and date
        header = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(50),
            spacing=dp(10)
        )

        # Username label
        username_label = MDLabel(
            text=username,
            theme_text_color="Custom",
            text_color=get_color_from_hex(COLORS['text'] + 'ff'),
            bold=True,
            size_hint=(0.6, 1),
            halign='left',
            valign='middle'
        )

        # Date label
        date_obj = datetime.strptime(submission_date, "%Y-%m-%d")
        formatted_date = date_obj.strftime("%b %d, %Y")
        date_label = MDLabel(
            text=formatted_date,
            theme_text_color="Custom",
            text_color=get_color_from_hex(COLORS['secondary_text'] + 'ff'),
            size_hint=(0.4, 1),
            halign='right',
            valign='middle'
        )

        header.add_widget(username_label)
        header.add_widget(date_label)

        self.post_content.add_widget(header)

        # Location if available
        if location_text:
            loc_box = BoxLayout(
                orientation='horizontal',
                size_hint=(1, None),
                height=dp(40)
            )

            loc_icon = MDIconButton(
                icon='map-marker',
                theme_text_color="Custom",
                text_color=get_color_from_hex(COLORS['primary'] + 'ff'),
                size_hint=(None, None),
                size=(dp(40), dp(40))
            )

            loc_label = MDLabel(
                text=location_text,
                theme_text_color="Custom",
                text_color=get_color_from_hex(COLORS['secondary_text'] + 'ff'),
                size_hint=(0.9, 1)
            )

            loc_box.add_widget(loc_icon)
            loc_box.add_widget(loc_label)
            self.post_content.add_widget(loc_box)

        # Task text
        task_label = MDLabel(
            text="Task:",
            theme_text_color="Custom",
            text_color=get_color_from_hex(COLORS['primary'] + 'ff'),
            bold=True,
            size_hint=(1, None),
            height=dp(30)
        )
        self.post_content.add_widget(task_label)

        task_text_label = MDLabel(
            text=task_text,
            theme_text_color="Custom",
            text_color=get_color_from_hex(COLORS['text'] + 'ff'),
            size_hint=(1, None),
            height=dp(80)
        )
        self.post_content.add_widget(task_text_label)

        # Post image
        if image_data:
            image_box = BoxLayout(
                orientation='vertical',
                size_hint=(1, None),
                height=dp(250),
                padding=[0, dp(10)]
            )

            # Save image to temp file
            temp_image = tempfile.NamedTemporaryFile(
                delete=False, suffix='.png')
            temp_image.write(image_data)
            temp_image.close()

            # Display image
            post_image = Image(
                source=temp_image.name,
                size_hint=(1, 1)
            )
            image_box.add_widget(post_image)
            self.post_content.add_widget(image_box)

        # Description heading
        desc_heading = MDLabel(
            text="Description:",
            theme_text_color="Custom",
            text_color=get_color_from_hex(COLORS['primary'] + 'ff'),
            bold=True,
            size_hint=(1, None),
            height=dp(30)
        )
        self.post_content.add_widget(desc_heading)

        # Description text
        desc_label = MDLabel(
            text=description,
            theme_text_color="Custom",
            text_color=get_color_from_hex(COLORS['text'] + 'ff'),
            size_hint=(1, None),
            height=dp(100)
        )
        desc_label.bind(texture_size=lambda instance, size: setattr(
            instance, 'height', max(dp(100), size[1])))
        self.post_content.add_widget(desc_label)

        # Back to map button
        back_to_map_btn = Button(
            text="Back to Map",
            background_color=get_color_from_hex(COLORS['button_blue'] + 'ff'),
            color=get_color_from_hex(COLORS['white'] + 'ff'),
            size_hint=(0.8, None),
            height=dp(50),
            pos_hint={'center_x': 0.5}
        )
        back_to_map_btn.bind(on_press=self.show_map)
        self.post_content.add_widget(back_to_map_btn)

        # Add spacing at bottom
        self.post_content.add_widget(
            BoxLayout(size_hint=(1, None), height=dp(20)))

        # Hide map, show post detail
        self.map_view.opacity = 0
        self.map_view.disabled = True
        self.post_detail.opacity = 1
        self.post_detail.disabled = False

        self.showing_map = False

    def show_map(self, *args):
        """Show the map view"""
        self.title_label.text = "Climate Action Map"

        # Hide post detail, show map
        self.map_view.opacity = 1
        self.map_view.disabled = False
        self.post_detail.opacity = 0
        self.post_detail.disabled = True

        self.showing_map = True

    def go_back(self, instance):
        """Handle back button press"""
        if not self.showing_map:
            # If showing post detail, go back to map
            self.show_map()
        else:
            # If showing map, go back to home
            self.manager.transition.direction = 'right'
            self.manager.current = 'home'

    # Navigation methods
    def go_to_home(self, instance):
        self.manager.transition.direction = 'right'
        self.manager.current = 'home'

    def go_to_social(self, instance):
        self.manager.transition.direction = 'right'
        self.manager.current = 'social'

    def go_to_news(self, instance):
        self.manager.transition.direction = 'left'
        self.manager.current = 'news'

    # Update rectangle methods
    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def _update_header_rect(self, instance, value):
        self.header_rect.pos = instance.pos
        self.header_rect.size = instance.size

    def _update_nav_rect(self, instance, value):
        self.nav_rect.pos = instance.pos
        self.nav_rect.size = instance.size
