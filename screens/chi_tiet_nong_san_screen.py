from PyQt6.QtWidgets import QWidget, QMessageBox
from PyQt6 import uic

from utils.window_manager import switch_window, get_current_user
from database.database_connector import get_connection
from logic.logic_giao_thuong import them_vao_gio_hang


class ChiTietNongSanScreen(QWidget):
    def __init__(self, activity_id=None):
        super().__init__()
        uic.loadUi("ui_files/chi_tiet_nong_san.ui", self)
        self.activity_id = activity_id

        # ĐIỀU HƯỚNG SIDEBAR
        if hasattr(self, 'btn_menu_trang_chu'):
            self.btn_menu_trang_chu.clicked.connect(self.ve_trang_chu)
        if hasattr(self, 'btn_menu_giao_thuong'):
            self.btn_menu_giao_thuong.clicked.connect(self.mo_giao_thuong)
        if hasattr(self, 'btn_menu_ho_so'):
            self.btn_menu_ho_so.clicked.connect(self.mo_ho_so)
        if hasattr(self, 'btn_dang_xuat'):
            self.btn_dang_xuat.clicked.connect(self.dang_xuat)

        if hasattr(self, 'btn_back'):
            self.btn_back.clicked.connect(self.quay_lai_danh_sach)
            
        if hasattr(self, 'btn_gio_hang_top'):
            self.btn_gio_hang_top.clicked.connect(self.mo_gio_hang)
        if hasattr(self, 'btn_don_hang_top'):
            self.btn_don_hang_top.clicked.connect(self.mo_don_hang)

        # XỬ LÝ CHÍNH
        if hasattr(self, 'btn_add_cart'):
            self.btn_add_cart.clicked.connect(self.xu_ly_them_vao_gio_hang)
        if hasattr(self, 'btn_plus'):
            self.btn_plus.clicked.connect(self.tang_so_luong)
        if hasattr(self, 'btn_minus'):
            self.btn_minus.clicked.connect(self.giam_so_luong)
            
        self.ton_kho = 0
        self.tai_du_lieu_chi_tiet()

    def tai_du_lieu_chi_tiet(self):
        if not self.activity_id:
            return
            
        conn = get_connection()
        cursor = conn.cursor()
        query = """
            SELECT c.crop_name, u.full_name, fa.plot_name, fa.status,
                   al.quantity, COALESCE(fa.selling_price, c.base_price),
                   fa.start_date
            FROM FarmingActivities fa
            JOIN Users u ON fa.farmer_id = u.user_id
            JOIN Crops c ON fa.crop_id = c.crop_id
            LEFT JOIN ActivityLog al ON fa.activity_id = al.activity_id AND al.action_type = 'Thu hoạch'
            WHERE fa.activity_id = ?
        """
        cursor.execute(query, (self.activity_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            QMessageBox.warning(self, "Lỗi", "Không tìm thấy thông tin nông sản.")
            self.quay_lai_danh_sach()
            return
            
        crop_name, full_name, plot_name, status, quantity, price, start_date = row
        self.ton_kho = quantity if quantity else 0
        
        # Cập nhật UI
        if hasattr(self, 'lbl_product_name'):
            self.lbl_product_name.setText(crop_name)
        if hasattr(self, 'btn_back'):
            self.btn_back.setText(f"← {crop_name}")
        if hasattr(self, 'lbl_breadcrumb'):
            self.lbl_breadcrumb.setText(f'<html><head/><body><p><span style=" color:#7D7D7D;">Danh sách mặt hàng &gt; </span><span style=" color:#1C1C1C;">{crop_name}</span></p></body></html>')
            
        if hasattr(self, 'lbl_farm_name'):
            self.lbl_farm_name.setText(f"◎ Nông trại của {full_name}")
        if hasattr(self, 'lbl_location'):
            self.lbl_location.setText(f"📍 {plot_name if plot_name else 'Khu vực chưa rõ'}")
            
        if hasattr(self, 'lbl_harvest_status'):
            self.lbl_harvest_status.setText(f'<html><body>🕒 Trạng thái:<br><span style="font-weight:bold; color:#1C1C1C;">{status}</span></body></html>')
            
        if hasattr(self, 'lbl_price_value'):
            gia_str = f"{price:,.0f}".replace(",", ".")
            self.lbl_price_value.setText(f'<html><body><span style="font-size:26pt; font-weight:900; color:#1C1C1C;">{gia_str}</span><span style="font-size:14pt; color:#4A4A4A;"> VND / kg</span></body></html>')
            
        if hasattr(self, 'lbl_stock_val'):
            qty_str = f"{self.ton_kho:,.0f}".replace(",", ".")
            self.lbl_stock_val.setText(f"{qty_str} kg")
            
        if hasattr(self, 'lbl_seller'):
            self.lbl_seller.setText(f'<html><body>👤 Người bán: <span style="font-weight:bold; color:#1C1C1C;">{full_name}</span></body></html>')
            
        if hasattr(self, 'txt_quantity'):
            self.txt_quantity.setText("1")

    def tang_so_luong(self):
        if not hasattr(self, 'txt_quantity'):
            return
        
        try:
            sl = float(self.txt_quantity.text())
            if sl < self.ton_kho:
                self.txt_quantity.setText(str(int(sl + 1)))
        except ValueError:
            self.txt_quantity.setText("1")

    def giam_so_luong(self):
        if not hasattr(self, 'txt_quantity'):
            return
            
        try:
            sl = float(self.txt_quantity.text())
            if sl > 1:
                self.txt_quantity.setText(str(int(sl - 1)))
        except ValueError:
            self.txt_quantity.setText("1")

    def xu_ly_them_vao_gio_hang(self):
        user = get_current_user()
        if not user or not self.activity_id:
            QMessageBox.warning(self, "Lỗi", "Vui lòng đăng nhập lại.")
            return
            
        merchant_id = user.get('user_id')
        
        if not hasattr(self, 'txt_quantity'):
            return
            
        try:
            quantity = float(self.txt_quantity.text())
            if quantity <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Lỗi số lượng", "Vui lòng nhập số lượng hợp lệ.")
            return
            
        if quantity > self.ton_kho:
            QMessageBox.warning(self, "Vượt quá tồn kho", f"Trong kho chỉ còn {self.ton_kho:,.0f} kg.")
            return
            
        success = them_vao_gio_hang(merchant_id, self.activity_id, quantity)
        if success:
            QMessageBox.information(self, "Thành công", "Đã thêm nông sản vào giỏ hàng!")
        else:
            QMessageBox.warning(self, "Thất bại", "Lỗi khi thêm vào giỏ hàng.")

    # ĐIỀU HƯỚNG
    def ve_trang_chu(self):
        from screens.home_chu_vua_screen import ChuVuaDashboardScreen
        switch_window(ChuVuaDashboardScreen())

    def mo_giao_thuong(self):
        from screens.search_list_mat_hang_screen import SearchListMatHangScreen
        switch_window(SearchListMatHangScreen())

    def mo_ho_so(self):
        from screens.profile_chu_vua_screen import ProfileChuVuaScreen
        switch_window(ProfileChuVuaScreen())

    def quay_lai_danh_sach(self):
        from screens.search_list_mat_hang_screen import SearchListMatHangScreen
        switch_window(SearchListMatHangScreen())

    def mo_gio_hang(self):
        from screens.gio_hang_screen import GioHangScreen
        switch_window(GioHangScreen())

    def mo_don_hang(self):
        from screens.danh_sach_don_hang_chu_vua_screen import DanhSachDonHangChuVuaScreen
        switch_window(DanhSachDonHangChuVuaScreen())

    def dang_xuat(self):
        reply = QMessageBox.question(self, 'Xác nhận', 'Bạn có chắc chắn muốn đăng xuất?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            from utils.window_manager import set_current_user
            set_current_user(None)
            from screens.login_screen import LoginScreen
            switch_window(LoginScreen())
