from kivymd.app import MDApp
from kivy.graphics.svg import Window
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.picker import MDDatePicker
from user import User
import requests

Window.size = (360, 600)


class PromoApp(MDApp):
    user = User()
    host_name = 'http://127.0.0.1:8000'
    path_reg = host_name + '/auth/users/'
    path_login = host_name + '/auth/token/login/'
    path_logout = host_name + '/auth/token/logout/'
    path_data_user = host_name + '/auth/users/me/'
    dialog = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        menu_items = [
            {
                'text': 'Редактировать',
                'viewclass': 'OneLineListItem',
                'on_release': lambda x='profile_edit_screen': (self.menu.dismiss(), self.update_screen(x), setattr(self.root, 'current', x)),
            },
            {
                'text': 'Выйти',
                'viewclass': 'OneLineListItem',
                'on_release': lambda: (self.menu.dismiss(), self.logout()),
            },
        ]
        self.menu = MDDropdownMenu(
            items=menu_items,
            width_mult=2.5,
        )
        self.manager_open = False
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            preview=True,
        )

    def file_manager_open(self):
        self.file_manager.show('/')
        self.manager_open = True

    def select_path(self, path):
        self.exit_manager()
        if self.root.current == 'profile_edit_screen':
            self.root.ids.prof_ed_screen.ids.edit_avatar.text = path

    def exit_manager(self, *args):
        self.manager_open = False
        self.file_manager.close()

    def events(self, instance, keyboard, keycode, text, modifiers):
        if keyboard in (1001, 27):
            if self.manager_open:
                self.file_manager.back()
        return True

    def menu_callback(self, button):
        self.menu.caller = button
        self.menu.open()

    def show_alert_dialog(self):
        self.dialog = MDDialog(
            title='Внимание!',
            buttons=[
                MDFlatButton(
                    text="Закрыть",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release=self.close_dialog,
                ),
            ],
        )
        self.dialog.open()

    def close_dialog(self, inst):
        self.dialog.dismiss()

    def on_save_date_picker(self, instance, value, date_range):
        if self.root.current == 'registration_screen':
            self.root.ids.reg_screen.ids.reg_birth_date.text = str(value)
        elif self.root.current == 'profile_edit_screen':
            self.root.ids.prof_ed_screen.ids.edit_birth_date.text = str(value)

    def on_cancel_date_picker(self, instance, value):
        pass

    def show_date_picker(self):
        date_dialog = MDDatePicker(min_year=1970, max_year=2022)
        date_dialog.bind(on_save=self.on_save_date_picker, on_cancel=self.on_cancel_date_picker)
        date_dialog.open()

    def registration(self, *args):
        email, first_name, last_name, middle_name, birth_date, phone_number, password, password2 = args
        data_reg = requests.post(self.path_reg,
                                 data={'email': email,
                                       'first_name': first_name,
                                       'last_name': last_name,
                                       'middle_name': middle_name,
                                       'birth_date': birth_date,
                                       'phone_number': phone_number,
                                       'password': password,
                                       're_password': password2, })
        if data_reg.__dict__.get('status_code') == 201:
            self.sing_in(email=email, password=password)
        elif data_reg.__dict__.get('status_code') == 400:
            for el in data_reg.json():
                if f'reg_{el}' in self.root.ids.reg_screen.ids:
                    if len(self.root.ids.reg_screen.ids.get(f'reg_{el}').text) > 0:
                        if el != 'password':
                            self.root.ids.reg_screen.ids.get(f'reg_{el}').error = True
                    self.root.ids.reg_screen.ids.get(f'reg_{el}').focus = True
                    self.root.ids.reg_screen.ids.get(f'reg_{el}').focus = False
                    if el == 'password':
                        self.show_alert_dialog()
                        self.dialog.text = ''.join([f'! {item} \n' for item in data_reg.json().get(el)])
                    else:
                        self.root.ids.reg_screen.ids.get(f'reg_{el}').helper_text = data_reg.json()[el][0]
                elif el == 'non_field_errors':
                    for item in ('password', 're_password'):
                        self.root.ids.reg_screen.ids.get(f'reg_{item}').error = True
                        self.root.ids.reg_screen.ids.get(f'reg_{item}').focus = True
                        self.root.ids.reg_screen.ids.get(f'reg_{item}').focus = False
                        self.root.ids.reg_screen.ids.get(f'reg_{item}').helper_text = data_reg.json()[el][0]

    def update_screen(self, screen):
        if screen == 'personal_area_screen':
            for el in self.root.ids.personal_area_screen.ids:
                if el[8:] in self.user.__dict__:
                    if el[8:] == 'avatar':
                        self.root.ids.personal_area_screen.ids[el].source = self.user.__dict__[el[8:]]
                    else:
                        self.root.ids.personal_area_screen.ids[el].text = self.user.__dict__[el[8:]]
                elif el[8:] == 'full_name':
                    self.root.ids.personal_area_screen.ids[el].text = f'{self.user.last_name} {self.user.first_name} {self.user.middle_name}'
        elif screen == 'profile_edit_screen':
            for el in self.root.ids.prof_ed_screen.ids:
                if el[5:] in self.user.__dict__:
                    if el[5:] == 'avatar':
                        self.root.ids.prof_ed_screen.ids[el].text = ''
                    else:
                        self.root.ids.prof_ed_screen.ids[el].text = self.user.__dict__[el[5:]]

    def sing_in(self, email, password):
        self.user.get_token(path=self.path_login, email=email, password=password)
        if self.user.token:
            self.user.update(self.user.data_user(path=self.path_data_user, token=self.user.token))
            self.update_screen('personal_area_screen')
            if self.root.current == 'login_screen':
                self.root.ids.log_screen.ids.email_field.text = ''
                self.root.ids.log_screen.ids.password_field.text = ''
            elif self.root.current == 'registration_screen':
                for el in self.root.ids.reg_screen.ids:
                    if el[:3] == 'reg':
                        self.root.ids.reg_screen.ids.get(el).text = ''
            self.root.current = 'personal_area_screen'
        else:
            self.show_alert_dialog()
            self.dialog.text = '! Неверно введён email или пароль'

    def edit_profile(self, *args):
        email, first_name, last_name, middle_name, birth_date, phone_number, site_one, site_two, avatar = args
        img = {'avatar': open(avatar, 'rb')} if avatar else None
        data_user = requests.patch(self.path_data_user, files=img, headers={'Authorization': f'Token {self.user.token}'}, data={
                                    'email': email,
                                    'first_name': first_name,
                                    'last_name': last_name,
                                    'middle_name': middle_name,
                                    'birth_date': birth_date,
                                    'phone_number': phone_number,
                                    'site_one': site_one,
                                    'site_two': site_two, })
        if data_user.__dict__.get('status_code') == 200:
            self.user.update(data_user.json())
            self.update_screen('personal_area_screen')
            self.show_alert_dialog()
            self.dialog.title = 'Успех'
            self.dialog.text = 'Данные Успешно изменены'
        elif data_user.__dict__.get('status_code') == 400:
            print(data_user.json())
            for el in data_user.json():
                if f'edit_{el}' in self.root.ids.prof_ed_screen.ids:
                    self.root.ids.prof_ed_screen.ids.get(f'edit_{el}').helper_text = data_user.json()[el][0]
                    self.root.ids.prof_ed_screen.ids.get(f'edit_{el}').error = True
                    self.root.ids.prof_ed_screen.ids.get(f'edit_{el}').focus = True
                    self.root.ids.prof_ed_screen.ids.get(f'edit_{el}').focus = False

    def logout(self):
        self.user.del_token(path=self.path_logout, token=self.user.token)
        self.root.current = 'start_screen'


if __name__ == '__main__':
    PromoApp().run()
