from PyQt6.QtWidgets import QWidget, QMessageBox
from PyQt6 import uic

from utils.window_manager import switch_window, get_current_user
from database.database_connector import get_connection
from logic.logic_giao_thuong import dang_ban

class DangSanPhamScreen(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui_files/dang_san_pham.ui", self)

        # ĐIỀU HƯỚNG SIDEBAR
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

        # Tab quản lý đơn hàng
        if hasattr(self, 'lbl_tab_quan_ly_don'):
            self.lbl_tab_quan_ly_don.mousePressEvent = self.mo_quan_ly_don

        # Nút chức năng chính
        if hasattr(self, 'btn_dang_ban_large'):
            self.btn_dang_ban_large.clicked.connect(self.thuc_hien_dang_ban)

        self.ds_chua_dang = []
        self.ds_da_dang = []
        
        self.tai_du_lieu()

    def tai_du_lieu(self):
        user = get_current_user()
        if not user:
            return
            
        farmer_id = user.get('user_id')
        if not farmer_id:
            return
            
        conn = get_connection()
        cursor = conn.cursor()
        
        # 1. Lấy danh sách chưa đăng bán (Đã thu hoạch)
        cursor.execute("""
            SELECT fa.activity_id, c.crop_name, al.quantity
            FROM FarmingActivities fa
            JOIN Crops c ON fa.crop_id = c.crop_id
            JOIN ActivityLog al ON fa.activity_id = al.activity_id AND al.action_type = 'Thu hoạch'
            WHERE fa.farmer_id = ? AND fa.status = 'Đã thu hoạch'
        """, (farmer_id,))
        self.ds_chua_dang = [{"activity_id": row[0], "crop_name": row[1], "quantity": row[2]} for row in cursor.fetchall()]

        # 2. Lấy danh sách đã đăng bán (Sẵn sàng bán)
        cursor.execute("""
            SELECT fa.activity_id, c.crop_name, al.quantity, fa.selling_price
            FROM FarmingActivities fa
            JOIN Crops c ON fa.crop_id = c.crop_id
            JOIN ActivityLog al ON fa.activity_id = al.activity_id AND al.action_type = 'Thu hoạch'
            WHERE fa.farmer_id = ? AND fa.status = 'Sẵn sàng bán'
        """, (farmer_id,))
        self.ds_da_dang = [{"activity_id": row[0], "crop_name": row[1], "quantity": row[2], "selling_price": row[3]} for row in cursor.fetchall()]
        
        conn.close()

        self.hien_thi_chua_dang()
        self.hien_thi_da_dang()

    def hien_thi_chua_dang(self):
        # UI có 5 slot item_h1 đến item_h5
        for i in range(1, 6):
            item_frame = getattr(self, f"item_h{i}", None)
            if item_frame:
                if i - 1 < len(self.ds_chua_dang):
                    sp = self.ds_chua_dang[i - 1]
                    item_frame.show()
                    getattr(self, f"name_h{i}").setText(sp["crop_name"])
                    getattr(self, f"qty_h{i}").setText(f"{sp['quantity']:,.0f} kg".replace(",", "."))
                    # Reset
                    getattr(self, f"chk_h{i}").setChecked(False)
                    getattr(self, f"txt_price_h{i}").clear()
                else:
                    item_frame.hide()

    def hien_thi_da_dang(self):
        # Update header
        tong_sp = len(self.ds_da_dang)
        if hasattr(self, 'lbl_list_subtitle'):
            self.lbl_list_subtitle.setText(f"{tong_sp} sản phẩm")
        if hasattr(self, 'lbl_badge_header'):
            self.lbl_badge_header.setText(f"{tong_sp} sản phẩm")

        # UI có 3 slot item_1 đến item_3 -> Sẽ mở rộng nếu cần, tạm xử lý tối đa hiện có trong file ui
        # Cập nhật: ui_files/dang_san_pham.ui có item_1, item_2, item_3, item_4 (có thể có không?)
        # Tạm duyệt 1 đến 5 để bao quát
        for i in range(1, 6):
            item_frame = getattr(self, f"item_{i}", None)
            if not item_frame:
                continue
            
            if i - 1 < len(self.ds_da_dang):
                sp = self.ds_da_dang[i - 1]
                item_frame.show()
                getattr(self, f"name_{i}").setText(sp["crop_name"])
                getattr(self, f"qty_{i}").setText(f"{sp['quantity']:,.0f} kg".replace(",", "."))
                gia = f"{sp['selling_price']:,.0f}".replace(",", ".") if sp['selling_price'] else "0"
                getattr(self, f"price_{i}").setText(f"{gia} VND / kg")
                
                # Buttons
                btn_out = getattr(self, f"btn_out_{i}", None)
                if btn_out:
                    # Ngắt các connect cũ
                    try:
                        btn_out.clicked.disconnect()
                    except:
                        pass
                    # Bắt sự kiện lambda
                    # Sử dụng tham số mặc định trong lambda để tránh binding muộn
                    btn_out.clicked.connect(lambda checked, aid=sp["activity_id"]: self.het_hang(aid))
            else:
                item_frame.hide()

    def thuc_hien_dang_ban(self):
        co_san_pham_duoc_chon = False
        loi = False
        for i in range(1, 6):
            chk = getattr(self, f"chk_h{i}", None)
            if chk and chk.isVisible() and chk.isChecked():
                # Lấy dữ liệu
                sp = self.ds_chua_dang[i - 1]
                txt_price = getattr(self, f"txt_price_h{i}").text().strip()
                try:
                    price = float(txt_price.replace(".", "").replace(",", ""))
                    if price <= 0:
                        raise ValueError
                except ValueError:
                    QMessageBox.warning(self, "Lỗi", f"Vui lòng nhập giá bán hợp lệ cho {sp['crop_name']}.")
                    loi = True
                    continue
                
                # Đăng bán
                thanh_cong = dang_ban(sp["activity_id"], selling_price=price)
                if thanh_cong:
                    co_san_pham_duoc_chon = True
                else:
                    QMessageBox.warning(self, "Lỗi", f"Không thể đăng bán {sp['crop_name']}.")
                    loi = True

        if co_san_pham_duoc_chon and not loi:
            QMessageBox.information(self, "Thành công", "Đã đăng bán các sản phẩm được chọn!")
            self.tai_du_lieu()
        elif not co_san_pham_duoc_chon and not loi:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn ít nhất một sản phẩm và nhập giá bán.")

    def het_hang(self, activity_id):
        reply = QMessageBox.question(self, 'Xác nhận', 'Chuyển sản phẩm này về trạng thái "Đã thu hoạch"?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            conn = get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("UPDATE FarmingActivities SET status = 'Đã thu hoạch' WHERE activity_id = ?", (activity_id,))
                conn.commit()
                QMessageBox.information(self, "Thành công", "Sản phẩm đã được gỡ khỏi danh sách đăng bán.")
                self.tai_du_lieu()
            except Exception as e:
                QMessageBox.warning(self, "Lỗi", f"Không thể gỡ sản phẩm: {e}")
            finally:
                conn.close()

    # ĐIỀU HƯỚNG
    def ve_trang_chu(self):
        from screens.home_nong_dan_screen import NongDanDashboardScreen
        switch_window(NongDanDashboardScreen())

    def mo_quan_ly_nong_trai(self):
        from screens.danh_sach_cay_trong_screen import DanhSachCayTrongScreen
        switch_window(DanhSachCayTrongScreen())

    def mo_ho_so(self):
        from screens.profile_nong_dan_screen import ProfileNongDanScreen
        switch_window(ProfileNongDanScreen())

    def mo_phan_tich(self):
        from screens.phan_tich_bao_cao_screen import PhanTichBaoCaoScreen
        switch_window(PhanTichBaoCaoScreen())

    def mo_quan_ly_don(self, event):
        from screens.danh_sach_don_hang_screen import DanhSachDonHangScreen
        switch_window(DanhSachDonHangScreen())

    def dang_xuat(self):
        reply = QMessageBox.question(self, 'Xác nhận', 'Bạn có chắc chắn muốn đăng xuất?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            from utils.window_manager import set_current_user
            set_current_user(None)
            from screens.login_screen import LoginScreen
            switch_window(LoginScreen())
