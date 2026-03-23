from PyQt6.QtWidgets import QWidget, QMessageBox, QFrame, QHBoxLayout, QLabel, QProgressBar, QSizePolicy
from PyQt6.QtCore import Qt
from PyQt6 import uic
from utils.window_manager import switch_window, get_current_user, set_current_user
from logic.logic_cay_trong import lay_danh_sach_cay
from logic.logic_mua_vu import lay_danh_sach_vu_mua
from screens.chinh_sua_cay_trong_screen import ChinhSuaCayTrongPopup

class DanhSachCayTrongScreen(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui_files/danh_sach_cay_trong.ui", self)

        # Kết nối sự kiện sidebar
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
        self._dynamic_widgets = []  # Lưu widget động để xoá khi refresh
        self.tai_du_lieu_cay_trong()

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

        grid = getattr(self, 'gridLayout_table', None)
        if not grid:
            return

        # Ẩn 5 dòng cũ đã thiết kế sẵn trong UI (td1_0...td5_0)
        for i in range(1, 6):
            for col in range(0, 5):
                w = getattr(self, f'td{i}_{col}', None)
                if w:
                    w.setVisible(False)

        # Xoá widget động từ lần tải trước
        for w in self._dynamic_widgets:
            try:
                w.setParent(None)
                w.deleteLater()
            except Exception:
                pass
        self._dynamic_widgets.clear()

        # Tạo động mỗi hàng cho từng vụ mùa
        row_colors = ['#FFFCF0', '#FFFFFF']
        for i, vm in enumerate(ds_vu_mua):
            row = i + 1  # row 0 = header
            activity_id = vm[0]
            crop_name = vm[1]
            plot_name = vm[2]
            area_m2 = vm[3] or 0
            if area_m2 < 10000:
                area_str = f"{area_m2:g} m²"
            else:
                area_str = f"{area_m2 / 10000:g} ha"
            status = vm[6]

            icon = '🌱'
            for k, v in ICON_MAP.items():
                if k.lower() in crop_name.lower():
                    icon = v
                    break

            ten_badge, bg, fg, prg = STATUS_MAP.get(status, (status, '#888888', 'white', 0))
            bg_color = row_colors[i % 2]

            # --- Col 0: Tên (Ảnh) ---
            td0 = QFrame()
            td0.setStyleSheet(f"background-color: {bg_color};")
            td0.setCursor(Qt.CursorShape.PointingHandCursor)
            td0.mousePressEvent = lambda event, aid=activity_id: self.mo_chi_tiet_cay_trong(aid)
            h0 = QHBoxLayout(td0)
            h0.setContentsMargins(20, 8, 10, 8)
            h0.setSpacing(15)
            lbl_icon = QLabel(icon)
            lbl_icon.setFixedSize(50, 50)
            lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_icon.setStyleSheet("font-size: 24pt; background: transparent; border: none;")
            h0.addWidget(lbl_icon)
            lbl_name = QLabel(crop_name)
            lbl_name.setStyleSheet("font-size: 12pt; font-weight: bold; color: #1C1C1C; background: transparent; border: none;")
            h0.addWidget(lbl_name)
            h0.addStretch()
            grid.addWidget(td0, row, 0)
            self._dynamic_widgets.append(td0)

            # --- Col 1: Thửa/Lô ---
            td1 = QLabel(plot_name)
            td1.setAlignment(Qt.AlignmentFlag.AlignCenter)
            td1.setStyleSheet(f"background-color: {bg_color}; font-size: 12pt; font-weight: bold; color: #4A4A4A; padding: 12px;")
            grid.addWidget(td1, row, 1)
            self._dynamic_widgets.append(td1)

            # --- Col 2: Diện tích ---
            td2 = QLabel(area_str)
            td2.setAlignment(Qt.AlignmentFlag.AlignCenter)
            td2.setStyleSheet(f"background-color: {bg_color}; font-size: 12pt; font-weight: bold; color: #4A4A4A; padding: 12px;")
            grid.addWidget(td2, row, 2)
            self._dynamic_widgets.append(td2)

            # --- Col 3: %Sinh trưởng ---
            td3 = QFrame()
            td3.setStyleSheet(f"background-color: {bg_color};")
            h3 = QHBoxLayout(td3)
            h3.setContentsMargins(15, 12, 15, 12)
            prg_bar = QProgressBar()
            prg_bar.setValue(prg)
            prg_bar.setTextVisible(False)
            prg_bar.setFixedHeight(14)
            prg_bar.setStyleSheet("""
                QProgressBar { background-color: #E0E0E0; border-radius: 7px; border: none; }
                QProgressBar::chunk { background-color: #4CAF50; border-radius: 7px; }
            """)
            h3.addWidget(prg_bar)
            grid.addWidget(td3, row, 3)
            self._dynamic_widgets.append(td3)

            # --- Col 4: Trạng thái ---
            td4 = QFrame()
            td4.setStyleSheet(f"background-color: {bg_color};")
            h4 = QHBoxLayout(td4)
            h4.setContentsMargins(10, 8, 10, 8)
            h4.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_badge = QLabel(ten_badge)
            lbl_badge.setStyleSheet(
                f"background-color: {bg}; color: {fg}; border-radius: 12px; padding: 4px 12px; font-weight: bold; font-size: 10pt;"
            )
            lbl_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            h4.addWidget(lbl_badge)
            grid.addWidget(td4, row, 4)
            self._dynamic_widgets.append(td4)

    def mo_popup_them_sua(self):
        self.popup = ChinhSuaCayTrongPopup()
        self.popup.show()

    # ------------------------------------------------------------
    # Điều hướng – lazy import để tránh vòng tròn
    # ------------------------------------------------------------
    def ve_trang_chu(self):
        from screens.home_nong_dan_screen import NongDanDashboardScreen
        switch_window(NongDanDashboardScreen)

    def mo_giao_thuong(self):
        from screens.dang_san_pham_screen import DangSanPhamScreen
        switch_window(DangSanPhamScreen)

    def mo_phan_tich(self):
        from screens.phan_tich_bao_cao_screen import PhanTichBaoCaoScreen
        switch_window(PhanTichBaoCaoScreen)

    def mo_ho_so(self):
        from screens.profile_nong_dan_screen import ProfileNongDanScreen
        switch_window(ProfileNongDanScreen)

    def mo_chi_tiet_cay_trong(self, activity_id=None):
        from screens.chi_tiet_cay_trong_screen import ChiTietCayTrongScreen
        if activity_id:
            switch_window(ChiTietCayTrongScreen, activity_id=activity_id)
        else:
            switch_window(ChiTietCayTrongScreen)

    def dang_xuat(self):
        reply = QMessageBox.question(self, 'Xác nhận', 'Bạn có chắc chắn muốn đăng xuất?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            set_current_user(None)
            from screens.login_screen import LoginScreen
            switch_window(LoginScreen)
