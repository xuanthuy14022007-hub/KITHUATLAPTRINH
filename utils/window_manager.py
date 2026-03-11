# utils/window_manager.py
"""
Quản lý chuyển màn hình bằng QStackedWidget và thông tin người dùng hiện tại.
Các hàm trong module này được import và sử dụng ở tất cả các màn hình.
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt

# Biến lưu thông tin người dùng đã đăng nhập
_current_user = None

# Biến lưu cửa sổ chính (MasterWindow) - sẽ được gán từ main.py
_main_window = None

def set_main_window(window):
    """
    Gán cửa sổ chính cho window_manager. Hàm này chỉ được gọi một lần từ main.py.
    
    Args:
        window (MasterWindow): Instance của cửa sổ chính (có stacked_widget).
    """
    global _main_window
    _main_window = window

def set_current_user(user_info):
    """
    Lưu thông tin người dùng sau khi đăng nhập thành công.
    
    Args:
        user_info (dict or None): Dictionary chứa thông tin user với các key:
            'user_id', 'username', 'role', 'full_name', 'email', 'address',
            'farm_name', 'description'. Nếu None thì xóa thông tin (đăng xuất).
    """
    global _current_user
    _current_user = user_info

def get_current_user():
    """
    Lấy thông tin người dùng hiện tại.
    
    Returns:
        dict or None: Thông tin user nếu đã đăng nhập, None nếu chưa.
    """
    return _current_user

def switch_window(window_class, **kwargs):
    """
    Chuyển sang màn hình mới bằng QStackedWidget.
    Hàm này sẽ được gọi từ các màn hình con.
    
    Args:
        window_class (class): Class của màn hình cần chuyển (kế thừa QWidget).
        **kwargs: Các tham số sẽ được truyền vào constructor của màn hình đó.
    
    Raises:
        RuntimeError: Nếu _main_window chưa được khởi tạo.
    """
    global _main_window
    if _main_window is None:
        raise RuntimeError("Main window chưa được khởi tạo. Gọi set_main_window trước.")

    # Tạo instance mới của màn hình với các tham số
    new_widget = window_class(**kwargs)

    # Ép PyQt vẽ lại màu nền (chống lỗi màn hình trắng khi dùng stylesheet)
    new_widget.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

    # Lấy widget hiện tại trong stacked_widget
    old_widget = _main_window.stacked_widget.currentWidget()

    # Thêm widget mới vào stack và hiển thị
    _main_window.stacked_widget.addWidget(new_widget)
    _main_window.stacked_widget.setCurrentWidget(new_widget)

    # Xóa widget cũ để giải phóng RAM
    if old_widget is not None:
        _main_window.stacked_widget.removeWidget(old_widget)
        old_widget.deleteLater()
