from datetime import datetime
from PyQt6.QtWidgets import QWidget, QMessageBox
from PyQt6 import uic
from utils.window_manager import switch_window, get_current_user
from database.database_connector import get_connection

BADGE_CONFIG = {
    'Chờ xác nhận': ('#F48FB1', '#1C1C1C'),   # Hồng - đen
    'Xác nhận':     ('#4CAF50', '#FFFFFF'),   # Xanh lá - trắng
    'Hủy đơn':      ('#F48FB1', '#1C1C1C'),   # Hồng - đen
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
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Cart WHERE merchant_id = ?", (merchant_id,))
            so_luong = cursor.fetchone()[0]
            conn.close()
            return so_luong
        except Exception:
            return 0

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            elif item.layout() is not None:
                self.clear_layout(item.layout())

    def _do_du_lieu_len_ui(self, danh_sach):
        if not hasattr(self, 'verticalLayout_scroll'):
            return
            
        # Tạm thời chỉ xóa các group order tĩnh nếu chúng còn tồn tại
        if hasattr(self, 'group_order_1') and self.group_order_1:
            self.group_order_1.deleteLater()
            self.group_order_1 = None
        if hasattr(self, 'group_order_2') and self.group_order_2:
            self.group_order_2.deleteLater()
            self.group_order_2 = None
            
        # Tìm widget order_list_container, nếu chưa có thì tạo
        if not hasattr(self, 'order_list_container'):
            from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QHBoxLayout, QPushButton
            from PyQt6.QtCore import Qt
            
            self.order_list_container = QFrame()
            self.order_list_layout = QVBoxLayout(self.order_list_container)
            self.order_list_layout.setSpacing(20)
            self.verticalLayout_scroll.insertWidget(2, self.order_list_container) # Insert after search/filter
            self.verticalLayout_scroll.addStretch()

        from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QHBoxLayout, QPushButton
        from PyQt6.QtCore import Qt
        
        self.clear_layout(self.order_list_layout)

        if not danh_sach:
            lbl_empty = QLabel("Không có đơn hàng nào khớp với tìm kiếm.")
            lbl_empty.setStyleSheet("font-size: 14pt; color: #4A4A4A; padding: 20px;")
            lbl_empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.order_list_layout.addWidget(lbl_empty)
            return

        for don in danh_sach:
            # Main group frame
            group_frame = QFrame()
            group_frame.setStyleSheet("QFrame { background-color: #FFFFFF; border: 1px solid #A0A0A0; border-radius: 10px; }")
            group_layout = QVBoxLayout(group_frame)
            group_layout.setContentsMargins(0, 0, 0, 0)
            group_layout.setSpacing(0)

            # Header
            header_frame = QFrame()
            header_frame.setMinimumHeight(50)
            header_frame.setStyleSheet("background-color: #619B5E; border-top-left-radius: 9px; border-top-right-radius: 9px; border-bottom: 1px solid #A0A0A0; border-left: none; border-right: none; border-top: none;")
            header_layout = QHBoxLayout(header_frame)
            header_layout.setContentsMargins(20, 0, 20, 0)

            lbl_farm = QLabel(f"🏪 {don['farm_name']}")
            lbl_farm.setStyleSheet("color: white; font-size: 13pt; font-weight: bold; border: none; background: transparent;")
            
            lbl_badge = QLabel(don['status'])
            bg, fg = BADGE_CONFIG.get(don['status'], ('#E0E0E0', '#1C1C1C'))
            lbl_badge.setStyleSheet(f"background-color: {bg}; color: {fg}; border-radius: 4px; padding: 4px 15px; font-weight: bold; font-size: 10pt; border: none;")

            header_layout.addWidget(lbl_farm)
            header_layout.addStretch()
            header_layout.addWidget(lbl_badge)

            # Item body
            item_frame = QFrame()
            item_frame.setStyleSheet("border-bottom: 1px solid #E0E0E0; border-top: none; border-left: none; border-right: none;")
            item_layout = QHBoxLayout(item_frame)
            item_layout.setContentsMargins(25, 15, 25, 15)
            item_layout.setSpacing(20)

            img_lbl = QLabel("🖼️")
            img_lbl.setFixedSize(80, 80)
            img_lbl.setStyleSheet("background-color: #F0F0F0; border: 1px solid #A0A0A0; border-radius: 8px; font-size: 24pt;")
            img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

            name_stock_layout = QVBoxLayout()
            name_stock_layout.setSpacing(5)
            lbl_name = QLabel(don['crop_name'])
            lbl_name.setStyleSheet("font-size: 15pt; font-weight: bold; color: #1C1C1C; border: none;")
            
            try:
                ngay = datetime.strptime(don['order_date'], '%Y-%m-%d').strftime('%d/%m/%Y')
            except Exception:
                ngay = don['order_date']
            lbl_stock = QLabel(f"Ngày đặt: {ngay}")
            lbl_stock.setStyleSheet("font-size: 11pt; color: #4A4A4A; border: none;")
            
            name_stock_layout.addWidget(lbl_name)
            name_stock_layout.addWidget(lbl_stock)
            
            price_layout = QVBoxLayout()
            lbl_p_title = QLabel("Đơn giá")
            lbl_p_title.setStyleSheet("font-weight: bold; color: #1C1C1C; border: none;")
            lbl_p_val = QLabel(f"{don['unit_price']:,.0f} VND / kg")
            lbl_p_val.setStyleSheet("border: none;")
            price_layout.addWidget(lbl_p_title, alignment=Qt.AlignmentFlag.AlignCenter)
            price_layout.addWidget(lbl_p_val, alignment=Qt.AlignmentFlag.AlignCenter)

            qty_layout = QVBoxLayout()
            lbl_q_title = QLabel("Số lượng")
            lbl_q_title.setStyleSheet("font-weight: bold; color: #1C1C1C; border: none;")
            lbl_q_val = QLabel(f"{don['quantity']:,.0f} kg")
            lbl_q_val.setStyleSheet("border: none;")
            qty_layout.addWidget(lbl_q_title, alignment=Qt.AlignmentFlag.AlignCenter)
            qty_layout.addWidget(lbl_q_val, alignment=Qt.AlignmentFlag.AlignCenter)

            total_layout = QVBoxLayout()
            lbl_t_title = QLabel("Thành tiền")
            lbl_t_title.setStyleSheet("font-weight: bold; color: #1C1C1C; border: none;")
            lbl_t_val = QLabel(f"{don['total']:,.0f} VND")
            lbl_t_val.setStyleSheet("font-weight: 900; font-size: 11pt; border: none;")
            total_layout.addWidget(lbl_t_title, alignment=Qt.AlignmentFlag.AlignCenter)
            total_layout.addWidget(lbl_t_val, alignment=Qt.AlignmentFlag.AlignCenter)

            item_layout.addWidget(img_lbl)
            item_layout.addLayout(name_stock_layout)
            item_layout.addStretch()
            item_layout.addLayout(price_layout)
            item_layout.addStretch()
            item_layout.addLayout(qty_layout)
            item_layout.addStretch()
            item_layout.addLayout(total_layout)

            # Footer
            footer_frame = QFrame()
            footer_frame.setMinimumHeight(60)
            footer_frame.setStyleSheet("border-top: 1px solid #E0E0E0; border-bottom: none; border-left: none; border-right: none;")
            footer_layout = QHBoxLayout(footer_frame)
            footer_layout.setContentsMargins(20, 0, 25, 0)

            lbl_summary = QLabel(
                f'<html><body>Tổng số tiền ({don["so_san_pham"]} sản phẩm): '
                f'<span style="font-weight:900; color:#1C1C1C; font-size:16pt;">{don["total"]:,.0f} VND</span></body></html>'
            )
            lbl_summary.setStyleSheet("color: #4A4A4A; font-size: 12pt; border: none;")
            
            footer_layout.addStretch()
            footer_layout.addWidget(lbl_summary)

            group_layout.addWidget(header_frame)
            group_layout.addWidget(item_frame)
            group_layout.addWidget(footer_frame)

            self.order_list_layout.addWidget(group_frame)

    def loc_don_hang(self):
        tu_khoa = self.txt_search.text().strip().lower() if hasattr(self, 'txt_search') else ''
        trang_thai = self.cmb_status_filter.currentText() if hasattr(self, 'cmb_status_filter') else 'Tất cả trạng thái'
        ket_qua = [
            don for don in self._tat_ca_don_hang
            if (trang_thai == 'Tất cả trạng thái' or don['status'] == trang_thai)
            and (not tu_khoa or tu_khoa in don['farm_name'].lower() or tu_khoa in don['crop_name'].lower())
        ]
        self._do_du_lieu_len_ui(ket_qua)

    # ------------------------------------------------------------
    # Điều hướng – lazy import để tránh vòng tròn
    # ------------------------------------------------------------
    def ve_trang_chu(self):
        from screens.home_chu_vua_screen import ChuVuaDashboardScreen
        switch_window(ChuVuaDashboardScreen)

    def mo_giao_thuong(self):
        from screens.search_list_mat_hang_screen import SearchListMatHangScreen
        switch_window(SearchListMatHangScreen)

    def mo_ho_so(self):
        from screens.profile_chu_vua_screen import ProfileChuVuaScreen
        switch_window(ProfileChuVuaScreen)

    def quay_lai(self):
        from screens.search_list_mat_hang_screen import SearchListMatHangScreen
        switch_window(SearchListMatHangScreen)

    def mo_gio_hang(self):
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
