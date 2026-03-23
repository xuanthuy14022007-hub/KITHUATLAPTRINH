from PyQt6.QtWidgets import QWidget, QMessageBox
from PyQt6 import uic
from utils.window_manager import switch_window, set_current_user
from logic.logic_dang_nhap import login

class LoginScreen(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui_files/login.ui", self)

        if hasattr(self, 'lbl_quen_mat_khau'):
            self.lbl_quen_mat_khau.mousePressEvent = self.mo_man_hinh_quen_mat_khau
        if hasattr(self, 'lbl_dang_ky'):
            self.lbl_dang_ky.mousePressEvent = self.mo_man_hinh_dang_ky
        if hasattr(self, 'btn_dang_nhap'):
            self.btn_dang_nhap.clicked.connect(self.xu_ly_dang_nhap)

    def xu_ly_dang_nhap(self):
        username = self.txt_ten_dang_nhap.text().strip() if hasattr(self, 'txt_ten_dang_nhap') else ''
        password = self.txt_mat_khau.text().strip() if hasattr(self, 'txt_mat_khau') else ''

        if not username or not password:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập Tên đăng nhập và Mật khẩu!")
            return

        chon_nong_dan = hasattr(self, 'rad_nong_dan') and self.rad_nong_dan.isChecked()
        chon_chu_vua = hasattr(self, 'rad_chu_vua') and self.rad_chu_vua.isChecked()

        if not chon_nong_dan and not chon_chu_vua:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn vai trò để đăng nhập!")
            return

        user = login(username, password)
        if not user:
            QMessageBox.warning(self, "Lỗi", "Tên đăng nhập hoặc mật khẩu không đúng!")
            return

        db_role = user[2]  # 'Farmer' hoặc 'Merchant'
        if chon_nong_dan and db_role != 'Farmer':
            QMessageBox.warning(self, "Lỗi", "Tài khoản này không phải Nông dân!")
            return
        if chon_chu_vua and db_role != 'Merchant':
            QMessageBox.warning(self, "Lỗi", "Tài khoản này không phải Thương lái!")
            return

        # Lưu thông tin user
        user_info = {
            'user_id': user[0], 'username': user[1], 'role': user[2],
            'full_name': user[3], 'email': user[4], 'address': user[5],
            'farm_name': user[6], 'description': user[7]
        }
        set_current_user(user_info)

        # Chuyển màn hình (lazy import)
        if chon_nong_dan:
            from screens.home_nong_dan_screen import NongDanDashboardScreen
            switch_window(NongDanDashboardScreen)
        else:
            from screens.home_chu_vua_screen import ChuVuaDashboardScreen
            switch_window(ChuVuaDashboardScreen)

    def mo_man_hinh_quen_mat_khau(self, event):
        from screens.forgot_key_screen import ForgotKeyScreen
        switch_window(ForgotKeyScreen)

    def mo_man_hinh_dang_ky(self, event):
        from screens.register_screen import RegisterScreen
        switch_window(RegisterScreen)
