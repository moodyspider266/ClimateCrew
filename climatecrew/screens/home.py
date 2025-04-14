from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivymd.uix.button import MDFloatingActionButton, MDIconButton
from kivymd.uix.label import MDLabel
import requests
from kivy.clock import Clock
from kivy.network.urlrequest import UrlRequest
import json

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
    def __init__(self, db_helper, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)
        self.name = 'home'
        self.db_helper = db_helper
        self.user_id = None

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
            self.header_rect = RoundedRectangle(
                size=header.size,
                pos=header.pos,
                radius=[0, 0, 0, dp(10)]  # Bottom corners rounded
            )
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

        # Content area
        content = BoxLayout(
            orientation='vertical',
            size_hint=(1, 0.82),
            pos_hint={'top': 0.92},
            padding=[dp(10), dp(5)]
        )

        # Leaderboard position
        leaderboard_btn = Button(
            text='',
            font_size=dp(18),
            background_color=get_color_from_hex('#FFD54F' + 'ff'),
            color=get_color_from_hex(COLORS['white'] + 'ff'),
            size_hint=(1, 0.08),
            pos_hint={'center_x': 0.5}
        )
        self.leaderboard_btn = leaderboard_btn
        leaderboard_btn.bind(on_press=self.go_to_leaderboard)
        content.add_widget(leaderboard_btn)

        # self.debug_user_id = Label(
        #     text=f"UserID: {self.user_id}",
        #     size_hint=(None, None),
        #     size=(dp(200), dp(30)),
        #     pos_hint={'top': 0.98, 'right': 0.99},
        #     color=(1, 0, 0, 1),  # Red text
        #     opacity=1  # Initially hidden
        # )
        # main_layout.add_widget(self.debug_user_id)

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

        # Add a status label for task errors
        self.task_status = Label(
            text="",
            color=(1, 0, 0, 1),
            size_hint=(1, 0.05),
            opacity=0,
            pos_hint={'center_x': 0.5}
        )
        content.add_widget(self.task_status)

        # Task card
        task_card = FloatLayout(
            size_hint=(1, 0.5)
        )

        with task_card.canvas.before:
            Color(rgba=get_color_from_hex(COLORS['task_bg'] + 'ff'))
            self.task_rect = RoundedRectangle(
                size=task_card.size,
                pos=task_card.pos,
                radius=[dp(10),]  # Add rounded corners
            )
        task_card.bind(size=self._update_task_rect, pos=self._update_task_rect)

        # Create scrollview for task text (to handle overflow)
        task_scroll = ScrollView(
            size_hint=(0.9, 0.7),  # Increased height
            pos_hint={'center_x': 0.5, 'top': 0.95},
            do_scroll_x=False,  # Only vertical scrolling
            do_scroll_y=True,
            bar_width=dp(5),
            bar_color=[0.8, 0.8, 0.8, 0.5],  # Light gray scrollbar
            bar_inactive_color=[0.8, 0.8, 0.8, 0.2],
            effect_cls='ScrollEffect'  # Smooth scrolling
        )

        # Task description
        task = MDLabel(
            text='Your personalized task will appear here.',
            font_size=dp(16),
            color=get_color_from_hex(COLORS['white'] + 'ff'),
            bold=True,
            halign='left',
            valign='top',
            size_hint=(1, None),
            text_size=(None, None)  # Set width constraint for text wrapping
        )
        self.task = task

        def update_text_size(instance, value):
            task.text_size = (instance.width * 0.9, None)
            task.texture_update()
            # After texture update, adjust height based on texture size
            task.height = max(task.texture_size[1], task_scroll.height)

        task_scroll.bind(width=update_text_size)
        task_scroll.add_widget(task)
        task_card.add_widget(task_scroll)

        # Impact points
        points_btn = Button(
            text='+20 Impact Points',
            font_size=dp(16),
            background_color=get_color_from_hex('#FFD54F' + 'ff'),
            color=get_color_from_hex(COLORS['white'] + 'ff'),
            size_hint=(0.5, 0.15),
            pos_hint={'center_x': 0.5, 'y': 0.05}
        )
        task_card.add_widget(points_btn)
        self.points_btn = points_btn

        content.add_widget(task_card)

        # Task buttons
        task_buttons = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 0.1),
            spacing=dp(10),
            padding=[dp(0), dp(10)]
        )

        # Custom button class for rounded corners
        class RoundedButton(Button):
            def __init__(self, **kwargs):
                super(RoundedButton, self).__init__(**kwargs)
                self.background_normal = ''
                self.background_down = ''
                with self.canvas.before:
                    Color(rgba=self.background_color)
                    self.rect = RoundedRectangle(
                        size=self.size,
                        pos=self.pos,
                        radius=[dp(8),]
                    )
                self.bind(pos=self.update_rect, size=self.update_rect,
                          background_color=self.update_rect_color)

            def update_rect(self, *args):
                self.rect.pos = self.pos
                self.rect.size = self.size

            def update_rect_color(self, *args):
                self.canvas.before.children[0].rgba = self.background_color

        change_task_btn = RoundedButton(
            text='Change Task',
            font_size=dp(16),
            background_color=get_color_from_hex(
                COLORS['secondary_text'] + 'ff'),
            color=get_color_from_hex(COLORS['white'] + 'ff'),  # White text
            size_hint=(0.5, 1)
        )
        change_task_btn.bind(on_press=self.get_new_task)
        task_buttons.add_widget(change_task_btn)

        submit_task_btn = RoundedButton(
            text='Submit Task',
            font_size=dp(16),
            background_color=get_color_from_hex(COLORS['button_blue'] + 'ff'),
            color=get_color_from_hex(COLORS['white'] + 'ff'),  # White text
            size_hint=(0.5, 1)
        )
        submit_task_btn.bind(on_press=self.submit_task)
        task_buttons.add_widget(submit_task_btn)

        content.add_widget(task_buttons)
        self.task_status = Label(
            text="",
            color=(1, 0, 0, 1),
            size_hint=(1, 0.1),
            opacity=0
        )
        content.add_widget(self.task_status)

        main_layout.add_widget(content)

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

    # Add this method to your HomeScreen class
    def on_enter(self):
        """Called when screen is entered - updates user ID"""
        from kivy.app import App

        # Get current user_id from app
        app = App.get_running_app()
        self.user_id = app.get_user_id()

        # Update debug label
        if hasattr(self, 'debug_user_id'):
            self.debug_user_id.text = f"UserID: {self.user_id}"

        print(f"Home screen entered with user_id: {self.user_id}")

        if self.user_id:
            self.load_user_task()

        # Update leaderboard/points display
        if self.user_id and self.db_helper:
            try:
                points, tasks_completed = self.db_helper.get_user_stats(
                    self.user_id)
                self.leaderboard_btn.text = f"Points: {points} | Tasks Completed: {tasks_completed}"
            except Exception as e:
                print(f"Error updating points display: {e}")

    def load_user_task(self):
        """Load user's current task from database"""
        if not self.user_id or not self.db_helper:
            self.show_task_status("User ID or database not available")
            return

        try:
            # Get task data from database
            task_data = self.db_helper.get_user_task(self.user_id)

            if task_data and task_data[0]:
                # Update task text
                self.task.text = task_data[0]

                # Update points button
                points = task_data[1]
                self.points_btn.text = "+20 Impact Points"

                # Force update of text size/layout
                self.task.texture_update()
                self.task.height = max(
                    self.task.texture_size[1], self.task.parent.height)
            else:
                self.task.text = "Could not load task. Try generating a new one."
        except Exception as e:
            print(f"Error loading user task: {e}")
            self.show_task_status(f"Error: {str(e)}")

    def get_task_for_user(self):
        """Generate a new task and save it to database"""
        if not self.user_id:
            self.show_task_status("No user ID available")
            return

        # Show loading status
        self.task.text = "Generating a new task for you..."

        # API endpoint
        url = f"http://localhost:5000/api/generate-task?user_id={self.user_id}"

        # Make API request
        UrlRequest(url, on_success=self.process_new_task_response,
                   on_error=self.handle_task_error,
                   on_failure=self.handle_task_error)

    def process_new_task_response(self, request, result):
        """Process the task API response and save to database"""
        try:
            # Get task and points from response
            task_text = result.get('task', "No task available")
            impact_points = result.get('impact_points', 20)

            # Update task in database
            if self.db_helper.update_user_task(self.user_id, task_text, impact_points):
                # Update UI
                self.task.text = task_text
                self.points_btn.text = f"+{impact_points} Impact Points"

                # Force update of text size/layout
                self.task.texture_update()
                self.task.height = self.task.texture_size[1]

                self.show_task_status("New task generated!")
            else:
                self.show_task_status("Failed to save new task")

        except Exception as e:
            print(f"Error processing task response: {e}")
            self.show_task_status(f"Error: {str(e)}")

    def get_new_task(self, instance):
        """Get a new task when Change Task button is clicked"""
        self.get_task_for_user()

    def handle_task_error(self, request, error):
        """Handle API errors"""
        print(f"Task API error: {error}")
        self.task.text = "Could not load personalized task. Try again later."
        self.show_task_status("Connection error")

    def show_task_status(self, message):
        """Show status message with auto-hide"""
        self.task_status.text = message
        self.task_status.opacity = 1
        Clock.schedule_once(lambda dt: setattr(
            self.task_status, 'opacity', 0), 3)

    def submit_task(self, instance):
        """Submit the current task as completed"""
        if not self.user_id or not self.db_helper:
            self.show_task_status(
                "Cannot submit task: User ID or database not available")
            return

        try:
            # Always award 20 points for a task
            task_points = 20

            # Update user's stats in database
            if self.db_helper.complete_task(self.user_id, task_points):
                # Show success message
                self.show_task_status(f"Task completed! +{task_points} points")

                # Update leaderboard button with new stats
                stats = self.db_helper.get_user_stats(self.user_id)
                if stats:
                    points, tasks_completed = stats
                    self.leaderboard_btn.text = f"🏆 Points: {points} | Tasks: {tasks_completed}"

                # Generate a new task automatically
                Clock.schedule_once(lambda dt: self.get_new_task(None), 1.5)
            else:
                self.show_task_status("Failed to submit task")

        except Exception as e:
            print(f"Error submitting task: {e}")
            self.show_task_status(f"Error: {str(e)}")

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
