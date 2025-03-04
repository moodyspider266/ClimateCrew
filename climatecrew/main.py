from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.core.window import Window
from screens.login import LoginScreen
from screens.registration import RegistrationScreen
from screens.onboarding import OnboardingScreen
from screens.home import HomeScreen
from screens.welcome import WelcomeScreen
from kivy.core.text import LabelBase
from db_helper import DatabaseHelper

# Set the app to mobile dimensions for testing
Window.size = (360, 640)

# Register Google Font globally
LabelBase.register(name="Roboto", fn_regular="assets/fonts/Roboto-VariableFont_wdth,wght.ttf")

# Color scheme based on your Figma design
COLORS = {
    'background': '#e3f8ee',
    'primary': '#446e49',
    'text': '#333333',
    'secondary_text': '#666666',
    'white': '#ffffff'
}

class ClimateCrewApp(App):
    def build(self):
        self.db_helper = DatabaseHelper()
        # Create the screen manager
        sm = ScreenManager(transition=SlideTransition())
        
        # Add screens
        login_screen = LoginScreen(self.db_helper, name='login')
        register_screen = RegistrationScreen(self.db_helper, name='register')
        home_screen = HomeScreen(name='home')
        sm.add_widget(WelcomeScreen())
        sm.add_widget(login_screen)
        sm.add_widget(register_screen)
        sm.add_widget(home_screen)
        sm.add_widget(OnboardingScreen())
        
        return sm

    def on_stop(self):
        # Close database connection when app closes
        self.db_helper.close()

if __name__ == '__main__':
    ClimateCrewApp().run()