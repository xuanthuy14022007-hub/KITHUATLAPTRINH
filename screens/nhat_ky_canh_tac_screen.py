from datetime import datetime

from PyQt6.QtWidgets import QWidget, QMessageBox, QInputDialog
from PyQt6 import uic

from utils.window_manager import get_current_user
from logic.logic_mua_vu import lay_danh_sach_vu_mua
from logic.logic_nhat_ky import lay_nhat_ky_theo_mua_vu, them_nhat_ky, ghi_nhan_thu_hoach
from logic.main import (
    switch_window,
    NongDanDashboardScreen,
    DanhSachCayTrongScreen,
    ChiTietCayTrongScreen,
    DangSanPhamScreen,
    PhanTichBaoCaoScreen,
    ProfileNongDanScreen,
    GoiYChamSocScreen,
    LoginScreen,
)

BADGE_COLOR_MAP = {
    'Gieo trồng': ('#F8E5E5', '#D66D6D'),
    'Tưới nước':  ('#E5F0FF', '#4A86D4'),
    'Bón phân':   ('#FFF4E5', '#D4924A'),
    'Thu hoạch':  ('#E5F8EA', '#4ABD6A'),
    'Khác':       ('#F0F0F0', '#888888'),
}


class NhatKyCanhTacScreen(QWidget):
    def __init__(self, activity_id=None):
        super().__init__()
        uic.loadUi("ui_files/nhat_ky_canh_tac.ui", self)

        user = get_current_user()
        self.activity_id = activity_id
        if self.activity_id is None and user:
            ds = lay_danh_sach_vu_mua(user.get('user_id'))
            if ds:
                self.activity_id = ds[0][0]

        #ĐIỀU HƯỚNG SIDEBAR
        if hasattr(self, 'btn_menu_trang_chu'):
            self.btn_menu_trang_chu.clicked.connect(self.ve_trang_chu)
        if hasattr(self, 'btn_menu_quan_ly'):
            self.btn_menu_quan_ly.clicked.connect(self.mo_quan_ly_nong_trai)
        if hasattr(self, 'btn_menu_giao_thuong'):
            self.btn_menu_giao_thuong.clicked.connect(self.mo_giao_thuong)
        if hasattr(self, 'btn_menu_phan_tich'):
            self.btn_menu_phan_tich.clicked.connect(self.mo_phan_tich)
        if hasattr(self, 'btn_menu_ho_so'):
            self.btn_menu_ho_so.clicked.connect(self.mo_ho_so)
        if hasattr(self, 'btn_dang_xuat'):
            self.btn_dang_xuat.clicked.connect(self.dang_xuat)

        #ĐIỀU HƯỚNG TAB NGANG
        if hasattr(self, 'lbl_tab_danh_sach'):
            self.lbl_tab_danh_sach.mousePressEvent = self.quay_lai_danh_sach
        if hasattr(self, 'lbl_tab_thong_tin'):
            self.lbl_tab_thong_tin.mousePressEvent = self.mo_thong_tin_chi_tiet
        if hasattr(self, 'lbl_tab_goi_y'):
            self.lbl_tab_goi_y.mousePressEvent = self.mo_goi_y

        #NÚT LƯU VÀ HỦY
        if hasattr(self, 'btn_luu'):
            self.btn_luu.clicked.connect(self.luu_nhat_ky)
        if hasattr(self, 'btn_huy'):
            self.btn_huy.clicked.connect(self.huy_nhat_ky)

        if hasattr(self, 'txt_ngay'):
            self.txt_ngay.setText(datetime.now().strftime('%d/%m/%Y'))

        self.tai_danh_sach_nhat_ky()

    #XỬ LÝ CHÍNH / LOGIC
    def tai_danh_sach_nhat_ky(self):
        if not self.activity_id:
            return
        danh_sach = lay_nhat_ky_theo_mua_vu(self.activity_id, limit=4)
        cards = [
            ('lbl_date_1', 'lbl_badge_1', 'lbl_desc_1', 'card_1'),
            ('lbl_date_2', 'lbl_badge_2', 'lbl_desc_2', 'card_2'),
            ('lbl_date_3', 'lbl_badge_3', 'lbl_desc_3', 'card_3'),
            ('lbl_date_4', 'lbl_badge_4', 'lbl_desc_4', 'card_4'),
        ]
        for i, (lbl_date, lbl_badge, lbl_desc, card_name) in enumerate(cards):
            card = getattr(self, card_name, None)
            if not card:
                continue
            if i < len(danh_sach):
                log = danh_sach[i]
                action_type = log[1] or 'Khác'
                try:
                    d = datetime.strptime(log[3], '%Y-%m-%d')
                    ngay_hien_thi = d.strftime('%d/%m/%Y')
                except Exception:
                    ngay_hien_thi = log[3]
                mo_ta = log[4] if log[4] else action_type
                if log[2] and float(log[2]) > 0:
                    mo_ta += f" – {log[2]} kg"
                bg, fg = BADGE_COLOR_MAP.get(action_type, ('#F0F0F0', '#888888'))
                if hasattr(self, lbl_date):
                    getattr(self, lbl_date).setText(f"🗓 {ngay_hien_thi}")
                if hasattr(self, lbl_badge):
                    w = getattr(self, lbl_badge)
                    w.setText(action_type)
                    w.setStyleSheet(
                        f"background-color: {bg}; color: {fg}; padding: 4px 15px; border-radius: 10px; font-weight: bold; font-size: 11pt;"
                    )
                if hasattr(self, lbl_desc):
                    getattr(self, lbl_desc).setText(mo_ta)
                card.setVisible(True)
            else:
                card.setVisible(False)

    def luu_nhat_ky(self):
        if not self.activity_id:
            QMessageBox.warning(self, "Lỗi", "Không tìm thấy vụ mùa để ghi nhật ký!")
            return
        loai_hd  = self.cmb_hoat_dong.currentText() if hasattr(self, 'cmb_hoat_dong') else ''
        ngay_str = self.txt_ngay.text().strip() if hasattr(self, 'txt_ngay') else ''
        noi_dung = self.txt_noidung.toPlainText().strip() if hasattr(self, 'txt_noidung') else ''
        if not ngay_str:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập ngày thực hiện!")
            return
        try:
            ngay_db = datetime.strptime(ngay_str, '%d/%m/%Y').strftime('%Y-%m-%d')
        except ValueError:
            QMessageBox.warning(self, "Lỗi", "Định dạng ngày không hợp lệ! (dd/mm/yyyy)")
            return
        if loai_hd == 'Thu hoạch':
            so_luong, ok = QInputDialog.getDouble(
                self, "Nhập sản lượng thu hoạch", "Số lượng thu hoạch (kg):", 0.0, 0.0, 999999.0, 1
            )
            if not ok:
                return
            ghi_nhan_thu_hoach(activity_id=self.activity_id, harvest_quantity=so_luong, log_date=ngay_db, note=noi_dung)
        else:
            them_nhat_ky(activity_id=self.activity_id, action_type=loai_hd, log_date=ngay_db, soil_status=noi_dung)
        QMessageBox.information(self, "Thành công", "Đã lưu nhật ký canh tác thành công!")
        if hasattr(self, 'txt_noidung'):
            self.txt_noidung.clear()
        if hasattr(self, 'txt_ngay'):
            self.txt_ngay.setText(datetime.now().strftime('%d/%m/%Y'))
        self.tai_danh_sach_nhat_ky()

    def huy_nhat_ky(self):
        if hasattr(self, 'txt_noidung'):
            self.txt_noidung.clear()
        if hasattr(self, 'txt_ngay'):
            self.txt_ngay.setText(datetime.now().strftime('%d/%m/%Y'))

    #ĐIỀU HƯỚNG / CHUYỂN MÀN HÌNH
    def ve_trang_chu(self):
        switch_window(NongDanDashboardScreen())
    def mo_quan_ly_nong_trai(self):
        switch_window(DanhSachCayTrongScreen())
    def mo_giao_thuong(self):
        switch_window(DangSanPhamScreen())
    def mo_phan_tich(self):
        switch_window(PhanTichBaoCaoScreen())
    def mo_ho_so(self):
        switch_window(ProfileNongDanScreen())
    def quay_lai_danh_sach(self, event):
        switch_window(DanhSachCayTrongScreen())
    def mo_thong_tin_chi_tiet(self, event):
        switch_window(ChiTietCayTrongScreen())
    def mo_goi_y(self, event):
        switch_window(GoiYChamSocScreen())

    def dang_xuat(self):
        reply = QMessageBox.question(
            self, 'Xác nhận', 'Bạn có chắc chắn muốn đăng xuất?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            from utils.window_manager import set_current_user
            set_current_user(None)
            switch_window(LoginScreen())