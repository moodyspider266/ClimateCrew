from kivy.uix.screenmanager import Screen, SlideTransition
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
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from kivy.core.window import Window
from kivymd.uix.button import MDFloatingActionButton, MDIconButton, MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineAvatarListItem
from kivymd.uix.filemanager import MDFileManager
from kivy.uix.camera import Camera
import io
import os
import base64
from PIL import Image as PILImage
import threading
import traceback

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


class ProfileScreen(Screen):
    def __init__(self, db_helper=None, **kwargs):  # Made db_helper optional
        super(ProfileScreen, self).__init__(**kwargs)
        self.name = 'profile'
        self.db_helper = db_helper
        self.user_id = None
        self.profile_image_data = None
        self.camera = None
        self.file_manager = None

        main_layout = FloatLayout()
        with main_layout.canvas.before:
            Color(rgba=get_color_from_hex(COLORS['background'] + 'ff'))
            self.rect = Rectangle(size=main_layout.size, pos=main_layout.pos)
        main_layout.bind(size=self._update_rect, pos=self._update_rect)

        # Header with back button
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

        # Back button
        back_btn = MDIconButton(
            icon='arrow-left',
            icon_size=dp(24),
            theme_text_color="Custom",
            text_color=get_color_from_hex(COLORS['white'] + 'ff'),
            size_hint=(0.1, 1)
        )
        back_btn.bind(on_press=self.go_back)
        header.add_widget(back_btn)

        # Title in the middle
        title_label = MDLabel(
            text="My Profile",
            halign="center",
            font_style="H6",
            theme_text_color="Custom",
            text_color=get_color_from_hex(COLORS['white'] + 'ff'),
            size_hint=(0.8, 1)
        )
        header.add_widget(title_label)

        # Placeholder for right side of header
        placeholder = BoxLayout(size_hint=(0.1, 1))
        header.add_widget(placeholder)

        main_layout.add_widget(header)

        # Scrollable content
        scroll = ScrollView(
            size_hint=(1, 0.75),
            pos_hint={'top': 0.88}
        )

        # Content layout
        content_layout = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(900),  # Increased height for all content
            spacing=dp(15),
            padding=[dp(20), dp(20)]
        )

        # Profile image section
        image_layout = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(220),
            spacing=dp(10)
        )

        # Profile image header
        profile_img_label = MDLabel(
            text="Profile Photo",
            halign="center",
            theme_text_color="Custom",
            text_color=get_color_from_hex(COLORS['primary'] + 'ff'),
            font_style="Subtitle1",
            size_hint=(1, None),
            height=dp(30)
        )
        image_layout.add_widget(profile_img_label)

        # Profile image
        try:
            # Use a default image that's more likely to exist
            default_img_path = 'atlas://data/images/defaulttheme/user'
            self.profile_image = Image(
                source=default_img_path,
                size_hint=(None, None),
                size=(dp(150), dp(150)),
                pos_hint={'center_x': 0.5}
            )
        except Exception as e:
            print(f"Error loading profile image: {e}")
            self.profile_image = Image(
                size_hint=(None, None),
                size=(dp(150), dp(150)),
                pos_hint={'center_x': 0.5}
            )

        image_layout.add_widget(self.profile_image)

        # Image buttons
        image_buttons = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(50),
            spacing=dp(20),
            pos_hint={'center_x': 0.5}
        )

        take_photo_btn = Button(
            text="Take Photo",
            background_color=get_color_from_hex(COLORS['primary'] + 'ff'),
            color=get_color_from_hex(COLORS['white'] + 'ff'),
            size_hint=(0.4, 1)
        )
        take_photo_btn.bind(on_press=self.open_camera)
        image_buttons.add_widget(take_photo_btn)

        choose_photo_btn = Button(
            text="Choose Photo",
            background_color=get_color_from_hex(COLORS['primary'] + 'ff'),
            color=get_color_from_hex(COLORS['white'] + 'ff'),
            size_hint=(0.4, 1)
        )
        choose_photo_btn.bind(on_press=self.open_file_manager)
        image_buttons.add_widget(choose_photo_btn)

        image_layout.add_widget(image_buttons)
        content_layout.add_widget(image_layout)

        # Read-only section header
        readonly_header = MDLabel(
            text="ACCOUNT INFORMATION (READ ONLY)",
            halign="left",
            theme_text_color="Custom",
            text_color=get_color_from_hex(COLORS['primary'] + 'ff'),
            font_style="Subtitle1",
            size_hint=(1, None),
            height=dp(30)
        )
        content_layout.add_widget(readonly_header)

        # Form fields - Read-Only fields
        self.readonly_fields = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(200),
            spacing=dp(10)
        )

        # User ID - Hidden field
        self.user_id_label = Label(
            text="User ID: ",
            color=get_color_from_hex(COLORS['text'] + 'ff'),
            halign='left',
            valign='middle',
            size_hint=(1, None),
            height=dp(0),  # Hide this field
            opacity=0
        )
        self.readonly_fields.add_widget(self.user_id_label)

        # Full name
        full_name_layout = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(60)
        )
        full_name_label = MDLabel(
            text="Full Name",
            theme_text_color="Custom",
            text_color=get_color_from_hex(COLORS['secondary_text'] + 'ff'),
            halign='left',
            size_hint=(1, None),
            height=dp(20)
        )
        self.full_name_field = TextInput(
            text="",
            multiline=False,
            readonly=True,
            background_color=get_color_from_hex(COLORS['white'] + 'ee'),
            foreground_color=get_color_from_hex(COLORS['text'] + 'ff'),
            size_hint=(1, None),
            height=dp(40)
        )
        full_name_layout.add_widget(full_name_label)
        full_name_layout.add_widget(self.full_name_field)
        self.readonly_fields.add_widget(full_name_layout)

        # Username
        username_layout = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(60)
        )
        username_label = MDLabel(
            text="Username",
            theme_text_color="Custom",
            text_color=get_color_from_hex(COLORS['secondary_text'] + 'ff'),
            halign='left',
            size_hint=(1, None),
            height=dp(20)
        )
        self.username_field = TextInput(
            text="",
            multiline=False,
            readonly=True,
            background_color=get_color_from_hex(COLORS['white'] + 'ee'),
            foreground_color=get_color_from_hex(COLORS['text'] + 'ff'),
            size_hint=(1, None),
            height=dp(40)
        )
        username_layout.add_widget(username_label)
        username_layout.add_widget(self.username_field)
        self.readonly_fields.add_widget(username_layout)

        # Email
        email_layout = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(60)
        )
        email_label = MDLabel(
            text="Email",
            theme_text_color="Custom",
            text_color=get_color_from_hex(COLORS['secondary_text'] + 'ff'),
            halign='left',
            size_hint=(1, None),
            height=dp(20)
        )
        self.email_field = TextInput(
            text="",
            multiline=False,
            readonly=True,
            background_color=get_color_from_hex(COLORS['white'] + 'ee'),
            foreground_color=get_color_from_hex(COLORS['text'] + 'ff'),
            size_hint=(1, None),
            height=dp(40)
        )
        email_layout.add_widget(email_label)
        email_layout.add_widget(self.email_field)
        self.readonly_fields.add_widget(email_layout)

        content_layout.add_widget(self.readonly_fields)

        # Editable section header
        editable_header = MDLabel(
            text="PERSONAL INFORMATION (EDITABLE)",
            halign="left",
            theme_text_color="Custom",
            text_color=get_color_from_hex(COLORS['primary'] + 'ff'),
            font_style="Subtitle1",
            size_hint=(1, None),
            height=dp(30)
        )
        content_layout.add_widget(editable_header)

        # Form fields - Editable fields
        self.editable_fields = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(240),
            spacing=dp(10)
        )

        # Contact
        contact_layout = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(60)
        )
        contact_label = MDLabel(
            text="Contact Number",
            theme_text_color="Custom",
            text_color=get_color_from_hex(COLORS['secondary_text'] + 'ff'),
            halign='left',
            size_hint=(1, None),
            height=dp(20)
        )
        self.contact_field = TextInput(
            text="",
            hint_text="Enter your phone number",
            multiline=False,
            background_color=get_color_from_hex(COLORS['white'] + 'ff'),
            foreground_color=get_color_from_hex(COLORS['text'] + 'ff'),
            size_hint=(1, None),
            height=dp(40)
        )
        contact_layout.add_widget(contact_label)
        contact_layout.add_widget(self.contact_field)
        self.editable_fields.add_widget(contact_layout)

        # City
        city_layout = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(60)
        )
        city_label = MDLabel(
            text="City",
            theme_text_color="Custom",
            text_color=get_color_from_hex(COLORS['secondary_text'] + 'ff'),
            halign='left',
            size_hint=(1, None),
            height=dp(20)
        )
        self.city_field = TextInput(
            text="",
            hint_text="Enter your city",
            multiline=False,
            background_color=get_color_from_hex(COLORS['white'] + 'ff'),
            foreground_color=get_color_from_hex(COLORS['text'] + 'ff'),
            size_hint=(1, None),
            height=dp(40)
        )
        city_layout.add_widget(city_label)
        city_layout.add_widget(self.city_field)
        self.editable_fields.add_widget(city_layout)

        # Country
        country_layout = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(60)
        )
        country_label = MDLabel(
            text="Country",
            theme_text_color="Custom",
            text_color=get_color_from_hex(COLORS['secondary_text'] + 'ff'),
            halign='left',
            size_hint=(1, None),
            height=dp(20)
        )
        self.country_field = TextInput(
            text="",
            hint_text="Enter your country",
            multiline=False,
            background_color=get_color_from_hex(COLORS['white'] + 'ff'),
            foreground_color=get_color_from_hex(COLORS['text'] + 'ff'),
            size_hint=(1, None),
            height=dp(40)
        )
        country_layout.add_widget(country_label)
        country_layout.add_widget(self.country_field)
        self.editable_fields.add_widget(country_layout)

        # Occupation
        occupation_layout = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(60)
        )
        occupation_label = MDLabel(
            text="Occupation",
            theme_text_color="Custom",
            text_color=get_color_from_hex(COLORS['secondary_text'] + 'ff'),
            halign='left',
            size_hint=(1, None),
            height=dp(20)
        )
        self.occupation_field = TextInput(
            text="",
            hint_text="Enter your occupation",
            multiline=False,
            background_color=get_color_from_hex(COLORS['white'] + 'ff'),
            foreground_color=get_color_from_hex(COLORS['text'] + 'ff'),
            size_hint=(1, None),
            height=dp(40)
        )
        occupation_layout.add_widget(occupation_label)
        occupation_layout.add_widget(self.occupation_field)
        self.editable_fields.add_widget(occupation_layout)

        content_layout.add_widget(self.editable_fields)

        # Save button
        save_button = MDRaisedButton(
            text="SAVE CHANGES",
            md_bg_color=get_color_from_hex(COLORS['primary'] + 'ff'),
            text_color=get_color_from_hex(COLORS['white'] + 'ff'),
            size_hint=(0.8, None),
            height=dp(50),
            pos_hint={'center_x': 0.5}
        )
        save_button.bind(on_press=self.save_profile)
        content_layout.add_widget(save_button)

        # Status message
        self.status_label = MDLabel(
            text="",
            theme_text_color="Custom",
            text_color=(0, 1, 0, 1),
            halign="center",
            size_hint=(1, None),
            height=dp(40),
            pos_hint={'center_x': 0.5}
        )
        content_layout.add_widget(self.status_label)

        scroll.add_widget(content_layout)
        main_layout.add_widget(scroll)

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
            icon_color=get_color_from_hex(COLORS['white'] + 'ff'),
            size_hint=(1, 0.7)
        )
        home_icon.bind(on_press=self.go_to_home)
        home_btn.add_widget(home_icon)
        nav_bar.add_widget(home_btn)

        # Map button
        map_btn = BoxLayout(orientation='vertical')
        map_icon = MDFloatingActionButton(
            icon='map',
            font_size=dp(24),
            md_bg_color=(68/255, 110/255, 73/255, 1),
            icon_color=get_color_from_hex(COLORS['white'] + 'ff'),
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
            icon_color=get_color_from_hex(COLORS['white'] + 'ff'),
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
            icon_color=get_color_from_hex(COLORS['white'] + 'ff'),
            size_hint=(1, 0.7)
        )
        news_icon.bind(on_press=self.go_to_news)
        news_btn.add_widget(news_icon)
        nav_bar.add_widget(news_btn)

        main_layout.add_widget(nav_bar)

        self.add_widget(main_layout)

        # Initialize database if available
        if self.db_helper:
            try:
                self.db_helper.create_user_profiles_table()
            except Exception as e:
                print(f"Error creating user profiles table: {e}")

    def set_user_id(self, user_id):
        """Set the user ID and load profile data"""
        self.user_id = user_id

    def on_enter(self):
        """Load user profile data when entering the screen"""
        if self.user_id and self.db_helper:
            try:
                self.load_profile_data()
            except Exception as e:
                print(f"Error loading profile data: {e}")
                self.status_label.text = "Could not load profile data"
                self.status_label.color = (1, 0, 0, 1)

    def load_profile_data(self):
        """Load profile data from database"""
        if not self.db_helper:
            self.status_label.text = "Database not available"
            self.status_label.color = (1, 0, 0, 1)
            return

        profile = self.db_helper.get_user_profile(self.user_id)

        if profile:
            user_id, full_name, username, email, contact, city, country, occupation, profile_image = profile

            # Set readonly fields
            self.user_id_label.text = f"User ID: {user_id}"
            self.full_name_field.text = full_name or ""
            self.username_field.text = username or ""
            self.email_field.text = email or ""

            # Set editable fields
            self.contact_field.text = contact or ""
            self.city_field.text = city or ""
            self.country_field.text = country or ""
            self.occupation_field.text = occupation or ""

            # Set profile image if available
            if profile_image:
                # Convert BLOB to image file in memory
                self.profile_image_data = profile_image
                self._display_profile_image()

    def _display_profile_image(self):
        """Display the profile image from binary data"""
        if self.profile_image_data:
            try:
                # Save to temp file and display
                temp_path = 'temp_profile_image.png'
                with open(temp_path, 'wb') as f:
                    f.write(self.profile_image_data)
                self.profile_image.source = temp_path
                self.profile_image.reload()
            except Exception as e:
                print(f"Error displaying profile image: {e}")

    def save_profile(self, instance):
        """Save profile changes to database"""
        if not self.db_helper:
            self.status_label.text = "Database not available"
            self.status_label.color = (1, 0, 0, 1)
            return

        if not self.user_id:
            self.status_label.text = "Error: No user ID available"
            self.status_label.color = (1, 0, 0, 1)
            return

        # Get field values
        contact = self.contact_field.text.strip()
        city = self.city_field.text.strip()
        country = self.country_field.text.strip()
        occupation = self.occupation_field.text.strip()

        try:
            # Update profile in database
            success = self.db_helper.update_user_profile(
                self.user_id,
                contact=contact,
                city=city,
                country=country,
                occupation=occupation,
                profile_image=self.profile_image_data
            )

            if success:
                self.status_label.text = "Profile updated successfully!"
                self.status_label.color = (0, 1, 0, 1)
                Clock.schedule_once(lambda dt: setattr(
                    self.status_label, 'text', ''), 3)
            else:
                self.status_label.text = "Error updating profile"
                self.status_label.color = (1, 0, 0, 1)
        except Exception as e:
            print(f"Error updating profile: {e}")
            self.status_label.text = f"Error updating profile: {str(e)}"
            self.status_label.color = (1, 0, 0, 1)

    def open_camera(self, instance):
        """Open camera to take profile photo"""
        try:
            # Simplified camera approach
            self.status_label.text = "Opening camera..."
            self.status_label.color = (0, 0, 1, 1)

            # Create a simple camera layout
            self.camera_layout = BoxLayout(orientation='vertical')

            # Create camera widget with proper configuration
            self.camera = Camera(
                # Lower resolution for better performance
                resolution=(320, 240),
                play=True
            )
            self.camera_layout.add_widget(self.camera)

            # Camera buttons
            camera_buttons = BoxLayout(size_hint=(1, 0.2))

            capture_btn = Button(
                text="Capture",
                size_hint=(0.5, 1),
                background_color=get_color_from_hex(COLORS['primary'] + 'ff'),
                color=get_color_from_hex(COLORS['white'] + 'ff'),
            )
            capture_btn.bind(on_press=self.capture_photo)
            camera_buttons.add_widget(capture_btn)

            cancel_btn = Button(
                text="Cancel",
                size_hint=(0.5, 1),
                background_color=get_color_from_hex(
                    COLORS['button_blue'] + 'ff'),
                color=get_color_from_hex(COLORS['white'] + 'ff'),
            )
            cancel_btn.bind(on_press=self.dismiss_camera)
            camera_buttons.add_widget(cancel_btn)

            self.camera_layout.add_widget(camera_buttons)

            # Display camera in a popup dialog
            self.camera_dialog = MDDialog(
                title="Take Profile Photo",
                type="custom",
                content_cls=self.camera_layout,
                size_hint=(0.9, 0.8),
                auto_dismiss=False  # Prevent accidental dismissal
            )

            self.camera_dialog.open()
            self.status_label.text = ""

        except Exception as e:
            print(f"Error opening camera: {e}")
            traceback.print_exc()
            self.status_label.text = f"Camera error: {str(e)}"
            self.status_label.color = (1, 0, 0, 1)

    # Replace the capture_photo and dismiss_camera methods with these:

    def capture_photo(self, instance):
        """Capture photo from camera"""
        try:
            if self.camera and self.camera.texture:
                self.status_label.text = "Processing photo..."

                # Create a temporary filename
                temp_path = 'temp_profile_image.png'

                # Using PIL to convert the texture to an image
                texture = self.camera.texture
                size = texture.size
                pixels = texture.pixels

                # Convert buffer to PIL Image
                pil_image = PILImage.frombytes(
                    mode='RGBA',
                    size=size,
                    data=pixels
                )

                # Save the PIL image
                pil_image.save(temp_path)

                # Read the file back as binary data
                with open(temp_path, 'rb') as f:
                    self.profile_image_data = f.read()

                # Update the profile image
                self.profile_image.source = temp_path
                self.profile_image.reload()

                # Close camera dialog
                self.dismiss_camera(None)

                self.status_label.text = "Photo captured!"
                self.status_label.color = (0, 1, 0, 1)
                Clock.schedule_once(lambda dt: setattr(
                    self.status_label, 'text', ''), 2)
            else:
                self.status_label.text = "Camera not ready"
                self.status_label.color = (1, 0, 0, 1)

        except Exception as e:
            print(f"Error capturing photo: {e}")
            traceback.print_exc()
            self.status_label.text = f"Error capturing photo: {str(e)}"
            self.status_label.color = (1, 0, 0, 1)
            # Try to dismiss the camera even if there's an error
            self.dismiss_camera(None)

    def dismiss_camera(self, instance):
        """Close the camera dialog"""
        try:
            if hasattr(self, 'camera') and self.camera:
                # Properly release the camera
                self.camera.play = False

                # Allow time for camera to stop
                def delayed_cleanup(dt):
                    if hasattr(self, 'camera_dialog') and self.camera_dialog:
                        self.camera_dialog.dismiss()
                    self.camera = None
                    self.camera_layout = None
                    self.camera_dialog = None

                # Schedule cleanup after a short delay
                Clock.schedule_once(delayed_cleanup, 0.5)

        except Exception as e:
            print(f"Error dismissing camera: {e}")
            traceback.print_exc()

            # Last resort - try to force close the dialog
            try:
                if hasattr(self, 'camera_dialog') and self.camera_dialog:
                    self.camera_dialog.dismiss()
                self.camera = None
            except:
                pass

    def open_file_manager(self, instance):
        """Open file manager to choose image"""
        try:
            self.file_manager = MDFileManager(
                exit_manager=self.exit_file_manager,
                select_path=self.select_image_path,
                preview=True,
            )
            self.file_manager.show('/')

        except Exception as e:
            print(f"Error opening file manager: {e}")
            self.status_label.text = f"Error: {str(e)}"
            self.status_label.color = (1, 0, 0, 1)

    def select_image_path(self, path):
        """Handle selected image from file manager"""
        try:
            # Check if file is an image
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
            if any(path.lower().endswith(ext) for ext in valid_extensions):
                with open(path, 'rb') as f:
                    self.profile_image_data = f.read()

                # Update image
                self.profile_image.source = path
                self.profile_image.reload()

                self.status_label.text = "Photo selected!"
                self.status_label.color = (0, 1, 0, 1)
                Clock.schedule_once(lambda dt: setattr(
                    self.status_label, 'text', ''), 2)

            self.exit_file_manager()
        except Exception as e:
            print(f"Error selecting image: {e}")
            self.exit_file_manager()
            self.status_label.text = f"Error selecting image: {str(e)}"
            self.status_label.color = (1, 0, 0, 1)

    def exit_file_manager(self, *args):
        """Close file manager"""
        if self.file_manager:
            self.file_manager.close()
            self.file_manager = None

    def go_back(self, instance):
        """Go back to previous screen"""
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'home'  # Change to the correct screen name

    def go_to_home(self, instance):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'home'  # Change to the correct screen name

    def go_to_map(self, instance):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'map'

    def go_to_social(self, instance):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'social'

    def go_to_news(self, instance):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'news'

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def _update_header_rect(self, instance, value):
        self.header_rect.pos = instance.pos
        self.header_rect.size = instance.size

    def _update_nav_rect(self, instance, value):
        self.nav_rect.pos = instance.pos
        self.nav_rect.size = instance.size
