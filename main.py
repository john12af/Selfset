import flet as ft
import base64
import json
import os
import random
import webbrowser
from datetime import datetime
from typing import Optional

# Google OAuth client ID
CLIENT_ID = "475953482378-313ua2c3so1muentri4susm7o9hgp0gc.apps.googleusercontent.com"

class XAppFeed:
    def __init__(self):
        self.page = None
        self.is_signed_in = False
        self.user_data = None
        self.current_banner_image = None
        self.banner_zoom = 100
        self.banner_position = 50
        self.banner_cache_buster = 0
        self.current_tab = "for_you"
        
    def main(self, page: ft.Page):
        self.page = page
        page.title = "X App Feed"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 0
        page.spacing = 0
        page.scroll = ft.ScrollMode.AUTO
        page.window_width = 400
        page.window_height = 800
        page.bgcolor = "#ffffff"
        
        # Load saved user data
        self.load_user_data()
        
        # Create all UI components
        self.create_ui()
        
        # Add everything to page
        page.add(self.main_container)
        
    def load_user_data(self):
        """Load user data from local storage"""
        try:
            if os.path.exists("user_data.json"):
                with open("user_data.json", "r") as f:
                    data = json.load(f)
                    self.is_signed_in = data.get("is_signed_in", False)
                    self.user_data = data.get("user_data")
                    if self.user_data and self.user_data.get("banner"):
                        self.current_banner_image = self.user_data["banner"]
                        self.banner_zoom = self.user_data.get("banner_zoom", 100)
                        self.banner_position = self.user_data.get("banner_position", 50)
                        self.banner_cache_buster = self.user_data.get("banner_cache_buster", 0)
        except:
            pass
    
    def save_user_data(self):
        """Save user data to local storage"""
        data = {
            "is_signed_in": self.is_signed_in,
            "user_data": self.user_data
        }
        with open("user_data.json", "w") as f:
            json.dump(data, f)
    
    def create_ui(self):
        """Create all UI components"""
        
        # Top Header
        self.header_profile_btn = ft.Container(
            width=32,
            height=32,
            border_radius=16,
            image_src=self.user_data["picture"] if self.user_data and self.is_signed_in else "https://pbs.twimg.com/profile_images/1536443352228368384/x-XyfcPq.jpg",
            image_fit=ft.ImageFit.COVER,
            on_click=lambda _: self.toggle_sidebar(),
        )
        
        header = ft.Container(
            content=ft.Row(
                controls=[
                    self.header_profile_btn,
                    ft.Container(
                        content=ft.Text("X", size=24, weight=ft.FontWeight.BOLD, color="#000000"),
                        expand=True,
                        alignment=ft.alignment.center,
                    ),
                    ft.Container(width=32),  # Placeholder for symmetry
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.padding.symmetric(horizontal=16, vertical=12),
            bgcolor="#ffffff",
            border=ft.border.only(bottom=ft.border.BorderSide(1, "#e0e0e0")),
        )
        
        # Timeline Tabs
        self.for_you_tab = ft.Container(
            content=ft.Text("For you", size=16, weight=ft.FontWeight.BOLD, color="#000000"),
            expand=True,
            alignment=ft.alignment.center,
            padding=16,
            on_click=lambda _: self.switch_tab("for_you"),
        )
        
        self.following_tab = ft.Container(
            content=ft.Text("Following", size=16, weight=ft.FontWeight.BOLD, color="#536471"),
            expand=True,
            alignment=ft.alignment.center,
            padding=16,
            on_click=lambda _: self.switch_tab("following"),
        )
        
        self.tab_indicator = ft.Container(
            width=200,
            height=3,
            bgcolor="#1d9bf0",
            border_radius=2,
            animate_position=ft.animation.Animation(300, ft.AnimationCurve.EASE),
        )
        
        tabs = ft.Container(
            content=ft.Stack(
                controls=[
                    ft.Row(
                        controls=[self.for_you_tab, self.following_tab],
                        spacing=0,
                    ),
                    ft.Container(
                        content=self.tab_indicator,
                        top=48,
                        left=0,
                    ),
                ],
            ),
            border=ft.border.only(bottom=ft.border.BorderSide(1, "#e0e0e0")),
            bgcolor="#ffffff",
        )
        
        # Posts
        posts = ft.Column(
            controls=[
                self.create_post_chad(),
                self.create_post_science(),
            ],
            spacing=0,
        )
        
        # Bottom Navigation
        bottom_nav = ft.Container(
            content=ft.Row(
                controls=[
                    self.create_nav_item(ft.icons.HOME, "Home", True, 0),
                    self.create_nav_item(ft.icons.SEARCH, "Search", False, 1),
                    self.create_nav_item(ft.icons.NOTIFICATIONS_NONE, "Notifications", False, 2),
                    self.create_nav_item(ft.icons.MAIL_OUTLINE, "Messages", False, 3),
                ],
                alignment=ft.MainAxisAlignment.SPACE_AROUND,
            ),
            padding=ft.padding.symmetric(horizontal=16, vertical=8),
            bgcolor="#ffffff",
            border=ft.border.only(top=ft.border.BorderSide(1, "#e0e0e0")),
        )
        
        # Sidebar
        self.sidebar_overlay = ft.Container(
            content=ft.Container(
                bgcolor=ft.colors.with_opacity(0.5, "#000000"),
                expand=True,
                on_click=lambda _: self.toggle_sidebar(),
            ),
            visible=False,
            expand=True,
        )
        
        self.sidebar = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Text("Menu", size=20, weight=ft.FontWeight.BOLD),
                                ft.IconButton(
                                    icon=ft.icons.CLOSE,
                                    icon_size=20,
                                    on_click=lambda _: self.toggle_sidebar(),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        padding=16,
                        border=ft.border.only(bottom=ft.border.BorderSide(1, "#e0e0e0")),
                    ),
                    ft.Column(
                        controls=[
                            self.create_sidebar_item(ft.icons.PERSON, "Profile", self.open_profile),
                            self.create_sidebar_item(ft.icons.STAR, "Creator Program", lambda _: self.show_alert("Creator Program feature coming soon!")),
                            self.create_sidebar_item(ft.icons.SETTINGS, "Settings", lambda _: self.show_alert("Settings feature coming soon!")),
                        ],
                        spacing=0,
                    ),
                ],
                spacing=0,
            ),
            width=280,
            bgcolor="#ffffff",
            right=-280,
            animate_position=ft.animation.Animation(300, ft.AnimationCurve.EASE),
            visible=False,
        )
        
        # Sign In Page
        self.signin_page = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.IconButton(
                            icon=ft.icons.ARROW_BACK,
                            icon_size=20,
                            on_click=lambda _: self.close_signin(),
                        ),
                        padding=16,
                    ),
                    ft.Column(
                        controls=[
                            ft.Text("X", size=48, weight=ft.FontWeight.BOLD),
                            ft.Text("Sign in to X", size=24, weight=ft.FontWeight.BOLD),
                            ft.Text("to continue to X App Feed", size=14, color="#536471"),
                            ft.Container(height=40),
                            ft.ElevatedButton(
                                content=ft.Row(
                                    controls=[
                                        ft.Image(src="https://www.google.com/favicon.ico", width=18, height=18),
                                        ft.Text("Continue with Google", size=15),
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER,
                                ),
                                style=ft.ButtonStyle(
                                    color="#000000",
                                    bgcolor="#ffffff",
                                    side=ft.BorderSide(1, "#cfd9de"),
                                    shape=ft.RoundedRectangleBorder(radius=20),
                                ),
                                width=300,
                                height=48,
                                on_click=lambda _: self.login_with_google(),
                            ),
                            ft.Container(height=10),
                            ft.Text("Loading Google login...", size=14, color="#536471", visible=False),
                            ft.Container(height=10),
                            ft.ElevatedButton(
                                content=ft.Text("Use Demo Account", size=15, color="#1d9bf0"),
                                style=ft.ButtonStyle(
                                    bgcolor="#ffffff",
                                    side=ft.BorderSide(1, "#1d9bf0"),
                                    shape=ft.RoundedRectangleBorder(radius=20),
                                ),
                                width=300,
                                height=48,
                                on_click=lambda _: self.use_demo_account(),
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        expand=True,
                    ),
                ],
                spacing=0,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor="#ffffff",
            visible=False,
            expand=True,
        )
        
        # Profile Page
        self.create_profile_page()
        
        # Edit Profile Page
        self.create_edit_profile_page()
        
        # Banner Settings Page
        self.create_banner_settings_page()
        
        # Main Stack
        self.main_container = ft.Stack(
            controls=[
                ft.Column(
                    controls=[header, tabs, posts, bottom_nav],
                    spacing=0,
                    scroll=ft.ScrollMode.AUTO,
                    expand=True,
                ),
                self.sidebar_overlay,
                self.sidebar,
                self.signin_page,
                self.profile_page,
                self.edit_profile_page,
                self.banner_settings_page,
            ],
            expand=True,
        )
    
    def create_nav_item(self, icon, label, active, index):
        color = "#1d9bf0" if active else "#536471"
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(icon, size=24, color=color),
                    ft.Text(label, size=10, color=color),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=4,
            ),
            padding=6,
            expand=True,
            on_click=lambda _: self.switch_nav(index),
        )
    
    def create_sidebar_item(self, icon, label, on_click):
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(icon, size=20, color="#536471"),
                    ft.Text(label, size=15),
                ],
                spacing=16,
            ),
            padding=ft.padding.symmetric(horizontal=16, vertical=14),
            on_click=on_click,
        )
    
    def create_post_chad(self):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(
                                width=40,
                                height=40,
                                border_radius=20,
                                image_src="https://pbs.twimg.com/profile_images/1536443352228368384/x-XyfcPq.jpg",
                                image_fit=ft.ImageFit.COVER,
                            ),
                            ft.Column(
                                controls=[
                                    ft.Row(
                                        controls=[
                                            ft.Text("Chad Infi", weight=ft.FontWeight.BOLD),
                                            ft.Image(
                                                src="https://upload.wikimedia.org/wikipedia/commons/e/e4/Twitter_Verified_Badge.svg",
                                                width=18,
                                                height=18,
                                            ),
                                            ft.Text("@chad_infi · 1d", color="#536471"),
                                        ],
                                        spacing=4,
                                    ),
                                ],
                                spacing=0,
                            ),
                            ft.Container(
                                content=ft.Icon(ft.icons.MORE_HORIZ, size=18, color="#536471"),
                                expand=True,
                                alignment=ft.alignment.center_right,
                            ),
                        ],
                    ),
                    ft.Container(
                        content=ft.Text("Bro have two sides", size=15),
                        margin=ft.margin.only(top=8, bottom=12),
                    ),
                    ft.Container(
                        content=ft.Stack(
                            controls=[
                                ft.Container(
                                    width=400,
                                    height=400,
                                    bgcolor="#e0e0e0",
                                    border_radius=12,
                                ),
                                ft.Container(
                                    content=ft.Icon(ft.icons.PLAY_ARROW, size=30, color="#ffffff"),
                                    width=60,
                                    height=60,
                                    border_radius=30,
                                    bgcolor=ft.colors.with_opacity(0.9, "#1d9bf0"),
                                    alignment=ft.alignment.center,
                                    left=170,
                                    top=170,
                                ),
                                ft.Container(
                                    content=ft.Text("0:17", size=12, color="#ffffff"),
                                    bgcolor=ft.colors.with_opacity(0.7, "#000000"),
                                    padding=ft.padding.symmetric(horizontal=6, vertical=2),
                                    border_radius=4,
                                    left=8,
                                    bottom=8,
                                ),
                            ],
                        ),
                        border_radius=12,
                        on_click=lambda _: self.show_alert("Video would play here"),
                    ),
                    self.create_action_row("62", "925", "11.8K", "350K"),
                ],
                spacing=0,
            ),
            padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border=ft.border.only(bottom=ft.border.BorderSide(1, "#e0e0e0")),
        )
    
    def create_post_science(self):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(
                                width=40,
                                height=40,
                                border_radius=20,
                                image_src="https://pbs.twimg.com/profile_images/1504867101923762178/gfZgsqoL.jpg",
                                image_fit=ft.ImageFit.COVER,
                            ),
                            ft.Column(
                                controls=[
                                    ft.Row(
                                        controls=[
                                            ft.Text("Science girl", weight=ft.FontWeight.BOLD),
                                            ft.Image(
                                                src="https://upload.wikimedia.org/wikipedia/commons/e/e4/Twitter_Verified_Badge.svg",
                                                width=18,
                                                height=18,
                                            ),
                                            ft.Text("@scienceg... · 21h", color="#536471"),
                                        ],
                                        spacing=4,
                                    ),
                                ],
                                spacing=0,
                            ),
                            ft.Container(
                                content=ft.Icon(ft.icons.MORE_HORIZ, size=18, color="#536471"),
                                expand=True,
                                alignment=ft.alignment.center_right,
                            ),
                        ],
                    ),
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Text("2025", size=32, weight=ft.FontWeight.BOLD),
                                ft.Container(
                                    content=ft.Text("SOON", color="#ffffff"),
                                    bgcolor="#1d9bf0",
                                    padding=ft.padding.symmetric(horizontal=10, vertical=4),
                                    border_radius=16,
                                ),
                                ft.Text("2026", size=32, weight=ft.FontWeight.BOLD),
                            ],
                            spacing=8,
                        ),
                        margin=ft.margin.symmetric(vertical=40),
                        alignment=ft.alignment.center,
                    ),
                    self.create_action_row("0", "0", "0", "0"),
                ],
                spacing=0,
            ),
            padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border=ft.border.only(bottom=ft.border.BorderSide(1, "#e0e0e0")),
        )
    
    def create_action_row(self, comments, retweets, likes, views):
        return ft.Row(
            controls=[
                self.create_action_item(ft.icons.CHAT_BUBBLE_OUTLINE, comments),
                self.create_action_item(ft.icons.REPEAT, retweets),
                self.create_action_item(ft.icons.FAVORITE_BORDER, likes),
                self.create_action_item(ft.icons.BAR_CHART, views),
                self.create_action_item(ft.icons.OPEN_IN_NEW, ""),
            ],
            spacing=0,
        )
    
    def create_action_item(self, icon, text):
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(icon, size=16, color="#536471"),
                    ft.Text(text, size=13, color="#536471") if text else ft.Container(),
                ],
                spacing=6,
            ),
            padding=8,
            border_radius=50,
            on_click=lambda _: self.show_alert("Action clicked"),
        )
    
    def create_profile_page(self):
        """Create profile page"""
        self.profile_avatar = ft.Container(
            width=120,
            height=120,
            border_radius=60,
            border=ft.border.all(4, "#ffffff"),
            image_src=self.user_data["picture"] if self.user_data and self.is_signed_in else "https://abs.twimg.com/sticky/default_profile_images/default_profile_normal.png",
            image_fit=ft.ImageFit.COVER,
        )
        
        self.profile_banner = ft.Container(
            height=150,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=["#667eea", "#764ba2"],
            ),
            on_click=lambda _: self.open_banner_settings(),
        )
        
        self.profile_name = ft.Text(
            self.user_data["name"] if self.user_data and self.is_signed_in else "John Doe",
            size=20,
            weight=ft.FontWeight.BOLD,
        )
        
        self.profile_handle = ft.Text(
            self.user_data["handle"] if self.user_data and self.is_signed_in else "@johndoe",
            size=14,
            color="#536471",
        )
        
        self.profile_bio = ft.Text(
            "Tech enthusiast | Building the future one line of code at a time 🚀",
            size=15,
        )
        
        self.profile_location = ft.Text("San Francisco, CA", size=14, color="#536471")
        self.profile_website = ft.Text("johndoe.dev", size=14, color="#536471")
        self.profile_joined = ft.Text("Joined January 2024", size=14, color="#536471")
        
        self.profile_page = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.IconButton(
                                    icon=ft.icons.ARROW_BACK,
                                    icon_size=18,
                                    on_click=lambda _: self.close_profile(),
                                ),
                                ft.Text("Profile", size=18, weight=ft.FontWeight.BOLD, expand=True),
                            ],
                        ),
                        padding=ft.padding.symmetric(horizontal=16, vertical=12),
                        border=ft.border.only(bottom=ft.border.BorderSide(1, "#e0e0e0")),
                        bgcolor="#ffffff",
                    ),
                    self.profile_banner,
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Container(
                                    content=self.profile_avatar,
                                    margin=ft.margin.only(top=-40, bottom=12),
                                ),
                                self.profile_name,
                                self.profile_handle,
                                self.profile_bio,
                                ft.Row(
                                    controls=[
                                        ft.Row(
                                            controls=[
                                                ft.Icon(ft.icons.LOCATION_ON, size=16, color="#536471"),
                                                self.profile_location,
                                            ],
                                            spacing=4,
                                        ),
                                        ft.Row(
                                            controls=[
                                                ft.Icon(ft.icons.LINK, size=16, color="#536471"),
                                                self.profile_website,
                                            ],
                                            spacing=4,
                                        ),
                                        ft.Row(
                                            controls=[
                                                ft.Icon(ft.icons.CALENDAR_TODAY, size=16, color="#536471"),
                                                self.profile_joined,
                                            ],
                                            spacing=4,
                                        ),
                                    ],
                                    spacing=16,
                                    wrap=True,
                                ),
                                ft.Container(
                                    content=ft.Column(
                                        controls=[
                                            ft.ElevatedButton(
                                                content=ft.Text("Edit profile", color="#ffffff"),
                                                style=ft.ButtonStyle(
                                                    bgcolor="#000000",
                                                    shape=ft.RoundedRectangleBorder(radius=20),
                                                ),
                                                width=300,
                                                on_click=lambda _: self.open_edit_profile(),
                                            ),
                                            ft.ElevatedButton(
                                                content=ft.Text("Sign out", color="#ff4d4f"),
                                                style=ft.ButtonStyle(
                                                    bgcolor="#ffffff",
                                                    side=ft.BorderSide(1, "#ff4d4f"),
                                                    shape=ft.RoundedRectangleBorder(radius=20),
                                                ),
                                                width=300,
                                                on_click=lambda _: self.sign_out(),
                                            ),
                                        ],
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        spacing=12,
                                    ),
                                    margin=ft.margin.symmetric(vertical=20),
                                    alignment=ft.alignment.center,
                                ),
                                ft.Row(
                                    controls=[
                                        ft.Column(
                                            controls=[
                                                ft.Text("1,234", weight=ft.FontWeight.BOLD),
                                                ft.Text("Following", color="#536471"),
                                            ],
                                            spacing=2,
                                        ),
                                        ft.Column(
                                            controls=[
                                                ft.Text("5,678", weight=ft.FontWeight.BOLD),
                                                ft.Text("Followers", color="#536471"),
                                            ],
                                            spacing=2,
                                        ),
                                    ],
                                    spacing=20,
                                ),
                            ],
                            spacing=8,
                        ),
                        padding=ft.padding.symmetric(horizontal=16, vertical=0, bottom=20),
                    ),
                ],
                spacing=0,
                scroll=ft.ScrollMode.AUTO,
            ),
            bgcolor="#ffffff",
            visible=False,
            expand=True,
        )
    
    def create_edit_profile_page(self):
        """Create edit profile page"""
        self.edit_name = ft.TextField(
            label="Name",
            value=self.user_data["name"] if self.user_data and self.is_signed_in else "John Doe",
            border_color="#e0e0e0",
            border_radius=4,
        )
        
        self.edit_username = ft.TextField(
            label="Username",
            value=self.user_data["handle"] if self.user_data and self.is_signed_in else "@johndoe",
            border_color="#e0e0e0",
            border_radius=4,
        )
        
        self.edit_bio = ft.TextField(
            label="Bio",
            value="Tech enthusiast | Building the future one line of code at a time 🚀",
            multiline=True,
            min_lines=3,
            max_lines=5,
            border_color="#e0e0e0",
            border_radius=4,
        )
        
        self.edit_location = ft.TextField(
            label="Location",
            value="San Francisco, CA",
            border_color="#e0e0e0",
            border_radius=4,
        )
        
        self.edit_website = ft.TextField(
            label="Website",
            value="johndoe.dev",
            border_color="#e0e0e0",
            border_radius=4,
        )
        
        self.avatar_preview = ft.Container(
            width=80,
            height=80,
            border_radius=40,
            image_src=self.user_data["picture"] if self.user_data and self.is_signed_in else "https://abs.twimg.com/sticky/default_profile_images/default_profile_normal.png",
            image_fit=ft.ImageFit.COVER,
        )
        
        self.edit_profile_page = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.IconButton(
                                    icon=ft.icons.CLOSE,
                                    icon_size=18,
                                    on_click=lambda _: self.close_edit_profile(),
                                ),
                                ft.Text("Edit profile", size=16, weight=ft.FontWeight.BOLD, expand=True, text_align=ft.TextAlign.CENTER),
                                ft.ElevatedButton(
                                    content=ft.Text("Save", color="#ffffff"),
                                    style=ft.ButtonStyle(
                                        bgcolor="#1d9bf0",
                                        shape=ft.RoundedRectangleBorder(radius=20),
                                    ),
                                    on_click=lambda _: self.save_profile(),
                                ),
                            ],
                        ),
                        padding=ft.padding.symmetric(horizontal=16, vertical=12),
                        border=ft.border.only(bottom=ft.border.BorderSide(1, "#e0e0e0")),
                        bgcolor="#ffffff",
                    ),
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                self.edit_name,
                                self.edit_username,
                                self.edit_bio,
                                self.edit_location,
                                self.edit_website,
                                ft.Text("Profile photo", size=14, color="#536471"),
                                ft.Row(
                                    controls=[
                                        self.avatar_preview,
                                        ft.ElevatedButton(
                                            content=ft.Text("Change photo"),
                                            style=ft.ButtonStyle(
                                                color="#000000",
                                                bgcolor="#ffffff",
                                                side=ft.BorderSide(1, "#cfd9de"),
                                                shape=ft.RoundedRectangleBorder(radius=20),
                                            ),
                                            on_click=lambda _: self.change_profile_picture(),
                                        ),
                                    ],
                                    spacing=16,
                                ),
                                ft.Text("Banner", size=14, color="#536471"),
                                ft.ElevatedButton(
                                    content=ft.Row(
                                        controls=[
                                            ft.Icon(ft.icons.IMAGE, size=20),
                                            ft.Text("Edit Banner"),
                                        ],
                                        spacing=12,
                                    ),
                                    style=ft.ButtonStyle(
                                        color="#000000",
                                        bgcolor="#ffffff",
                                        side=ft.BorderSide(2, "#cfd9de"),
                                        shape=ft.RoundedRectangleBorder(radius=12),
                                    ),
                                    width=400,
                                    height=60,
                                    on_click=lambda _: self.open_banner_settings(),
                                ),
                            ],
                            spacing=24,
                        ),
                        padding=20,
                        expand=True,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                ],
                spacing=0,
            ),
            bgcolor="#ffffff",
            visible=False,
            expand=True,
        )
    
    def create_banner_settings_page(self):
        """Create banner settings page"""
        self.banner_preview = ft.Container(
            height=150,
            bgcolor="#f0f0f0",
            border=ft.border.all(2, "#e0e0e0", ft.BorderStyle.DASHED),
            border_radius=8,
        )
        
        self.no_banner_message = ft.Column(
            controls=[
                ft.Icon(ft.icons.IMAGE, size=48, color="#cfd9de"),
                ft.Text("No banner selected", size=14, color="#536471"),
                ft.Text("Upload an image to set as your banner", size=12, color="#536471"),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=16,
        )
        
        self.zoom_slider = ft.Slider(
            min=50,
            max=200,
            value=100,
            divisions=150,
            label="{value}%",
            on_change=lambda e: self.update_zoom(e.control.value),
        )
        
        self.zoom_level = ft.Text("100%", size=14)
        
        self.position_slider = ft.Slider(
            min=0,
            max=100,
            value=50,
            divisions=100,
            label="{value}%",
            on_change=lambda e: self.update_position(e.control.value),
        )
        
        self.position_level = ft.Text("50%", size=14)
        
        self.crop_controls = ft.Column(
            controls=[
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[ft.Text("Zoom:", size=14, color="#536471"), self.zoom_level],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            self.zoom_slider,
                        ],
                        spacing=4,
                    ),
                    margin=ft.margin.only(bottom=16),
                ),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[ft.Text("Position:", size=14, color="#536471"), self.position_level],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            self.position_slider,
                        ],
                        spacing=4,
                    ),
                    margin=ft.margin.only(bottom=16),
                ),
                ft.Row(
                    controls=[
                        ft.ElevatedButton(
                            content=ft.Text("Reset"),
                            style=ft.ButtonStyle(
                                color="#000000",
                                bgcolor="#ffffff",
                                side=ft.BorderSide(1, "#cfd9de"),
                                shape=ft.RoundedRectangleBorder(radius=20),
                            ),
                            expand=True,
                            on_click=lambda _: self.reset_banner_crop(),
                        ),
                        ft.ElevatedButton(
                            content=ft.Text("Save Banner"),
                            style=ft.ButtonStyle(
                                color="#ffffff",
                                bgcolor="#1d9bf0",
                                shape=ft.RoundedRectangleBorder(radius=20),
                            ),
                            expand=True,
                            on_click=lambda _: self.save_banner(),
                        ),
                    ],
                    spacing=12,
                ),
            ],
            visible=False,
        )
        
        self.banner_settings_page = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.IconButton(
                                    icon=ft.icons.ARROW_BACK,
                                    icon_size=18,
                                    on_click=lambda _: self.close_banner_settings(),
                                ),
                                ft.Text("Edit Banner", size=16, weight=ft.FontWeight.BOLD, expand=True, text_align=ft.TextAlign.CENTER),
                                ft.ElevatedButton(
                                    content=ft.Text("Save", color="#ffffff"),
                                    style=ft.ButtonStyle(
                                        bgcolor="#1d9bf0",
                                        shape=ft.RoundedRectangleBorder(radius=20),
                                    ),
                                    on_click=lambda _: self.save_banner(),
                                ),
                            ],
                        ),
                        padding=ft.padding.symmetric(horizontal=16, vertical=12),
                        border=ft.border.only(bottom=ft.border.BorderSide(1, "#e0e0e0")),
                        bgcolor="#ffffff",
                    ),
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                self.banner_preview,
                                ft.Container(
                                    content=self.no_banner_message,
                                    margin=ft.margin.symmetric(vertical=20),
                                ),
                                ft.ElevatedButton(
                                    content=ft.Row(
                                        controls=[
                                            ft.Icon(ft.icons.UPLOAD, size=20),
                                            ft.Text("Upload Banner Image"),
                                        ],
                                        spacing=12,
                                    ),
                                    style=ft.ButtonStyle(
                                        color="#000000",
                                        bgcolor="#ffffff",
                                        side=ft.BorderSide(2, "#cfd9de", ft.BorderStyle.DASHED),
                                        shape=ft.RoundedRectangleBorder(radius=12),
                                    ),
                                    width=400,
                                    height=60,
                                    on_click=lambda _: self.upload_banner_image(),
                                ),
                                self.crop_controls,
                            ],
                            spacing=20,
                        ),
                        padding=20,
                        expand=True,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                ],
                spacing=0,
            ),
            bgcolor="#ffffff",
            visible=False,
            expand=True,
        )
    
    def switch_tab(self, tab):
        """Switch between For You and Following tabs"""
        self.current_tab = tab
        if tab == "for_you":
            self.for_you_tab.content.color = "#000000"
            self.following_tab.content.color = "#536471"
            self.tab_indicator.left = 0
        else:
            self.for_you_tab.content.color = "#536471"
            self.following_tab.content.color = "#000000"
            self.tab_indicator.left = 200
        self.page.update()
    
    def switch_nav(self, index):
        """Switch bottom navigation"""
        self.show_alert(f"Navigation to {index} coming soon!")
    
    def toggle_sidebar(self):
        """Toggle sidebar visibility"""
        if self.sidebar.visible:
            self.sidebar.visible = False
            self.sidebar_overlay.visible = False
            self.sidebar.right = -280
        else:
            self.sidebar.visible = True
            self.sidebar_overlay.visible = True
            self.sidebar.right = 0
        self.page.update()
    
    def open_profile(self, e=None):
        """Open profile page"""
        self.toggle_sidebar()
        if not self.is_signed_in:
            self.signin_page.visible = True
        else:
            self.profile_page.visible = True
        self.page.update()
    
    def close_profile(self):
        """Close profile page"""
        self.profile_page.visible = False
        self.page.update()
    
    def close_signin(self):
        """Close sign in page"""
        self.signin_page.visible = False
        self.page.update()
    
    def open_edit_profile(self):
        """Open edit profile page"""
        self.profile_page.visible = False
        self.edit_profile_page.visible = True
        self.page.update()
    
    def close_edit_profile(self):
        """Close edit profile page"""
        self.edit_profile_page.visible = False
        self.profile_page.visible = True
        self.page.update()
    
    def open_banner_settings(self):
        """Open banner settings page"""
        self.banner_settings_page.visible = True
        if self.current_banner_image:
            self.update_banner_preview()
        else:
            self.no_banner_message.visible = True
            self.crop_controls.visible = False
        self.page.update()
    
    def close_banner_settings(self):
        """Close banner settings page"""
        self.banner_settings_page.visible = False
        self.page.update()
    
    def upload_banner_image(self):
        """Upload banner image"""
        def pick_files_result(e: ft.FilePickerResultEvent):
            if e.files:
                file_path = e.files[0].path
                with open(file_path, "rb") as f:
                    image_data = base64.b64encode(f.read()).decode()
                    self.current_banner_image = f"data:image/jpeg;base64,{image_data}"
                    self.banner_zoom = 100
                    self.banner_position = 50
                    self.update_banner_preview()
                    self.no_banner_message.visible = False
                    self.crop_controls.visible = True
                    self.page.update()
        
        file_picker = ft.FilePicker(on_result=pick_files_result)
        self.page.overlay.append(file_picker)
        self.page.update()
        file_picker.pick_files(allow_multiple=False, allowed_extensions=["png", "jpg", "jpeg", "gif"])
    
    def update_banner_preview(self):
        """Update banner preview with current settings"""
        if self.current_banner_image:
            self.banner_preview.image_src = f"{self.current_banner_image}&t={self.banner_cache_buster}"
            self.banner_preview.image_fit = ft.ImageFit.COVER
            self.banner_preview.gradient = None
            self.no_banner_message.visible = False
            self.crop_controls.visible = True
        else:
            self.no_banner_message.visible = True
            self.crop_controls.visible = False
        self.page.update()
    
    def update_profile_banner(self):
        """Update profile banner"""
        if self.current_banner_image:
            self.banner_cache_buster += 1
            self.profile_banner.image_src = f"{self.current_banner_image}&t={self.banner_cache_buster}"
            self.profile_banner.image_fit = ft.ImageFit.COVER
            self.profile_banner.gradient = None
        else:
            self.profile_banner.image_src = None
            self.profile_banner.gradient = ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=["#667eea", "#764ba2"],
            )
        self.page.update()
    
    def update_zoom(self, value):
        """Update zoom level"""
        self.banner_zoom = value
        self.zoom_level.value = f"{int(value)}%"
        self.page.update()
    
    def update_position(self, value):
        """Update position level"""
        self.banner_position = value
        self.position_level.value = f"{int(value)}%"
        self.page.update()
    
    def reset_banner_crop(self):
        """Reset banner crop settings"""
        self.banner_zoom = 100
        self.banner_position = 50
        self.zoom_slider.value = 100
        self.position_slider.value = 50
        self.zoom_level.value = "100%"
        self.position_level.value = "50%"
        self.page.update()
    
    def save_banner(self):
        """Save banner settings"""
        if self.current_banner_image and self.is_signed_in and self.user_data:
            self.user_data["banner"] = self.current_banner_image
            self.user_data["banner_zoom"] = self.banner_zoom
            self.user_data["banner_position"] = self.banner_position
            self.user_data["banner_cache_buster"] = self.banner_cache_buster
            self.save_user_data()
            self.update_profile_banner()
            self.close_banner_settings()
            self.show_alert("Banner saved successfully!")
        else:
            self.show_alert("Please upload a banner image first.")
    
    def change_profile_picture(self):
        """Change profile picture"""
        def pick_files_result(e: ft.FilePickerResultEvent):
            if e.files:
                file_path = e.files[0].path
                with open(file_path, "rb") as f:
                    image_data = base64.b64encode(f.read()).decode()
                    new_image = f"data:image/jpeg;base64,{image_data}"
                    
                    self.header_profile_btn.image_src = new_image
                    self.profile_avatar.image_src = new_image
                    self.avatar_preview.image_src = new_image
                    
                    if self.is_signed_in and self.user_data:
                        self.user_data["picture"] = new_image
                        self.save_user_data()
                    
                    self.show_alert("Profile picture changed successfully!")
                    self.page.update()
        
        file_picker = ft.FilePicker(on_result=pick_files_result)
        self.page.overlay.append(file_picker)
        self.page.update()
        file_picker.pick_files(allow_multiple=False, allowed_extensions=["png", "jpg", "jpeg", "gif"])
    
    def save_profile(self):
        """Save profile changes"""
        name = self.edit_name.value
        username = self.edit_username.value
        bio = self.edit_bio.value
        location = self.edit_location.value
        website = self.edit_website.value
        
        self.profile_name.value = name
        self.profile_handle.value = username
        self.profile_bio.value = bio
        self.profile_location.value = location
        self.profile_website.value = website
        
        if self.is_signed_in and self.user_data:
            self.user_data["name"] = name
            self.user_data["handle"] = username
            self.user_data["location"] = location
            self.user_data["website"] = website
            self.save_user_data()
        
        self.close_edit_profile()
        self.show_alert("Profile saved successfully!")
    
    def login_with_google(self):
        """Login with Google (simulated)"""
        self.show_alert("Google login is simulated. Please use Demo Account.")
        self.use_demo_account()
    
    def use_demo_account(self):
        """Use demo account"""
        self.user_data = {
            "name": "Demo User",
            "email": "demo@example.com",
            "picture": "https://api.dicebear.com/7.x/avataaars/svg?seed=DemoUser",
            "handle": "@demouser",
            "location": "San Francisco, CA",
            "website": "johndoe.dev",
            "banner": None,
            "banner_zoom": 100,
            "banner_position": 50,
            "banner_cache_buster": 0
        }
        
        self.is_signed_in = True
        self.save_user_data()
        self.update_profile_ui()
        self.close_signin()
        self.show_alert("Welcome, Demo User!")
    
    def sign_out(self):
        """Sign out user"""
        self.user_data = None
        self.is_signed_in = False
        self.current_banner_image = None
        self.banner_zoom = 100
        self.banner_position = 50
        self.banner_cache_buster = 0
        
        if os.path.exists("user_data.json"):
            os.remove("user_data.json")
        
        # Reset UI
        self.header_profile_btn.image_src = "https://pbs.twimg.com/profile_images/1536443352228368384/x-XyfcPq.jpg"
        self.profile_avatar.image_src = "https://abs.twimg.com/sticky/default_profile_images/default_profile_normal.png"
        self.profile_name.value = "John Doe"
        self.profile_handle.value = "@johndoe"
        self.profile_bio.value = "Tech enthusiast | Building the future one line of code at a time 🚀"
        self.profile_location.value = "San Francisco, CA"
        self.profile_website.value = "johndoe.dev"
        self.avatar_preview.image_src = "https://abs.twimg.com/sticky/default_profile_images/default_profile_normal.png"
        self.edit_name.value = "John Doe"
        self.edit_username.value = "@johndoe"
        self.edit_location.value = "San Francisco, CA"
        self.edit_website.value = "johndoe.dev"
        
        # Reset banner
        self.profile_banner.image_src = None
        self.profile_banner.gradient = ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=["#667eea", "#764ba2"],
        )
        
        self.close_profile()
        self.show_alert("Signed out successfully!")
        self.page.update()
    
    def update_profile_ui(self):
        """Update profile UI with user data"""
        if not self.user_data:
            return
        
        self.header_profile_btn.image_src = self.user_data["picture"]
        self.profile_avatar.image_src = self.user_data["picture"]
        self.profile_name.value = self.user_data["name"]
        self.profile_handle.value = self.user_data["handle"]
        self.avatar_preview.image_src = self.user_data["picture"]
        self.edit_name.value = self.user_data["name"]
        self.edit_username.value = self.user_data["handle"]
        
        if self.user_data.get("location"):
            self.profile_location.value = self.user_data["location"]
            self.edit_location.value = self.user_data["location"]
        
        if self.user_data.get("website"):
            self.profile_website.value = self.user_data["website"]
            self.edit_website.value = self.user_data["website"]
        
        if self.user_data.get("banner"):
            self.current_banner_image = self.user_data["banner"]
            self.banner_zoom = self.user_data.get("banner_zoom", 100)
            self.banner_position = self.user_data.get("banner_position", 50)
            self.banner_cache_buster = self.user_data.get("banner_cache_buster", 0)
            self.update_profile_banner()
        
        self.page.update()
    
    def show_alert(self, message):
        """Show alert dialog"""
        def close_dialog(e):
            page.dialog.open = False
            page.update()
        
        page = self.page
        page.dialog = ft.AlertDialog(
            title=ft.Text("Info"),
            content=ft.Text(message),
            actions=[ft.TextButton("OK", on_click=close_dialog)],
        )
        page.dialog.open = True
        page.update()

def main(page: ft.Page):
    app = XAppFeed()
    app.main(page)

if __name__ == "__main__":
    ft.app(target=main)