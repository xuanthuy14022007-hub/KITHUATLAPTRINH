# screens/danh_sach_don_hang.py
from PyQt6.QtWidgets import QWidget, QMessageBox
from PyQt6 import uic
from logic.trade import lay_danh_sach_don_hang_den
from utils.window_manager import switch_window, get_current_user
from screens.nong_dan_dashboard import NongDanDashboardScreen
from screens.danh_sach_cay_trong import DanhSachCayTrongScreen
from screens.profile_nong_dan import ProfileNongDanScreen
from screens.phan_tich_bao_cao import PhanTichBaoCaoScreen
from screens.dang_san_pham import DangSanPhamScreen
from screens.chi_tiet_don_hang import ChiTietDonHangScreen
from screens.login import LoginScreen

class DanhSachDonHangScreen(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui_files/danh_sach_don_hang.ui", self)
        self.current_user = get_current_user()
        if not self.current_user:
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

        # Tab chuyển trang
        if hasattr(self, 'lbl_tab_dang_ban'):
            self.lbl_tab_dang_ban.mousePressEvent = self.mo_dang_ban
        if hasattr(self, 'lbl_tab_quan_ly_don'):
            self.lbl_tab_quan_ly_don.mousePressEvent = self.mo_quan_ly_don

        # ComboBox lọc
        if hasattr(self, 'cmb_status'):
            self.cmb_status.currentTextChanged.connect(self.loc_don_hang)

        # Các nút chi tiết
        self.detail_buttons = []
        for i in range(1, 4):
            btn = getattr(self, f'btn_detail_{i}', None)
            if btn:
                self.detail_buttons.append(btn)
                btn.clicked.connect(self.mo_chi_tiet_don_hang)

        # Các label hiển thị
        self.order_labels = []
        for i in range(1, 4):
            labels = {
                'avatar': getattr(self, f'avatar_{i}', None),
                'name': getattr(self, f'name_{i}', None),
                'badge': getattr(self, f'badge_{i}', None),
                'desc': getattr(self, f'desc_{i}', None),
                'price': getattr(self, f'price_{i}', None),
            }
            self.order_labels.append(labels)

        self.load_data()

    def load_data(self):
        try:
            orders = lay_danh_sach_don_hang_den(self.farmer_id)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể tải dữ liệu: {str(e)}")
            return

        # Hiển thị tối đa 3 đơn
        for idx, order in enumerate(orders[:3]):
            order_id, merchant_name, total_amount, order_date, status = order
            labels = self.order_labels[idx]

            if labels['name']:
                labels['name'].setText(merchant_name)
            if labels['badge']:
                labels['badge'].setText(status)
            if labels['desc']:
                labels['desc'].setText(f"#{order_id} - {order_date}")
            if labels['price']:
                labels['price'].setText(f"{total_amount:,.0f} VND")
            if idx < len(self.detail_buttons):
                self.detail_buttons[idx].setProperty('order_id', order_id)
                self.detail_buttons[idx].setVisible(True)
            if labels['avatar']:
                labels['avatar'].setVisible(True)

        # Ẩn các đơn không có
        for j in range(len(orders), 3):
            for lbl in self.order_labels[j].values():
                if lbl:
                    lbl.hide()
            if j < len(self.detail_buttons):
                self.detail_buttons[j].hide()

    def mo_chi_tiet_don_hang(self):
        sender = self.sender()
        order_id = sender.property('order_id')
        if order_id:
            switch_window(ChiTietDonHangScreen, order_id=order_id)

    def mo_dang_ban(self, event):
        switch_window(DangSanPhamScreen)

    def mo_quan_ly_don(self, event):
        # Đã ở màn hình này, có thể reload
        self.load_data()

    def loc_don_hang(self, status):
        # TODO: Lọc theo trạng thái
        pass

    def ve_trang_chu(self):
        switch_window(NongDanDashboardScreen)

    def mo_quan_ly_nong_trai(self):
        switch_window(DanhSachCayTrongScreen)

    def mo_ho_so(self):
        switch_window(ProfileNongDanScreen)

    def mo_phan_tich(self):
        switch_window(PhanTichBaoCaoScreen)

    def dang_xuat(self):
        reply = QMessageBox.question(self, 'Xác nhận', 'Bạn có chắc chắn muốn đăng xuất?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            from utils.window_manager import set_current_user
            set_current_user(None)
            switch_window(LoginScreen)
