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
from kivy.graphics import Color, Rectangle, RoundedRectangle, Ellipse
from kivy.graphics.instructions import InstructionGroup
from kivymd.uix.button import MDFloatingActionButton, MDIconButton
from kivymd.uix.label import MDLabel
from kivy.uix.behaviors import ButtonBehavior
from kivy.clock import Clock
from kivy.app import App
from kivy.core.window import Window
import io
import tempfile
import os
from datetime import datetime

# Color scheme based on your app
COLORS = {
    'background': '#e3f8ee',
    'primary': '#446e49',
    'text': '#333333',
    'secondary_text': '#666666',
    'white': '#ffffff',
    'task_bg': '#446e49',
    'yellow': '#ffc107',
    'button_blue': '#2196F3',
    'error': '#f44336',
    'upvote': '#4CAF50'
}


class CircularImage(ButtonBehavior, BoxLayout):
    """Custom class for circular profile images with click behavior"""

    def __init__(self, source=None, size_hint=(None, None), size=(dp(40), dp(40)), **kwargs):
        super(CircularImage, self).__init__(
            size_hint=size_hint, size=size, **kwargs)
        self.source = source
        self.size_hint = size_hint
        self.size = size

        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.mask = Ellipse(size=self.size, pos=self.pos)

        self.image = Image(source=source, size_hint=(1, 1))
        self.add_widget(self.image)

        self.bind(pos=self.update_mask, size=self.update_mask)

    def update_mask(self, *args):
        self.mask.size = self.size
        self.mask.pos = self.pos

    def set_source(self, source):
        self.image.source = source


