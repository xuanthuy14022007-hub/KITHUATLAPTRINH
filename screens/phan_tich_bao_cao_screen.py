from PyQt6.QtWidgets import QWidget, QMessageBox
from PyQt6 import uic

from utils.window_manager import switch_window, get_current_user
from logic.logic_tinh_toan import lay_ket_qua_tai_chinh_tong_quat, them_chi_phi


class PhanTichBaoCaoScreen(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui_files/phan_tich_bao_cao.ui", self)

        # ĐIỀU HƯỚNG SIDEBAR
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

        # KẾT NỐI TƯƠNG TÁC NÚT
        if hasattr(self, 'btn_nhap'):
            self.btn_nhap.clicked.connect(self.xu_ly_them_chi_phi)
        if hasattr(self, 'btn_tinh_toan'):
            self.btn_tinh_toan.clicked.connect(self.tai_du_lieu_bao_cao)
        if hasattr(self, 'btn_xuat_bao_cao'):
            self.btn_xuat_bao_cao.clicked.connect(self.xuat_bao_cao)

        self.tai_du_lieu_bao_cao()

    # XỬ LÝ CHÍNH
    def tai_du_lieu_bao_cao(self):
        user = get_current_user()
        if not user:
            return
        farmer_id = user.get('user_id')
        if not farmer_id:
            return
            
        stats = lay_ket_qua_tai_chinh_tong_quat(farmer_id)
        dt = stats.get('doanh_thu', 0)
        cp = stats.get('chi_phi', 0)
        ln = stats.get('loi_nhuan', 0)
        
        # Format values
        dt_str = f"{dt:,.0f}".replace(",", ".")
        cp_str = f"{cp:,.0f}".replace(",", ".")
        ln_str = f"{ln:,.0f}".replace(",", ".")
        
        # HTML formatting for labels
        html_tln = f'<html><head/><body><p><span style=" font-size:24pt; font-weight:bold; color:#1C1C1C;">{ln_str}</span><span style=" font-size:16pt; color:#3E7B40;"> VND</span></p></body></html>'
        html_dt = f'<html><head/><body><p><span style=" font-size:18pt; color:#1C1C1C;">{dt_str}</span><span style=" font-size:12pt; color:#4A4A4A;"> VND</span></p></body></html>'
        html_cp = f'<html><head/><body><p><span style=" font-size:18pt; color:#1C1C1C;">{cp_str}</span><span style=" font-size:12pt; color:#4A4A4A;"> VND</span></p></body></html>'
        html_ln = f'<html><head/><body><p><span style=" font-size:18pt; color:#1C1C1C;">{ln_str}</span><span style=" font-size:12pt; color:#4A4A4A;"> VND</span></p></body></html>'

        if hasattr(self, 'lbl_val_tln'):
            self.lbl_val_tln.setText(html_tln)
        if hasattr(self, 'lbl_dt_val'):
            self.lbl_dt_val.setText(html_dt)
        if hasattr(self, 'lbl_cp_val'):
            self.lbl_cp_val.setText(html_cp)
        if hasattr(self, 'lbl_ln_val'):
            self.lbl_ln_val.setText(html_ln)

    def xu_ly_them_chi_phi(self):
        user = get_current_user()
        if not user:
            QMessageBox.warning(self, "Lỗi", "Vui lòng đăng nhập lại.")
            return
            
        loai_cp = self.cmb_loai_chi_phi.currentText() if hasattr(self, 'cmb_loai_chi_phi') else "Khác"
        tien_str = self.txt_so_tien.text().strip() if hasattr(self, 'txt_so_tien') else "0"
        
        if not tien_str:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập số tiền chi phí.")
            return
            
        try:
            # Loại bỏ các dấu phẩy hoặc chấm phân cách để cast sang int
            tien_str = tien_str.replace(",", "").replace(".", "")
            amount = float(tien_str)
            if amount < 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Lỗi", "Số tiền không hợp lệ. Vui lòng nhập số dương.")
            return
            
        # Gọi logic gán chi phí cho mục chung farmer
        farmer_id = user.get('user_id')
        success = them_chi_phi(farmer_id, loai_cp, amount)
        if success:
            QMessageBox.information(self, "Thành công", f"Đã thêm chi phí {loai_cp}: {amount:,.0f} VND".replace(",", "."))
            if hasattr(self, 'txt_so_tien'):
                self.txt_so_tien.clear()
            self.tai_du_lieu_bao_cao() # Tải lại báo cáo
        else:
            QMessageBox.warning(self, "Thất bại", "Không thể thêm chi phí.")

    def xuat_bao_cao(self):
        QMessageBox.information(self, "Báo cáo", "Tính năng xuất báo cáo đang được phát triển.")

    # ĐIỀU HƯỚNG
    def ve_trang_chu(self):
        from screens.home_nong_dan_screen import NongDanDashboardScreen
        switch_window(NongDanDashboardScreen())

    def mo_quan_ly_nong_trai(self):
        from screens.danh_sach_cay_trong_screen import DanhSachCayTrongScreen
        switch_window(DanhSachCayTrongScreen())

    def mo_giao_thuong(self):
        from screens.dang_san_pham_screen import DangSanPhamScreen
        switch_window(DangSanPhamScreen())

    def mo_ho_so(self):
        from screens.profile_nong_dan_screen import ProfileNongDanScreen
        switch_window(ProfileNongDanScreen())

    def dang_xuat(self):
        reply = QMessageBox.question(self, 'Xác nhận', 'Bạn có chắc chắn muốn đăng xuất?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            from utils.window_manager import set_current_user
            set_current_user(None)
            from screens.login_screen import LoginScreen
            switch_window(LoginScreen())
