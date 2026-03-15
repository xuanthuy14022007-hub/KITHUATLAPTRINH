from PyQt6.QtWidgets import QWidget, QMessageBox, QLabel
from PyQt6 import uic

from utils.window_manager import get_current_user
from logic.logic_mua_vu import lay_danh_sach_vu_mua
from logic.logic_nhat_ky import lay_nhat_ky_theo_mua_vu
from logic.main import (
    switch_window,
    NongDanDashboardScreen,
    DanhSachCayTrongScreen,
    ChiTietCayTrongScreen,
    NhatKyCanhTacScreen,
    LuanCanhScreen,
    DangSanPhamScreen,
    PhanTichBaoCaoScreen,
    ProfileNongDanScreen,
    LoginScreen,
)

GOI_Y_CHAM_SOC = {
    'Đang trồng':    [('🚰', 'Tưới nước đều đặn mỗi ngày'), ('🌿', 'Kiểm tra sâu bệnh định kỳ'), ('🪣', 'Bón phân theo chu kỳ')],
    'Sắp thu hoạch': [('🌾', 'Chuẩn bị dụng cụ thu hoạch'), ('📋', 'Kiểm tra chất lượng nông sản'), ('📦', 'Liên hệ đầu ra tiêu thụ')],
    'Đã thu hoạch':  [('🔄', 'Làm đất cho vụ tiếp theo'), ('💧', 'Tưới ẩm đất sau thu hoạch'), ('📝', 'Ghi nhật ký tổng kết vụ mùa')],
}
CHU_Y_MAP = {
    'Tưới nước': [('⚠️', 'Kiểm tra độ ẩm đất sau khi tưới'), ('🌡️', 'Tránh tưới vào giờ nắng gắt'), ('💧', 'Đảm bảo lượng nước đủ cho cây')],
    'Bón phân':  [('⚠️', 'Không bón quá liều lượng khuyến nghị'), ('🌱', 'Kết hợp tưới nước sau khi bón phân'), ('📏', 'Giữ khoảng cách bón phân hợp lý')],
    'Gieo trồng':[('🌱', 'Theo dõi tỷ lệ nảy mầm'), ('☀️', 'Đảm bảo ánh sáng và độ ẩm cho hạt'), ('🔍', 'Kiểm tra đất trước khi gieo')],
    'Thu hoạch': [('📦', 'Bảo quản nông sản đúng cách'), ('🌡️', 'Chú ý nhiệt độ kho lưu trữ'), ('✅', 'Phân loại chất lượng sản phẩm')],
}
CHU_Y_DEFAULT = [('🔍', 'Theo dõi tình trạng cây trồng hàng ngày'), ('📋', 'Ghi chép đầy đủ nhật ký canh tác'), ('☎️', 'Liên hệ kỹ thuật viên khi cần hỗ trợ')]


class GoiYChamSocScreen(QWidget):
    def __init__(self, activity_id=None):
        super().__init__()
        uic.loadUi("ui_files/goi_y_cham_soc.ui", self)

        user = get_current_user()
        self.activity_id = activity_id
        self.trang_thai_vu_mua = 'Đang trồng'
        if self.activity_id is None and user:
            ds = lay_danh_sach_vu_mua(user.get('user_id'))
            if ds:
                self.activity_id = ds[0][0]
                self.trang_thai_vu_mua = ds[0][6]

        # ĐIỀU HƯỚNG SIDEBAR
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

        # ĐIỀU HƯỚNG TAB
        if hasattr(self, 'lbl_tab_danh_sach'):
            self.lbl_tab_danh_sach.mousePressEvent = self.quay_lai_danh_sach
        if hasattr(self, 'lbl_tab_thong_tin'):
            self.lbl_tab_thong_tin.mousePressEvent = self.mo_thong_tin_chi_tiet
        if hasattr(self, 'lbl_tab_nhat_ky'):
            self.lbl_tab_nhat_ky.mousePressEvent = self.mo_nhat_ky
        if hasattr(self, 'lbl_subtab_luancanh'):
            self.lbl_subtab_luancanh.mousePressEvent = self.mo_luan_canh

        self.tai_noi_dung_goi_y()

    #XỬ LÝ CHÍNH / LOGIC

    def tai_noi_dung_goi_y(self):
        ds_goi_y = GOI_Y_CHAM_SOC.get(self.trang_thai_vu_mua, GOI_Y_CHAM_SOC['Đang trồng'])
        if hasattr(self, 'lbl_title_1'):
            ten_cay = ''
            if self.activity_id:
                from logic.logic_nhat_ky import lay_thong_tin_vu_mua
                info = lay_thong_tin_vu_mua(self.activity_id)
                if info:
                    ten_cay = f' – {info[1]}'
            self.lbl_title_1.setText(f'Gợi ý chăm sóc hôm nay{ten_cay}')
        self._cap_nhat_dong_checklist('vbox_list_1', ds_goi_y)
        ds_chu_y = CHU_Y_DEFAULT
        if self.activity_id:
            nhat_ky = lay_nhat_ky_theo_mua_vu(self.activity_id, limit=1)
            if nhat_ky:
                ds_chu_y = CHU_Y_MAP.get(nhat_ky[0][1], CHU_Y_DEFAULT)
        self._cap_nhat_dong_checklist('vbox_list_2', ds_chu_y)

    def _cap_nhat_dong_checklist(self, vbox_name, danh_sach):
        vbox = getattr(self, vbox_name, None)
        if not vbox:
            return
        layout = vbox.layout()
        if not layout:
            return
        for i, (icon, text) in enumerate(danh_sach):
            if i >= layout.count():
                break
            item = layout.itemAt(i)
            if not item:
                continue
            hbox = item.layout()
            if not hbox or hbox.count() < 2:
                continue
            lbl_icon = hbox.itemAt(0).widget()
            lbl_text = hbox.itemAt(1).widget()
            if isinstance(lbl_icon, QLabel):
                lbl_icon.setText(icon)
            if isinstance(lbl_text, QLabel):
                lbl_text.setText(f'  {text}')

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
    def mo_luan_canh(self, event):
        switch_window(LuanCanhScreen())

    def dang_xuat(self):
        reply = QMessageBox.question(
            self, 'Xác nhận', 'Bạn có chắc chắn muốn đăng xuất?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            from utils.window_manager import set_current_user
            set_current_user(None)
            switch_window(LoginScreen())