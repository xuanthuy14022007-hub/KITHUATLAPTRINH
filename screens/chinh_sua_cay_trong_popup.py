from PyQt6.QtWidgets import QWidget, QMessageBox, QApplication
from PyQt6.QtCore import Qt
from PyQt6 import uic

from datetime import datetime
from utils.window_manager import get_current_user
from logic.logic_mua_vu import them_vu_mua, sua_vu_mua, lay_chi_tiet_vu_mua, xoa_vu_mua
from logic.logic_cay_trong import get_or_create_crop, lay_chi_tiet_cay

class ChinhSuaCayTrongPopup(QWidget):
    """Popup nhỏ để thêm/sửa/xoá cây trồng (không dùng switch_window)."""
    def __init__(self, activity_id=None):
        super().__init__()
        uic.loadUi("ui_files/chinh_sua_cay_trong.ui", self)
        
        self.activity_id = activity_id

        # Giữ popup nổi lên trên cùng
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)

        if hasattr(self, 'btn_close'):
            self.btn_close.clicked.connect(self.close)
        if hasattr(self, 'btn_huy'):
            self.btn_huy.clicked.connect(self.close)
        if hasattr(self, 'btn_luu'):
            self.btn_luu.clicked.connect(self.luu_thong_tin)
            
        # Nút xóa (nếu UI có)
        if hasattr(self, 'btn_xoa'):
            self.btn_xoa.clicked.connect(self.xoa_thong_tin)
            self.btn_xoa.setVisible(self.activity_id is not None)

        self.center()
        self.tai_du_lieu()

    def center(self):
        qr = self.frameGeometry()
        cp = QApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def tai_du_lieu(self):
        if hasattr(self, 'txt_ngay'):
            self.txt_ngay.setText(datetime.now().strftime("%d/%m/%Y"))
            
        if not self.activity_id:
            if hasattr(self, 'lbl_title'): self.lbl_title.setText("Thêm Cây Trồng")
            return
            
        if hasattr(self, 'lbl_title'): self.lbl_title.setText("Sửa Cây Trồng")
        
        vu_mua = lay_chi_tiet_vu_mua(self.activity_id)
        if not vu_mua: return
        
        _, _, crop_id, plot_name, area, start_date, _, status = vu_mua
        crop = lay_chi_tiet_cay(crop_id)
        
        if crop and hasattr(self, 'txt_ten_cay'): self.txt_ten_cay.setText(crop[1])
        if crop and hasattr(self, 'cb_loai_cay'): self.cb_loai_cay.setCurrentText(crop[2])
        if hasattr(self, 'txt_thua_dat'): self.txt_thua_dat.setText(plot_name)
        if hasattr(self, 'txt_dien_tich'): self.txt_dien_tich.setText(f"{area}")
        
        if hasattr(self, 'txt_ngay') and start_date:
            try:
                dt = datetime.strptime(start_date, '%Y-%m-%d')
                self.txt_ngay.setText(dt.strftime("%d/%m/%Y"))
            except Exception:
                self.txt_ngay.setText(start_date)
                
    def luu_thong_tin(self):
        user = get_current_user()
        if not user:
            QMessageBox.warning(self, "Lỗi", "Vui lòng đăng nhập lại!")
            return
            
        ten_cay = self.txt_ten_cay.text().strip() if hasattr(self, 'txt_ten_cay') else ''
        loai_cay = self.cb_loai_cay.currentText() if hasattr(self, 'cb_loai_cay') else 'Khác'
        thua_dat = self.txt_thua_dat.text().strip() if hasattr(self, 'txt_thua_dat') else ''
        dt_str = self.txt_dien_tich.text().strip().replace('m2', '').replace('ha', '').replace(' ', '') if hasattr(self, 'txt_dien_tich') else '0'
        ngay_str = self.txt_ngay.text().strip() if hasattr(self, 'txt_ngay') else ''
        
        if not ten_cay or not thua_dat or not dt_str:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đầy đủ thông tin bắt buộc!")
            return
            
        try:
            dien_tich = float(dt_str)
        except ValueError:
            QMessageBox.warning(self, "Lỗi", "Diện tích phải là số!")
            return
            
        try:
            ngay_db = datetime.strptime(ngay_str, "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            QMessageBox.warning(self, "Lỗi", "Ngày gieo trồng sai định dạng (dd/mm/yyyy)!")
            return
            
        crop_id = get_or_create_crop(ten_cay, loai_cay)
        
        if self.activity_id:
            vu_mua = lay_chi_tiet_vu_mua(self.activity_id)
            current_status = vu_mua[7] if vu_mua else 'Đang trồng'
            sua_vu_mua(self.activity_id, crop_id, thua_dat, dien_tich, ngay_db, None, current_status)
            QMessageBox.information(self, "Thành công", "Đã cập nhật thông tin cây trồng!")
        else:
            them_vu_mua(user.get('user_id'), crop_id, thua_dat, dien_tich, ngay_db)
            QMessageBox.information(self, "Thành công", "Đã thêm cây trồng mới!")
            
        # Đóng popup và reload lại danh sách cây trồng
        self.close()
        from screens.danh_sach_cay_trong_screen import DanhSachCayTrongScreen
        from utils.window_manager import switch_window
        switch_window(DanhSachCayTrongScreen())

    def xoa_thong_tin(self):
        if not self.activity_id: return
        reply = QMessageBox.question(self, 'Xác nhận', 'Bạn có chắc chắn muốn xóa vụ mùa này?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                xoa_vu_mua(self.activity_id)
                QMessageBox.information(self, "Thành công", "Đã xóa vụ mùa!")
                self.close()
                # Need to return to list screen
                from screens.danh_sach_cay_trong_screen import DanhSachCayTrongScreen
                from utils.window_manager import switch_window
                switch_window(DanhSachCayTrongScreen())
            except Exception as e:
                QMessageBox.warning(self, "Lỗi", str(e))
