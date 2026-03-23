# screens/danh_sach_don_hang_screen.py
"""
Màn hình danh sách đơn hàng dành cho nông dân.
Hiển thị các đơn hàng đến, cho phép xem chi tiết, lọc và sắp xếp.
"""

from PyQt6.QtWidgets import QWidget, QMessageBox, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QFrame
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from PyQt6 import uic
from logic.logic_giao_thuong import lay_danh_sach_don_hang_den
from utils.window_manager import switch_window, get_current_user

# Cấu hình màu badge theo trạng thái
BADGE_COLORS = {
    'Xác nhận':     ('#4CAF50', '#FFFFFF'),   # Xanh lá - trắng
    'Chờ xác nhận': ('#F48FB1', '#1C1C1C'),   # Hồng - đen
    'Hủy đơn':      ('#F48FB1', '#1C1C1C'),   # Hồng - đen
}

class DanhSachDonHangScreen(QWidget):
    """
    Màn hình danh sách đơn hàng (dành cho nông dân).
    """
    def __init__(self):
        super().__init__()
        uic.loadUi("ui_files/danh_sach_don_hang.ui", self)

        self.current_user = get_current_user()
        if not self.current_user:
            from screens.login_screen import LoginScreen
            switch_window(LoginScreen)
            return
        self.farmer_id = self.current_user['user_id']

        # Kết nối sidebar
        if hasattr(self, 'btn_menu_trang_chu'):
            self.btn_menu_trang_chu.clicked.connect(self.ve_trang_chu)
        if hasattr(self, 'btn_menu_quan_ly'):
            self.btn_menu_quan_ly.clicked.connect(self.mo_quan_ly_nong_trai)
        if hasattr(self, 'btn_menu_ho_so'):
            self.btn_menu_ho_so.clicked.connect(self.mo_ho_so)
        if hasattr(self, 'btn_menu_phan_tich'):
            self.btn_menu_phan_tich.clicked.connect(self.mo_phan_tich)
        if hasattr(self, 'btn_dang_xuat'):
            self.btn_dang_xuat.clicked.connect(self.dang_xuat)

        # Tab
        if hasattr(self, 'lbl_tab_dang_ban'):
            self.lbl_tab_dang_ban.mousePressEvent = self.mo_dang_ban
        if hasattr(self, 'lbl_tab_quan_ly_don'):
            self.lbl_tab_quan_ly_don.mousePressEvent = self.mo_quan_ly_don

        # ComboBox lọc trạng thái
        if hasattr(self, 'cmb_status'):
            self.cmb_status.currentTextChanged.connect(self.loc_va_hien_thi)

        # ComboBox sắp xếp
        if hasattr(self, 'cmb_sort'):
            self.cmb_sort.currentTextChanged.connect(self.loc_va_hien_thi)

        # Lưu trữ tất cả đơn hàng
        self._tat_ca_don_hang = []
        self.load_data()

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            elif item.layout() is not None:
                self.clear_layout(item.layout())

    def load_data(self):
        """Tải toàn bộ đơn hàng từ DB rồi lọc + hiển thị."""
        try:
            self._tat_ca_don_hang = lay_danh_sach_don_hang_den(self.farmer_id)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể tải dữ liệu: {str(e)}")
            return
        self.loc_va_hien_thi()

    def loc_va_hien_thi(self):
        """Lọc theo trạng thái + sắp xếp rồi hiển thị lên UI."""
        orders = list(self._tat_ca_don_hang)

        # --- Lọc theo trạng thái ---
        if hasattr(self, 'cmb_status'):
            trang_thai = self.cmb_status.currentText()
            if trang_thai and trang_thai != 'Tất cả':
                orders = [o for o in orders if o[4] == trang_thai]

        # --- Sắp xếp ---
        if hasattr(self, 'cmb_sort'):
            sort_text = self.cmb_sort.currentText()
            if sort_text == 'Cũ nhất':
                orders.sort(key=lambda o: o[3])          # order_date ASC
            else:
                orders.sort(key=lambda o: o[3], reverse=True)  # order_date DESC

        self._do_du_lieu_len_ui(orders)

    def _do_du_lieu_len_ui(self, orders):
        """Đổ danh sách đơn hàng (đã lọc/sắp xếp) lên giao diện một cách động."""
        if hasattr(self, 'verticalLayout_list'):
            self.clear_layout(self.verticalLayout_list)
        else:
            return

        if not orders:
            lbl_empty = QLabel("Không có đơn hàng nào khớp với tìm kiếm.")
            lbl_empty.setStyleSheet("font-size: 14pt; color: #4A4A4A; padding: 20px;")
            lbl_empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.verticalLayout_list.addWidget(lbl_empty)
            return

        for idx, order in enumerate(orders):
            order_id, merchant_name, total_amount, order_date, status = order
            
            # Khung chứa 1 order
            item_widget = QWidget()
            item_layout = QHBoxLayout(item_widget)
            item_layout.setContentsMargins(0, 0, 0, 0)
            item_layout.setSpacing(20)

            # Avatar
            lbl_avatar = QLabel()
            lbl_avatar.setFixedSize(80, 80)
            lbl_avatar.setStyleSheet("background-color: #E6D7FF; border-radius: 40px; border: 2px solid white;")
            lbl_avatar.setPixmap(QPixmap("../Hình ảnh/icon_user_purple.png"))
            lbl_avatar.setScaledContents(True)

            # --- Vùng Thông tin (Tên vựa, Badge, Mô tả) ---
            info_layout = QVBoxLayout()
            info_layout.setSpacing(5)

            name_badge_layout = QHBoxLayout()
            name_badge_layout.setSpacing(10)

            lbl_name = QLabel(merchant_name)
            lbl_name.setStyleSheet("font-size: 16pt; font-weight: bold; color: #1C1C1C; border: none; background: transparent;")

            lbl_badge = QLabel(status)
            bg, fg = BADGE_COLORS.get(status, ('#E0E0E0', '#1C1C1C'))
            lbl_badge.setStyleSheet(f"background-color: {bg}; color: {fg}; padding: 4px 12px; border-radius: 6px; font-weight: bold; font-size: 10pt;")

            name_badge_layout.addWidget(lbl_name)
            name_badge_layout.addWidget(lbl_badge)
            name_badge_layout.addStretch()

            lbl_desc = QLabel(f"#{order_id} - {order_date}")
            lbl_desc.setStyleSheet("color: #4A4A4A; font-size: 11pt; line-height: 1.5; border: none; background: transparent;")

            info_layout.addLayout(name_badge_layout)
            info_layout.addWidget(lbl_desc)

            # --- Vùng Giá và Nút chi tiết ---
            action_layout = QVBoxLayout()
            action_layout.setSpacing(10)

            lbl_price = QLabel(f'<html><body><p><span style="font-size:12pt; color:#1C1C1C;">Tổng giá trị: </span><span style="font-size:16pt; font-weight:bold; color:#1C1C1C;">{total_amount:,.0f}</span><span style="font-size:12pt; color:#1C1C1C;"> VND</span></p></body></html>')
            lbl_price.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTrailing | Qt.AlignmentFlag.AlignVCenter)

            btn_detail = QPushButton("Xem chi tiết →")
            btn_detail.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_detail.setStyleSheet("QPushButton { background-color: #FFFFFF; border: 1px solid #7D7D7D; border-radius: 4px; padding: 6px 15px; font-size: 11pt; font-weight: bold; color: #1C1C1C; } QPushButton:hover { background-color: #F0F0F0; }")
            btn_detail.setProperty('order_id', order_id)
            btn_detail.clicked.connect(self.mo_chi_tiet_don_hang)

            btn_layout = QHBoxLayout()
            btn_layout.addStretch()
            btn_layout.addWidget(btn_detail)

            action_layout.addWidget(lbl_price)
            action_layout.addLayout(btn_layout)

            # Gắn vào layout chính của item
            item_layout.addWidget(lbl_avatar)
            item_layout.addLayout(info_layout)
            item_layout.addLayout(action_layout)

            self.verticalLayout_list.addWidget(item_widget)

            # Dòng kẻ ngăn cách
            if idx < len(orders) - 1:
                line = QFrame()
                line.setFixedHeight(2)
                line.setStyleSheet("background-color: #3E7B40;")
                self.verticalLayout_list.addWidget(line)

        # Thêm stretch vào cuối để list đẩy lên trên cùng
        self.verticalLayout_list.addStretch()

    def mo_chi_tiet_don_hang(self):
        sender = self.sender()
        order_id = sender.property('order_id')
        if order_id is not None:
            from screens.chi_tiet_don_hang_screen import ChiTietDonHangScreen
            switch_window(ChiTietDonHangScreen, order_id=order_id)

    def mo_dang_ban(self, event):
        from screens.dang_san_pham_screen import DangSanPhamScreen
        switch_window(DangSanPhamScreen)

    def mo_quan_ly_don(self, event):
        self.load_data()

    def ve_trang_chu(self):
        from screens.home_nong_dan_screen import NongDanDashboardScreen
        switch_window(NongDanDashboardScreen)

    def mo_quan_ly_nong_trai(self):
        from screens.danh_sach_cay_trong_screen import DanhSachCayTrongScreen
        switch_window(DanhSachCayTrongScreen)

    def mo_ho_so(self):
        from screens.profile_nong_dan_screen import ProfileNongDanScreen
        switch_window(ProfileNongDanScreen)

    def mo_phan_tich(self):
        from screens.phan_tich_bao_cao_screen import PhanTichBaoCaoScreen
        switch_window(PhanTichBaoCaoScreen)

    def dang_xuat(self):
        reply = QMessageBox.question(self, 'Xác nhận', 'Bạn có chắc chắn muốn đăng xuất?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            from utils.window_manager import set_current_user
            from screens.login_screen import LoginScreen
            set_current_user(None)
            switch_window(LoginScreen)
