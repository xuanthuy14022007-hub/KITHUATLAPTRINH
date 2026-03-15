from PyQt6.QtWidgets import QWidget, QMessageBox
from PyQt6 import uic

from utils.window_manager import get_current_user
from logic.main import (
    switch_window,
    ChuVuaDashboardScreen,
    SearchListMatHangScreen,
    ProfileChuVuaScreen,
    PreOrderScreen,
    DanhSachDonHangChuVuaScreen,
    LoginScreen,
)


class GioHangScreen(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui_files/gio_hang.ui", self)

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
        if hasattr(self, 'btn_don_hang_top'):
            self.btn_don_hang_top.clicked.connect(self.mo_don_hang)
        if hasattr(self, 'btn_checkout'):
            self.btn_checkout.clicked.connect(self.mua_hang)

        for i in range(1, 4):
            btn_m = getattr(self, f'btn_m_{i}', None)
            btn_p = getattr(self, f'btn_p_{i}', None)
            txt_q = getattr(self, f'txt_q_{i}', None)
            chk   = getattr(self, f'chk_item_{i}', None)
            if btn_m: btn_m.clicked.connect(lambda _, idx=i:
                self.thay_doi_so_luong(idx, -1))
            if btn_p: btn_p.clicked.connect(lambda _, idx=i:
                self.thay_doi_so_luong(idx, 1))
            if txt_q: txt_q.textChanged.connect(lambda _, idx=i:
                self.cap_nhat_thanh_tien(idx))
            if chk:
                chk.stateChanged.connect(self.cap_nhat_tong_tien)

        self._don_gia = {}
        self.tai_du_lieu_gio_hang()

    def tai_du_lieu_gio_hang(self):
        user = get_current_user()
        if not user:
            return
        merchant_id = user.get('user_id')
        gio_hang = self._lay_gio_hang(merchant_id)
        item_configs = [
            {'frame': 'frame_item_1', 'lbl_name': 'lbl_name_1', 'lbl_rem': 'lbl_rem_1', 'lbl_p': 'lbl_p_val_1', 'txt_q': 'txt_q_1', 'lbl_t': 'lbl_t_val_1', 'chk': 'chk_item_1'},
            {'frame': 'frame_item_2', 'lbl_name': 'lbl_name_2', 'lbl_rem': 'lbl_rem_2', 'lbl_p': 'lbl_p_val_2', 'txt_q': 'txt_q_2', 'lbl_t': 'lbl_t_val_2', 'chk': 'chk_item_2'},
            {'frame': 'frame_item_3', 'lbl_name': 'lbl_name_3', 'lbl_rem': 'lbl_rem_3', 'lbl_p': 'lbl_p_val_3', 'txt_q': 'txt_q_3', 'lbl_t': 'lbl_t_val_3', 'chk': 'chk_item_3'},
        ]
        for i, cfg in enumerate(item_configs):
            frame = getattr(self, cfg['frame'], None)
            if not frame: continue
            if i >= len(gio_hang):
                frame.setVisible(False)
                continue
            frame.setVisible(True)
            item = gio_hang[i]
            crop_name, quantity, don_gia, ton_kho = item[1], item[2], item[3], item[4]
            thanh_tien = quantity * don_gia
            self._don_gia[i + 1] = don_gia
            if hasattr(self, cfg['lbl_name']):
                getattr(self, cfg['lbl_name']).setText(crop_name)
            if hasattr(self, cfg['lbl_rem']):
                getattr(self, cfg['lbl_rem']).setText(f"Còn lại: {ton_kho:,.0f} kg")
            if hasattr(self, cfg['lbl_p']):
                getattr(self, cfg['lbl_p']).setText(
                    f'<html><body><span style="font-weight:bold; font-size:13pt;">{don_gia:,.0f}</span><span style="font-size:11pt; color:#4A4A4A;"> VND / kg</span></body></html>'
                )
            if hasattr(self, cfg['txt_q']):
                getattr(self, cfg['txt_q']).setText(str(int(quantity)))
            if hasattr(self, cfg['lbl_t']):
                getattr(self, cfg['lbl_t']).setText(
                    f'<html><body><span style="font-weight:bold; font-size:13pt;">{thanh_tien:,.0f}</span><span style="font-size:11pt; color:#4A4A4A;"> VND</span></body></html>'
                )
            if hasattr(self, cfg['chk']):
                getattr(self, cfg['chk']).setChecked(True)
        so_sp = min(len(gio_hang), 3)
        if hasattr(self, 'btn_back'):
            self.btn_back.setText(f"← Giỏ hàng ({so_sp})")
        self.cap_nhat_tong_tien()

    def _lay_gio_hang(self, merchant_id):
        try:
            from database.database_connector import get_connection
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT cart.cart_id, c.crop_name, cart.quantity,
                       COALESCE(fa.selling_price, c.base_price) as price,
                       al.quantity as ton_kho, cart.activity_id
                FROM Cart cart
                JOIN FarmingActivities fa ON cart.activity_id = fa.activity_id
                JOIN Crops c ON fa.crop_id = c.crop_id
                LEFT JOIN ActivityLog al ON fa.activity_id = al.activity_id AND al.action_type = 'Thu hoạch'
                WHERE cart.merchant_id = ? ORDER BY cart.cart_id
            """, (merchant_id,))
            rows = cursor.fetchall()
            conn.close()
            return rows
        except Exception as e:
            print(f"Lỗi lấy giỏ hàng: {e}")
            return []

    def thay_doi_so_luong(self, item_idx, delta):
        txt_q = getattr(self, f'txt_q_{item_idx}', None)
        if not txt_q: return
        try:
            so_luong = max(1, int(txt_q.text()) + delta)
            txt_q.setText(str(so_luong))
        except ValueError:
            txt_q.setText('1')

    def cap_nhat_thanh_tien(self, item_idx):
        txt_q   = getattr(self, f'txt_q_{item_idx}', None)
        lbl_t   = getattr(self, f'lbl_t_val_{item_idx}', None)
        don_gia = self._don_gia.get(item_idx, 0)
        if not txt_q or not lbl_t: return
        try:
            thanh_tien = float(txt_q.text()) * don_gia
            lbl_t.setText(
                f'<html><body><span style="font-weight:bold; font-size:13pt;">{thanh_tien:,.0f}</span><span style="font-size:11pt; color:#4A4A4A;"> VND</span></body></html>'
            )
        except ValueError:
            pass
        self.cap_nhat_tong_tien()

    def cap_nhat_tong_tien(self):
        tong_tien = 0
        so_sp_chon = 0
        for i in range(1, 4):
            chk   = getattr(self, f'chk_item_{i}', None)
            txt_q = getattr(self, f'txt_q_{i}', None)
            don_gia = self._don_gia.get(i, 0)
            if chk and chk.isChecked() and txt_q:
                try:
                    tong_tien += float(txt_q.text()) * don_gia
                    so_sp_chon += 1
                except ValueError:
                    pass
        if hasattr(self, 'lbl_summary_text'):
            self.lbl_summary_text.setText(f"Tổng cộng ({so_sp_chon} sản phẩm):")
        if hasattr(self, 'lbl_summary_total'):
            self.lbl_summary_total.setText(f"{tong_tien:,.0f} VND")

    def ve_trang_chu(self):
        switch_window(ChuVuaDashboardScreen())
    def mo_giao_thuong(self):
        switch_window(SearchListMatHangScreen())
    def mo_ho_so(self):
        switch_window(ProfileChuVuaScreen())
    def quay_lai(self):
        switch_window(SearchListMatHangScreen())
    def mo_don_hang(self):
        switch_window(DanhSachDonHangChuVuaScreen())
    def mua_hang(self):
        switch_window(PreOrderScreen())

    def dang_xuat(self):
        reply = QMessageBox.question(
            self, 'Xác nhận', 'Bạn có chắc chắn muốn đăng xuất?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            from utils.window_manager import set_current_user
            set_current_user(None)
            switch_window(LoginScreen())