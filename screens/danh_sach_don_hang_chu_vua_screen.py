from datetime import datetime

from PyQt6.QtWidgets import QWidget, QMessageBox
from PyQt6 import uic

from utils.window_manager import get_current_user
from logic.main import (
    switch_window,
    ChuVuaDashboardScreen,
    SearchListMatHangScreen,
    ProfileChuVuaScreen,
    GioHangScreen,
    LoginScreen,
)

BADGE_CONFIG = {
    'Chờ xác nhận': ('#BDE08B', '#1C1C1C'),
    'Xác nhận':     ('#A6CE89', '#1C1C1C'),
    'Hủy đơn':      ('#E0E0E0', '#888888'),
}


class DanhSachDonHangChuVuaScreen(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui_files/danh_sach_don_hang_chu_vua.ui", self)

        if hasattr(self, 'btn_menu_trang_chu'):
            self.btn_menu_trang_chu.clicked.connect(self.ve_trang_chu)
        if hasattr(self, 'btn_menu_giao_thuong'):
            self.btn_menu_giao_thuong.clicked.connect(self.mo_giao_thuong)
        if hasattr(self, 'btn_menu_ho_so'):
            self.btn_menu_ho_so.clicked.connect(self.mo_ho_so)
        if hasattr(self, 'btn_dang_xuat'):
            self.btn_dang_xuat.clicked.connect(self.dang_xuat)
        if hasattr(self, 'btn_back'):
            self.btn_back.clicked.connect(self.quay_lai)
        if hasattr(self, 'btn_gio_hang_top'):
            self.btn_gio_hang_top.clicked.connect(self.mo_gio_hang)
        if hasattr(self, 'btn_search_icon'):
            self.btn_search_icon.clicked.connect(self.loc_don_hang)
        if hasattr(self, 'txt_search'):
            self.txt_search.returnPressed.connect(self.loc_don_hang)
        if hasattr(self, 'cmb_status_filter'):
            self.cmb_status_filter.currentIndexChanged.connect(self.loc_don_hang)

        self._tat_ca_don_hang = []
        self.tai_du_lieu()

    def tai_du_lieu(self):
        user = get_current_user()
        if not user:
            return
        merchant_id = user.get('user_id')
        self._tat_ca_don_hang = self._lay_don_hang_merchant(merchant_id)
        tong_don = len(self._tat_ca_don_hang)
        if hasattr(self, 'btn_back'):
            self.btn_back.setText(f"← Đơn hàng ({tong_don})")
        so_gio = self._dem_gio_hang(merchant_id)
        if hasattr(self, 'btn_gio_hang_top'):
            self.btn_gio_hang_top.setText(f"🛒 Giỏ hàng ({so_gio})")
        self._do_du_lieu_len_ui(self._tat_ca_don_hang)

    def _lay_don_hang_merchant(self, merchant_id):
        try:
            from database.database_connector import get_connection
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT o.order_id, u.full_name, u.farm_name, o.status, o.total_amount, o.order_date
                FROM Orders o JOIN Users u ON o.farmer_id = u.user_id
                WHERE o.merchant_id = ? ORDER BY o.order_date DESC
            """, (merchant_id,))
            orders = cursor.fetchall()
            ket_qua = []
            for order in orders:
                order_id, farmer_name, farm_name, status, total, order_date = order
                cursor.execute("SELECT c.crop_name, oi.quantity, oi.unit_price FROM OrderItems oi JOIN Crops c ON oi.crop_id = c.crop_id WHERE oi.order_id = ? LIMIT 1", (order_id,))
                item = cursor.fetchone()
                cursor.execute("SELECT COUNT(*) FROM OrderItems WHERE order_id = ?", (order_id,))
                so_san_pham = cursor.fetchone()[0]
                ket_qua.append({
                    'order_id': order_id, 'farmer_name': farmer_name,
                    'farm_name': farm_name or farmer_name, 'status': status,
                    'total': total, 'order_date': order_date,
                    'crop_name': item[0] if item else '—',
                    'quantity': item[1] if item else 0,
                    'unit_price': item[2] if item else 0,
                    'so_san_pham': so_san_pham,
                })
            conn.close()
            return ket_qua
        except Exception as e:
            print(f"Lỗi lấy đơn hàng: {e}")
            return []

    def _dem_gio_hang(self, merchant_id):
        try:
            from database.database_connector import get_connection
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Cart WHERE merchant_id = ?", (merchant_id,))
            so_luong = cursor.fetchone()[0]
            conn.close()
            return so_luong
        except Exception:
            return 0

    def _do_du_lieu_len_ui(self, danh_sach):
        groups = [
            {'group': 'group_order_1', 'lbl_farm': 'lbl_farm1', 'lbl_badge': 'lbl_badge1', 'lbl_name': 'lbl_name1', 'lbl_stock': 'lbl_stock1', 'lbl_p_val': 'lbl_p_val1', 'lbl_q_val': 'lbl_q_val1', 'lbl_t_val': 'lbl_t_val1', 'lbl_summary': 'lbl_summary1'},
            {'group': 'group_order_2', 'lbl_farm': 'lbl_farm2', 'lbl_badge': 'lbl_badge2', 'lbl_name': 'lbl_name2', 'lbl_stock': 'lbl_stock2', 'lbl_p_val': 'lbl_p_val2', 'lbl_q_val': 'lbl_q_val2', 'lbl_t_val': 'lbl_t_val2', 'lbl_summary': 'lbl_summary2'},
        ]
        for i, cfg in enumerate(groups):
            group = getattr(self, cfg['group'], None)
            if not group: continue
            if i >= len(danh_sach):
                group.setVisible(False)
                continue
            group.setVisible(True)
            don = danh_sach[i]
            if hasattr(self, cfg['lbl_farm']):
                getattr(self, cfg['lbl_farm']).setText(f"🏪 {don['farm_name']}")
            if hasattr(self, cfg['lbl_badge']):
                badge_w = getattr(self, cfg['lbl_badge'])
                badge_w.setText(don['status'])
                bg, fg = BADGE_CONFIG.get(don['status'], ('#E0E0E0', '#1C1C1C'))
                badge_w.setStyleSheet(f"background-color: {bg}; color: {fg}; border-radius: 4px; padding: 4px 15px; font-weight: bold; font-size: 10pt; border: none;")
            if hasattr(self, cfg['lbl_name']):
                getattr(self, cfg['lbl_name']).setText(don['crop_name'])
            if hasattr(self, cfg['lbl_stock']):
                try:
                    ngay = datetime.strptime(don['order_date'], '%Y-%m-%d').strftime('%d/%m/%Y')
                except Exception:
                    ngay = don['order_date']
                getattr(self, cfg['lbl_stock']).setText(f"Ngày đặt: {ngay}")
            if hasattr(self, cfg['lbl_p_val']):
                getattr(self, cfg['lbl_p_val']).setText(f"{don['unit_price']:,.0f} VND / kg")
            if hasattr(self, cfg['lbl_q_val']):
                getattr(self, cfg['lbl_q_val']).setText(f"{don['quantity']:,.0f} kg")
            if hasattr(self, cfg['lbl_t_val']):
                getattr(self, cfg['lbl_t_val']).setText(f"{don['total']:,.0f} VND")
            if hasattr(self, cfg['lbl_summary']):
                getattr(self, cfg['lbl_summary']).setText(
                    f'<html><body>Tổng số tiền ({don["so_san_pham"]} sản phẩm): '
                    f'<span style="font-weight:900; color:#1C1C1C; font-size:16pt;">{don["total"]:,.0f} VND</span></body></html>'
                )

    def loc_don_hang(self):
        tu_khoa = self.txt_search.text().strip().lower() if hasattr(self, 'txt_search') else ''
        trang_thai = self.cmb_status_filter.currentText() if hasattr(self, 'cmb_status_filter') else 'Tất cả trạng thái'
        ket_qua = [
            don for don in self._tat_ca_don_hang
            if (trang_thai == 'Tất cả trạng thái' or don['status'] == trang_thai)
            and (not tu_khoa or tu_khoa in don['farm_name'].lower() or tu_khoa in don['crop_name'].lower())
        ]
        self._do_du_lieu_len_ui(ket_qua)

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
        reply = QMessageBox.question(
            self, 'Xác nhận', 'Bạn có chắc chắn muốn đăng xuất?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            from utils.window_manager import set_current_user
            set_current_user(None)
            switch_window(LoginScreen())