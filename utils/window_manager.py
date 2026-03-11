# utils/window_manager.py
"""
Quản lý chuyển màn hình và thông tin người dùng hiện tại.
Các hàm trong module này được import và sử dụng ở tất cả các màn hình.
"""

# Biến toàn cục lưu cửa sổ hiện tại (được quản lý bởi main.py, nhưng để ở đây cho tiện)
_current_window = None

# Biến lưu thông tin người dùng đã đăng nhập
_current_user = None

def set_current_user(user_info):
    """
    Lưu thông tin người dùng sau khi đăng nhập thành công.
    
    Args:
        user_info (dict or None): Dictionary chứa thông tin user với các key:
            'user_id', 'username', 'role', 'full_name', 'email', 'address',
            'farm_name', 'description'. Nếu None thì xóa thông tin (đăng xuất).
    
    Returns:
        None
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
    Chuyển sang màn hình mới. Hàm này sẽ được gọi từ các màn hình con.
    
    Args:
        window_class (class): Class của màn hình cần chuyển (kế thừa QWidget).
        **kwargs: Các tham số sẽ được truyền vào constructor của màn hình đó.
    
    Returns:
        None
    
    Lưu ý:
        - Hàm này sẽ được main.py gán giá trị cho _current_window khi khởi tạo.
        - Các màn hình con chỉ cần gọi switch_window(SomeScreen, ...) mà không cần
          quan tâm đến cơ chế bên trong.
    """
    global _current_window
    # Tạo instance mới với các tham số
    new_window = window_class(**kwargs)
    # Hiển thị toàn màn hình
    new_window.showMaximized()
    # Đóng cửa sổ cũ nếu có
    if _current_window is not None:
        _current_window.close()
    # Cập nhật cửa sổ hiện tại
    _current_window = new_window
