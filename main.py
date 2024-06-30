import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
import requests

kivy.require('1.11.1')

def find_instagram_profile(user_id):
    url = f"https://i.instagram.com/api/v1/users/{user_id}/info/"
    headers = {
        'User-Agent': 'Instagram 10.3.2 (iPhone7,2; iPhone OS 9_3_3; en_US; en-US; scale=2.00; 750x1334) AppleWebKit/420+',
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        user_info = response.json()
        username = user_info['user']['username']
        return username
    else:
        return "Unable to retrieve profile."

def find_instagram_id_by_username(username):
    url = f"https://www.instagram.com/{username}/"
    response = requests.get(url)
    if response.status_code == 200:
        user_id_start = response.text.find('"profilePage_', 0) + len('"profilePage_')
        user_id_end = response.text.find('"', user_id_start)
        user_id = response.text[user_id_start:user_id_end]
        return user_id
    else:
        return None

class InstagramUserIDFinderApp(App):
    def build(self):
        self.title = "Instagram User ID Finder"

        self.option_var = "user_id"

        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Option selection
        options_layout = GridLayout(cols=2, size_hint_y=None, height=150)

        label_option = Label(text="Select search option:", font_size=18, color=(1, 1, 1, 1))
        options_layout.add_widget(label_option)
        options_layout.add_widget(Label())  # Empty cell for alignment

        button_user_id = Button(text="Enter User ID", on_press=self.select_user_id, font_size=16, background_color=(0.1, 0.6, 0.2, 1))
        options_layout.add_widget(button_user_id)
        
        button_user_id_file = Button(text="Upload User ID File", on_press=self.upload_user_id_file, font_size=16, background_color=(0.1, 0.6, 0.2, 1))
        options_layout.add_widget(button_user_id_file)

        button_username = Button(text="Enter Username", on_press=self.select_username, font_size=16, background_color=(0.1, 0.6, 0.2, 1))
        options_layout.add_widget(button_username)
        
        button_username_file = Button(text="Upload Username File", on_press=self.upload_username_file, font_size=16, background_color=(0.1, 0.6, 0.2, 1))
        options_layout.add_widget(button_username_file)

        main_layout.add_widget(options_layout)

        # User ID input
        self.label_user_id = Label(text="Enter User ID:", font_size=18, color=(1, 1, 1, 1))
        main_layout.add_widget(self.label_user_id)
        self.entry_user_id = TextInput(font_size=16)
        main_layout.add_widget(self.entry_user_id)

        # Username input
        self.label_username = Label(text="Enter Username:", font_size=18, color=(1, 1, 1, 1))
        main_layout.add_widget(self.label_username)
        self.entry_username = TextInput(font_size=16)
        main_layout.add_widget(self.entry_username)

        # Search button
        button_search = Button(text="Search", on_press=self.perform_search, size_hint_y=None, height=50, font_size=18, background_color=(0.1, 0.6, 0.2, 1))
        main_layout.add_widget(button_search)

        # Result text
        self.result_text = TextInput(readonly=True, size_hint_y=None, height=300, font_size=16, background_color=(0.2, 0.2, 0.2, 1), foreground_color=(1, 1, 1, 1))
        scroll_view = ScrollView(size_hint=(1, None), height=300)
        scroll_view.add_widget(self.result_text)
        main_layout.add_widget(scroll_view)

        self.update_visibility()
        
        return main_layout

    def update_visibility(self):
        self.label_user_id.opacity = 1 if self.option_var == "user_id" else 0
        self.entry_user_id.opacity = 1 if self.option_var == "user_id" else 0
        self.label_username.opacity = 1 if self.option_var == "username" else 0
        self.entry_username.opacity = 1 if self.option_var == "username" else 0

    def select_user_id(self, instance):
        self.option_var = "user_id"
        self.update_visibility()

    def select_username(self, instance):
        self.option_var = "username"
        self.update_visibility()

    def upload_user_id_file(self, instance):
        self.option_var = "user_id_file"
        self.show_file_chooser(self.search_by_user_ids_from_file)

    def upload_username_file(self, instance):
        self.option_var = "username_file"
        self.show_file_chooser(self.search_by_usernames_from_file)

    def show_file_chooser(self, callback):
        file_chooser = FileChooserIconView()
        popup = Popup(title="Select File", content=file_chooser, size_hint=(0.9, 0.9))

        def on_selection(instance, selection):
            if selection:
                callback(selection[0])
            popup.dismiss()

        file_chooser.bind(on_selection=on_selection)
        popup.open()

    def perform_search(self, instance):
        self.result_text.text = ""
        if self.option_var == "user_id":
            self.search_by_user_id()
        elif self.option_var == "user_id_file":
            self.search_by_user_ids_from_file(self.file_path)
        elif self.option_var == "username":
            self.search_by_username()
        elif self.option_var == "username_file":
            self.search_by_usernames_from_file(self.file_path)

    def search_by_user_id(self):
        user_id = self.entry_user_id.text
        if user_id:
            username = find_instagram_profile(user_id)
            self.result_text.text += f"User ID: {user_id}\nUsername: {username}\n" + "-"*50 + "\n"
        else:
            self.show_warning("Input Error", "Please enter a user ID")

    def search_by_user_ids_from_file(self, file_path):
        with open(file_path, 'r') as file:
            user_ids = [line.strip() for line in file]
        for user_id in user_ids:
            username = find_instagram_profile(user_id)
            self.result_text.text += f"User ID: {user_id}\nUsername: {username}\n" + "-"*50 + "\n"

    def search_by_username(self):
        username = self.entry_username.text
        if username:
            user_id = find_instagram_id_by_username(username)
            if user_id:
                self.result_text.text += f"Username: {username}\nUser ID: {user_id}\n" + "-"*50 + "\n"
            else:
                self.result_text.text += f"Username: {username}\nUnable to retrieve user ID\n" + "-"*50 + "\n"
        else:
            self.show_warning("Input Error", "Please enter a username")

    def search_by_usernames_from_file(self, file_path):
        with open(file_path, 'r') as file:
            usernames = [line.strip() for line in file]
        for username in usernames:
            user_id = find_instagram_id_by_username(username)
            if user_id:
                self.result_text.text += f"Username: {username}\nUser ID: {user_id}\n" + "-"*50 + "\n"
            else:
                self.result_text.text += f"Username: {username}\nUnable to retrieve user ID\n" + "-"*50 + "\n"

    def show_warning(self, title, message):
        popup = Popup(title=title, content=Label(text=message), size_hint=(0.6, 0.4))
        popup.open()

if __name__ == '__main__':
    InstagramUserIDFinderApp().run()
