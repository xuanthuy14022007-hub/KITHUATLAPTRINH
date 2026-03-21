from PyQt6.QtWidgets import QWidget, QMessageBox
from PyQt6 import uic

from utils.window_manager import get_current_user, set_current_user, switch_window
from logic.logic_nguoi_dung import lay_thong_tin_nguoi_dung
from screens.home_chu_vua_screen import ChuVuaDashboardScreen
from screens.danh_sach_cay_trong_screen import DanhSachCayTrongScreen
from screens.danh_sach_don_hang_chu_vua_screen import DanhSachDonHangScreen
from screens.login_screen import LoginScreen

class ProfileChuVuaScreen(QWidget):

    def __init__(self):
        super().__init__()
        uic.loadUi("ui_files/profile_chu_vua.ui", self)
        if hasattr(self, "btn_menu_trang_chu"):
            self.btn_menu_trang_chu.clicked.connect(self.ve_trang_chu)
        if hasattr(self, "btn_menu_giao_thuong"):
            self.btn_menu_giao_thuong.clicked.connect(self.mo_giao_thuong)
        if hasattr(self, "btn_menu_ho_so"):
            self.btn_menu_ho_so.clicked.connect(self.reload_profile)
        if hasattr(self, "btn_dang_xuat"):
            self.btn_dang_xuat.clicked.connect(self.dang_xuat)
        if hasattr(self, "btn_chinh_sua"):
            self.btn_chinh_sua.clicked.connect(self.mo_chinh_sua)

        self.tai_du_lieu()

    def tai_du_lieu(self):
        user = get_current_user()
        if not user:
            return
        user_id = user.get("user_id")
        thong_tin = lay_thong_tin_nguoi_dung(user_id)
        if not thong_tin:
            return

        (
            user_id,
            username,
            role,
            full_name,
            email,
            address,
            farm_name,
            description
        ) = thong_tin

        if hasattr(self, "lbl_profile_name"):
            self.lbl_profile_name.setText(full_name or username)
        if hasattr(self, "lbl_profile_farm"):
            self.lbl_profile_farm.setText(farm_name or "")
        if hasattr(self, "lbl_profile_loc"):
            self.lbl_profile_loc.setText(address or "")
        if hasattr(self, "lbl_email_val"):
            self.lbl_email_val.setText(email or "")
        if hasattr(self, "lbl_phone_val"):
            self.lbl_phone_val.setText("0123456789")
        if hasattr(self, "lbl_addr_val"):
            self.lbl_addr_val.setText(address or "")
        if hasattr(self, "lbl_mota_desc"):
            self.lbl_mota_desc.setText(description or "")

    def mo_chinh_sua(self):
        switch_window(EditProfileChuVuaScreen())

    def ve_trang_chu(self):
        switch_window(ChuVuaDashboardScreen())

    def mo_giao_thuong(self):
        switch_window(SearchListMatHangScreen())

    def reload_profile(self):
        switch_window(ProfileChuVuaScreen())

    def dang_xuat(self):
        reply = QMessageBox.question(
            self,
            "Xác nhận",
            "Bạn có chắc chắn muốn đăng xuất?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            set_current_user(None)
            switch_window(LoginScreen())