class UpvoteButton(ButtonBehavior, BoxLayout):
    """Custom upvote button with count display"""

    def __init__(self, count=0, callback=None, submission_id=None, **kwargs):
        super(UpvoteButton, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint = (None, None)
        self.size = (dp(100), dp(40))
        self.padding = [dp(5), dp(5)]
        self.count = count
        self.callback = callback
        self.submission_id = submission_id

        # Icon button
        self.icon_btn = MDIconButton(
            icon='thumb-up-outline',
            theme_text_color="Custom",
            text_color=get_color_from_hex(COLORS['upvote'] + 'ff'),
            size_hint=(None, None),
            size=(dp(40), dp(40)),
            pos_hint={'center_y': 0.5}
        )

        # Count label
        self.count_label = Label(
            text=str(count),
            color=get_color_from_hex(COLORS['text'] + 'ff'),
            size_hint=(None, None),
            size=(dp(50), dp(40)),
            halign='left',
            valign='middle'
        )

        self.add_widget(self.icon_btn)
        self.add_widget(self.count_label)

        self.icon_btn.bind(on_press=self.on_upvote)

    def on_upvote(self, instance):
        """Handle upvote button press"""
        if self.callback and self.submission_id:
            new_count = self.callback(self.submission_id)
            if new_count:
                self.count = new_count
                self.count_label.text = str(new_count)
                self.icon_btn.icon = 'thumb-up'  # Change to filled icon

    def update_count(self, count):
        """Update the displayed count"""
        self.count = count
        self.count_label.text = str(count)


# Update the PostCard class with better spacing and alignment
class PostCard(BoxLayout):
    """A card displaying a user's post"""

    def __init__(self, post_data, db_helper, on_upvote_callback, **kwargs):
        super(PostCard, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint = (1, None)
        self.height = dp(600)  # Will be adjusted based on content
        self.padding = [dp(15), dp(15)]  # Increased padding
        self.spacing = dp(15)  # Increased spacing between all elements
        self.post_data = post_data
        self.db_helper = db_helper

        # Unpack post data
        post_id, user_id, task_text, image_data, latitude, longitude, location_text, description, submission_date, upvotes = post_data

        # Get username from database
        user_profile = db_helper.get_user_profile(user_id)
        username = user_profile[2] if user_profile else f"User {user_id}"

        # Card background with larger border radius
        with self.canvas.before:
            Color(rgba=get_color_from_hex(COLORS['white'] + 'ff'))
            self.card_bg = RoundedRectangle(
                size=self.size,
                pos=self.pos,
                radius=[dp(15),]  # Increased radius for softer corners
            )
        self.bind(size=self.update_card_bg, pos=self.update_card_bg)

        # Header with profile pic, username, and date
        header = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(50),
            spacing=dp(10),
            padding=[0, dp(5)]  # Add some vertical padding
        )

        # Load profile image from database if available
        profile_image_data = None
        if user_profile and len(user_profile) > 8:
            profile_image_data = user_profile[8]

        # Create profile image
        self.profile_pic = CircularImage(size=(dp(40), dp(40)))

        # Set default or actual profile image
        if profile_image_data:
            # Save to temp file
            temp_profile = tempfile.NamedTemporaryFile(
                delete=False, suffix='.png')
            temp_profile.write(profile_image_data)
            temp_profile.close()
            self.profile_pic.set_source(temp_profile.name)

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
            size_hint=(0.3, 1),
            halign='right',
            valign='middle'
        )

        header.add_widget(self.profile_pic)
        header.add_widget(username_label)
        header.add_widget(date_label)

        self.add_widget(header)

        # Location label with spacing before
        if location_text:
            location_layout = BoxLayout(
                orientation='horizontal',
                size_hint=(1, None),
                height=dp(30),
                padding=[dp(5), 0]  # Add horizontal padding
            )

            location_icon = MDIconButton(
                icon='map-marker',
                theme_text_color="Custom",
                text_color=get_color_from_hex(COLORS['primary'] + 'ff'),
                size_hint=(None, 1),
                width=dp(30),
                pos_hint={'center_y': 0.5}
            )

            location_label = MDLabel(
                text=location_text,
                theme_text_color="Custom",
                text_color=get_color_from_hex(COLORS['secondary_text'] + 'ff'),
                size_hint=(0.9, 1),
                halign='left',
                valign='middle'
            )

            location_layout.add_widget(location_icon)
            location_layout.add_widget(location_label)
            self.add_widget(location_layout)

        # Task text (above image)
        task_label = MDLabel(
            text=f"Task: {task_text[:80] + ('...' if len(task_text) > 80 else '')}",
            theme_text_color="Custom",
            text_color=get_color_from_hex(COLORS['primary'] + 'ff'),
            size_hint=(1, None),
            height=dp(30),
            halign='left',
            valign='middle',
            padding=[dp(5), 0]  # Add some padding
        )
        self.add_widget(task_label)

        # Post image with container for better spacing
        image_container = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(270),  # Increased height
            padding=[0, dp(10)]  # Add vertical padding
        )

        self.post_image = Image(
            size_hint=(1, 1),
            allow_stretch=True,
            keep_ratio=True
        )

        # Save image data to temp file and load
        if image_data:
            temp_image = tempfile.NamedTemporaryFile(
                delete=False, suffix='.png')
            temp_image.write(image_data)
            temp_image.close()
            self.post_image.source = temp_image.name

        image_container.add_widget(self.post_image)
        self.add_widget(image_container)

        # Upvote button in its own container
        upvote_container = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(50),
            padding=[dp(5), dp(5)]
        )

        # Upvote button
        self.upvote_btn = UpvoteButton(
            count=upvotes,
            callback=on_upvote_callback,
            submission_id=post_id
        )

        upvote_container.add_widget(self.upvote_btn)

        # Add a spacer to push upvote button to the left
        spacer = BoxLayout(size_hint=(1, 1))
        upvote_container.add_widget(spacer)

        self.add_widget(upvote_container)

        # Description text with better formatting
        description_heading = MDLabel(
            text="Description:",
            theme_text_color="Custom",
            text_color=get_color_from_hex(COLORS['primary'] + 'ff'),
            bold=True,
            size_hint=(1, None),
            height=dp(30),
            halign='left'
        )
        self.add_widget(description_heading)

        description_layout = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(100),  # Will be adjusted based on content
            padding=[dp(5), 0]  # Add horizontal padding
        )

        description_scroll = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=dp(5),
            bar_color=[0.7, 0.7, 0.7, 0.9],
            bar_inactive_color=[0.7, 0.7, 0.7, 0.2]
        )

        self.description_label = MDLabel(
            text=description,
            theme_text_color="Custom",
            text_color=get_color_from_hex(COLORS['text'] + 'ff'),
            size_hint=(1, None),
            halign='left',
            valign='top',
            text_size=(Window.width - dp(50), None)  # Account for padding
        )
        self.description_label.bind(
            texture_size=self.update_description_height)

        description_scroll.add_widget(self.description_label)
        description_layout.add_widget(description_scroll)

        self.add_widget(description_layout)

        # Adjust overall card height
        Clock.schedule_once(self.adjust_height, 0.1)

    # Add these methods to the PostCard class
    def update_card_bg(self, instance, value):
        """Update card background on size/pos change"""
        self.card_bg.size = self.size
        self.card_bg.pos = self.pos

    def update_description_height(self, instance, value):
        """Update height based on description text size"""
        instance.height = value[1]  # Set height to texture height

    def adjust_height(self, dt):
        """Adjust overall card height based on content"""
        try:
            # Calculate content height
            content_height = sum(c.height for c in self.children)
            # Add spacing
            content_height += self.spacing * (len(self.children) - 1)
            # Add padding
            content_height += self.padding[1] * 2
            # Set card height with a small margin
            self.height = content_height + dp(10)

            # Ensure parent container updates its size if needed
            if hasattr(self.parent, 'height') and self.parent.height != self.height:
                self.parent.height = max(self.parent.height, self.height)
        except Exception as e:
            print(f"Error adjusting card height: {e}")


