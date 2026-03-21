from PyQt6.QtWidgets import QWidget, QMessageBox
from PyQt6 import uic

from utils.window_manager import switch_window
from screens.login_screen import LoginScreen
from screens.nhap_profile_info_screen import NhapProfileInfoScreen

class RegisterXacThucScreen(QWidget):
    def __init__(self, user_data=None):
        super().__init__()
        self.user_data = user_data or {}
        uic.loadUi("ui_files/register_xacthuc.ui", self)

        # Thu thập các ô nhập OTP
        self.otp_boxes = []
        for i in range(1, 7):
            box = getattr(self, f'txt_otp_{i}', None)
            if box:
                self.otp_boxes.append(box)

        # Auto-focus ô tiếp theo khi nhập xong
        for i in range(len(self.otp_boxes)):
            self.otp_boxes[i].textChanged.connect(lambda text, idx=i: self.auto_focus_next(text, idx))

        if self.otp_boxes:
            self.otp_boxes[0].setFocus()

        if hasattr(self, 'btn_xac_nhan'):
            self.btn_xac_nhan.clicked.connect(self.chuyen_sang_profile)
        if hasattr(self, 'lbl_dctk'):
            self.lbl_dctk.mousePressEvent = self.quay_lai_login

    def auto_focus_next(self, text, index):
        if len(text) == 1 and index + 1 < len(self.otp_boxes):
            self.otp_boxes[index + 1].setFocus()
            self.otp_boxes[index + 1].selectAll()

    def chuyen_sang_profile(self):
        otp_code = "".join([box.text() for box in self.otp_boxes])
        if len(otp_code) < 6:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đầy đủ mã xác thực 6 số!")
            return
        switch_window(NhapProfileInfoScreen(self.user_data))

    def quay_lai_login(self, event):
        switch_window(LoginScreen())
