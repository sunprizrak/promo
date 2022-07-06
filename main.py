from kivymd.app import MDApp
from kivy.graphics.svg import Window
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.picker import MDDatePicker
import requests
from user import User


Window.size = (360, 600)


class PromoApp(MDApp):
    user = User()
    host_name = 'http://127.0.0.1:8000'
    path_reg = host_name + '/auth/users/'
    path_login = host_name + '/auth/token/login/'
    path_logout = host_name + '/auth/token/logout/'
    path_data_user = host_name + '/auth/users/me/'
    dialog = None

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
        self.root.ids.reg_screen.ids.reg_birth_date.text = str(value)

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
                    if el == 'birth_date':
                        self.root.ids.reg_screen.ids.get(f'reg_{el}').helper_text = data_reg.json()[el][0].split('.')[1]
                    elif el == 'password':
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

    def sing_in(self, email, password):
        self.user.get_token(path=self.path_login, email=email, password=password)
        if self.user.token:
            self.user.update(self.user.data_user(path=self.path_data_user, token=self.user.token))
            self.root.ids.personal_area_screen.ids.profile_avatar.source = self.user.avatar
            self.root.ids.personal_area_screen.ids.profile_full_name.text = f'{self.user.first_name} {self.user.last_name} {self.user.middle_name}'
            self.root.ids.personal_area_screen.ids.profile_email.text = self.user.email
            self.root.ids.personal_area_screen.ids.profile_birth_date.text = self.user.birth_date
            self.root.ids.personal_area_screen.ids.profile_position.text = self.user.position
            self.root.ids.personal_area_screen.ids.profile_phone_number.text = self.user.phone_number
            self.root.ids.personal_area_screen.ids.profile_site_one.text = self.user.site_one
            self.root.ids.personal_area_screen.ids.profile_site_two.text = self.user.site_two
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

    def logout(self):
        self.user.del_token(path=self.path_logout, token=self.user.token)
        self.root.current = 'start_screen'


if __name__ == '__main__':
    PromoApp().run()
