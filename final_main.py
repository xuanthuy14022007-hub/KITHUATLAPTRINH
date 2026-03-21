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
# Import tất cả các màn hình (các class này sẽ được switch_window gọi)
from screens.splash_screen import SplashScreen
from screens.home_nong_dan_screen import NongDanDashboardScreen
from screens.home_chu_vua_screen import ChuVuaDashboardScreen
from screens.danh_sach_cay_trong_screen import DanhSachCayTrongScreen
from screens.chi_tiet_cay_trong_screen import ChiTietCayTrongScreen
from screens.nhat_ky_canh_tac_screen import NhatKyCanhTacScreen
from screens.goi_y_cham_soc_screen import GoiYChamSocScreen
from screens.luan_canh_screen import LuanCanhScreen
from screens.profile_nong_dan_screen import ProfileNongDanScreen
from screens.edit_profile_nong_dan_screen import EditProfileNongDanScreen
from screens.dang_san_pham_screen import DangSanPhamScreen
from screens.danh_sach_don_hang_screen import DanhSachDonHangScreen
from screens.chi_tiet_don_hang_screen import ChiTietDonHangScreen
from screens.search_list_mat_hang_screen import SearchListMatHangScreen
from screens.chi_tiet_nong_san_screen import ChiTietNongSanScreen
from screens.gio_hang_screen import GioHangScreen
from screens.pre_order_screen import PreOrderScreen
from screens.danh_sach_don_hang_chu_vua_screen import DanhSachDonHangChuVuaScreen
from screens.phan_tich_bao_cao_screen import PhanTichBaoCaoScreen
from screens.nhap_profile_in4_screen import NhapProfileInfoScreen
from screens.register_xacthuc_screen import RegisterXacThucScreen
from screens.register_screen import RegisterScreen
from screens.new_password_screen import NewPasswordScreen
from screens.otp_screen import OtpScreen
from screens.forgot_key_screen import ForgotKeyScreen
# from screens.chinh_sua_cay_trong_popup import ChinhSuaCayTrongPopup
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
