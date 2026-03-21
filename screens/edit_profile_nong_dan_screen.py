from PyQt6.QtWidgets import QWidget, QMessageBox
from PyQt6 import uic

from utils.window_manager import switch_window, get_current_user
from logic.logic_nguoi_dung import lay_thong_tin_nguoi_dung



class EditProfileNongDanScreen(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui_files/edit_profile_nong_dan.ui", self)

        if hasattr(self, "btn_back"):
            self.btn_back.clicked.connect(self.quay_lai_ho_so)
        if hasattr(self, "btn_luu_thay_doi"):
            self.btn_luu_thay_doi.clicked.connect(self.luu_thay_doi)

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
            phone,
            farm_name,
            description
        ) = thong_tin


        if hasattr(self, "lbl_edit_name_title"):
            self.lbl_edit_name_title.setText(username or full_name)
        if hasattr(self, "txt_edit_farm"):
            self.txt_edit_farm.setText(farm_name or "")
        if hasattr(self, "txt_edit_loc"):
            self.txt_edit_loc.setText(address or "")
        if hasattr(self, "txt_edit_desc"):
            self.txt_edit_desc.setPlainText(description or "")
        if hasattr(self, "lbl_email_val"):
            self.lbl_email_val.setText(email or "")
        if hasattr(self, "lbl_phone_val"):
            self.lbl_phone_val.setText(phone or "")


    def luu_thay_doi(self):
        farm_name = self.txt_edit_farm.text().strip()
        address = self.txt_edit_loc.text().strip()
        description = self.txt_edit_desc.toPlainText().strip()

        email = self.lbl_email_val.text().strip()
        phone = self.lbl_phone_val.text().strip()
        full_name = self.lbl_edit_name_title.text().strip()

        if not full_name:
            QMessageBox.warning(self, "Lỗi", "Tên người dùng không hợp lệ")
            return
        if not farm_name:
            QMessageBox.warning(self, "Lỗi", "Không được để trống tên vựa")
            return
        if not address:
            QMessageBox.warning(self, "Lỗi", "Không được để trống địa chỉ")
            return
        if not email or "@" not in email:
            QMessageBox.warning(self, "Lỗi", "Email không hợp lệ")
            return
        if phone and not phone.isdigit():
            QMessageBox.warning(self, "Lỗi", "SĐT không hợp lệ")
            return
        if len(description) > 300:
            QMessageBox.warning(self, "Lỗi", "Mô tả tối đa 300 ký tự")
            return

        QMessageBox.information(self, "Thành công", "Đã lưu thông tin hồ sơ thành công!")
        self.quay_lai_ho_so()


    def quay_lai_ho_so(self):
        switch_window(ProfileNongDanScreen())
