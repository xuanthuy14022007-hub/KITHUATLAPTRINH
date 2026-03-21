from PyQt6.QtWidgets import QWidget
from PyQt6 import uic

from utils.window_manager import switch_window
from logic.logic_dang_nhap import kiem_tra_ton_tai_user
from screens.otp_screen import OtpScreen
from screens.login_screen import LoginScreen
from PyQt6.QtWidgets import QMessageBox

class ForgotKeyScreen(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui_files/forgot_key.ui", self)

        if hasattr(self, 'lbl_quay_lai'):
            self.lbl_quay_lai.mousePressEvent = self.quay_lai_login
        if hasattr(self, 'btn_gui_email'):
            self.btn_gui_email.clicked.connect(self.chuyen_sang_otp)

    def quay_lai_login(self, event):
        switch_window(LoginScreen())

    def chuyen_sang_otp(self):
        identifier = self.txt_email_sdt.text().strip() if hasattr(self, 'txt_email_sdt') else ''
        if not identifier:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập Email hoặc Số điện thoại!")
            return
            
        username = kiem_tra_ton_tai_user(identifier)
        if not username:
            QMessageBox.warning(self, "Lỗi", "Tài khoản không tồn tại!")
            return
        switch_window(OtpScreen(username))
