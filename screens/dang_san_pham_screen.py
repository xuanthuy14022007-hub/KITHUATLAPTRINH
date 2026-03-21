# screens/dang_san_pham.py
from PyQt6.QtWidgets import QWidget, QMessageBox
from PyQt6 import uic
from database.database_connector import get_connection
from logic.giao_thuong import dang_ban
from utils.window_manager import switch_window, get_current_user, set_current_user

# Import các màn hình khác (đường dẫn tương đối từ thư mục gốc)
from screens.home_nong_dan_screen import NongDanDashboardScreen
from screens.danh_sach_cay_trong_screen import DanhSachCayTrongScreen
from screens.profile_nong_dan_screen import ProfileNongDanScreen
from screens.phan_tich_bao_cao_screen import PhanTichBaoCaoScreen
from screens.danh_sach_don_hang_screen import DanhSachDonHangScreen
from screens.login_screen import LoginScreen

class DangSanPhamScreen(QWidget):
    """
    Màn hình đăng bán nông sản dành cho nông dân.
    Hiển thị danh sách các vụ mùa đã thu hoạch (chưa đăng bán) và đã đăng bán.
    Cho phép chọn nhiều vụ, nhập giá bán và đăng lên sàn.
    """
    def __init__(self):
        super().__init__()
        uic.loadUi("ui_files/dang_san_pham.ui", self)

        # Lấy thông tin người dùng hiện tại
        self.current_user = get_current_user()
        if not self.current_user:
            switch_window(LoginScreen)
            return
        self.farmer_id = self.current_user['user_id']

        # --- Kết nối sự kiện sidebar ---
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

        # Tab chuyển sang quản lý đơn hàng
        if hasattr(self, 'lbl_tab_quan_ly_don'):
            self.lbl_tab_quan_ly_don.mousePressEvent = self.mo_quan_ly_don

        # Nút đăng bán
        if hasattr(self, 'btn_dang_ban_large'):
            self.btn_dang_ban_large.clicked.connect(self.thuc_hien_dang_ban)

        # Danh sách dữ liệu
        self.ds_chua_dang = []      # [{"activity_id": int, "crop_name": str, "quantity": float}]
        self.ds_da_dang = []        # [{"activity_id": int, "crop_name": str, "quantity": float, "selling_price": float}]

        self.tai_du_lieu()

    # ------------------------------------------------------------
    # Tải dữ liệu từ database
    # ------------------------------------------------------------
    def tai_du_lieu(self):
        """Lấy danh sách vụ mùa chưa đăng và đã đăng bán."""
        conn = get_connection()
        cursor = conn.cursor()

        # 1. Vụ mùa đã thu hoạch nhưng chưa đăng bán (status = 'Đã thu hoạch')
        cursor.execute("""
            SELECT fa.activity_id, c.crop_name, al.quantity
            FROM FarmingActivities fa
            JOIN Crops c ON fa.crop_id = c.crop_id
            JOIN ActivityLog al ON fa.activity_id = al.activity_id AND al.action_type = 'Thu hoạch'
            WHERE fa.farmer_id = ? AND fa.status = 'Đã thu hoạch'
        """, (self.farmer_id,))
        self.ds_chua_dang = [
            {"activity_id": row[0], "crop_name": row[1], "quantity": row[2]}
            for row in cursor.fetchall()
        ]

        # 2. Vụ mùa đang đăng bán (status = 'Sẵn sàng bán')
        cursor.execute("""
            SELECT fa.activity_id, c.crop_name, al.quantity, fa.selling_price
            FROM FarmingActivities fa
            JOIN Crops c ON fa.crop_id = c.crop_id
            JOIN ActivityLog al ON fa.activity_id = al.activity_id AND al.action_type = 'Thu hoạch'
            WHERE fa.farmer_id = ? AND fa.status = 'Sẵn sàng bán'
        """, (self.farmer_id,))
        self.ds_da_dang = [
            {"activity_id": row[0], "crop_name": row[1], "quantity": row[2], "selling_price": row[3]}
            for row in cursor.fetchall()
        ]

        conn.close()

        # Hiển thị lên giao diện
        self.hien_thi_chua_dang()
        self.hien_thi_da_dang()

    # ------------------------------------------------------------
    # Hiển thị danh sách chưa đăng bán (phần trên)
    # ------------------------------------------------------------
    def hien_thi_chua_dang(self):
        """Hiển thị tối đa 5 sản phẩm chưa đăng bán (item_h1..item_h5)."""
        for i in range(1, 6):
            item_frame = getattr(self, f"item_h{i}", None)
            if not item_frame:
                continue

            if i - 1 < len(self.ds_chua_dang):
                sp = self.ds_chua_dang[i - 1]
                item_frame.show()
                # Tên sản phẩm
                if hasattr(self, f"name_h{i}"):
                    getattr(self, f"name_h{i}").setText(sp["crop_name"])
                # Số lượng tồn kho
                if hasattr(self, f"qty_h{i}"):
                    getattr(self, f"qty_h{i}").setText(f"{sp['quantity']:,.0f} kg".replace(",", "."))
                # Reset checkbox và ô nhập giá
                if hasattr(self, f"chk_h{i}"):
                    getattr(self, f"chk_h{i}").setChecked(False)
                if hasattr(self, f"txt_price_h{i}"):
                    getattr(self, f"txt_price_h{i}").clear()
            else:
                item_frame.hide()

    # ------------------------------------------------------------
    # Hiển thị danh sách đã đăng bán (phần dưới)
    # ------------------------------------------------------------
    def hien_thi_da_dang(self):
        """Hiển thị tối đa 5 sản phẩm đã đăng bán (item_1..item_5)."""
        # Cập nhật số lượng sản phẩm trên header
        tong_sp = len(self.ds_da_dang)
        if hasattr(self, 'lbl_list_subtitle'):
            self.lbl_list_subtitle.setText(f"{tong_sp} sản phẩm")
        if hasattr(self, 'lbl_badge_header'):
            self.lbl_badge_header.setText(f"{tong_sp} sản phẩm")

        for i in range(1, 6):
            item_frame = getattr(self, f"item_{i}", None)
            if not item_frame:
                continue

            if i - 1 < len(self.ds_da_dang):
                sp = self.ds_da_dang[i - 1]
                item_frame.show()
                # Tên sản phẩm
                if hasattr(self, f"name_{i}"):
                    getattr(self, f"name_{i}").setText(sp["crop_name"])
                # Số lượng tồn kho
                if hasattr(self, f"qty_{i}"):
                    getattr(self, f"qty_{i}").setText(f"{sp['quantity']:,.0f} kg".replace(",", "."))
                # Giá bán
                if hasattr(self, f"price_{i}"):
                    gia = f"{sp['selling_price']:,.0f}".replace(",", ".") if sp['selling_price'] else "0"
                    getattr(self, f"price_{i}").setText(f"{gia} VND / kg")

                # Nút "Hết hàng" (gỡ đăng bán)
                btn_out = getattr(self, f"btn_out_{i}", None)
                if btn_out:
                    # Ngắt kết nối cũ tránh trùng lặp
                    try:
                        btn_out.clicked.disconnect()
                    except:
                        pass
                    # Gắn sự kiện mới với activity_id
                    btn_out.clicked.connect(lambda checked, aid=sp["activity_id"]: self.het_hang(aid))
            else:
                item_frame.hide()

    # ------------------------------------------------------------
    # Đăng bán các sản phẩm đã chọn
    # ------------------------------------------------------------
    def thuc_hien_dang_ban(self):
        """Xử lý khi nhấn nút 'Đăng bán'."""
        co_san_pham_duoc_chon = False
        loi = False

        for i in range(1, 6):
            chk = getattr(self, f"chk_h{i}", None)
            if not chk or not chk.isVisible() or not chk.isChecked():
                continue

            # Lấy thông tin sản phẩm tương ứng
            if i - 1 >= len(self.ds_chua_dang):
                continue
            sp = self.ds_chua_dang[i - 1]

            # Lấy giá từ ô nhập
            txt_price = getattr(self, f"txt_price_h{i}").text().strip()
            if not txt_price:
                QMessageBox.warning(self, "Lỗi", f"Vui lòng nhập giá bán cho {sp['crop_name']}.")
                loi = True
                continue

            # Chuyển đổi giá (hỗ trợ cả dấu chấm và dấu phẩy)
            try:
                price = float(txt_price.replace(".", "").replace(",", ""))
                if price <= 0:
                    raise ValueError
            except ValueError:
                QMessageBox.warning(self, "Lỗi", f"Giá bán không hợp lệ cho {sp['crop_name']}.")
                loi = True
                continue

            # Gọi backend đăng bán
            if dang_ban(sp["activity_id"], selling_price=price):
                co_san_pham_duoc_chon = True
            else:
                QMessageBox.warning(self, "Lỗi", f"Không thể đăng bán {sp['crop_name']}. Vui lòng thử lại.")
                loi = True

        if co_san_pham_duoc_chon and not loi:
            QMessageBox.information(self, "Thành công", "Đã đăng bán các sản phẩm được chọn!")
            self.tai_du_lieu()   # refresh
        elif not co_san_pham_duoc_chon and not loi:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn ít nhất một sản phẩm và nhập giá bán.")

    # ------------------------------------------------------------
    # Gỡ đăng bán (chuyển trạng thái về 'Đã thu hoạch')
    # ------------------------------------------------------------
    def het_hang(self, activity_id):
        """Xử lý khi nhấn nút 'Hết hàng' - gỡ sản phẩm khỏi danh sách đăng bán."""
        reply = QMessageBox.question(
            self, 'Xác nhận',
            'Chuyển sản phẩm này về trạng thái "Đã thu hoạch"?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE FarmingActivities SET status = 'Đã thu hoạch' WHERE activity_id = ?",
                (activity_id,)
            )
            conn.commit()
            QMessageBox.information(self, "Thành công", "Sản phẩm đã được gỡ khỏi danh sách đăng bán.")
            self.tai_du_lieu()  # refresh
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể gỡ sản phẩm: {e}")
            conn.rollback()
        finally:
            conn.close()

    # ------------------------------------------------------------
    # Điều hướng sidebar
    # ------------------------------------------------------------
    def ve_trang_chu(self):
        switch_window(NongDanDashboardScreen)

    def mo_quan_ly_nong_trai(self):
        switch_window(DanhSachCayTrongScreen)

    def mo_ho_so(self):
        switch_window(ProfileNongDanScreen)

    def mo_phan_tich(self):
        switch_window(PhanTichBaoCaoScreen)

    def mo_quan_ly_don(self, event):
        switch_window(DanhSachDonHangScreen)

    def dang_xuat(self):
        reply = QMessageBox.question(
            self, 'Xác nhận',
            'Bạn có chắc chắn muốn đăng xuất?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            set_current_user(None)
            switch_window(LoginScreen)
