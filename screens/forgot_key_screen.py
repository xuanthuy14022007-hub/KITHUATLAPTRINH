from PyQt6.QtWidgets import QWidget, QMessageBox
from PyQt6 import uic
from utils.window_manager import switch_window
from database.database_connector import get_connection

class ForgotKeyScreen(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui_files/forgot_key.ui", self)

        if hasattr(self, 'lbl_quay_lai'):
            self.lbl_quay_lai.mousePressEvent = self.quay_lai_login
        if hasattr(self, 'btn_gui_email'):
            self.btn_gui_email.clicked.connect(self.chuyen_sang_otp)

    def quay_lai_login(self, event):
        from screens.login_screen import LoginScreen
        switch_window(LoginScreen)

    def kiem_tra_ton_tai_user(self, identifier):
        """Kiểm tra email hoặc số điện thoại có tồn tại trong bảng Users hay không.
           Trả về username nếu tìm thấy, None nếu không."""
        conn = get_connection()
        cursor = conn.cursor()
        # Giả sử identifier có thể là email hoặc số điện thoại (nếu có cột phone)
        # Trong database hiện tại chưa có cột phone, nên chỉ kiểm tra email
        cursor.execute("SELECT username FROM Users WHERE email = ?", (identifier,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None

    def chuyen_sang_otp(self):
        identifier = self.txt_email_sdt.text().strip() if hasattr(self, 'txt_email_sdt') else ''
        if not identifier:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập Email hoặc Số điện thoại!")
            return

        username = self.kiem_tra_ton_tai_user(identifier)
        if not username:
            QMessageBox.warning(self, "Lỗi", "Tài khoản không tồn tại!")
            return

        # Lưu tạm username để dùng ở màn hình OTP (có thể dùng session hoặc truyền)
        # Ở đây ta có thể truyền username qua tham số cho OTP screen
        from screens.otp_screen import OtpScreen
        switch_window(OtpScreen, username=username)