class SocialScreen(Screen):
    def __init__(self, db_helper=None, **kwargs):
        super(SocialScreen, self).__init__(**kwargs)
        self.name = 'social'
        self.db_helper = db_helper
        self.user_id = None
        self.current_index = 0
        self.posts = []
        self.showing_user_posts_only = False

        main_layout = FloatLayout()
        with main_layout.canvas.before:
            Color(rgba=get_color_from_hex(COLORS['background'] + 'ff'))
            self.rect = Rectangle(size=main_layout.size, pos=main_layout.pos)
        main_layout.bind(size=self._update_rect, pos=self._update_rect)

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
        title_label = MDLabel(
            text="Climate Community",
            halign="center",
            theme_text_color="Custom",
            text_color=get_color_from_hex(COLORS['white'] + 'ff'),
            font_style="H6",
            size_hint=(0.8, 1),
            pos_hint={'center_y': 0.5}
        )
        header.add_widget(title_label)

        # Refresh button
        refresh_btn = MDIconButton(
            icon='refresh',
            pos_hint={'center_y': 0.5},
            theme_text_color="Custom",
            text_color=get_color_from_hex(COLORS['white'] + 'ff'),
            size_hint=(0.1, 1)
        )
        refresh_btn.bind(on_press=self.refresh_posts)
        header.add_widget(refresh_btn)

        main_layout.add_widget(header)

        # Content area
        content_area = FloatLayout(
            size_hint=(1, 0.82),
            pos_hint={'top': 0.92}
        )

        # Filter toggle button
        self.filter_btn = Button(
            text="Show My Posts Only",
            background_color=get_color_from_hex('#FFD54F' + 'ff'),
            color=get_color_from_hex(COLORS['text'] + 'ff'),
            size_hint=(0.8, 0.06),
            pos_hint={'center_x': 0.5, 'top': 1}
        )
        self.filter_btn.bind(on_press=self.toggle_filter)
        content_area.add_widget(self.filter_btn)

        self.post_scroll = ScrollView(
            # Reduced height to make room for navigation buttons
            size_hint=(1, 0.78),
            pos_hint={'center_x': 0.5, 'top': 0.93},
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=dp(10),
            bar_color=[0.7, 0.7, 0.7, 0.9],
            bar_inactive_color=[0.7, 0.7, 0.7, 0.2],
            scroll_type=['bars', 'content']
        )

        # Create a container for the posts inside the scroll view
        self.post_container = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),  # Height will be set dynamically
            padding=[dp(10), dp(10)]
        )
        # Ensure the container expands to fit its children
        self.post_container.bind(
            minimum_height=self.post_container.setter('height'))

        self.post_scroll.add_widget(self.post_container)
        content_area.add_widget(self.post_scroll)

        # Navigation buttons
        nav_buttons = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 0.09),
            pos_hint={'center_x': 0.5, 'y': 0},
            spacing=dp(20),
            padding=[dp(20), dp(5)]
        )

        self.prev_btn = Button(
            text="Previous",
            background_color=get_color_from_hex(COLORS['primary'] + 'ff'),
            color=get_color_from_hex(COLORS['white'] + 'ff'),
            size_hint=(0.5, 1),
            disabled=True
        )
        self.prev_btn.bind(on_press=self.show_previous_post)

        self.next_btn = Button(
            text="Next",
            background_color=get_color_from_hex(COLORS['primary'] + 'ff'),
            color=get_color_from_hex(COLORS['white'] + 'ff'),
            size_hint=(0.5, 1),
            disabled=True
        )
        self.next_btn.bind(on_press=self.show_next_post)

        nav_buttons.add_widget(self.prev_btn)
        nav_buttons.add_widget(self.next_btn)
        content_area.add_widget(nav_buttons)

        # Status label
        self.status_label = Label(
            text="",
            color=(1, 0, 0, 1),
            size_hint=(1, 0.1),
            pos_hint={'center_x': 0.5, 'y': 0.45},
            opacity=0
        )
        content_area.add_widget(self.status_label)

        main_layout.add_widget(content_area)

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

        # Social button (active)
        social_btn = BoxLayout(orientation='vertical')
        social_icon = MDFloatingActionButton(
            icon='account-group',
            font_size=dp(24),
            md_bg_color=(1, 0.8, 0, 1),  # Highlight active button
            size_hint=(1, 0.7)
        )
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

        main_layout.add_widget(nav_bar)

        self.add_widget(main_layout)

    def on_enter(self):
        """Called when screen is entered"""
        from kivy.app import App

        # Get current user_id from app
        app = App.get_running_app()
        self.user_id = app.get_user_id()

        print(f"Social screen entered with user_id: {self.user_id}")

        # Load posts
        self.load_posts()

    def load_posts(self):
        """Load posts from database"""
        if not self.db_helper:
            self.show_status("Database not available")
            return

        try:
            # Clear current posts
            self.posts = []

            # Get submissions based on filter setting
            if self.showing_user_posts_only and self.user_id:
                self.posts = self.db_helper.get_user_submissions(self.user_id)
            else:
                self.posts = self.db_helper.get_user_submissions()

            # Update filter button text
            self.filter_btn.text = "Show All Posts" if self.showing_user_posts_only else "Show My Posts Only"

            if not self.posts:
                self.show_status("No posts available")
                self.prev_btn.disabled = True
                self.next_btn.disabled = True
                self.post_container.clear_widgets()
                return

            # Reset to first post
            self.current_index = 0

            # Show first post
            self.display_current_post()

            # Update navigation buttons
            self.update_nav_buttons()

        except Exception as e:
            print(f"Error loading posts: {e}")
            self.show_status(f"Error: {str(e)}")

    def display_current_post(self):
        """Display the current post"""
        if not self.posts or self.current_index >= len(self.posts):
            self.show_status("No posts to display")
            return

        # Clear container
        self.post_container.clear_widgets()

        # Create post card for current post
        post_card = PostCard(
            post_data=self.posts[self.current_index],
            db_helper=self.db_helper,
            on_upvote_callback=self.handle_upvote
        )

        # Add to container
        # Update the display_current_post method
        self.post_container.add_widget(post_card)

    def display_current_post(self):
        """Display the current post"""
        if not self.posts or self.current_index >= len(self.posts):
            self.show_status("No posts to display")
            return

        # Clear container
        self.post_container.clear_widgets()

        try:
            # Create post card for current post
            post_card = PostCard(
                post_data=self.posts[self.current_index],
                db_helper=self.db_helper,
                on_upvote_callback=self.handle_upvote
            )

            # Add to container
            self.post_container.add_widget(post_card)

            # Reset scroll position to top
            Clock.schedule_once(lambda dt: setattr(
                self.post_scroll, 'scroll_y', 1), 0.1)

        except Exception as e:
            print(f"Error displaying post: {e}")
            self.show_status("Error displaying post")

    def show_next_post(self, instance):
        """Show the next post"""
        if self.current_index < len(self.posts) - 1:
            self.current_index += 1
            self.display_current_post()
            self.update_nav_buttons()

    def show_previous_post(self, instance):
        """Show the previous post"""
        if self.current_index > 0:
            self.current_index -= 1
            self.display_current_post()
            self.update_nav_buttons()

    def update_nav_buttons(self):
        """Update navigation button states"""
        self.prev_btn.disabled = self.current_index == 0
        self.next_btn.disabled = self.current_index >= len(self.posts) - 1

    def toggle_filter(self, instance):
        """Toggle between showing all posts and only user's posts"""
        self.showing_user_posts_only = not self.showing_user_posts_only
        self.load_posts()

    def handle_upvote(self, submission_id):
        """Handle upvoting a post"""
        if not self.db_helper:
            self.show_status("Database not available")
            return None

        try:
            # Update upvote in database
            new_count = self.db_helper.upvote_submission(submission_id)

            # Also update in local data
            for i, post in enumerate(self.posts):
                if post[0] == submission_id:  # post[0] is the post_id
                    # Create a new tuple with updated upvote count
                    post_list = list(post)
                    post_list[9] = new_count  # post[9] is the upvotes count
                    self.posts[i] = tuple(post_list)

            return new_count
        except Exception as e:
            print(f"Error upvoting post: {e}")
            self.show_status(f"Error upvoting: {str(e)}")
            return None

    def refresh_posts(self, instance):
        """Refresh posts from database"""
        self.load_posts()

    def show_status(self, message):
        """Show status message with auto-hide"""
        self.status_label.text = message
        self.status_label.opacity = 1
        Clock.schedule_once(lambda dt: setattr(
            self.status_label, 'opacity', 0), 3)

    # Navigation methods
    def go_back(self, instance):
        self.manager.transition.direction = 'right'
        self.manager.current = 'home'

    def go_to_home(self, instance):
        self.manager.transition.direction = 'right'
        self.manager.current = 'home'

    def go_to_map(self, instance):
        self.manager.transition.direction = 'right'
        self.manager.current = 'map'

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
