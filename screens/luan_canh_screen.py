from PyQt6.QtWidgets import QWidget, QMessageBox
from PyQt6 import uic

from utils.window_manager import get_current_user
from logic.logic_mua_vu import lay_danh_sach_vu_mua, lay_chi_tiet_vu_mua
from logic.logic_luan_canh import goi_y_luan_canh
from logic.main import (
    switch_window,
    NongDanDashboardScreen,
    DanhSachCayTrongScreen,
    ChiTietCayTrongScreen,
    NhatKyCanhTacScreen,
    GoiYChamSocScreen,
    DangSanPhamScreen,
    PhanTichBaoCaoScreen,
    ProfileNongDanScreen,
    LoginScreen,
)


class LuanCanhScreen(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui_files/luan_canh.ui", self)

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

        #ĐIỀU HƯỚNG TAB
        if hasattr(self, 'lbl_tab_danh_sach'):
            self.lbl_tab_danh_sach.mousePressEvent = self.quay_lai_danh_sach
        if hasattr(self, 'lbl_tab_thong_tin'):
            self.lbl_tab_thong_tin.mousePressEvent = self.mo_thong_tin_chi_tiet
        if hasattr(self, 'lbl_tab_nhat_ky'):
            self.lbl_tab_nhat_ky.mousePressEvent = self.mo_nhat_ky
        if hasattr(self, 'lbl_tab_nhac_nho'):
            self.lbl_tab_nhac_nho.mousePressEvent = self.mo_goi_y_cham_soc
        if hasattr(self, 'lbl_tab_goi_y'):
            self.lbl_tab_goi_y.mousePressEvent = self.mo_goi_y_cham_soc

        self.tai_du_lieu_luan_canh()

    #XỬ LÝ CHÍNH / LOGIC

    def tai_du_lieu_luan_canh(self):
        user = get_current_user()
        if not user:
            return
        danh_sach_vu_mua = lay_danh_sach_vu_mua(user.get('user_id'))
        vu_hien_thi = danh_sach_vu_mua[:3]
        card_configs = [
            {'card': 'card_1', 'lbl_title': 'lbl_title_1', 'grid': 'lbl_g1_{r}_{c}', 'goi_y': ['lbl_g1_n_0', 'lbl_g1_n_1', 'lbl_g1_n_2'], 'lido': 'txt_lido_1'},
            {'card': 'card_2', 'lbl_title': 'lbl_title_2', 'grid': 'lbl_g2_{r}_{c}', 'goi_y': ['lbl_g2_n_0', 'lbl_g2_n_1', 'lbl_g2_n_2'], 'lido': 'txt_lido_2'},
            {'card': 'card_3', 'lbl_title': 'lbl_title_3', 'grid': 'lbl_g3_{r}_{c}', 'goi_y': ['lbl_g3_n_0', 'lbl_g3_n_1', 'lbl_g3_n_2'], 'lido': 'txt_lido_3'},
        ]
        for i, cfg in enumerate(card_configs):
            card = getattr(self, cfg['card'], None)
            if not card:
                continue
            if i >= len(vu_hien_thi):
                card.setVisible(False)
                continue
            card.setVisible(True)
            vm = vu_hien_thi[i]
            crop_name = vm[1]
            plot_name = vm[2] or f'Thửa {i + 1}'
            if hasattr(self, cfg['lbl_title']):
                getattr(self, cfg['lbl_title']).setText(plot_name)
            for r in range(3):
                for c in range(3):
                    lbl_name = cfg['grid'].format(r=r, c=c)
                    if hasattr(self, lbl_name):
                        getattr(self, lbl_name).setText(crop_name)
            ds_goi_y = self._lay_goi_y_cho_vu_mua(vm[0])
            for j, lbl_name in enumerate(cfg['goi_y']):
                if hasattr(self, lbl_name):
                    if j < len(ds_goi_y):
                        getattr(self, lbl_name).setText(ds_goi_y[j][1])
                        getattr(self, lbl_name).setStyleSheet(
                            "border: 1px solid #71B269; padding: 10px; color: #3E7B40; background-color: #E8F5E9; font-weight: bold;"
                        )
                    else:
                        getattr(self, lbl_name).setText('—')
            if hasattr(self, cfg['lido']):
                getattr(self, cfg['lido']).setText(self._tao_ly_do(crop_name, ds_goi_y))

    def _lay_goi_y_cho_vu_mua(self, activity_id):
        try:
            chi_tiet = lay_chi_tiet_vu_mua(activity_id)
            if not chi_tiet:
                return []
            return goi_y_luan_canh(chi_tiet[2])[:3]
        except Exception:
            return []

    def _tao_ly_do(self, crop_hien_tai, ds_goi_y):
        if not ds_goi_y:
            return f"Nên luân canh sau khi thu hoạch {crop_hien_tai} để cải thiện độ màu mỡ của đất và giảm nguy cơ sâu bệnh tích tụ."
        ten_goi_y = ', '.join([g[1] for g in ds_goi_y[:3]])
        category  = ds_goi_y[0][2] if ds_goi_y[0][2] else 'loại cây khác'
        return (f"Sau khi trồng {crop_hien_tai}, nên chuyển sang {ten_goi_y} ({category}) "
                f"để cân bằng dinh dưỡng đất, hạn chế sâu bệnh tích lũy và tăng năng suất cho vụ tiếp theo.")

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
    def mo_nhat_ky(self, event):
        switch_window(NhatKyCanhTacScreen())
    def mo_goi_y_cham_soc(self, event):
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