from PyQt6.QtWidgets import QWidget, QMessageBox, QApplication
from PyQt6.QtCore import Qt
from PyQt6 import uic

from utils.window_manager import switch_window, get_current_user
from logic.logic_cay_trong import lay_danh_sach_cay
from logic.logic_mua_vu import lay_danh_sach_vu_mua
from screens.chinh_sua_cay_trong_popup import ChinhSuaCayTrongPopup
from screens.home_nong_dan_screen import NongDanDashboardScreen
from screens.dang_san_pham_screen import DangSanPhamScreen
from screens.phan_tich_bao_cao_screen import PhanTichBaoCaoScreen
from screens.profile_nong_dan_screen import ProfileNongDanScreen
from screens.chi_tiet_cay_trong_screen import ChiTietCayTrongScreen
from utils.window_manager import set_current_user
from screens.login_screen import LoginScreen

class DanhSachCayTrongScreen(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui_files/danh_sach_cay_trong.ui", self)

        # ĐIỀU HƯỚNG SIDEBAR
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

        # Popup thêm cây trồng
        if hasattr(self, 'btn_them_cay_trong'):
            self.btn_them_cay_trong.clicked.connect(self.mo_popup_them_sua)

        self.popup = None
        self.tai_du_lieu_cay_trong()

    # XỬ LÝ CHÍNH
    def tai_du_lieu_cay_trong(self):
        user = get_current_user()
        if not user:
            return
        
        ds_vu_mua = lay_danh_sach_vu_mua(user.get('user_id'))
        
        ICON_MAP = {'Ngô': '🌽', 'Lúa': '🌾', 'Rau': '🥬', 'Táo': '🍎', 'Nhãn': '🍎'}
        STATUS_MAP = {
            'Sắp thu hoạch': ('🌱 Sắp thu hoạch',   '#213C22', 'white',    85),
            'Đang trồng':    ('✔️ Đang sinh trưởng', '#A6D089', '#1C1C1C', 50),
            'Đã thu hoạch':  ('✅ Đã thu hoạch',     '#4CAF50', 'white',   100),
            'Sẵn sàng bán':  ('✅ Sẵn sàng bán',     '#4CAF50', 'white',   100),
        }
        
        # Ẩn tất cả frame con mặc định (hoặc clear data nếu muốn giữ lưới)
        for i in range(1, 6):
            td_frame = getattr(self, f'td{i}_0', None)
            if td_frame:
                td_frame.setVisible(False)
            td_1 = getattr(self, f'td{i}_1', None)
            if td_1: td_1.setVisible(False)
            td_2 = getattr(self, f'td{i}_2', None)
            if td_2: td_2.setVisible(False)
            td_3 = getattr(self, f'td{i}_3', None)
            if td_3: td_3.setVisible(False)
            td_4 = getattr(self, f'td{i}_4', None)
            if td_4: td_4.setVisible(False)

        # Hiển thị dữ liệu thực tế
        for i, vm in enumerate(ds_vu_mua):
            row = i + 1
            if row > 5:
                break
                
            activity_id = vm[0]
            crop_name = vm[1]
            plot_name = vm[2]
            area_m2 = vm[3] or 0
            area_ha = round(area_m2 / 10000, 1)
            status = vm[6]
            
            # Icon 
            icon = '🌱'
            for k, v in ICON_MAP.items():
                if k.lower() in crop_name.lower():
                    icon = v
                    break
            
            # Badge 
            ten_badge, bg, fg, prg = STATUS_MAP.get(status, (status, '#888888', 'white', 0))

            td_frame = getattr(self, f'td{row}_0', None)
            if td_frame:
                td_frame.setVisible(True)
                td_frame.mousePressEvent = lambda event, aid=activity_id: self.mo_chi_tiet_cay_trong(aid)
                
            lbl_img = getattr(self, f'img_{row}', None)
            if lbl_img: lbl_img.setText(icon)
            
            lbl_name = getattr(self, f'name_{row}', None)
            if lbl_name: lbl_name.setText(crop_name)
            
            lbl_plot = getattr(self, f'td{row}_1', None)
            if lbl_plot: 
                lbl_plot.setVisible(True)
                lbl_plot.setText(plot_name)
                
            lbl_area = getattr(self, f'td{row}_2', None)
            if lbl_area: 
                lbl_area.setVisible(True)
                lbl_area.setText(f"{area_ha} ha")
                
            td_3 = getattr(self, f'td{row}_3', None)
            if td_3: td_3.setVisible(True)
            prg_bar = getattr(self, f'prg_{row}', None)
            if prg_bar: prg_bar.setValue(prg)
            
            td_4 = getattr(self, f'td{row}_4', None)
            if td_4: td_4.setVisible(True)
            lbl_badge = getattr(self, f'badge_{row}', None)
            if lbl_badge:
                lbl_badge.setText(ten_badge)
                lbl_badge.setStyleSheet(
                    f"background-color: {bg}; color: {fg}; border-radius: 12px; padding: 4px 12px; font-weight: bold; font-size: 10pt;"
                )
    def mo_popup_them_sua(self):
        self.popup = ChinhSuaCayTrongPopup()
        self.popup.show()

    # ĐIỀU HƯỚNG
    def ve_trang_chu(self):
        switch_window(NongDanDashboardScreen())

    def mo_giao_thuong(self):
        switch_window(DangSanPhamScreen())

    def mo_phan_tich(self):
        switch_window(PhanTichBaoCaoScreen())

    def mo_ho_so(self):
        switch_window(ProfileNongDanScreen())

    def mo_chi_tiet_cay_trong(self, activity_id=None):
        # Cần cách truyền activity_id sang ChiTietCayTrongScreen thay vì constructor rỗng nếu muốn
        screen = ChiTietCayTrongScreen(activity_id=activity_id) if activity_id else ChiTietCayTrongScreen()
        switch_window(screen)

    def dang_xuat(self):
        reply = QMessageBox.question(self, 'Xác nhận', 'Bạn có chắc chắn muốn đăng xuất?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            set_current_user(None)
            switch_window(LoginScreen())
