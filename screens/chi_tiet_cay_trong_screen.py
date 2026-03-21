from PyQt6.QtWidgets import QWidget, QMessageBox
from PyQt6 import uic

from utils.window_manager import switch_window, get_current_user
from logic.logic_mua_vu import lay_danh_sach_vu_mua
from screens.chinh_sua_cay_trong import ChinhSuaCayTrongPopup
from screens.home_nong_dan_screen import NongDanDashboardScreen
from screens.danh_sach_cay_trong_screen import DanhSachCayTrongScreen
from screens.dang_san_pham_screen import DangSanPhamScreen
from screens.phan_tich_bao_cao_screen import PhanTichBaoCaoScreen
from screens.profile_nong_dan_screen import ProfileNongDanScreen
from screens.profile_nong_dan_screen import ProfileNongDanScreen
from screens.danh_sach_cay_trong_screen import DanhSachCayTrongScreen
from screens.nhat_ky_canh_tac_screen import NhatKyCanhTacScreen
from screens.goi_y_cham_soc_screen import GoiYChamSocScreen
from utils.window_manager import set_current_user
from screens.login_screen import LoginScreen

class ChiTietCayTrongScreen(QWidget):
    def __init__(self, activity_id=None):
        super().__init__()
        uic.loadUi("ui_files/chi_tiet_cay_trong.ui", self)
        
        self.activity_id = activity_id

        # ĐIỀU HƯỚNG SIDEBAR
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

        # ĐIỀU HƯỚNG TAB
        if hasattr(self, 'lbl_tab_danh_sach'):
            self.lbl_tab_danh_sach.mousePressEvent = self.quay_lai_danh_sach
        if hasattr(self, 'lbl_tab_nhat_ky'):
            self.lbl_tab_nhat_ky.mousePressEvent = self.mo_nhat_ky
        if hasattr(self, 'lbl_tab_goi_y'):
            self.lbl_tab_goi_y.mousePressEvent = self.mo_goi_y

        # Nút chỉnh sửa/xóa cây trồng
        if hasattr(self, 'btn_edit_delete'):
            self.btn_edit_delete.clicked.connect(self.mo_popup_them_sua)

        self.popup = None
        self.tai_du_lieu()

    def tai_du_lieu(self):
        if not self.activity_id:
            user = get_current_user()
            if user:
                # Nếu không có activity_id được truyền, lấy id mới nhất của nông dân để ko bị trống
                ds = lay_danh_sach_vu_mua(user.get('user_id'))
                if ds:
                    self.activity_id = ds[0][0]
                else:
                    return
            else:
                return
                
        user = get_current_user()
        farmer_id = user.get('user_id')
        ds_vu_mua = lay_danh_sach_vu_mua(farmer_id)
        vu_mua = next((vm for vm in ds_vu_mua if vm[0] == self.activity_id), None)
        if not vu_mua:
            return
            
        activity_id, crop_name, plot_name, area_m2, start_date, selling_price, status = vu_mua
        area_ha = round((area_m2 or 0) / 10000, 1)
        
        ICON_MAP = {'Ngô': '🌽', 'Lúa': '🌾', 'Rau': '🥬', 'Táo': '🍎', 'Nhãn': '🍎'}
        icon = '🌱'
        for k, v in ICON_MAP.items():
            if k.lower() in crop_name.lower():
                icon = v
                break
                
        STATUS_MAP = {
            'Sắp thu hoạch': ('🌱 Sắp thu hoạch',   '#213C22', 'white',    85),
            'Đang trồng':    ('✔️ Đang sinh trưởng', '#A6D089', '#1C1C1C', 50),
            'Đã thu hoạch':  ('✅ Đã thu hoạch',     '#4CAF50', 'white',   100),
            'Sẵn sàng bán':  ('✅ Sẵn sàng bán',     '#4CAF50', 'white',   100),
        }
        ten_badge, bg, fg, prg = STATUS_MAP.get(status, (status, '#888888', 'white', 0))
        
        if hasattr(self, 'img_cay_trong'): self.img_cay_trong.setText(f"{icon}")
        if hasattr(self, 'lbl_ten_cay_to'): self.lbl_ten_cay_to.setText(crop_name)
        if hasattr(self, 'lbl_badge_thua'): self.lbl_badge_thua.setText(f"Thửa đất: {plot_name}")
        if hasattr(self, 'lbl_badge_status_main'): 
            self.lbl_badge_status_main.setText(ten_badge)
            self.lbl_badge_status_main.setStyleSheet(
                f"background-color: {bg}; color: {fg}; font-size: 12pt; font-weight: bold; border-radius: 18px; padding: 8px 20px;"
            )
            
        if hasattr(self, 'lbl_ttc_col2_1'): self.lbl_ttc_col2_1.setText(crop_name)
        if hasattr(self, 'lbl_ttc_col2_2'): self.lbl_ttc_col2_2.setText(plot_name)
        if hasattr(self, 'lbl_ttc_col2_3'): self.lbl_ttc_col2_3.setText(f"{area_ha} ha")
        if hasattr(self, 'lbl_ttc_col2_4'):
            # Convert date format if needed
            self.lbl_ttc_col2_4.setText(start_date or "")
            
        if hasattr(self, 'lbl_badge_canhbao'): self.lbl_badge_canhbao.setVisible(False)
        if hasattr(self, 'prg_sinh_truong'): self.prg_sinh_truong.setValue(prg)

    def mo_popup_them_sua(self):
        self.popup = ChinhSuaCayTrongPopup(activity_id=self.activity_id)
        self.popup.show()

    # ĐIỀU HƯỚNG
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
        switch_window(NhatKyCanhTacScreen(activity_id=self.activity_id))

    def mo_goi_y(self, event):
        switch_window(GoiYChamSocScreen(activity_id=self.activity_id))

    def dang_xuat(self):
        reply = QMessageBox.question(self, 'Xác nhận', 'Bạn có chắc chắn muốn đăng xuất?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            set_current_user(None)
            switch_window(LoginScreen())
