from PyQt6.QtWidgets import QWidget, QMessageBox
from PyQt6 import uic
from utils.window_manager import get_current_user, switch_window
from logic.logic_mua_vu import lay_danh_sach_vu_mua
from logic.logic_nhat_ky import lay_nhat_ky_theo_mua_vu

class NongDanDashboardScreen(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui_files/home_nong_dan.ui", self)

        # Kết nối sidebar
        if hasattr(self, 'btn_menu_quan_ly'):
            self.btn_menu_quan_ly.clicked.connect(self.mo_quan_ly_nong_trai)
        if hasattr(self, 'btn_menu_ho_so'):
            self.btn_menu_ho_so.clicked.connect(self.mo_ho_so)
        if hasattr(self, 'btn_menu_giao_thuong'):
            self.btn_menu_giao_thuong.clicked.connect(self.mo_giao_thuong)
        if hasattr(self, 'btn_menu_phan_tich'):
            self.btn_menu_phan_tich.clicked.connect(self.mo_phan_tich)
        if hasattr(self, 'btn_dang_xuat'):
            self.btn_dang_xuat.clicked.connect(self.dang_xuat)

        if hasattr(self, 'lbl_xem_goi_y'):
            self.lbl_xem_goi_y.mousePressEvent = self.mo_goi_y
        if hasattr(self, 'lbl_btn_qlnt'):
            self.lbl_btn_qlnt.mousePressEvent = self.mo_quan_ly_nong_trai_lbl

        self.tai_du_lieu()

    def tai_du_lieu(self):
        user = get_current_user()
        if not user:
            return
        ten_hien_thi = user.get('full_name') or user.get('username', '')
        if hasattr(self, 'lbl_username'):
            self.lbl_username.setText(ten_hien_thi)
        farmer_id = user.get('user_id')
        if not farmer_id:
            return
        danh_sach_vu_mua = lay_danh_sach_vu_mua(farmer_id)
        self._do_du_lieu_card_tong_quan(danh_sach_vu_mua)
        self._do_du_lieu_mua_vu(danh_sach_vu_mua)
        self._do_du_lieu_cong_viec(farmer_id, danh_sach_vu_mua)

    def _do_du_lieu_card_tong_quan(self, danh_sach_vu_mua):
        tong_dien_tich = sum(vm[3] for vm in danh_sach_vu_mua if vm[3])
        tong_ha = round(tong_dien_tich / 10000, 1) if tong_dien_tich else 0
        if hasattr(self, 'lbl_c1_value'):
            self.lbl_c1_value.setText(
                f'<html><body><p>{tong_ha} <span style="font-size:14pt;">ha</span></p></body></html>'
            )
        sap_thu_hoach = sum(1 for vm in danh_sach_vu_mua if vm[6] == 'Sắp thu hoạch')
        if hasattr(self, 'lbl_c2_value'):
            self.lbl_c2_value.setText(
                f'<html><body><p>{sap_thu_hoach:02d} <span style="font-size:14pt;">lô ruộng</span></p></body></html>'
            )
        dang_trong = sum(1 for vm in danh_sach_vu_mua if vm[6] == 'Đang trồng')
        if hasattr(self, 'lbl_c3_value'):
            self.lbl_c3_value.setText(
                f'<html><body><p>{dang_trong:02d} <span style="font-size:14pt;">lô ruộng</span></p></body></html>'
            )
        tong_vu_mua = len(danh_sach_vu_mua)
        if hasattr(self, 'lbl_c4_value'):
            self.lbl_c4_value.setText(
                f'<html><body><p>{tong_vu_mua:02d} <span style="font-size:14pt;">công việc</span></p></body></html>'
            )

    def _do_du_lieu_mua_vu(self, danh_sach_vu_mua):
        STATUS_MAP = {
            'Sắp thu hoạch': ('🌱 Sắp thu hoạch',   '#213C22', 'white',    85),
            'Đang trồng':    ('✔️ Đang sinh trưởng', '#A6D089', '#1C1C1C', 50),
            'Đã thu hoạch':  ('✅ Đã thu hoạch',     '#4CAF50', 'white',   100),
        }
        vu_hien_thi = [vm for vm in danh_sach_vu_mua if vm[6] in ('Sắp thu hoạch', 'Đang trồng')][:2]
        if len(vu_hien_thi) >= 1:
            vm1 = vu_hien_thi[0]
            area1 = round(vm1[3] / 10000, 1) if vm1[3] else 0
            ten_badge1, bg1, fg1, prg1 = STATUS_MAP.get(vm1[6], (vm1[6], '#888888', 'white', 0))
            if hasattr(self, 'label_8'):
                self.label_8.setText(vm1[1])
            if hasattr(self, 'label_9'):
                self.label_9.setText(f"{area1} ha")
            if hasattr(self, 'lbl_status_1'):
                self.lbl_status_1.setText(ten_badge1)
                self.lbl_status_1.setStyleSheet(
                    f"background-color: {bg1}; color: {fg1}; border-radius: 15px; font-weight: bold; font-size: 10pt; border: none;"
                )
            if hasattr(self, 'progressBar'):
                self.progressBar.setValue(prg1)
        if len(vu_hien_thi) >= 2:
            vm2 = vu_hien_thi[1]
            area2 = round(vm2[3] / 10000, 1) if vm2[3] else 0
            ten_badge2, bg2, fg2, prg2 = STATUS_MAP.get(vm2[6], (vm2[6], '#888888', 'white', 0))
            if hasattr(self, 'label_10'):
                self.label_10.setText(vm2[1])
            if hasattr(self, 'label_11'):
                self.label_11.setText(f"{area2} ha")
            if hasattr(self, 'lbl_status_2'):
                self.lbl_status_2.setText(ten_badge2)
                self.lbl_status_2.setStyleSheet(
                    f"background-color: {bg2}; color: {fg2}; border-radius: 15px; font-weight: bold; font-size: 10pt; border: none;"
                )
            if hasattr(self, 'progressBar_2'):
                self.progressBar_2.setValue(prg2)

    def _do_du_lieu_cong_viec(self, farmer_id, danh_sach_vu_mua):
        cong_viec = []
        for vm in danh_sach_vu_mua[:3]:
            nhat_ky = lay_nhat_ky_theo_mua_vu(vm[0], limit=1)
            if nhat_ky:
                log = nhat_ky[0]
                mo_ta = f"{log[1]} – {vm[1]}"
                if log[5]:
                    mo_ta += f" ({log[5]})"
                cong_viec.append(mo_ta)
            if len(cong_viec) >= 2:
                break
        if len(cong_viec) >= 1 and hasattr(self, 'chk_cv1'):
            self.chk_cv1.setText(f" {cong_viec[0]}")
            self.chk_cv1.setChecked(True)
        if len(cong_viec) >= 2 and hasattr(self, 'chk_cv2'):
            self.chk_cv2.setText(f" {cong_viec[1]}")

    # Điều hướng (lazy import để tránh vòng tròn)
    def mo_quan_ly_nong_trai_lbl(self, event):
        from screens.danh_sach_cay_trong_screen import DanhSachCayTrongScreen
        switch_window(DanhSachCayTrongScreen)

    def mo_quan_ly_nong_trai(self):
        from screens.danh_sach_cay_trong_screen import DanhSachCayTrongScreen
        switch_window(DanhSachCayTrongScreen)

    def mo_ho_so(self):
        from screens.profile_nong_dan_screen import ProfileNongDanScreen
        switch_window(ProfileNongDanScreen)

    def mo_giao_thuong(self):
        from screens.dang_san_pham_screen import DangSanPhamScreen
        switch_window(DangSanPhamScreen)

    def mo_phan_tich(self):
        from screens.phan_tich_bao_cao_screen import PhanTichBaoCaoScreen
        switch_window(PhanTichBaoCaoScreen)

    def mo_goi_y(self, event):
        from screens.goi_y_cham_soc_screen import GoiYChamSocScreen
        switch_window(GoiYChamSocScreen)

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
