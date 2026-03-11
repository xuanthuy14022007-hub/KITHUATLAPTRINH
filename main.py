import sys
import traceback
from PyQt6.QtWidgets import QApplication, QWidget, QMessageBox, QFileDialog, QMainWindow, QStackedWidget, \
    QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPixmap
from PyQt6 import uic


# ==========================================
# CƠ CHẾ BẮT LỖI TỰ ĐỘNG - CHỐNG VĂNG APP
# ==========================================
def global_exception_handler(exc_type, exc_value, exc_traceback):
    """Bắt mọi lỗi Python và hiển thị lên Pop-up thay vì đánh sập App"""
    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    print(error_msg)  # Vẫn in ra terminal để dev xem
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Icon.Critical)
    msg.setWindowTitle("Lỗi Hệ Thống")
    msg.setText("Phát hiện lỗi kỹ thuật! Vui lòng kiểm tra lại file UI hoặc Object Name.")
    msg.setDetailedText(error_msg)
    msg.exec()


# Gắn bộ bắt lỗi vào hệ thống
sys.excepthook = global_exception_handler


# ==========================================
# HỆ THỐNG QUẢN LÝ CHUYỂN TRANG AN TOÀN (QSTACKEDWIDGET)
# ==========================================
class MasterWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nông Ơi! - Quản lý Nông Trại")
        self.resize(1280, 800)
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)


main_app_window = None


def switch_window(new_window):
    """Hàm trung tâm để chuyển đổi giữa các màn hình full-screen, chống lỗi rác bộ nhớ"""
    global main_app_window
    if main_app_window is None:
        return

    # ========================================================
    # 🌟 FIX LỖI MÀN HÌNH TRẮNG: Ép PyQt vẽ lại màu nền (CSS)
    # ========================================================
    new_window.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

    old_widget = main_app_window.stacked_widget.currentWidget()

    # Đưa màn hình mới vào QStackedWidget và hiển thị
    main_app_window.stacked_widget.addWidget(new_window)
    main_app_window.stacked_widget.setCurrentWidget(new_window)

    # Xóa màn hình cũ để giải phóng RAM
    if old_widget is not None:
        main_app_window.stacked_widget.removeWidget(old_widget)
        old_widget.deleteLater()


# ==========================================
# MÀN HÌNH POPUP NHỎ (KHÔNG DÙNG SWITCH_WINDOW)
# ==========================================
class ChinhSuaCayTrongPopup(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("chinh_sua_cay_trong.ui", self)

        # Giữ lại thanh tiêu đề, chỉ thiết lập cửa sổ nổi lên trên cùng
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)

        # Gắn sự kiện cho các nút đóng
        if hasattr(self, 'btn_close'):
            self.btn_close.clicked.connect(self.close)
        if hasattr(self, 'btn_huy'):
            self.btn_huy.clicked.connect(self.close)
        if hasattr(self, 'btn_luu'):
            self.btn_luu.clicked.connect(self.luu_thong_tin)

        # Gọi hàm canh giữa màn hình
        self.center()

    def center(self):
        # Lấy kích thước khung của popup
        qr = self.frameGeometry()
        # Lấy tọa độ tâm của màn hình chính hiện tại
        cp = QApplication.primaryScreen().availableGeometry().center()
        # Đưa tâm của popup vào đúng tâm của màn hình
        qr.moveCenter(cp)
        # Di chuyển popup đến tọa độ đã tính
        self.move(qr.topLeft())

    def luu_thong_tin(self):
        QMessageBox.information(self, "Thành công", "Đã lưu thông tin cây trồng!")
        self.close()


