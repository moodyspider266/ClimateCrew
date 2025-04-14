from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivymd.uix.button import MDFloatingActionButton, MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivy.clock import Clock
from kivy.app import App
from datetime import datetime
from plyer import filechooser
import os
from kivy.core.window import Window

# Color scheme based on your Figma design
COLORS = {
    'background': '#e3f8ee',
    'primary': '#446e49',
    'text': '#333333',
    'secondary_text': '#666666',
    'white': '#ffffff',
    'task_bg': '#446e49',
    'yellow': '#ffc107',
    'button_blue': '#2196F3',
    'error': '#f44336'
}


class SubmitTaskScreen(Screen):
    def __init__(self, db_helper=None, **kwargs):
        super(SubmitTaskScreen, self).__init__(**kwargs)
        self.name = 'submit_task'
        self.db_helper = db_helper
        self.user_id = None
        self.task_text = None
        self.task_points = 20
        self.image_data = None  # Store the selected image data
        self.latitude = None
        self.longitude = None

        main_layout = FloatLayout()
        with main_layout.canvas.before:
            Color(rgba=get_color_from_hex(COLORS['background'] + 'ff'))
            self.rect = Rectangle(size=main_layout.size, pos=main_layout.pos)
        main_layout.bind(size=self._update_rect, pos=self._update_rect)

        # Header with back button and title
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
            text="Submit Task",
            halign="center",
            theme_text_color="Custom",
            text_color=get_color_from_hex(COLORS['white'] + 'ff'),
            font_style="H6",
            size_hint=(0.8, 1),
            pos_hint={'center_y': 0.5}
        )
        header.add_widget(title_label)

        # Placeholder for right side of header
        placeholder = BoxLayout(size_hint=(0.1, 1))
        header.add_widget(placeholder)

        main_layout.add_widget(header)

        # Content area - scrollable for smaller screens
        scroll = ScrollView(
            size_hint=(1, 0.82),
            pos_hint={'top': 0.92}
        )

        content = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            padding=[dp(15), dp(15)],
            spacing=dp(20)
        )
        content.bind(minimum_height=content.setter('height'))

        # # Current task display
        # task_card = BoxLayout(
        #     orientation='vertical',
        #     size_hint=(1, None),
        #     height=dp(120),
        #     padding=[dp(10), dp(10)],
        #     spacing=dp(5)
        # )

        # with task_card.canvas.before:
        #     Color(rgba=get_color_from_hex(COLORS['task_bg'] + 'ff'))
        #     self.task_rect = RoundedRectangle(
        #         size=task_card.size,
        #         pos=task_card.pos,
        #         radius=[dp(10),]
        #     )
        # task_card.bind(size=self._update_task_rect, pos=self._update_task_rect)

        # task_card_label = MDLabel(
        #     text="Your Current Task:",
        #     theme_text_color="Custom",
        #     text_color=get_color_from_hex(COLORS['white'] + 'ff'),
        #     font_style="Subtitle1",
        #     bold=True,
        #     size_hint=(1, None),
        #     height=dp(30)
        # )
        # task_card.add_widget(task_card_label)

        # self.task_display = MDLabel(
        #     text="Task will appear here",
        #     theme_text_color="Custom",
        #     text_color=get_color_from_hex(COLORS['white'] + 'ff'),
        #     size_hint=(1, None),
        #     height=dp(80)
        # )
        # task_card.add_widget(self.task_display)

        # content.add_widget(task_card)

        # Image selection
        image_section = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(220),
            spacing=dp(10)
        )

        image_label = MDLabel(
            text="Add Photo Evidence:",
            theme_text_color="Custom",
            text_color=get_color_from_hex(COLORS['text'] + 'ff'),
            size_hint=(1, None),
            height=dp(30)
        )
        image_section.add_widget(image_label)

        image_container = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(180)
        )

        with image_container.canvas.before:
            Color(rgba=get_color_from_hex('#E0E0E0' + 'ff'))
            self.image_rect = RoundedRectangle(
                size=image_container.size,
                pos=image_container.pos,
                radius=[dp(8),]
            )
        image_container.bind(size=self._update_image_rect,
                             pos=self._update_image_rect)

        self.selected_image = Image(
            source='',
            size_hint=(1, 1),
            allow_stretch=True,
            keep_ratio=True
        )
        image_container.add_widget(self.selected_image)

        self.image_placeholder = MDLabel(
            text="Tap to select an image",
            theme_text_color="Custom",
            text_color=get_color_from_hex(COLORS['secondary_text'] + 'ff'),
            halign="center",
            valign="middle",
            size_hint=(1, 1),
            opacity=1
        )
        image_container.add_widget(self.image_placeholder)

        image_container.bind(on_touch_down=self.select_image)
        image_section.add_widget(image_container)

        content.add_widget(image_section)

        # Location Section
        location_section = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(150),
            spacing=dp(10)
        )

        location_label = MDLabel(
            text="Location:",
            theme_text_color="Custom",
            text_color=get_color_from_hex(COLORS['text'] + 'ff'),
            size_hint=(1, None),
            height=dp(30)
        )
        location_section.add_widget(location_label)

        # Location text input
        self.location_input = MDTextField(
            hint_text="Enter location name",
            helper_text="e.g., Central Park, New York",
            helper_text_mode="on_focus",
            size_hint=(1, None),
            height=dp(50)
        )
        location_section.add_widget(self.location_input)

        # Coordinates input layout
        coords_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(50),
            spacing=dp(10)
        )

        self.latitude_input = MDTextField(
            hint_text="Latitude",
            helper_text="e.g., 40.7128",
            helper_text_mode="on_focus",
            size_hint=(0.5, None),
            height=dp(50)
        )
        coords_layout.add_widget(self.latitude_input)

        self.longitude_input = MDTextField(
            hint_text="Longitude",
            helper_text="e.g., -74.0060",
            helper_text_mode="on_focus",
            size_hint=(0.5, None),
            height=dp(50)
        )
        coords_layout.add_widget(self.longitude_input)

        location_section.add_widget(coords_layout)

        content.add_widget(location_section)

        # Description input
        description_section = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(150),
            spacing=dp(10)
        )

        description_label = MDLabel(
            text="Description:",
            theme_text_color="Custom",
            text_color=get_color_from_hex(COLORS['text'] + 'ff'),
            size_hint=(1, None),
            height=dp(30)
        )
        description_section.add_widget(description_label)

        self.description_input = TextInput(
            hint_text="Tell us about your experience completing this task...",
            multiline=True,
            size_hint=(1, None),
            height=dp(100),
            padding=[dp(10), dp(10)],
            background_color=(0.95, 0.95, 0.95, 1)
        )
        description_section.add_widget(self.description_input)

        content.add_widget(description_section)

        # Date completion
        date_section = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(90),
            spacing=dp(10)
        )

        date_label = MDLabel(
            text="Date Completed:",
            theme_text_color="Custom",
            text_color=get_color_from_hex(COLORS['text'] + 'ff'),
            size_hint=(1, None),
            height=dp(30)
        )
        date_section.add_widget(date_label)

        # Current date by default
        current_date = datetime.now().strftime("%Y-%m-%d")
        self.date_input = MDTextField(
            text=current_date,
            hint_text="YYYY-MM-DD",
            helper_text="Date format: YYYY-MM-DD",
            helper_text_mode="on_focus",
            size_hint=(1, None),
            height=dp(50)
        )
        date_section.add_widget(self.date_input)

        content.add_widget(date_section)

        # Submit button
        self.status_label = Label(
            text="",
            color=(1, 0, 0, 1),
            size_hint=(1, None),
            height=dp(30),
            opacity=0
        )
        content.add_widget(self.status_label)

        submit_btn = Button(
            text="Submit",
            font_size=dp(18),
            background_color=get_color_from_hex(COLORS['button_blue'] + 'ff'),
            color=get_color_from_hex(COLORS['white'] + 'ff'),
            size_hint=(0.8, None),
            height=dp(50),
            pos_hint={'center_x': 0.5}
        )
        submit_btn.bind(on_press=self.submit_post)
        content.add_widget(submit_btn)

        # Add padding at the bottom for better spacing
        content.add_widget(BoxLayout(size_hint=(1, None), height=dp(20)))

        scroll.add_widget(content)
        main_layout.add_widget(scroll)

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

        main_layout.add_widget(nav_bar)

        self.add_widget(main_layout)

    def on_enter(self):
        """Called when screen is entered"""
        from kivy.app import App

        # Get current user_id from app
        app = App.get_running_app()
        self.user_id = app.get_user_id()

        print(f"Submit Task screen entered with user_id: {self.user_id}")

        self.reset_form()

        # Load current task
        if self.user_id and self.db_helper:
            try:
                task_data = self.db_helper.get_user_task(self.user_id)
                if task_data and task_data[0]:
                    self.task_text = task_data[0]
                    # self.task_display.text = self.task_text
            except Exception as e:
                print(f"Error loading task: {e}")

    def select_image(self, instance, touch):
        if instance.collide_point(*touch.pos):
            try:
                filechooser.open_file(on_selection=self.handle_selection,
                                      filters=[("Images", "*.png", "*.jpg", "*.jpeg")])
            except Exception as e:
                print(f"Error opening file chooser: {e}")
                self.show_status(f"Error: {str(e)}", 'error')

    def handle_selection(self, selection):
        if selection and len(selection) > 0:
            try:
                image_path = selection[0]

                # Set the image source for display
                self.selected_image.source = image_path

                # Hide the placeholder text
                self.image_placeholder.opacity = 0

                # Read the image data
                with open(image_path, 'rb') as f:
                    self.image_data = f.read()

                print(
                    f"Image selected: {image_path}, size: {len(self.image_data)} bytes")
            except Exception as e:
                print(f"Error loading image: {e}")
                self.show_status(f"Error loading image: {str(e)}", 'error')

    def submit_post(self, instance):
        """Submit the task post"""
        if not self.user_id or not self.db_helper:
            self.show_status(
                "Cannot submit: User ID or database not available", 'error')
            return

        # Validate required fields
        if not self.task_text:
            self.show_status("Cannot submit: No task is assigned", 'error')
            return

        if not self.image_data:
            self.show_status("Please select an image to continue", 'error')
            return

        location = self.location_input.text.strip()
        if not location:
            self.show_status("Please enter a location", 'error')
            return

        try:
            # Get latitude/longitude if provided
            lat = self.latitude_input.text.strip()
            lon = self.longitude_input.text.strip()

            if lat:
                self.latitude = float(lat)

            if lon:
                self.longitude = float(lon)

        except ValueError:
            self.show_status(
                "Invalid coordinates. Use decimal format (e.g., 40.7128)", 'error')
            return

        description = self.description_input.text.strip()
        if not description:
            self.show_status("Please enter a description", 'error')
            return

        date_text = self.date_input.text.strip()
        if not date_text:
            self.show_status("Please enter a valid date", 'error')
            return

        try:
            # Attempt to parse date to validate format
            submission_date = datetime.strptime(
                date_text, "%Y-%m-%d").strftime("%Y-%m-%d")

            # Submit to database
            success = self.db_helper.add_submission(
                user_id=self.user_id,
                task_text=self.task_text,
                image=self.image_data,
                latitude=self.latitude,
                longitude=self.longitude,
                location_text=location,
                description=description,
                submission_date=submission_date
            )

            if success:
                # Get current stats before update
                old_stats = self.db_helper.get_user_stats(self.user_id)
                if old_stats:
                    old_points, old_tasks = old_stats
                    print(
                        f"Before task completion: Points={old_points}, Tasks={old_tasks}")

                # Mark task as completed and award points
                if self.db_helper.complete_task(self.user_id, self.task_points):
                    # Get updated stats
                    new_stats = self.db_helper.get_user_stats(self.user_id)
                    if new_stats:
                        new_points, new_tasks = new_stats
                        points_earned = new_points - \
                            (old_points if old_stats else 0)

                        # Show success message with points earned
                        self.show_status(
                            f"Task completed! +{points_earned} points", 'success')
                        print(
                            f"After task completion: Points={new_points}, Tasks={new_tasks}")
                        print(f"Points earned: {points_earned}")
                    else:
                        self.show_status(
                            f"Task completed! +{self.task_points} points", 'success')

                    self.reset_form()
                    # Return to home after a short delay
                    Clock.schedule_once(self.return_to_home, 2)
                else:
                    self.show_status(
                        "Task submitted but couldn't update completion status", 'error')
            else:
                self.show_status("Failed to submit task", 'error')

        except ValueError:
            self.show_status("Invalid date format. Use YYYY-MM-DD", 'error')
        except Exception as e:
            print(f"Error submitting post: {e}")
            self.show_status(f"Error: {str(e)}", 'error')

    def show_status(self, message, status_type='info'):
        """Show status message with styling based on type"""
        self.status_label.text = message

        if status_type == 'error':
            self.status_label.color = get_color_from_hex(
                COLORS['error'] + 'ff')
        elif status_type == 'success':
            self.status_label.color = (0, 0.8, 0, 1)  # Green
        else:
            self.status_label.color = (0.3, 0.3, 0.3, 1)  # Gray for info

        self.status_label.opacity = 1

        # Auto-hide after 5 seconds unless it's an error
        if status_type != 'error':
            Clock.schedule_once(lambda dt: setattr(
                self.status_label, 'opacity', 0), 5)

    def reset_form(self):
        """Reset all input fields to their default state"""
        # Reset image selection
        self.selected_image.source = ''
        self.image_placeholder.opacity = 1
        self.image_data = None

        # Reset location fields
        self.location_input.text = ''
        self.latitude_input.text = ''
        self.longitude_input.text = ''
        self.latitude = None
        self.longitude = None

        # Reset description
        self.description_input.text = ''

        # Reset date to current date
        current_date = datetime.now().strftime("%Y-%m-%d")
        self.date_input.text = current_date

        print("Form has been reset")

    def return_to_home(self, dt):
        """Return to home screen"""
        self.manager.transition.direction = 'right'
        self.manager.current = 'home'

    # Navigation methods
    def go_back(self, instance):
        self.manager.transition.direction = 'right'
        self.manager.current = 'home'

    def go_to_home(self, instance):
        self.manager.transition.direction = 'right'
        self.manager.current = 'home'

    def go_to_map(self, instance):
        self.manager.transition.direction = 'left'
        self.manager.current = 'map'

    def go_to_social(self, instance):
        self.manager.transition.direction = 'left'
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

    def _update_task_rect(self, instance, value):
        self.task_rect.pos = instance.pos
        self.task_rect.size = instance.size

    def _update_image_rect(self, instance, value):
        self.image_rect.pos = instance.pos
        self.image_rect.size = instance.size

    def _update_nav_rect(self, instance, value):
        self.nav_rect.pos = instance.pos
        self.nav_rect.size = instance.size
