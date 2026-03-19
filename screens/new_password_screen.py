from PyQt6.QtWidgets import QWidget, QMessageBox
from PyQt6 import uic

from utils.window_manager import switch_window
from logic.logic_dang_nhap import reset_password

class NewPasswordScreen(QWidget):
    def __init__(self, username=None):
        super().__init__()
        self.username = username
        uic.loadUi("ui_files/new_password.ui", self)

        if hasattr(self, 'btn_luu'):
            self.btn_luu.clicked.connect(self.ve_man_hinh_login)

    def ve_man_hinh_login(self):
        if (hasattr(self, 'txt_mat_khau_moi') and not self.txt_mat_khau_moi.text() or
                hasattr(self, 'txt_xac_nhan_mat_khau') and not self.txt_xac_nhan_mat_khau.text()):
            QMessageBox.warning(self, "Thông báo", "Vui lòng nhập đầy đủ Mật khẩu mới và Xác nhận mật khẩu!")
            return

        if hasattr(self, 'txt_mat_khau_moi') and hasattr(self, 'txt_xac_nhan_mat_khau'):
            if self.txt_mat_khau_moi.text() != self.txt_xac_nhan_mat_khau.text():
                QMessageBox.warning(self, "Lỗi", "Mật khẩu xác nhận không khớp!")
                return

        if not self.username:
            QMessageBox.warning(self, "Lỗi", "Không xác định được tài khoản!")
            return

        success = reset_password(self.username, self.txt_mat_khau_moi.text().strip())
        if success:
            QMessageBox.information(self, "Thành công", "Mật khẩu đã được cập nhật! Vui lòng đăng nhập lại.")
            from screens.login_screen import LoginScreen
            switch_window(LoginScreen())
        else:
            QMessageBox.warning(self, "Lỗi", "Cập nhật thất bại!")
