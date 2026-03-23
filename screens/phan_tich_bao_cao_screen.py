from PyQt6.QtWidgets import QWidget, QMessageBox, QLabel, QHBoxLayout, QSpacerItem, QSizePolicy
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt
from PyQt6 import uic

from utils.window_manager import switch_window, get_current_user, set_current_user

# --- IMPORT CÁC HÀM XỬ LÝ LOGIC ---
from logic.logic_tinh_toan import (
    lay_ket_qua_tai_chinh_tong_quat,
    them_chi_phi,
    tinh_co_cau_tai_chinh_theo_doanh_thu,
    lay_ti_le_don_hang,
    lay_chi_tiet_chi_phi
)
# Import hàm vẽ biểu đồ từ file logic_bao_cao
from logic.logic_bao_cao import tao_anh_bieu_do

# Bảng màu dùng chung cho biểu đồ và chú thích (phải trùng với logic_bao_cao.py)
COLORS_THEME = ['#4db6ac', '#9575cd', '#9ccc65', '#ffb74d', '#ff8a65']


class PhanTichBaoCaoScreen(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui_files/phan_tich_bao_cao.ui", self)

        # ĐIỀU HƯỚNG SIDEBAR
        if hasattr(self, 'btn_menu_trang_chu'):
            self.btn_menu_trang_chu.clicked.connect(self.ve_trang_chu)
        if hasattr(self, 'btn_menu_quan_ly'):
            self.btn_menu_quan_ly.clicked.connect(self.mo_quan_ly_nong_trai)
        if hasattr(self, 'btn_menu_giao_thuong'):
            self.btn_menu_giao_thuong.clicked.connect(self.mo_giao_thuong)
        if hasattr(self, 'btn_menu_ho_so'):
            self.btn_menu_ho_so.clicked.connect(self.mo_ho_so)
        if hasattr(self, 'btn_dang_xuat'):
            self.btn_dang_xuat.clicked.connect(self.dang_xuat)

        # KẾT NỐI TƯƠNG TÁC NÚT
        if hasattr(self, 'btn_nhap'):
            self.btn_nhap.clicked.connect(self.xu_ly_them_chi_phi)
        if hasattr(self, 'btn_tinh_toan'):
            self.btn_tinh_toan.clicked.connect(self.tai_du_lieu_bao_cao)
        if hasattr(self, 'btn_xuat_bao_cao'):
            self.btn_xuat_bao_cao.clicked.connect(self.xuat_bao_cao)

        self.tai_du_lieu_bao_cao()

    # XỬ LÝ CHÍNH
    def tai_du_lieu_bao_cao(self):
        user = get_current_user()
        if not user:
            return
        farmer_id = user.get('user_id')
        if not farmer_id:
            return

        # 1. TẢI VÀ HIỂN THỊ CÁC CON SỐ
        stats = lay_ket_qua_tai_chinh_tong_quat(farmer_id)
        dt = stats.get('doanh_thu', 0)
        cp = stats.get('chi_phi', 0)
        ln = stats.get('loi_nhuan', 0)

        # Format values
        dt_str = f"{dt:,.0f}".replace(",", ".")
        cp_str = f"{cp:,.0f}".replace(",", ".")
        ln_str = f"{ln:,.0f}".replace(",", ".")

        # HTML formatting for labels
        html_tln = f'<html><head/><body><p><span style=" font-size:24pt; font-weight:bold; color:#1C1C1C;">{ln_str}</span><span style=" font-size:16pt; color:#3E7B40;"> VND</span></p></body></html>'
        html_dt = f'<html><head/><body><p><span style=" font-size:18pt; color:#1C1C1C;">{dt_str}</span><span style=" font-size:12pt; color:#4A4A4A;"> VND</span></p></body></html>'
        html_cp = f'<html><head/><body><p><span style=" font-size:18pt; color:#1C1C1C;">{cp_str}</span><span style=" font-size:12pt; color:#4A4A4A;"> VND</span></p></body></html>'
        html_ln = f'<html><head/><body><p><span style=" font-size:18pt; color:#1C1C1C;">{ln_str}</span><span style=" font-size:12pt; color:#4A4A4A;"> VND</span></p></body></html>'

        if hasattr(self, 'lbl_val_tln'):
            self.lbl_val_tln.setText(html_tln)
        if hasattr(self, 'lbl_dt_val'):
            self.lbl_dt_val.setText(html_dt)
        if hasattr(self, 'lbl_cp_val'):
            self.lbl_cp_val.setText(html_cp)
        if hasattr(self, 'lbl_ln_val'):
            self.lbl_ln_val.setText(html_ln)

        # ==========================================
        # 2. TẢI VÀ HIỂN THỊ BIỂU ĐỒ (PHẦN MỚI THÊM)
        # ==========================================

        # Lọc bỏ giá trị âm trước khi vẽ (tránh lỗi matplotlib)
        co_cau_pct = tinh_co_cau_tai_chinh_theo_doanh_thu(farmer_id)
        if co_cau_pct:
            co_cau_pct = {k: v for k, v in co_cau_pct.items() if v > 0}
        ti_le_sp = lay_ti_le_don_hang(farmer_id)

        # Xử lý Biểu đồ lớn (Cơ cấu tài chính)
        if hasattr(self, 'img_big_pie') and co_cau_pct:
            buf_big = tao_anh_bieu_do(co_cau_pct, "")
            if buf_big:
                img = QImage.fromData(buf_big.getvalue())
                pixmap = QPixmap.fromImage(img)
                self.img_big_pie.setPixmap(pixmap.scaled(self.img_big_pie.size(), Qt.AspectRatioMode.KeepAspectRatio,
                                                         Qt.TransformationMode.SmoothTransformation))
                self.img_big_pie.setText("")
                self.img_big_pie.setStyleSheet("background: transparent; border: none;")
            # Cập nhật chú thích bên phải biểu đồ lớn
            if hasattr(self, 'vbox_legend_big'):
                self._cap_nhat_chu_thich(self.vbox_legend_big, co_cau_pct)

        # Xử lý Biểu đồ nhỏ (Tỉ lệ đơn hàng)
        if hasattr(self, 'img_small_pie') and ti_le_sp:
            buf_small = tao_anh_bieu_do(ti_le_sp, "")
            if buf_small:
                img = QImage.fromData(buf_small.getvalue())
                pixmap = QPixmap.fromImage(img)
                self.img_small_pie.setPixmap(
                    pixmap.scaled(self.img_small_pie.size(), Qt.AspectRatioMode.KeepAspectRatio,
                                  Qt.TransformationMode.SmoothTransformation))
                self.img_small_pie.setText("")
                self.img_small_pie.setStyleSheet("background: transparent; border: none;")
            # Cập nhật chú thích bên phải biểu đồ nhỏ
            if hasattr(self, 'vbox_legend_small'):
                self._cap_nhat_chu_thich(self.vbox_legend_small, ti_le_sp)

        # Cập nhật Danh sách chi phí
        if hasattr(self, 'vbox_list_items'):
            chi_tiet = lay_chi_tiet_chi_phi(farmer_id)
            self._cap_nhat_danh_sach_chi_phi(self.vbox_list_items, chi_tiet)

    # ==========================================
    # Hàm cập nhật chú thích (legend) động
    # ==========================================
    def _cap_nhat_chu_thich(self, layout, data_dict):
        """Xoá chú thích cũ trong layout và tạo mới theo data + màu trùng biểu đồ."""
        # Xoá toàn bộ widget/item cũ trong layout
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            elif item.layout():
                # Xoá layout con
                sub = item.layout()
                while sub.count():
                    sub_item = sub.takeAt(0)
                    w = sub_item.widget()
                    if w:
                        w.deleteLater()
            elif item.spacerItem():
                pass  # spacer tự bị xoá

        # Thêm spacer phía trên
        layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Tạo các dòng chú thích mới
        for i, (label_text, value) in enumerate(data_dict.items()):
            color = COLORS_THEME[i % len(COLORS_THEME)]

            row_layout = QHBoxLayout()
            row_layout.setSpacing(10)

            # Ô màu nhỏ (16x16)
            color_box = QLabel()
            color_box.setFixedSize(16, 16)
            color_box.setStyleSheet(f"background-color: {color}; border-radius: 8px; border: none;")
            row_layout.addWidget(color_box)

            # Tên chú thích + phần trăm
            text_label = QLabel(f"{label_text} ({value:.1f}%)")
            text_label.setStyleSheet("font-size: 11pt; color: #4A4A4A; border: none;")
            row_layout.addWidget(text_label)

            # Spacer đẩy sang phải
            row_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

            layout.addLayout(row_layout)

        # Thêm spacer phía dưới
        layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

    def _cap_nhat_danh_sach_chi_phi(self, layout, dict_chi_phi):
        """Xoá danh sách chi phí cũ và tạo mới."""
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            elif item.layout():
                sub = item.layout()
                while sub.count():
                    sub_item = sub.takeAt(0)
                    w = sub_item.widget()
                    if w:
                        w.deleteLater()
            elif item.spacerItem():
                pass

        color_map = {
            "Phân bón": "#BDE08B",
            "Nhân công": "#F4B8B8",
            "Hạt giống": "#FFDAB9",
            "Khác": "#FFFACD"
        }

        for loai, tien in dict_chi_phi.items():
            color = color_map.get(loai, "#CCCCCC")
            row_layout = QHBoxLayout()
            
            lbl_ten = QLabel(loai)
            lbl_ten.setStyleSheet("font-size: 12pt; color: #4A4A4A; border: none;")
            row_layout.addWidget(lbl_ten)
            
            tien_str = f"{tien:,.0f} VND".replace(",", ".")
            lbl_tien = QLabel(tien_str)
            lbl_tien.setStyleSheet("font-size: 12pt; color: #3E7B40; border: none;")
            lbl_tien.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            row_layout.addWidget(lbl_tien)
            
            layout.addLayout(row_layout)


    def xu_ly_them_chi_phi(self):
        user = get_current_user()
        if not user:
            QMessageBox.warning(self, "Lỗi", "Vui lòng đăng nhập lại.")
            return

        loai_cp = self.cmb_loai_chi_phi.currentText() if hasattr(self, 'cmb_loai_chi_phi') else "Khác"
        tien_str = self.txt_so_tien.text().strip() if hasattr(self, 'txt_so_tien') else "0"

        if not tien_str:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập số tiền chi phí.")
            return

        try:
            # Loại bỏ các dấu phẩy hoặc chấm phân cách để cast sang int
            tien_str = tien_str.replace(",", "").replace(".", "")
            amount = float(tien_str)
            if amount < 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Lỗi", "Số tiền không hợp lệ. Vui lòng nhập số dương.")
            return

        # Đổi 'Khác' thành 'Chi phí khác' để khớp với CHECK của CSDL
        loai_cp_db = "Chi phí khác" if loai_cp == "Khác" else loai_cp

        # Gọi logic gán chi phí cho mục chung farmer
        farmer_id = user.get('user_id')
        success = them_chi_phi(farmer_id, loai_cp_db, amount)
        if success:
            QMessageBox.information(self, "Thành công",
                                    f"Đã thêm chi phí {loai_cp}: {amount:,.0f} VND".replace(",", "."))
            if hasattr(self, 'txt_so_tien'):
                self.txt_so_tien.clear()
            self.tai_du_lieu_bao_cao()  # Tải lại báo cáo, biểu đồ sẽ tự vẽ lại theo số mới
        else:
            QMessageBox.warning(self, "Thất bại", "Không thể thêm chi phí.")

    def xuat_bao_cao(self):
        user = get_current_user()
        if not user:
            QMessageBox.warning(self, "Lỗi", "Vui lòng đăng nhập.")
            return

        farmer_id = user.get('user_id')
        try:
            # Gọi trực tiếp hàm xuất PDF từ logic_bao_cao.py
            from logic.logic_bao_cao import xuat_bao_cao as xuat_pdf
            xuat_pdf(farmer_id)
            QMessageBox.information(self, "Thành công",
                                    f"Đã xuất báo cáo thành công!\nFile: Bao_cao_tai_chinh_{farmer_id}.pdf")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể xuất báo cáo. Chi tiết lỗi: {e}")

    # ĐIỀU HƯỚNG
    def ve_trang_chu(self):
        from screens.home_nong_dan_screen import NongDanDashboardScreen
        switch_window(NongDanDashboardScreen)

    def mo_quan_ly_nong_trai(self):
        from screens.danh_sach_cay_trong_screen import DanhSachCayTrongScreen
        switch_window(DanhSachCayTrongScreen)

    def mo_giao_thuong(self):
        from screens.dang_san_pham_screen import DangSanPhamScreen
        switch_window(DangSanPhamScreen)

    def mo_ho_so(self):
        from screens.profile_nong_dan_screen import ProfileNongDanScreen
        switch_window(ProfileNongDanScreen)

    def dang_xuat(self):
        reply = QMessageBox.question(self, 'Xác nhận', 'Bạn có chắc chắn muốn đăng xuất?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            set_current_user(None)
            from screens.login_screen import LoginScreen
            switch_window(LoginScreen)
