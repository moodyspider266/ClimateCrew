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

# Color scheme based on app's design
COLORS = {
    'background': '#e3f8ee',
    'primary': '#446e49',
    'text': '#333333',
    'secondary_text': '#666666',
    'white': '#ffffff',
    'task_bg': '#446e49',
    'yellow': '#ffc107',
    'gold': '#FFD700',
    'silver': '#C0C0C0',
    'bronze': '#CD7F32',
    'button_blue': '#2196F3'
}


class LeaderboardScreen(Screen):
    def __init__(self, db_helper=None, **kwargs):
        super(LeaderboardScreen, self).__init__(**kwargs)
        self.name = 'leaderboard'
        self.db_helper = db_helper
        self.user_id = None
        self.leaderboard_data = []

        # Main layout
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
            text="Leaderboard",
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
        refresh_btn.bind(on_press=self.refresh_leaderboard)
        header.add_widget(refresh_btn)

        main_layout.add_widget(header)

        # Content area with scrollable table
        content_area = BoxLayout(
            orientation='vertical',
            size_hint=(1, 0.82),
            pos_hint={'top': 0.92},
            padding=[dp(10), dp(10)]
        )

        # Table header
        table_header = GridLayout(
            cols=3,
            size_hint=(1, None),
            height=dp(50),
            spacing=[1, 1]
        )

        # Add header background
        with table_header.canvas.before:
            Color(rgba=get_color_from_hex(COLORS['primary'] + 'ee'))
            self.header_bg = Rectangle(
                size=table_header.size, pos=table_header.pos)
        table_header.bind(size=self._update_header_bg,
                          pos=self._update_header_bg)

        # Header labels
        for header_text, size in [("Rank", 0.2), ("Username", 0.5), ("Points", 0.3)]:
            header_label = Label(
                text=header_text,
                color=get_color_from_hex(COLORS['white'] + 'ff'),
                font_size=dp(18),
                bold=True,
                size_hint_x=size
            )
            table_header.add_widget(header_label)

        content_area.add_widget(table_header)

        # Table content with scrollview
        self.table_scroll = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=dp(10),
            bar_color=[0.7, 0.7, 0.7, 0.9],
            bar_inactive_color=[0.7, 0.7, 0.7, 0.2],
            scroll_type=['bars', 'content']
        )

        self.table_content = GridLayout(
            cols=1,
            size_hint=(1, None),
            spacing=[0, dp(2)]
        )
        self.table_content.bind(
            minimum_height=self.table_content.setter('height'))

        self.table_scroll.add_widget(self.table_content)
        content_area.add_widget(self.table_scroll)

        main_layout.add_widget(content_area)

        # Status label for notifications
        self.status_label = Label(
            text="",
            color=(1, 0, 0, 1),
            size_hint=(1, 0.05),
            pos_hint={'center_x': 0.5, 'y': 0.45},
            opacity=0
        )
        main_layout.add_widget(self.status_label)

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

        print(f"Leaderboard screen entered with user_id: {self.user_id}")

        # Load leaderboard data
        self.load_leaderboard()

    def load_leaderboard(self):
        """Load leaderboard data from database"""
        if not self.db_helper:
            self.show_status("Database not available")
            return

        try:
            # Fetch leaderboard data
            self.leaderboard_data = self.get_leaderboard_data()
            print(
                f"Retrieved {len(self.leaderboard_data)} users for leaderboard")

            # Update table display
            self.display_leaderboard()

        except Exception as e:
            print(f"Error loading leaderboard: {e}")
            self.show_status(f"Error: {str(e)}")

    def get_leaderboard_data(self):
        """Get leaderboard data from database"""
        try:
            # Use a SQL query that joins task_management with users to get usernames
            query = '''
                SELECT u.username, t.points, t.num_tasks_completed, u.id
                FROM task_management t
                JOIN users u ON t.user_id = u.id
                ORDER BY t.points DESC
            '''

            self.db_helper.cursor.execute(query)
            results = self.db_helper.cursor.fetchall()
            return results

        except Exception as e:
            print(f"Error getting leaderboard data: {e}")
            return []

    def display_leaderboard(self):
        """Display leaderboard data in the table"""
        # Clear existing content
        self.table_content.clear_widgets()

        if not self.leaderboard_data:
            empty_row = BoxLayout(
                orientation='vertical',
                size_hint=(1, None),
                height=dp(50)
            )
            empty_label = Label(
                text="No data available",
                color=get_color_from_hex(COLORS['text'] + 'ff')
            )
            empty_row.add_widget(empty_label)
            self.table_content.add_widget(empty_row)
            return

        # Add user rows to table
        for rank, user_data in enumerate(self.leaderboard_data, start=1):
            username, points, tasks_completed, user_id = user_data

            # Create row
            row = GridLayout(
                cols=3,
                size_hint=(1, None),
                height=dp(50)
            )

            # Add background color - alternate colors for readability
            with row.canvas.before:
                if rank % 2 == 0:
                    Color(rgba=get_color_from_hex('#f5f5f5ff'))
                else:
                    Color(rgba=get_color_from_hex('#ffffffff'))

                # Highlight current user's row
                if user_id == self.user_id:
                    Color(rgba=get_color_from_hex('#e3f2fd' + 'ff'))

                # Medal colors for top 3
                if rank == 1:
                    Color(rgba=get_color_from_hex(COLORS['gold'] + '33'))
                elif rank == 2:
                    Color(rgba=get_color_from_hex(COLORS['silver'] + '33'))
                elif rank == 3:
                    Color(rgba=get_color_from_hex(COLORS['bronze'] + '33'))

                row_bg = Rectangle(size=row.size, pos=row.pos)
                row.bind(size=lambda obj, val, bg=row_bg: setattr(bg, 'size', val),
                         pos=lambda obj, val, bg=row_bg: setattr(bg, 'pos', val))

            # Rank with medal icon for top 3
            rank_text = str(rank)
            if rank <= 3:
                medal_icons = ['', '', '']
                rank_text = f"{medal_icons[rank-1]} {rank}"

            rank_label = Label(
                text=rank_text,
                color=get_color_from_hex(COLORS['text'] + 'ff'),
                bold=True if rank <= 3 else False,
                size_hint_x=0.2
            )

            # Username
            username_label = Label(
                text=username,
                color=get_color_from_hex(COLORS['text'] + 'ff'),
                bold=True if user_id == self.user_id else False,
                size_hint_x=0.5,
                halign='left',
                text_size=(dp(150), None)
            )

            # Points with task count
            points_label = Label(
                text=f"{points} pts ({tasks_completed} tasks)",
                color=get_color_from_hex(COLORS['primary'] + 'ff'),
                bold=True,
                size_hint_x=0.3
            )

            row.add_widget(rank_label)
            row.add_widget(username_label)
            row.add_widget(points_label)

            self.table_content.add_widget(row)

        # Set total height
        self.table_content.height = len(self.leaderboard_data) * dp(50)

    def refresh_leaderboard(self, *args):
        """Refresh leaderboard data"""
        self.load_leaderboard()
        self.show_status("Leaderboard refreshed")

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

    def _update_header_bg(self, instance, value):
        self.header_bg.pos = instance.pos
        self.header_bg.size = instance.size

    def _update_nav_rect(self, instance, value):
        self.nav_rect.pos = instance.pos
        self.nav_rect.size = instance.size
