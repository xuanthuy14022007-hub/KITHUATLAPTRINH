from PyQt6.QtWidgets import QWidget, QMessageBox, QLabel
from PyQt6 import uic

from utils.window_manager import switch_window, get_current_user
from logic.logic_giao_thuong import lay_danh_sach_nong_san
from screens.chi_tiet_nong_san_screen import ChiTietNongSanScreen
from screens.home_chu_vua_screen import ChuVuaDashboardScreen
from screens.profile_chu_vua_screen import ProfileChuVuaScreen
from screens.gio_hang_screen import GioHangScreen
from screens.danh_sach_don_hang_chu_vua_screen import DanhSachDonHangChuVuaScreen
from utils.window_manager import set_current_user

class SearchListMatHangScreen(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui_files/search_list_mat_hang.ui", self)

        # ĐIỀU HƯỚNG SIDEBAR
        if hasattr(self, 'btn_menu_trang_chu'):
            self.btn_menu_trang_chu.clicked.connect(self.ve_trang_chu)
        if hasattr(self, 'btn_menu_ho_so'):
            self.btn_menu_ho_so.clicked.connect(self.mo_ho_so)
        if hasattr(self, 'btn_dang_xuat'):
            self.btn_dang_xuat.clicked.connect(self.dang_xuat)

        # Nút giỏ hàng và đơn hàng
        if hasattr(self, 'btn_gio_hang_top'):
            self.btn_gio_hang_top.clicked.connect(self.mo_gio_hang)
        if hasattr(self, 'btn_don_hang_top'):
            self.btn_don_hang_top.clicked.connect(self.mo_don_hang)

        # Chức năng tìm kiếm
        if hasattr(self, 'btn_search_icon'):
            self.btn_search_icon.clicked.connect(self.tai_du_lieu)
        if hasattr(self, 'txt_search'):
            self.txt_search.returnPressed.connect(self.tai_du_lieu)
            
        # Lọc
        if hasattr(self, 'btn_loc'):
            self.btn_loc.clicked.connect(self.tai_du_lieu)

        # Tải danh sách lúc khởi động
        self.tai_du_lieu()

    def tai_du_lieu(self):
        tu_khoa = ""
        if hasattr(self, 'txt_search'):
            tu_khoa = self.txt_search.text().strip()
            
        # Gọi logic lấy danh sách
        # list: (activity_id, full_name, crop_name, quantity, price, plot_name)
        danh_sach = lay_danh_sach_nong_san(tu_khoa)
        
        # Cập nhật số lượng
        if hasattr(self, 'lbl_page_title'):
            # self.lbl_page_title.setText(f"DANH SÁCH MẶT HÀNG ({len(danh_sach)})")
            pass
            
        # Hiển thị lên tối đa 6 thẻ UI tĩnh (card_1 -> card_6)
        for i in range(1, 7):
            card = getattr(self, f"card_{i}", None)
            if not card:
                continue
                
            if i - 1 < len(danh_sach):
                sp = danh_sach[i - 1]
                card.show()
                # sp = (0: activity_id, 1: full_name, 2: crop_name, 3: quantity, 4: price, 5: plot_name)
                
                # Cập nhật thông tin qua order của QLabel
                labels = card.findChildren(QLabel)
                if len(labels) >= 8:
                    # labels[1]: crop_name
                    labels[1].setText(sp[2])
                    # labels[3]: full_name
                    labels[3].setText(sp[1] if sp[1] else "Nông trại")
                    # labels[4]: plot_name / region
                    vung_mien = "📍 " + (sp[5] if sp[5] else "Chưa rõ")
                    labels[4].setText(vung_mien)
                    # labels[6]: quantity
                    qty_str = f"{sp[3] if sp[3] else 0:,.0f} kg".replace(",", ".")
                    labels[6].setText(qty_str)
                    # labels[7]: price
                    gia_str = f"{sp[4] if sp[4] else 0:,.0f} VND / kg".replace(",", ".")
                    labels[7].setText(gia_str)
                
                # Bắt event click
                # Dùng thuộc tính tuỳ chỉnh để chứa ID
                card.activity_id = sp[0]
                # Viết lại mousePressEvent
                card.mousePressEvent = lambda event, c=card: self.mo_chi_tiet_nong_san(c.activity_id)
            else:
                card.hide()

    def mo_chi_tiet_nong_san(self, activity_id):
        # Mở màn hình chi tiết và truyền ID
        screen = ChiTietNongSanScreen(activity_id)
        switch_window(screen)

    # ĐIỀU HƯỚNG
    def ve_trang_chu(self):
        switch_window(ChuVuaDashboardScreen())

    def mo_ho_so(self):
        switch_window(ProfileChuVuaScreen())

    def mo_gio_hang(self):
        switch_window(GioHangScreen())

    def mo_don_hang(self):
        switch_window(DanhSachDonHangChuVuaScreen())

    def dang_xuat(self):
        reply = QMessageBox.question(self, 'Xác nhận', 'Bạn có chắc chắn muốn đăng xuất?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            set_current_user(None)
            switch_window(LoginScreen())