# ==========================================
# PHẦN 1: CÁC MÀN HÌNH CỦA NÔNG DÂN
# ==========================================
class NongDanDashboardScreen(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("home_nong_dan.ui", self)

        if hasattr(self, 'btn_menu_quan_ly'):
            self.btn_menu_quan_ly.clicked.connect(self.mo_quan_ly_nong_trai)
        if hasattr(self, 'btn_menu_ho_so'):
            self.btn_menu_ho_so.clicked.connect(self.mo_ho_so)
        if hasattr(self, 'btn_menu_giao_thuong'):
            self.btn_menu_giao_thuong.clicked.connect(self.mo_giao_thuong)
        if hasattr(self, 'btn_menu_phan_tich'):
            self.btn_menu_phan_tich.clicked.connect(self.mo_phan_tich)
        if hasattr(self, 'btn_dang_xuat'):
            self.btn_dang_xuat.clicked.connect(self.dang_xuat)

        # Click chữ "Xem gợi ý chăm sóc" chuyển sang màn hình Gợi ý chăm sóc
        if hasattr(self, 'lbl_xem_goi_y'):
            self.lbl_xem_goi_y.mousePressEvent = self.mo_goi_y

        # Click nút "Quản lý nông trại >" trong khung Mùa vụ
        if hasattr(self, 'lbl_btn_qlnt'):
            self.lbl_btn_qlnt.mousePressEvent = self.mo_quan_ly_nong_trai_lbl

    def mo_quan_ly_nong_trai_lbl(self, event):
        switch_window(DanhSachCayTrongScreen())

    def mo_quan_ly_nong_trai(self):
        switch_window(DanhSachCayTrongScreen())

    def mo_ho_so(self):
        switch_window(ProfileNongDanScreen())

    def mo_giao_thuong(self):
        switch_window(DangSanPhamScreen())

    def mo_phan_tich(self):
        switch_window(PhanTichBaoCaoScreen())

    def mo_goi_y(self, event):
        switch_window(GoiYChamSocScreen())

    def dang_xuat(self):
        reply = QMessageBox.question(self, 'Xác nhận', 'Bạn có chắc chắn muốn đăng xuất?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            switch_window(LoginScreen())


class DanhSachCayTrongScreen(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("danh_sach_cay_trong.ui", self)

        # Điều hướng Sidebar cho Nông dân
        if hasattr(self, 'btn_menu_trang_chu'):
            self.btn_menu_trang_chu.clicked.connect(self.ve_trang_chu)
        if hasattr(self, 'btn_menu_giao_thuong'):
            self.btn_menu_giao_thuong.clicked.connect(self.mo_giao_thuong)
        if hasattr(self, 'btn_menu_phan_tich'):
            self.btn_menu_phan_tich.clicked.connect(self.mo_phan_tich)
        if hasattr(self, 'btn_menu_ho_so'):
            self.btn_menu_ho_so.clicked.connect(self.mo_ho_so)
        if hasattr(self, 'btn_dang_xuat'):
            self.btn_dang_xuat.clicked.connect(self.dang_xuat)

        # Click vào các hàng (khung chứa Tên và Ảnh) để xem chi tiết
        if hasattr(self, 'td1_0'):
            self.td1_0.mousePressEvent = self.mo_chi_tiet_cay_trong
        if hasattr(self, 'td2_0'):
            self.td2_0.mousePressEvent = self.mo_chi_tiet_cay_trong
        if hasattr(self, 'td3_0'):
            self.td3_0.mousePressEvent = self.mo_chi_tiet_cay_trong
        if hasattr(self, 'td4_0'):
            self.td4_0.mousePressEvent = self.mo_chi_tiet_cay_trong
        if hasattr(self, 'td5_0'):
            self.td5_0.mousePressEvent = self.mo_chi_tiet_cay_trong

        # Sự kiện mở Popup "Thêm cây trồng"
        if hasattr(self, 'btn_them_cay_trong'):
            self.btn_them_cay_trong.clicked.connect(self.mo_popup_them_sua)

        # Khởi tạo biến chứa popup để không bị dọn dẹp bởi Garbage Collector
        self.popup = None

    def mo_popup_them_sua(self):
        self.popup = ChinhSuaCayTrongPopup()
        self.popup.show()

    def ve_trang_chu(self):
        switch_window(NongDanDashboardScreen())

    def mo_giao_thuong(self):
        switch_window(DangSanPhamScreen())

    def mo_phan_tich(self):
        switch_window(PhanTichBaoCaoScreen())

    def mo_ho_so(self):
        switch_window(ProfileNongDanScreen())

    def mo_chi_tiet_cay_trong(self, event):
        switch_window(ChiTietCayTrongScreen())

    def dang_xuat(self):
        reply = QMessageBox.question(self, 'Xác nhận', 'Bạn có chắc chắn muốn đăng xuất?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            switch_window(LoginScreen())


class ChiTietCayTrongScreen(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("chi_tiet_cay_trong.ui", self)

        # Điều hướng Sidebar cho Nông dân
        if hasattr(self, 'btn_menu_trang_chu'):
            self.btn_menu_trang_chu.clicked.connect(self.ve_trang_chu)
        if hasattr(self, 'btn_menu_quan_ly'):
            self.btn_menu_quan_ly.clicked.connect(self.mo_quan_ly_nong_trai)
        if hasattr(self, 'btn_menu_giao_thuong'):
            self.btn_menu_giao_thuong.clicked.connect(self.mo_giao_thuong)
        if hasattr(self, 'btn_menu_phan_tich'):
            self.btn_menu_phan_tich.clicked.connect(self.mo_phan_tich)
        if hasattr(self, 'btn_menu_ho_so'):
            self.btn_menu_ho_so.clicked.connect(self.mo_ho_so)
        if hasattr(self, 'btn_dang_xuat'):
            self.btn_dang_xuat.clicked.connect(self.dang_xuat)

        # Điều hướng Tabs (Bảo vệ bằng hasattr)
        if hasattr(self, 'lbl_tab_danh_sach'):
            self.lbl_tab_danh_sach.mousePressEvent = self.quay_lai_danh_sach
        if hasattr(self, 'lbl_tab_nhat_ky'):
            self.lbl_tab_nhat_ky.mousePressEvent = self.mo_nhat_ky
        if hasattr(self, 'lbl_tab_goi_y'):
            self.lbl_tab_goi_y.mousePressEvent = self.mo_goi_y

        # Nút "Chỉnh sửa/Xoá cây trồng"
        if hasattr(self, 'btn_edit_delete'):
            self.btn_edit_delete.clicked.connect(self.mo_popup_them_sua)

        self.popup = None

    def mo_popup_them_sua(self):
        self.popup = ChinhSuaCayTrongPopup()
        self.popup.show()

    def ve_trang_chu(self):
        switch_window(NongDanDashboardScreen())

    def mo_quan_ly_nong_trai(self):
        switch_window(DanhSachCayTrongScreen())

    def mo_giao_thuong(self):
        switch_window(DangSanPhamScreen())

    def mo_phan_tich(self):
        switch_window(PhanTichBaoCaoScreen())

    def mo_ho_so(self):
        switch_window(ProfileNongDanScreen())

    def quay_lai_danh_sach(self, event):
        switch_window(DanhSachCayTrongScreen())

    def mo_nhat_ky(self, event):
        switch_window(NhatKyCanhTacScreen())

    def mo_goi_y(self, event):
        switch_window(GoiYChamSocScreen())

    def dang_xuat(self):
        reply = QMessageBox.question(self, 'Xác nhận', 'Bạn có chắc chắn muốn đăng xuất?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            switch_window(LoginScreen())


class NhatKyCanhTacScreen(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("nhat_ky_canh_tac.ui", self)

        # Điều hướng Sidebar cho Nông dân
        if hasattr(self, 'btn_menu_trang_chu'):
            self.btn_menu_trang_chu.clicked.connect(self.ve_trang_chu)
        if hasattr(self, 'btn_menu_quan_ly'):
            self.btn_menu_quan_ly.clicked.connect(self.mo_quan_ly_nong_trai)
        if hasattr(self, 'btn_menu_giao_thuong'):
            self.btn_menu_giao_thuong.clicked.connect(self.mo_giao_thuong)
        if hasattr(self, 'btn_menu_phan_tich'):
            self.btn_menu_phan_tich.clicked.connect(self.mo_phan_tich)
        if hasattr(self, 'btn_menu_ho_so'):
            self.btn_menu_ho_so.clicked.connect(self.mo_ho_so)
        if hasattr(self, 'btn_dang_xuat'):
            self.btn_dang_xuat.clicked.connect(self.dang_xuat)

        # Điều hướng Tab ngang (Bảo vệ bằng hasattr)
        if hasattr(self, 'lbl_tab_danh_sach'):
            self.lbl_tab_danh_sach.mousePressEvent = self.quay_lai_danh_sach
        if hasattr(self, 'lbl_tab_thong_tin'):
            self.lbl_tab_thong_tin.mousePressEvent = self.mo_thong_tin_chi_tiet
        if hasattr(self, 'lbl_tab_goi_y'):
            self.lbl_tab_goi_y.mousePressEvent = self.mo_goi_y

        # Các nút
        if hasattr(self, 'btn_luu'):
            self.btn_luu.clicked.connect(self.luu_nhat_ky)
        if hasattr(self, 'btn_huy'):
            self.btn_huy.clicked.connect(self.huy_nhat_ky)

    def ve_trang_chu(self):
        switch_window(NongDanDashboardScreen())

    def mo_quan_ly_nong_trai(self):
        switch_window(DanhSachCayTrongScreen())

    def mo_giao_thuong(self):
        switch_window(DangSanPhamScreen())

    def mo_phan_tich(self):
        switch_window(PhanTichBaoCaoScreen())

    def mo_ho_so(self):
        switch_window(ProfileNongDanScreen())

    def quay_lai_danh_sach(self, event):
        switch_window(DanhSachCayTrongScreen())

    def mo_thong_tin_chi_tiet(self, event):
        switch_window(ChiTietCayTrongScreen())

    def mo_goi_y(self, event):
        switch_window(GoiYChamSocScreen())

    def luu_nhat_ky(self):
        QMessageBox.information(self, "Thành công", "Đã lưu nhật ký canh tác thành công!")
        if hasattr(self, 'txt_noidung'):
            self.txt_noidung.clear()

    def huy_nhat_ky(self):
        if hasattr(self, 'txt_noidung'):
            self.txt_noidung.clear()

    def dang_xuat(self):
        reply = QMessageBox.question(self, 'Xác nhận', 'Bạn có chắc chắn muốn đăng xuất?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            switch_window(LoginScreen())


class GoiYChamSocScreen(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("goi_y_cham_soc.ui", self)

        # Điều hướng Sidebar cho Nông dân
        if hasattr(self, 'btn_menu_trang_chu'):
            self.btn_menu_trang_chu.clicked.connect(self.ve_trang_chu)
        if hasattr(self, 'btn_menu_quan_ly'):
            self.btn_menu_quan_ly.clicked.connect(self.mo_quan_ly_nong_trai)
        if hasattr(self, 'btn_menu_giao_thuong'):
            self.btn_menu_giao_thuong.clicked.connect(self.mo_giao_thuong)
        if hasattr(self, 'btn_menu_phan_tich'):
            self.btn_menu_phan_tich.clicked.connect(self.mo_phan_tich)
        if hasattr(self, 'btn_menu_ho_so'):
            self.btn_menu_ho_so.clicked.connect(self.mo_ho_so)
        if hasattr(self, 'btn_dang_xuat'):
            self.btn_dang_xuat.clicked.connect(self.dang_xuat)

        # Điều hướng Tab ngang (Bảo vệ bằng hasattr)
        if hasattr(self, 'lbl_tab_danh_sach'):
            self.lbl_tab_danh_sach.mousePressEvent = self.quay_lai_danh_sach
        if hasattr(self, 'lbl_tab_thong_tin'):
            self.lbl_tab_thong_tin.mousePressEvent = self.mo_thong_tin_chi_tiet
        if hasattr(self, 'lbl_tab_nhat_ky'):
            self.lbl_tab_nhat_ky.mousePressEvent = self.mo_nhat_ky

        # Click Tab Luân Canh
        if hasattr(self, 'lbl_subtab_luancanh'):
            self.lbl_subtab_luancanh.mousePressEvent = self.mo_luan_canh
        if hasattr(self, 'lbl_tab_luan_canh'):
            self.lbl_tab_luan_canh.mousePressEvent = self.mo_luan_canh

    def ve_trang_chu(self):
        switch_window(NongDanDashboardScreen())

    def mo_quan_ly_nong_trai(self):
        switch_window(DanhSachCayTrongScreen())

    def mo_giao_thuong(self):
        switch_window(DangSanPhamScreen())

    def mo_phan_tich(self):
        switch_window(PhanTichBaoCaoScreen())

    def mo_ho_so(self):
        switch_window(ProfileNongDanScreen())

    def quay_lai_danh_sach(self, event):
        switch_window(DanhSachCayTrongScreen())

    def mo_thong_tin_chi_tiet(self, event):
        switch_window(ChiTietCayTrongScreen())

    def mo_nhat_ky(self, event):
        switch_window(NhatKyCanhTacScreen())

    def mo_luan_canh(self, event):
        switch_window(LuanCanhScreen())

    def dang_xuat(self):
        reply = QMessageBox.question(self, 'Xác nhận', 'Bạn có chắc chắn muốn đăng xuất?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            switch_window(LoginScreen())


class LuanCanhScreen(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("luan_canh.ui", self)

        # Điều hướng Sidebar cho Nông dân
        if hasattr(self, 'btn_menu_trang_chu'):
            self.btn_menu_trang_chu.clicked.connect(self.ve_trang_chu)
        if hasattr(self, 'btn_menu_quan_ly'):
            self.btn_menu_quan_ly.clicked.connect(self.mo_quan_ly_nong_trai)
        if hasattr(self, 'btn_menu_giao_thuong'):
            self.btn_menu_giao_thuong.clicked.connect(self.mo_giao_thuong)
        if hasattr(self, 'btn_menu_phan_tich'):
            self.btn_menu_phan_tich.clicked.connect(self.mo_phan_tich)
        if hasattr(self, 'btn_menu_ho_so'):
            self.btn_menu_ho_so.clicked.connect(self.mo_ho_so)
        if hasattr(self, 'btn_dang_xuat'):
            self.btn_dang_xuat.clicked.connect(self.dang_xuat)

        # Điều hướng Tab ngang (Bảo vệ bằng hasattr)
        if hasattr(self, 'lbl_tab_danh_sach'):
            self.lbl_tab_danh_sach.mousePressEvent = self.quay_lai_danh_sach
        if hasattr(self, 'lbl_tab_thong_tin'):
            self.lbl_tab_thong_tin.mousePressEvent = self.mo_thong_tin_chi_tiet
        if hasattr(self, 'lbl_tab_nhat_ky'):
            self.lbl_tab_nhat_ky.mousePressEvent = self.mo_nhat_ky

        # Click Tab Nhắc nhở (hoặc Gợi ý chăm sóc) để quay lại
        if hasattr(self, 'lbl_tab_nhac_nho'):
            self.lbl_tab_nhac_nho.mousePressEvent = self.mo_goi_y_cham_soc
        if hasattr(self, 'lbl_tab_goi_y'):
            self.lbl_tab_goi_y.mousePressEvent = self.mo_goi_y_cham_soc

    def ve_trang_chu(self):
        switch_window(NongDanDashboardScreen())

    def mo_quan_ly_nong_trai(self):
        switch_window(DanhSachCayTrongScreen())

    def mo_giao_thuong(self):
        switch_window(DangSanPhamScreen())

    def mo_phan_tich(self):
        switch_window(PhanTichBaoCaoScreen())

    def mo_ho_so(self):
        switch_window(ProfileNongDanScreen())

    def quay_lai_danh_sach(self, event):
        switch_window(DanhSachCayTrongScreen())

    def mo_thong_tin_chi_tiet(self, event):
        switch_window(ChiTietCayTrongScreen())

    def mo_nhat_ky(self, event):
        switch_window(NhatKyCanhTacScreen())

    def mo_goi_y_cham_soc(self, event):
        switch_window(GoiYChamSocScreen())

    def dang_xuat(self):
        reply = QMessageBox.question(self, 'Xác nhận', 'Bạn có chắc chắn muốn đăng xuất?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            switch_window(LoginScreen())


class ProfileNongDanScreen(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("profile_nong_dan.ui", self)

        if hasattr(self, 'btn_menu_trang_chu'):
            self.btn_menu_trang_chu.clicked.connect(self.ve_trang_chu)
        if hasattr(self, 'btn_menu_quan_ly'):
            self.btn_menu_quan_ly.clicked.connect(self.mo_quan_ly_nong_trai)
        if hasattr(self, 'btn_menu_giao_thuong'):
            self.btn_menu_giao_thuong.clicked.connect(self.mo_giao_thuong)
        if hasattr(self, 'btn_menu_phan_tich'):
            self.btn_menu_phan_tich.clicked.connect(self.mo_phan_tich)
        if hasattr(self, 'btn_chinh_sua'):
            self.btn_chinh_sua.clicked.connect(self.mo_chinh_sua_ho_so)
        if hasattr(self, 'btn_dang_xuat'):
            self.btn_dang_xuat.clicked.connect(self.dang_xuat)

    def ve_trang_chu(self):
        switch_window(NongDanDashboardScreen())

    def mo_quan_ly_nong_trai(self):
        switch_window(DanhSachCayTrongScreen())

    def mo_giao_thuong(self):
        switch_window(DangSanPhamScreen())

    def mo_phan_tich(self):
        switch_window(PhanTichBaoCaoScreen())

    def mo_chinh_sua_ho_so(self):
        switch_window(EditProfileNongDanScreen())

    def dang_xuat(self):
        reply = QMessageBox.question(self, 'Xác nhận', 'Bạn có chắc chắn muốn đăng xuất?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            switch_window(LoginScreen())


class EditProfileNongDanScreen(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("edit_profile_nong_dan.ui", self)

        if hasattr(self, 'btn_back'):
            self.btn_back.clicked.connect(self.quay_lai_ho_so)
        if hasattr(self, 'btn_huy'):
            self.btn_huy.clicked.connect(self.quay_lai_ho_so)
        if hasattr(self, 'btn_luu_thay_doi'):
            self.btn_luu_thay_doi.clicked.connect(self.luu_thay_doi)

    def quay_lai_ho_so(self):
        switch_window(ProfileNongDanScreen())

    def luu_thay_doi(self):
        QMessageBox.information(self, "Thành công", "Đã lưu thông tin hồ sơ thành công!")
        switch_window(ProfileNongDanScreen())


# ==========================================
# PHẦN 2: CÁC MÀN HÌNH CỦA CHỦ VỰA
# ==========================================
class ChuVuaDashboardScreen(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("home_chu_vua.ui", self)

        if hasattr(self, 'btn_menu_ho_so'):
            self.btn_menu_ho_so.clicked.connect(self.mo_ho_so)
        if hasattr(self, 'btn_menu_giao_thuong'):
            self.btn_menu_giao_thuong.clicked.connect(self.mo_giao_thuong)
        if hasattr(self, 'btn_dang_xuat'):
            self.btn_dang_xuat.clicked.connect(self.dang_xuat)

    def mo_ho_so(self):
        switch_window(ProfileChuVuaScreen())

    def mo_giao_thuong(self):
        switch_window(SearchListMatHangScreen())

    def dang_xuat(self):
        reply = QMessageBox.question(self, 'Xác nhận', 'Bạn có chắc chắn muốn đăng xuất?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            switch_window(LoginScreen())


class ProfileChuVuaScreen(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("profile_chu_vua.ui", self)

        if hasattr(self, 'btn_menu_trang_chu'):
            self.btn_menu_trang_chu.clicked.connect(self.ve_trang_chu)
        if hasattr(self, 'btn_menu_giao_thuong'):
            self.btn_menu_giao_thuong.clicked.connect(self.mo_giao_thuong)
        if hasattr(self, 'btn_chinh_sua'):
            self.btn_chinh_sua.clicked.connect(self.mo_chinh_sua_ho_so)
        if hasattr(self, 'btn_dang_xuat'):
            self.btn_dang_xuat.clicked.connect(self.dang_xuat)

    def ve_trang_chu(self):
        switch_window(ChuVuaDashboardScreen())

    def mo_giao_thuong(self):
        switch_window(SearchListMatHangScreen())

    def mo_chinh_sua_ho_so(self):
        switch_window(EditProfileChuVuaScreen())

    def dang_xuat(self):
        reply = QMessageBox.question(self, 'Xác nhận', 'Bạn có chắc chắn muốn đăng xuất?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            switch_window(LoginScreen())


class EditProfileChuVuaScreen(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("edit_profile_chu_vua.ui", self)

        if hasattr(self, 'btn_back'):
            self.btn_back.clicked.connect(self.quay_lai_ho_so)
        if hasattr(self, 'btn_huy'):
            self.btn_huy.clicked.connect(self.quay_lai_ho_so)
        if hasattr(self, 'btn_luu_thay_doi'):
            self.btn_luu_thay_doi.clicked.connect(self.luu_thay_doi)

    def quay_lai_ho_so(self):
        switch_window(ProfileChuVuaScreen())

    def luu_thay_doi(self):
        QMessageBox.information(self, "Thành công", "Đã lưu thông tin hồ sơ thành công!")
        switch_window(ProfileChuVuaScreen())


# ==========================================
# PHẦN 3: GIAO THƯƠNG NÔNG DÂN
# ==========================================
class DangSanPhamScreen(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("dang_san_pham.ui", self)

        if hasattr(self, 'btn_menu_trang_chu'):
            self.btn_menu_trang_chu.clicked.connect(self.ve_trang_chu)
        if hasattr(self, 'btn_menu_quan_ly'):
            self.btn_menu_quan_ly.clicked.connect(self.mo_quan_ly_nong_trai)
        if hasattr(self, 'btn_menu_ho_so'):
            self.btn_menu_ho_so.clicked.connect(self.mo_ho_so)
        if hasattr(self, 'btn_menu_phan_tich'):
            self.btn_menu_phan_tich.clicked.connect(self.mo_phan_tich)
        if hasattr(self, 'btn_dang_xuat'):
            self.btn_dang_xuat.clicked.connect(self.dang_xuat)

        if hasattr(self, 'lbl_tab_quan_ly_don'):
            self.lbl_tab_quan_ly_don.mousePressEvent = self.mo_quan_ly_don

    def ve_trang_chu(self):
        switch_window(NongDanDashboardScreen())

    def mo_quan_ly_nong_trai(self):
        switch_window(DanhSachCayTrongScreen())

    def mo_ho_so(self):
        switch_window(ProfileNongDanScreen())

    def mo_phan_tich(self):
        switch_window(PhanTichBaoCaoScreen())

    def mo_quan_ly_don(self, event):
        switch_window(DanhSachDonHangScreen())

    def dang_xuat(self):
        reply = QMessageBox.question(self, 'Xác nhận', 'Bạn có chắc chắn muốn đăng xuất?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            switch_window(LoginScreen())


class DanhSachDonHangScreen(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("danh_sach_don_hang.ui", self)

        if hasattr(self, 'btn_menu_trang_chu'):
            self.btn_menu_trang_chu.clicked.connect(self.ve_trang_chu)
        if hasattr(self, 'btn_menu_quan_ly'):
            self.btn_menu_quan_ly.clicked.connect(self.mo_quan_ly_nong_trai)
        if hasattr(self, 'btn_menu_ho_so'):
            self.btn_menu_ho_so.clicked.connect(self.mo_ho_so)
        if hasattr(self, 'btn_menu_phan_tich'):
            self.btn_menu_phan_tich.clicked.connect(self.mo_phan_tich)
        if hasattr(self, 'btn_dang_xuat'):
            self.btn_dang_xuat.clicked.connect(self.dang_xuat)

        if hasattr(self, 'lbl_tab_dang_ban'):
            self.lbl_tab_dang_ban.mousePressEvent = self.mo_dang_ban

        if hasattr(self, 'btn_detail_1'):
            self.btn_detail_1.clicked.connect(self.mo_chi_tiet_don_hang)
        if hasattr(self, 'btn_detail_2'):
            self.btn_detail_2.clicked.connect(self.mo_chi_tiet_don_hang)
        if hasattr(self, 'btn_detail_3'):
            self.btn_detail_3.clicked.connect(self.mo_chi_tiet_don_hang)

    def ve_trang_chu(self):
        switch_window(NongDanDashboardScreen())

    def mo_quan_ly_nong_trai(self):
        switch_window(DanhSachCayTrongScreen())

    def mo_ho_so(self):
        switch_window(ProfileNongDanScreen())

    def mo_phan_tich(self):
        switch_window(PhanTichBaoCaoScreen())

    def mo_dang_ban(self, event):
        switch_window(DangSanPhamScreen())

    def mo_chi_tiet_don_hang(self):
        switch_window(ChiTietDonHangScreen())

    def dang_xuat(self):
        reply = QMessageBox.question(self, 'Xác nhận', 'Bạn có chắc chắn muốn đăng xuất?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            switch_window(LoginScreen())


class ChiTietDonHangScreen(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("chi_tiet_don_hang.ui", self)

        if hasattr(self, 'btn_menu_trang_chu'):
            self.btn_menu_trang_chu.clicked.connect(self.ve_trang_chu)
        if hasattr(self, 'btn_menu_quan_ly'):
            self.btn_menu_quan_ly.clicked.connect(self.mo_quan_ly_nong_trai)
        if hasattr(self, 'btn_menu_ho_so'):
            self.btn_menu_ho_so.clicked.connect(self.mo_ho_so)
        if hasattr(self, 'btn_menu_phan_tich'):
            self.btn_menu_phan_tich.clicked.connect(self.mo_phan_tich)
        if hasattr(self, 'btn_dang_xuat'):
            self.btn_dang_xuat.clicked.connect(self.dang_xuat)

        if hasattr(self, 'btn_back'):
            self.btn_back.clicked.connect(self.quay_lai_danh_sach)
        if hasattr(self, 'btn_xac_nhan'):
            self.btn_xac_nhan.clicked.connect(self.xac_nhan_don)
        if hasattr(self, 'btn_tu_choi'):
            self.btn_tu_choi.clicked.connect(self.tu_choi_don)

    def ve_trang_chu(self):
        switch_window(NongDanDashboardScreen())

    def mo_quan_ly_nong_trai(self):
        switch_window(DanhSachCayTrongScreen())

    def mo_ho_so(self):
        switch_window(ProfileNongDanScreen())

    def mo_phan_tich(self):
        switch_window(PhanTichBaoCaoScreen())

    def quay_lai_danh_sach(self):
        switch_window(DanhSachDonHangScreen())

    def xac_nhan_don(self):
        QMessageBox.information(self, "Thành công", "Đã xác nhận đơn hàng thành công!")
        self.quay_lai_danh_sach()

    def tu_choi_don(self):
        QMessageBox.information(self, "Thành công", "Đã từ chối đơn hàng!")
        self.quay_lai_danh_sach()

    def dang_xuat(self):
        reply = QMessageBox.question(self, 'Xác nhận', 'Bạn có chắc chắn muốn đăng xuất?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            switch_window(LoginScreen())


# ==========================================
# PHẦN 4: GIAO THƯƠNG CHỦ VỰA (MUA HÀNG)
# ==========================================
class SearchListMatHangScreen(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("search_list_mat_hang.ui", self)

        # Điều hướng Sidebar cho Chủ Vựa
        if hasattr(self, 'btn_menu_trang_chu'):
            self.btn_menu_trang_chu.clicked.connect(self.ve_trang_chu)
        if hasattr(self, 'btn_menu_ho_so'):
            self.btn_menu_ho_so.clicked.connect(self.mo_ho_so)
        if hasattr(self, 'btn_dang_xuat'):
            self.btn_dang_xuat.clicked.connect(self.dang_xuat)

        # Bấm vào thẻ mặt hàng để xem chi tiết
        if hasattr(self, 'card_1'): self.card_1.mousePressEvent = self.mo_chi_tiet_nong_san
        if hasattr(self, 'card_2'): self.card_2.mousePressEvent = self.mo_chi_tiet_nong_san
        if hasattr(self, 'card_3'): self.card_3.mousePressEvent = self.mo_chi_tiet_nong_san
        if hasattr(self, 'card_4'): self.card_4.mousePressEvent = self.mo_chi_tiet_nong_san
        if hasattr(self, 'card_5'): self.card_5.mousePressEvent = self.mo_chi_tiet_nong_san
        if hasattr(self, 'card_6'): self.card_6.mousePressEvent = self.mo_chi_tiet_nong_san

        # Nút chuyển sang Giỏ hàng và Đơn hàng
        if hasattr(self, 'btn_gio_hang_top'):
            self.btn_gio_hang_top.clicked.connect(self.mo_gio_hang)
        if hasattr(self, 'btn_don_hang_top'):
            self.btn_don_hang_top.clicked.connect(self.mo_don_hang)

    def ve_trang_chu(self):
        switch_window(ChuVuaDashboardScreen())

    def mo_ho_so(self):
        switch_window(ProfileChuVuaScreen())

    def mo_gio_hang(self):
        switch_window(GioHangScreen())

    def mo_don_hang(self):
        switch_window(DanhSachDonHangChuVuaScreen())

    def mo_chi_tiet_nong_san(self, event):
        switch_window(ChiTietNongSanScreen())

    def dang_xuat(self):
        reply = QMessageBox.question(self, 'Xác nhận', 'Bạn có chắc chắn muốn đăng xuất?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            switch_window(LoginScreen())


class ChiTietNongSanScreen(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("chi_tiet_nong_san.ui", self)

        # Điều hướng Sidebar cho Chủ Vựa
        if hasattr(self, 'btn_menu_trang_chu'):
            self.btn_menu_trang_chu.clicked.connect(self.ve_trang_chu)
        if hasattr(self, 'btn_menu_giao_thuong'):
            self.btn_menu_giao_thuong.clicked.connect(self.mo_giao_thuong)
        if hasattr(self, 'btn_menu_ho_so'):
            self.btn_menu_ho_so.clicked.connect(self.mo_ho_so)
        if hasattr(self, 'btn_dang_xuat'):
            self.btn_dang_xuat.clicked.connect(self.dang_xuat)

        # Nút Trở về (Back)
        if hasattr(self, 'btn_back'):
            self.btn_back.clicked.connect(self.quay_lai_danh_sach)

        # Nút Thêm vào giỏ hàng
        if hasattr(self, 'btn_add_cart'):
            self.btn_add_cart.clicked.connect(self.them_vao_gio_hang)

        # Nút chuyển sang Giỏ hàng và Đơn hàng
        if hasattr(self, 'btn_gio_hang_top'):
            self.btn_gio_hang_top.clicked.connect(self.mo_gio_hang)
        if hasattr(self, 'btn_don_hang_top'):
            self.btn_don_hang_top.clicked.connect(self.mo_don_hang)

    def ve_trang_chu(self):
        switch_window(ChuVuaDashboardScreen())

    def mo_giao_thuong(self):
        switch_window(SearchListMatHangScreen())

    def mo_ho_so(self):
        switch_window(ProfileChuVuaScreen())

    def quay_lai_danh_sach(self):
        switch_window(SearchListMatHangScreen())

    def mo_gio_hang(self):
        switch_window(GioHangScreen())

    def mo_don_hang(self):
        switch_window(DanhSachDonHangChuVuaScreen())

    def them_vao_gio_hang(self):
        QMessageBox.information(self, "Thành công", "Đã thêm nông sản vào giỏ hàng!")

    def dang_xuat(self):
        reply = QMessageBox.question(self, 'Xác nhận', 'Bạn có chắc chắn muốn đăng xuất?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            switch_window(LoginScreen())


class GioHangScreen(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("gio_hang.ui", self)

        # Điều hướng Sidebar cho Chủ Vựa
        if hasattr(self, 'btn_menu_trang_chu'):
            self.btn_menu_trang_chu.clicked.connect(self.ve_trang_chu)
        if hasattr(self, 'btn_menu_giao_thuong'):
            self.btn_menu_giao_thuong.clicked.connect(self.mo_giao_thuong)
        if hasattr(self, 'btn_menu_ho_so'):
            self.btn_menu_ho_so.clicked.connect(self.mo_ho_so)
        if hasattr(self, 'btn_dang_xuat'):
            self.btn_dang_xuat.clicked.connect(self.dang_xuat)

        # Nút Trở về (Back) và Mua hàng
        if hasattr(self, 'btn_back'):
            self.btn_back.clicked.connect(self.quay_lai)
        if hasattr(self, 'btn_checkout'):
            self.btn_checkout.clicked.connect(self.mua_hang)

        # Nút chuyển sang Đơn hàng
        if hasattr(self, 'btn_don_hang_top'):
            self.btn_don_hang_top.clicked.connect(self.mo_don_hang)

    def ve_trang_chu(self):
        switch_window(ChuVuaDashboardScreen())

    def mo_giao_thuong(self):
        switch_window(SearchListMatHangScreen())

    def mo_ho_so(self):
        switch_window(ProfileChuVuaScreen())

    def quay_lai(self):
        switch_window(SearchListMatHangScreen())

    def mua_hang(self):
        switch_window(PreOrderScreen())

    def mo_don_hang(self):
        switch_window(DanhSachDonHangChuVuaScreen())

    def dang_xuat(self):
        reply = QMessageBox.question(self, 'Xác nhận', 'Bạn có chắc chắn muốn đăng xuất?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            switch_window(LoginScreen())


class PreOrderScreen(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("pre_order.ui", self)

        # Điều hướng Sidebar cho Chủ Vựa
        if hasattr(self, 'btn_menu_trang_chu'):
            self.btn_menu_trang_chu.clicked.connect(self.ve_trang_chu)
        if hasattr(self, 'btn_menu_giao_thuong'):
            self.btn_menu_giao_thuong.clicked.connect(self.mo_giao_thuong)
        if hasattr(self, 'btn_menu_ho_so'):
            self.btn_menu_ho_so.clicked.connect(self.mo_ho_so)
        if hasattr(self, 'btn_dang_xuat'):
            self.btn_dang_xuat.clicked.connect(self.dang_xuat)

        # Nút Trở về
        if hasattr(self, 'btn_back'):
            self.btn_back.clicked.connect(self.quay_lai_gio_hang)
        if hasattr(self, 'btn_quay_lai'):
            self.btn_quay_lai.clicked.connect(self.quay_lai_gio_hang)

        # Nút Xác nhận đặt hàng
        if hasattr(self, 'btn_xac_nhan_dat_hang'):
            self.btn_xac_nhan_dat_hang.clicked.connect(self.hoan_tat_dat_hang)

    def ve_trang_chu(self):
        switch_window(ChuVuaDashboardScreen())

    def mo_giao_thuong(self):
        switch_window(SearchListMatHangScreen())

    def mo_ho_so(self):
        switch_window(ProfileChuVuaScreen())

    def quay_lai_gio_hang(self):
        switch_window(GioHangScreen())

    def hoan_tat_dat_hang(self):
        QMessageBox.information(self, "Thành công", "Đã đặt hàng thành công! Đơn hàng đang chờ xác nhận từ nông trại.")
        switch_window(DanhSachDonHangChuVuaScreen())

    def dang_xuat(self):
        reply = QMessageBox.question(self, 'Xác nhận', 'Bạn có chắc chắn muốn đăng xuất?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            switch_window(LoginScreen())


class DanhSachDonHangChuVuaScreen(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("danh_sach_don_hang_chu_vua.ui", self)

        # Điều hướng Sidebar cho Chủ Vựa
        if hasattr(self, 'btn_menu_trang_chu'):
            self.btn_menu_trang_chu.clicked.connect(self.ve_trang_chu)
        if hasattr(self, 'btn_menu_giao_thuong'):
            self.btn_menu_giao_thuong.clicked.connect(self.mo_giao_thuong)
        if hasattr(self, 'btn_menu_ho_so'):
            self.btn_menu_ho_so.clicked.connect(self.mo_ho_so)
        if hasattr(self, 'btn_dang_xuat'):
            self.btn_dang_xuat.clicked.connect(self.dang_xuat)

        # Nút Trở về và Giỏ hàng
        if hasattr(self, 'btn_back'):
            self.btn_back.clicked.connect(self.quay_lai)
        if hasattr(self, 'btn_gio_hang_top'):
            self.btn_gio_hang_top.clicked.connect(self.mo_gio_hang)

    def ve_trang_chu(self):
        switch_window(ChuVuaDashboardScreen())

    def mo_giao_thuong(self):
        switch_window(SearchListMatHangScreen())

    def mo_ho_so(self):
        switch_window(ProfileChuVuaScreen())

    def quay_lai(self):
        switch_window(SearchListMatHangScreen())

    def mo_gio_hang(self):
        switch_window(GioHangScreen())

    def dang_xuat(self):
        reply = QMessageBox.question(self, 'Xác nhận', 'Bạn có chắc chắn muốn đăng xuất?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            switch_window(LoginScreen())


# ==========================================
# PHẦN 5: PHÂN TÍCH & BÁO CÁO
# ==========================================
class PhanTichBaoCaoScreen(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("phan_tich_bao_cao.ui", self)

        # Điều hướng Sidebar
        if hasattr(self, 'btn_menu_trang_chu'):
            self.btn_menu_trang_chu.clicked.connect(self.ve_trang_chu)
        if hasattr(self, 'btn_menu_quan_ly'):
            self.btn_menu_quan_ly.clicked.connect(self.mo_quan_ly_nong_trai)
        if hasattr(self, 'btn_menu_giao_thuong'):
            self.btn_menu_giao_thuong.clicked.connect(self.mo_giao_thuong)
        if hasattr(self, 'btn_menu_ho_so'):
            self.btn_menu_ho_so.clicked.connect(self.mo_ho_so)
        if hasattr(self, 'btn_dang_xuat'):
            self.btn_dang_xuat.clicked.connect(self.dang_xuat)

    def ve_trang_chu(self):
        switch_window(NongDanDashboardScreen())

    def mo_quan_ly_nong_trai(self):
        switch_window(DanhSachCayTrongScreen())

    def mo_giao_thuong(self):
        switch_window(DangSanPhamScreen())

    def mo_ho_so(self):
        switch_window(ProfileNongDanScreen())

    def dang_xuat(self):
        reply = QMessageBox.question(self, 'Xác nhận', 'Bạn có chắc chắn muốn đăng xuất?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            switch_window(LoginScreen())


# ==========================================
# PHẦN 6: ĐĂNG NHẬP / ĐĂNG KÝ / XÁC THỰC
# ==========================================
class NhapProfileInfoScreen(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("nhap_profile_in4.ui", self)

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

        QMessageBox.information(self, "Chúc mừng", "Tạo hồ sơ thành công! Vui lòng đăng nhập.")
        switch_window(LoginScreen())


class RegisterXacThucScreen(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("register_xacthuc.ui", self)

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
        switch_window(NhapProfileInfoScreen())

    def quay_lai_login(self, event):
        switch_window(LoginScreen())


class RegisterScreen(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("register.ui", self)
        if hasattr(self, 'btn_dang_ky'):
            self.btn_dang_ky.clicked.connect(self.xu_ly_dang_ky)
        if hasattr(self, 'lbl_dctk'):
            self.lbl_dctk.mousePressEvent = self.quay_lai_login

    def xu_ly_dang_ky(self):
        if hasattr(self, 'chk_dieu_khoan') and not self.chk_dieu_khoan.isChecked():
            QMessageBox.warning(self, "Nhắc nhở", "Vui lòng đồng ý với Điều khoản & Chính sách để tiếp tục!")
            return

        if (hasattr(self, 'txt_ten_dang_nhap') and not self.txt_ten_dang_nhap.text() or
                hasattr(self, 'txt_mat_khau') and not self.txt_mat_khau.text()):
            QMessageBox.warning(self, "Thông báo", "Vui lòng nhập đầy đủ Tên đăng nhập và Mật khẩu!")
            return

        if hasattr(self, 'txt_mat_khau') and hasattr(self, 'txt_xac_nhan_mat_khau'):
            if self.txt_mat_khau.text() != self.txt_xac_nhan_mat_khau.text():
                QMessageBox.warning(self, "Lỗi", "Mật khẩu xác nhận không khớp!")
                return

        switch_window(RegisterXacThucScreen())

    def quay_lai_login(self, event):
        switch_window(LoginScreen())


class NewPasswordScreen(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("new_password.ui", self)
        if hasattr(self, 'btn_luu'):
            self.btn_luu.clicked.connect(self.ve_man_hinh_login)

    def ve_man_hinh_login(self):
        if (hasattr(self, 'txt_mat_khau_moi') and not self.txt_mat_khau_moi.text() or
                hasattr(self, 'txt_xac_nhan_mat_khau') and not self.txt_xac_nhan_mat_khau.text()):
            QMessageBox.warning(self, "Thông báo", "Vui lòng nhập đầy đủ Mật khẩu mới và Xác nhận mật khẩu!")
            return

        if hasattr(self, 'txt_mat_khau_moi') and hasattr(self, 'txt_xac_nhan_mat_khau'):
            if self.txt_mat_khau_moi.text() != self.txt_xac_nhan_mat_khau.text():
                QMessageBox.warning(self, "Lỗi", "Mật khẩu xác nhận không khớp!")
                return

        QMessageBox.information(self, "Thành công", "Mật khẩu đã được cập nhật! Vui lòng đăng nhập lại.")
        switch_window(LoginScreen())


class OtpScreen(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("otp.ui", self)

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
        switch_window(NewPasswordScreen())


class ForgotKeyScreen(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("forgot_key.ui", self)
        if hasattr(self, 'lbl_quay_lai'):
            self.lbl_quay_lai.mousePressEvent = self.quay_lai_login
        if hasattr(self, 'btn_gui_email'):
            self.btn_gui_email.clicked.connect(self.chuyen_sang_otp)

    def quay_lai_login(self, event):
        switch_window(LoginScreen())

    def chuyen_sang_otp(self):
        switch_window(OtpScreen())


class LoginScreen(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("login.ui", self)

        if hasattr(self, 'lbl_quen_mat_khau'):
            self.lbl_quen_mat_khau.mousePressEvent = self.mo_man_hinh_quen_mat_khau
        if hasattr(self, 'lbl_dang_ky'):
            self.lbl_dang_ky.mousePressEvent = self.mo_man_hinh_dang_ky
        if hasattr(self, 'btn_dang_nhap'):
            self.btn_dang_nhap.clicked.connect(self.xu_ly_dang_nhap)

    def xu_ly_dang_nhap(self):
        if (hasattr(self, 'txt_ten_dang_nhap') and not self.txt_ten_dang_nhap.text() or
                hasattr(self, 'txt_mat_khau') and not self.txt_mat_khau.text()):
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập Tên đăng nhập và Mật khẩu!")
            return

        if (hasattr(self, 'rad_nong_dan') and not self.rad_nong_dan.isChecked() and
                hasattr(self, 'rad_chu_vua') and not self.rad_chu_vua.isChecked()):
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn vai trò để đăng nhập!")
            return

        # Không cần thông báo nữa để vô thẳng cho nhanh
        if hasattr(self, 'rad_nong_dan') and self.rad_nong_dan.isChecked():
            switch_window(NongDanDashboardScreen())
        else:
            switch_window(ChuVuaDashboardScreen())

    def mo_man_hinh_quen_mat_khau(self, event):
        switch_window(ForgotKeyScreen())

    def mo_man_hinh_dang_ky(self, event):
        switch_window(RegisterScreen())


# ==========================================
# PHẦN 7: MÀN HÌNH CHỜ (SPLASH)
# ==========================================
class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("splash_screen.ui", self)
        # Sửa thành QGraphicsOpacityEffect để tương thích với QStackedWidget
        self.effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.effect)
        self.effect.setOpacity(1.0)

        QTimer.singleShot(3000, self.bat_dau_fade_out)

    def bat_dau_fade_out(self):
        self.animation = QPropertyAnimation(self.effect, b"opacity")
        self.animation.setDuration(1000)
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.animation.finished.connect(self.chuyen_sang_login)
        self.animation.start()

    def chuyen_sang_login(self):
        switch_window(LoginScreen())


# ==========================================
# KHỞI CHẠY ỨNG DỤNG
# ==========================================
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Bật MasterWindow (Khung Chứa)
    main_app_window = MasterWindow()
    main_app_window.showMaximized()

    # Mở màn hình đầu tiên (Tự động lọt vào trong Khung)
    switch_window(SplashScreen())

    sys.exit(app.exec())