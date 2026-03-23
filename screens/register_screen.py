from PyQt6.QtWidgets import QWidget, QMessageBox
from PyQt6 import uic
from utils.window_manager import switch_window

class RegisterScreen(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui_files/register.ui", self)

        if hasattr(self, 'btn_dang_ky'):
            self.btn_dang_ky.clicked.connect(self.xu_ly_dang_ky)
        if hasattr(self, 'lbl_dctk'):
            self.lbl_dctk.mousePressEvent = self.quay_lai_login

    def xu_ly_dang_ky(self):
        if hasattr(self, 'chk_dieu_khoan') and not self.chk_dieu_khoan.isChecked():
            QMessageBox.warning(self, "Nhắc nhở", "Vui lòng đồng ý với Điều khoản & Chính sách để tiếp tục!")
            return

        if (hasattr(self, 'txt_ten_dang_nhap') and not self.txt_ten_dang_nhap.text() or
                hasattr(self, 'txt_mat_khau') and not self.txt_mat_khau.text()):
            QMessageBox.warning(self, "Thông báo", "Vui lòng nhập đầy đủ Tên đăng nhập và Mật khẩu!")
            return

        if hasattr(self, 'txt_mat_khau') and hasattr(self, 'txt_xac_nhan_mat_khau'):
            if self.txt_mat_khau.text() != self.txt_xac_nhan_mat_khau.text():
                QMessageBox.warning(self, "Lỗi", "Mật khẩu xác nhận không khớp!")
                return

        role = 'Farmer'
        if hasattr(self, 'rad_chu_vua') and self.rad_chu_vua.isChecked():
            role = 'Merchant'

        user_data = {
            'username': self.txt_ten_dang_nhap.text().strip(),
            'password': self.txt_mat_khau.text().strip(),
            'role': role
        }

        from screens.register_xacthuc_screen import RegisterXacThucScreen
        switch_window(RegisterXacThucScreen, user_data=user_data)

    def quay_lai_login(self, event):
        from screens.login_screen import LoginScreen
        switch_window(LoginScreen)
