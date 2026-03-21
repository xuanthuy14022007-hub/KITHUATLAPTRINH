from PyQt6.QtWidgets import QWidget
from PyQt6 import uic

from utils.window_manager import switch_window
from PyQt6.QtWidgets import QMessageBox
from screens.new_password_screen import NewPasswordScreen

class OtpScreen(QWidget):
    def __init__(self, username=None):
        super().__init__()
        self.username = username
        uic.loadUi("ui_files/otp.ui", self)

        self.otp_boxes = []
        for i in range(1, 7):
            box = getattr(self, f'txt_otp_{i}', None)
            if box:
                self.otp_boxes.append(box)

        for i in range(len(self.otp_boxes)):
            self.otp_boxes[i].textChanged.connect(lambda text, idx=i: self.auto_focus_next(text, idx))

        if self.otp_boxes:
            self.otp_boxes[0].setFocus()

        if hasattr(self, 'btn_xac_nhan'):
            self.btn_xac_nhan.clicked.connect(self.chuyen_sang_doi_mat_khau)

    def auto_focus_next(self, text, index):
        if len(text) == 1 and index + 1 < len(self.otp_boxes):
            self.otp_boxes[index + 1].setFocus()
            self.otp_boxes[index + 1].selectAll()

    def chuyen_sang_doi_mat_khau(self):
        otp_code = "".join([box.text() for box in self.otp_boxes])
        if len(otp_code) < 6:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đủ 6 số OTP!")
            return
            
        switch_window(NewPasswordScreen(self.username))
