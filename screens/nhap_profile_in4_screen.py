from PyQt6.QtWidgets import QWidget, QMessageBox, QFileDialog
from PyQt6.QtGui import QPixmap
from PyQt6 import uic

from utils.window_manager import switch_window


from logic.logic_dang_nhap import register

class NhapProfileInfoScreen(QWidget):
    def __init__(self, user_data=None):
        super().__init__()
        self.user_data = user_data or {}
        uic.loadUi("ui_files/nhap_profile_in4.ui", self)

        if hasattr(self, 'btn_hoan_thanh'):
            self.btn_hoan_thanh.clicked.connect(self.hoan_tat_profile)
        if hasattr(self, 'lbl_avatar'):
            self.lbl_avatar.mousePressEvent = self.chon_anh_dai_dien

    def chon_anh_dai_dien(self, event):
        file_name, _ = QFileDialog.getOpenFileName(self, "Chọn ảnh đại diện", "",
                                                   "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if file_name:
            pixmap = QPixmap(file_name)
            self.lbl_avatar.setPixmap(pixmap)
            self.lbl_avatar.setScaledContents(True)

    def hoan_tat_profile(self):
        if (hasattr(self, 'txt_ho_ten') and not self.txt_ho_ten.text() or
                hasattr(self, 'txt_sdt') and not self.txt_sdt.text() or
                hasattr(self, 'txt_ten_nong_trai') and not self.txt_ten_nong_trai.text() or
                hasattr(self, 'txt_dia_chi') and not self.txt_dia_chi.text() or
                hasattr(self, 'txt_quan_huyen') and not self.txt_quan_huyen.text() or
                hasattr(self, 'txt_xa_phuong') and not self.txt_xa_phuong.text() or
                hasattr(self, 'txt_tinh_thanh') and not self.txt_tinh_thanh.text()):
            QMessageBox.warning(self, "Thông báo", "Vui lòng nhập đầy đủ thông tin hồ sơ!")
            return

        username = self.user_data.get('username', '')
        password = self.user_data.get('password', '')
        role = self.user_data.get('role', 'Farmer')

        full_name = self.txt_ho_ten.text().strip()
        email = self.txt_sdt.text().strip()
        farm_name = self.txt_ten_nong_trai.text().strip()
        address = f"{self.txt_dia_chi.text().strip()}, {self.txt_xa_phuong.text().strip()}, {self.txt_quan_huyen.text().strip()}, {self.txt_tinh_thanh.text().strip()}"
        description = "Mô tả nông trại" # Default description

        success = register(username, password, role, full_name, email, address, farm_name, description)
        if not success:
            QMessageBox.warning(self, "Lỗi", "Tên đăng nhập hoặc SĐT/Email đã tồn tại!")
            return

        QMessageBox.information(self, "Chúc mừng", "Tạo hồ sơ thành công! Vui lòng đăng nhập.")
        from screens.login_screen import LoginScreen
        switch_window(LoginScreen())
