import sys
import traceback
from PyQt6.QtWidgets import QApplication, QMessageBox

# Import tất cả các màn hình chỗ này
#
#
#
# Import hàm chuyển màn hình từ utils
from utils.window_manager import switch_window

# ==========================================
# CƠ CHẾ BẮT LỖI TỰ ĐỘNG
# ==========================================
def global_exception_handler(exc_type, exc_value, exc_traceback):
    """Bắt mọi lỗi Python chưa xử lý và hiển thị popup thay vì crash app."""
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
# KHỞI CHẠY ỨNG DỤNG
# ==========================================
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Bắt đầu với màn hình Splash
    switch_window(SplashScreen)

    sys.exit(app.exec())
