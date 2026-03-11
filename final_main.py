# main.py
"""
File chính của ứng dụng Nông Ơi!
Khởi tạo QApplication, cửa sổ chính (MasterWindow) với QStackedWidget,
cài đặt bắt lỗi toàn cục và hiển thị màn hình đầu tiên.
"""

import sys
import traceback
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6 import uic

# Import tất cả các màn hình (các class này sẽ được switch_window gọi)
#
#
# Import các hàm từ window_manager
from utils.window_manager import set_main_window, switch_window, set_current_user, get_current_user

# ==========================================
# CƠ CHẾ BẮT LỖI TỰ ĐỘNG
# ==========================================
def global_exception_handler(exc_type, exc_value, exc_traceback):
    """
    Bắt mọi lỗi Python chưa được xử lý và hiển thị popup thay vì để app crash.
    """
    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    print(error_msg)  # In ra terminal để debug
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Icon.Critical)
    msg.setWindowTitle("Lỗi Hệ Thống")
    msg.setText("Phát hiện lỗi kỹ thuật! Vui lòng kiểm tra lại file UI hoặc Object Name.")
    msg.setDetailedText(error_msg)
    msg.exec()

# Gắn bộ bắt lỗi vào hệ thống
sys.excepthook = global_exception_handler

# ==========================================
# CỬA SỔ CHÍNH (MASTER WINDOW) VỚI QSTACKEDWIDGET
# ==========================================
class MasterWindow(QMainWindow):
    """
    Cửa sổ chính của ứng dụng, chứa QStackedWidget để quản lý các màn hình con.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nông Ơi! - Quản lý Nông Trại")
        self.resize(1280, 800)  # Kích thước mặc định, có thể thay đổi sau

        # Tạo stacked widget và đặt làm central widget
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Có thể thêm các thiết lập khác như menu bar, status bar nếu cần

# ==========================================
# KHỞI CHẠY ỨNG DỤNG
# ==========================================
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Tạo cửa sổ chính
    main_window = MasterWindow()
    # Gán cho window_manager để các màn hình có thể dùng switch_window
    set_main_window(main_window)

    # Hiển thị màn hình đầu tiên (SplashScreen)
    switch_window(SplashScreen)

    # Hiển thị cửa sổ chính
    main_window.show()

    sys.exit(app.exec())
