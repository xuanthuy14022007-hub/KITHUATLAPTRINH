from datetime import date
from PyQt6.QtWidgets import QWidget, QMessageBox
from PyQt6 import uic
from utils.window_manager import get_current_user, switch_window
from logic.logic_giao_thuong import thanh_toan_gio_hang

class PreOrderScreen(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui_files/pre_order.ui", self)

        if hasattr(self, 'btn_menu_trang_chu'):
            self.btn_menu_trang_chu.clicked.connect(self.ve_trang_chu)
        if hasattr(self, 'btn_menu_giao_thuong'):
            self.btn_menu_giao_thuong.clicked.connect(self.mo_giao_thuong)
        if hasattr(self, 'btn_menu_ho_so'):
            self.btn_menu_ho_so.clicked.connect(self.mo_ho_so)
        if hasattr(self, 'btn_dang_xuat'):
            self.btn_dang_xuat.clicked.connect(self.dang_xuat)
        if hasattr(self, 'btn_back'):
            self.btn_back.clicked.connect(self.quay_lai_gio_hang)
        if hasattr(self, 'btn_quay_lai'):
            self.btn_quay_lai.clicked.connect(self.quay_lai_gio_hang)
        if hasattr(self, 'btn_xac_nhan_dat_hang'):
            self.btn_xac_nhan_dat_hang.clicked.connect(self.xac_nhan_dat_hang)

        self.tai_du_lieu()

    def tai_du_lieu(self):
        user = get_current_user()
        if not user:
            return
        if hasattr(self, 'txt_ten_nguoi_nhan'):
            self.txt_ten_nguoi_nhan.setText(user.get('full_name', ''))
        if hasattr(self, 'txt_sdt'):
            self.txt_sdt.setPlaceholderText('Nhập số điện thoại')
            self.txt_sdt.clear()
        if hasattr(self, 'txt_dia_chi'):
            self.txt_dia_chi.setPlainText(user.get('address', ''))
        gio_hang = self._lay_gio_hang(user.get('user_id'))
        self._do_tom_tat_don_hang(gio_hang)

    def _lay_gio_hang(self, merchant_id):
        try:
            from database.database_connector import get_connection
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT cart.cart_id, c.crop_name, cart.quantity,
                       COALESCE(fa.selling_price, c.base_price) as price,
                       al.quantity as ton_kho, cart.activity_id,
                       u.full_name as farmer_name, u.farm_name
                FROM Cart cart
                JOIN FarmingActivities fa ON cart.activity_id = fa.activity_id
                JOIN Crops c ON fa.crop_id = c.crop_id
                JOIN Users u ON fa.farmer_id = u.user_id
                LEFT JOIN ActivityLog al ON fa.activity_id = al.activity_id AND al.action_type = 'Thu hoạch'
                WHERE cart.merchant_id = ? ORDER BY cart.cart_id
            """, (merchant_id,))
            rows = cursor.fetchall()
            conn.close()
            return rows
        except Exception as e:
            print(f"Lỗi lấy giỏ hàng: {e}")
            return []

    def _do_tom_tat_don_hang(self, gio_hang):
        if gio_hang and hasattr(self, 'lbl_farm_name'):
            self.lbl_farm_name.setText(f"🏪 {gio_hang[0][7] or gio_hang[0][6]}")
        tong_tien = 0
        for i, (frame_name, lbl_name, lbl_qty, lbl_total) in enumerate([
            ('item_1', 'name_1', 'qty_1', 'total_1'),
            ('item_2', 'name_2', 'qty_2', 'total_2'),
            ('item_3', 'name_3', 'qty_3', 'total_3'),
        ]):
            frame = getattr(self, frame_name, None)
            if not frame:
                continue
            if i >= len(gio_hang):
                frame.setVisible(False)
                continue
            frame.setVisible(True)
            item = gio_hang[i]
            quantity, don_gia = item[2], item[3]
            thanh_tien = quantity * don_gia
            tong_tien += thanh_tien
            if hasattr(self, lbl_name):
                getattr(self, lbl_name).setText(item[1])
            if hasattr(self, lbl_qty):
                getattr(self, lbl_qty).setText(
                    f'<html><body>{quantity:,.0f} <span style="font-size:10pt;">kg</span></body></html>'
                )
            if hasattr(self, lbl_total):
                getattr(self, lbl_total).setText(
                    f'<html><body><span style="color:#1C1C1C;">{thanh_tien:,.0f}</span> <span style="font-size:10pt;">VND</span></body></html>'
                )
        if hasattr(self, 'lbl_tong_cong'):
            self.lbl_tong_cong.setText(
                f'<html><body>Tổng cộng: <span style="font-size:18pt; font-weight:bold;">{tong_tien:,.0f}</span>'
                f'<span style="font-size:12pt; font-weight:normal; color:#4A4A4A;"> VND</span></body></html>'
            )

    def xac_nhan_dat_hang(self):
        ten = self.txt_ten_nguoi_nhan.text().strip() if hasattr(self, 'txt_ten_nguoi_nhan') else ''
        sdt = self.txt_sdt.text().strip() if hasattr(self, 'txt_sdt') else ''
        dia_chi = self.txt_dia_chi.toPlainText().strip() if hasattr(self, 'txt_dia_chi') else ''
        if not ten:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập tên người nhận!")
            return
        if not sdt:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập số điện thoại!")
            return
        if not dia_chi:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập địa chỉ nhận hàng!")
            return
        user = get_current_user()
        if not user:
            return
        try:
            thanh_toan_gio_hang(user.get('user_id'), date.today().strftime('%Y-%m-%d'))
            QMessageBox.information(self, "Thành công", "Đã đặt hàng thành công!\nĐơn hàng đang chờ xác nhận từ nông trại.")
            from screens.danh_sach_don_hang_chu_vua_screen import DanhSachDonHangChuVuaScreen
            switch_window(DanhSachDonHangChuVuaScreen)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể đặt hàng: {e}")

    def ve_trang_chu(self):
        from screens.home_chu_vua_screen import ChuVuaDashboardScreen
        switch_window(ChuVuaDashboardScreen)

    def mo_giao_thuong(self):
        from screens.search_list_mat_hang_screen import SearchListMatHangScreen
        switch_window(SearchListMatHangScreen)

    def mo_ho_so(self):
        from screens.profile_chu_vua_screen import ProfileChuVuaScreen
        switch_window(ProfileChuVuaScreen)

    def quay_lai_gio_hang(self):
        from screens.gio_hang_screen import GioHangScreen
        switch_window(GioHangScreen)

    def dang_xuat(self):
        reply = QMessageBox.question(
            self, 'Xác nhận', 'Bạn có chắc chắn muốn đăng xuất?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            from utils.window_manager import set_current_user
            from screens.login_screen import LoginScreen
            set_current_user(None)
            switch_window(LoginScreen)
