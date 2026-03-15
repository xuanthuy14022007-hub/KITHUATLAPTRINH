from datetime import date

from PyQt6.QtWidgets import QWidget, QMessageBox
from PyQt6 import uic

from utils.window_manager import get_current_user
from logic.main import (
    switch_window,
    ChuVuaDashboardScreen,
    ProfileChuVuaScreen,
    SearchListMatHangScreen,
    LoginScreen,
)


class ChuVuaDashboardScreen(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui_files/home_chu_vua.ui", self)

        if hasattr(self, 'btn_menu_trang_chu'):
            self.btn_menu_trang_chu.clicked.connect(self.ve_trang_chu)
        if hasattr(self, 'btn_menu_ho_so'):
            self.btn_menu_ho_so.clicked.connect(self.mo_ho_so)
        if hasattr(self, 'btn_menu_giao_thuong'):
            self.btn_menu_giao_thuong.clicked.connect(self.mo_giao_thuong)
        if hasattr(self, 'btn_dang_xuat'):
            self.btn_dang_xuat.clicked.connect(self.dang_xuat)

        self.tai_du_lieu()

    def tai_du_lieu(self):
        user = get_current_user()
        if not user:
            return
        ten_hien_thi = user.get('full_name') or user.get('username', '')
        if hasattr(self, 'lbl_username'):
            self.lbl_username.setText(ten_hien_thi)
        merchant_id = user.get('user_id')
        if not merchant_id:
            return
        danh_sach_don = self._lay_don_hang_cua_merchant(merchant_id)
        self._do_du_lieu_card(danh_sach_don, merchant_id)
        self._do_du_lieu_bang_nguon_hang(danh_sach_don)

    def _lay_don_hang_cua_merchant(self, merchant_id):
        try:
            from database.database_connector import get_connection
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT o.order_id, u.full_name, o.total_amount, o.order_date, o.status
                FROM Orders o JOIN Users u ON o.farmer_id = u.user_id
                WHERE o.merchant_id = ? ORDER BY o.order_date DESC
            """, (merchant_id,))
            rows = cursor.fetchall()
            conn.close()
            return rows
        except Exception as e:
            print(f"Lỗi lấy đơn hàng chủ vựa: {e}")
            return []

    def _do_du_lieu_card(self, danh_sach_don, merchant_id):
        don_dang_xu_ly = sum(1 for d in danh_sach_don if d[4] == 'Chờ xác nhận')
        if hasattr(self, 'lbl_c1_value'):
            self.lbl_c1_value.setText(
                f'<html><body><p>{don_dang_xu_ly} <span style="font-size:14pt;">đơn</span></p></body></html>'
            )
        hom_nay = date.today().strftime('%Y-%m-%d')
        tong_kg = 0
        try:
            from database.database_connector import get_connection
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT SUM(oi.quantity) FROM Orders o
                JOIN OrderItems oi ON o.order_id = oi.order_id
                WHERE o.merchant_id = ? AND o.status = 'Xác nhận' AND DATE(o.order_date) = ?
            """, (merchant_id, hom_nay))
            result = cursor.fetchone()
            tong_kg = result[0] or 0
            conn.close()
        except Exception as e:
            print(f"Lỗi tính hàng nhập: {e}")
        if hasattr(self, 'lbl_c2_value'):
            self.lbl_c2_value.setText(
                f'<html><body><p>{tong_kg:,.0f} <span style="font-size:14pt;">kg</span></p></body></html>'
            )

    def _do_du_lieu_bang_nguon_hang(self, danh_sach_don):
        BADGE_CONFIG = {
            'Xác nhận':     ('✔️ Đã nhập kho',     '#A6CE89', '#1C1C1C'),
            'Chờ xác nhận': ('🚚 Đang vận chuyển', '#F8B4B4', 'white'),
            'Hủy đơn':      ('❌ Đã hủy',          '#E0E0E0', '#888888'),
        }
        rows = [
            {'td1': 'td1_1', 'td2': 'td1_2', 'td3': 'td1_3', 'td4': 'td1_4', 'badge': 'lbl_badge_nhap_kho'},
            {'td1': 'td2_1', 'td2': 'td2_2', 'td3': 'td2_3', 'td4': 'td2_4', 'badge': 'lbl_badge_van_chuyen'},
        ]
        for i, row_cfg in enumerate(rows):
            if i >= len(danh_sach_don):
                for key in ['td1', 'td2', 'td3', 'td4']:
                    w = getattr(self, row_cfg[key], None)
                    if w: w.setText('—')
                continue
            don = danh_sach_don[i]
            order_id, farmer_name, total, order_date, status = don
            crop_name, so_luong = self._lay_chi_tiet_don(order_id)
            try:
                from datetime import datetime
                dt = datetime.strptime(order_date, '%Y-%m-%d')
                thoi_gian = dt.strftime('%d/%m/%Y')
            except Exception:
                thoi_gian = order_date or '—'
            if hasattr(self, row_cfg['td1']):
                getattr(self, row_cfg['td1']).setText(farmer_name or '—')
            if hasattr(self, row_cfg['td2']):
                getattr(self, row_cfg['td2']).setText(crop_name)
            if hasattr(self, row_cfg['td3']):
                getattr(self, row_cfg['td3']).setText(f"{so_luong:,.1f}" if so_luong else '—')
            if hasattr(self, row_cfg['td4']):
                getattr(self, row_cfg['td4']).setText(thoi_gian)
            badge_text, badge_bg, badge_fg = BADGE_CONFIG.get(status, (status, '#E0E0E0', '#1C1C1C'))
            badge_w = getattr(self, row_cfg['badge'], None)
            if badge_w:
                badge_w.setText(badge_text)
                badge_w.setStyleSheet(f"background-color: {badge_bg}; color: {badge_fg}; border-radius: 17px; font-weight: bold; font-size: 10pt;")

    def _lay_chi_tiet_don(self, order_id):
        try:
            from database.database_connector import get_connection
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.crop_name, SUM(oi.quantity) FROM OrderItems oi
                JOIN Crops c ON oi.crop_id = c.crop_id
                WHERE oi.order_id = ? GROUP BY c.crop_name ORDER BY SUM(oi.quantity) DESC LIMIT 1
            """, (order_id,))
            row = cursor.fetchone()
            conn.close()
            return (row[0], row[1]) if row else ('—', 0)
        except Exception:
            return ('—', 0)

    def ve_trang_chu(self):
        switch_window(ChuVuaDashboardScreen())
    def mo_ho_so(self):
        switch_window(ProfileChuVuaScreen())
    def mo_giao_thuong(self):
        switch_window(SearchListMatHangScreen())

    def dang_xuat(self):
        reply = QMessageBox.question(
            self, 'Xác nhận', 'Bạn có chắc chắn muốn đăng xuất?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            from utils.window_manager import set_current_user
            set_current_user(None)
            switch_window(LoginScreen())