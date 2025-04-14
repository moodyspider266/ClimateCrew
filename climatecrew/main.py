from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.core.window import Window
from screens.login import LoginScreen
from screens.registration import RegistrationScreen
from screens.onboarding import OnboardingScreen
from screens.home import HomeScreen
from screens.welcome import WelcomeScreen
from screens.profile import ProfileScreen
from screens.news import NewsScreen
from screens.submit_task import SubmitTaskScreen
from screens.social import SocialScreen
from screens.map import MapScreen
from screens.leaderboard import LeaderboardScreen
from kivy.core.text import LabelBase
from db_helper import DatabaseHelper

# Set the app to mobile dimensions for testing
Window.size = (360, 640)

# Register Google Font globally
LabelBase.register(
    name="Roboto", fn_regular="assets/fonts/Roboto-VariableFont_wdth,wght.ttf")

# Color scheme based on your Figma design
COLORS = {
    'background': '#e3f8ee',
    'primary': '#446e49',
    'text': '#333333',
    'secondary_text': '#666666',
    'white': '#ffffff'
}


class ClimateCrewApp(MDApp):
    def __init__(self, **kwargs):
        super(ClimateCrewApp, self).__init__(**kwargs)
        self.current_user_id = None  # Store the current user's ID here

    def set_user_id(self, user_id):
        """Set the current user ID"""
        self.current_user_id = user_id
        print(f"User ID set in app: {self.current_user_id}")

    def get_user_id(self):
        """Get the current user ID"""
        return self.current_user_id

    def build(self):
        self.db_helper = DatabaseHelper()
        # Create the screen manager
        sm = ScreenManager(transition=SlideTransition())

        # Add screens
        login_screen = LoginScreen(self.db_helper, name='login')
        register_screen = RegistrationScreen(self.db_helper, name='register')
        home_screen = HomeScreen(
            db_helper=self.db_helper, name='home')
        profile_screen = ProfileScreen(self.db_helper, name='profile')
        news_screen = NewsScreen(name='news')
        submit_task_screen = SubmitTaskScreen(
            self.db_helper, name='submit_task')
        social_screen = SocialScreen(self.db_helper, name='social')
        map_screen = MapScreen(self.db_helper, name='map')
        leaderboard_screen = LeaderboardScreen(
            self.db_helper, name='leaderboard')
        sm.add_widget(WelcomeScreen())
        sm.add_widget(login_screen)
        sm.add_widget(register_screen)
        sm.add_widget(home_screen)
        sm.add_widget(OnboardingScreen())
        sm.add_widget(profile_screen)
        sm.add_widget(news_screen)
        sm.add_widget(submit_task_screen)
        sm.add_widget(social_screen)
        sm.add_widget(map_screen)
        sm.add_widget(leaderboard_screen)

        return sm

    def on_stop(self):
        """Called when the application is closing"""
        if self.db_helper:
            self.db_helper.close()
            print("Database connection closed")


if __name__ == '__main__':
    ClimateCrewApp().run()
