# screens/chi_tiet_don_hang.py
"""
Màn hình chi tiết đơn hàng.
Hiển thị thông tin người mua, danh sách sản phẩm, tổng khối lượng, tổng giá trị,
và các nút xác nhận / từ chối đơn.
"""

from PyQt6.QtWidgets import QWidget, QMessageBox
from PyQt6 import uic
from logic.trade import lay_chi_tiet_don_hang, cap_nhat_trang_thai_don_hang, lay_thong_tin_don_hang
from utils.window_manager import switch_window, get_current_user
from screens.nong_dan_dashboard import NongDanDashboardScreen
from screens.danh_sach_cay_trong import DanhSachCayTrongScreen
from screens.profile_nong_dan import ProfileNongDanScreen
from screens.phan_tich_bao_cao import PhanTichBaoCaoScreen
from screens.danh_sach_don_hang import DanhSachDonHangScreen
from screens.login import LoginScreen

class ChiTietDonHangScreen(QWidget):
    """
    Màn hình chi tiết đơn hàng. Nhận order_id từ tham số khởi tạo.
    """
    def __init__(self, order_id):
        super().__init__()
        self.order_id = order_id
        uic.loadUi("ui_files/chi_tiet_don_hang.ui", self)

        # Kiểm tra đăng nhập
        self.current_user = get_current_user()
        if not self.current_user:
            switch_window(LoginScreen)
            return
        self.farmer_id = self.current_user['user_id']

        # --- Kết nối sidebar ---
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

        # --- Nút điều khiển ---
        if hasattr(self, 'btn_back'):
            self.btn_back.clicked.connect(self.quay_lai_danh_sach)
        if hasattr(self, 'btn_xac_nhan'):
            self.btn_xac_nhan.clicked.connect(self.xac_nhan_don)
        if hasattr(self, 'btn_tu_choi'):
            self.btn_tu_choi.clicked.connect(self.tu_choi_don)

        # --- Các label thông tin chung (theo tên trong Object Inspector) ---
        self.lbl_avatar_kh = getattr(self, 'lbl_avatar_kh', None)
        self.lbl_ten_kh = getattr(self, 'lbl_ten_kh', None)
        self.lbl_badge_status = getattr(self, 'lbl_badge_status', None)
        self.lbl_desc_kh = getattr(self, 'lbl_desc_kh', None)
        self.lbl_tong_khoi_luong = getattr(self, 'lbl_tong_khoi_luong', None)
        self.lbl_tong_gia_tri = getattr(self, 'lbl_tong_gia_tri', None)

        # --- Các label cho từng dòng sản phẩm (td1_1..td5_4) ---
        self.product_labels = []
        for row in range(1, 6):
            row_labels = []
            for col in range(1, 5):
                label = getattr(self, f'td{row}_{col}', None)
                row_labels.append(label)
            self.product_labels.append(row_labels)

        # Tải dữ liệu
        self.load_data()

    def load_data(self):
        """
        Tải thông tin đơn hàng và chi tiết sản phẩm từ backend.
        """
        try:
            # 1. Lấy thông tin tổng quan đơn hàng
            order_info = lay_thong_tin_don_hang(self.order_id)
            if not order_info:
                QMessageBox.warning(self, "Thông báo", "Không tìm thấy thông tin đơn hàng.")
                self.quay_lai_danh_sach()
                return

            order_id, merchant_name, total_amount, order_date, status = order_info

            # Cập nhật các label thông tin chung
            if self.lbl_ten_kh:
                self.lbl_ten_kh.setText(merchant_name)
            if self.lbl_badge_status:
                self.lbl_badge_status.setText(status)
            if self.lbl_desc_kh:
                # Tạm thời hiển thị mã đơn và ngày, số lượng mặt hàng sẽ cập nhật sau
                self.lbl_desc_kh.setText(f"#{order_id} - {order_date}")

            # 2. Lấy chi tiết sản phẩm
            details = lay_chi_tiet_don_hang(self.order_id)
            if not details:
                QMessageBox.warning(self, "Thông báo", "Đơn hàng không có sản phẩm nào.")
                self.quay_lai_danh_sach()
                return

            # Hiển thị từng mặt hàng (tối đa 5)
            tong_khoi_luong = 0
            tong_gia_tri = 0
            for i, item in enumerate(details[:5]):
                crop_name, quantity, unit_price, thanh_tien, plot_name = item
                tong_khoi_luong += quantity
                tong_gia_tri += thanh_tien

                labels = self.product_labels[i]
                if labels[0]:
                    labels[0].setText(crop_name)
                if labels[1]:
                    labels[1].setText(f"{quantity} kg")
                if labels[2]:
                    labels[2].setText(f"{unit_price:,.0f} VND")
                if labels[3]:
                    labels[3].setText(f"{thanh_tien:,.0f} VND")

            # Ẩn các dòng trống
            for j in range(len(details), 5):
                for label in self.product_labels[j]:
                    if label:
                        label.hide()

            # Cập nhật tổng khối lượng và tổng giá trị
            if self.lbl_tong_khoi_luong:
                self.lbl_tong_khoi_luong.setText(f"{tong_khoi_luong} kg")
            if self.lbl_tong_gia_tri:
                self.lbl_tong_gia_tri.setText(f"{tong_gia_tri:,.0f} VND")

            # Cập nhật lại lbl_desc_kh để hiển thị số lượng mặt hàng
            if self.lbl_desc_kh:
                self.lbl_desc_kh.setText(f"#{order_id} - {len(details)} mặt hàng - {order_date}")

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể tải dữ liệu: {str(e)}")
            self.quay_lai_danh_sach()

    def xac_nhan_don(self):
        """Xác nhận đơn hàng (chuyển trạng thái 'Xác nhận')."""
        reply = QMessageBox.question(
            self, "Xác nhận",
            "Bạn có chắc chắn muốn xác nhận đơn hàng này?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                success = cap_nhat_trang_thai_don_hang(self.order_id, 'Xác nhận')
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Lỗi khi xác nhận: {str(e)}")
                return
            if success:
                QMessageBox.information(self, "Thành công", "Đã xác nhận đơn hàng!")
            else:
                QMessageBox.critical(self, "Lỗi", "Xác nhận thất bại!")
            self.quay_lai_danh_sach()

    def tu_choi_don(self):
        """Từ chối đơn hàng (chuyển trạng thái 'Hủy đơn')."""
        reply = QMessageBox.question(
            self, "Xác nhận",
            "Bạn có chắc chắn muốn từ chối đơn hàng này?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                success = cap_nhat_trang_thai_don_hang(self.order_id, 'Hủy đơn')
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Lỗi khi từ chối: {str(e)}")
                return
            if success:
                QMessageBox.information(self, "Thành công", "Đã từ chối đơn hàng!")
            else:
                QMessageBox.critical(self, "Lỗi", "Từ chối thất bại!")
            self.quay_lai_danh_sach()

    def quay_lai_danh_sach(self):
        """Quay lại màn hình danh sách đơn hàng."""
        switch_window(DanhSachDonHangScreen)

    def ve_trang_chu(self):
        """Về trang chủ nông dân."""
        switch_window(NongDanDashboardScreen)

    def mo_quan_ly_nong_trai(self):
        """Chuyển sang quản lý nông trại."""
        switch_window(DanhSachCayTrongScreen)

    def mo_ho_so(self):
        """Chuyển sang hồ sơ."""
        switch_window(ProfileNongDanScreen)

    def mo_phan_tich(self):
        """Chuyển sang phân tích báo cáo."""
        switch_window(PhanTichBaoCaoScreen)

    def dang_xuat(self):
        """Đăng xuất."""
        reply = QMessageBox.question(
            self, 'Xác nhận',
            'Bạn có chắc chắn muốn đăng xuất?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            from utils.window_manager import set_current_user
            set_current_user(None)
            switch_window(LoginScreen)
