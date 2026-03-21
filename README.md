HƯỚNG DẪN CÀI ĐẶT VÀ CHẠY ỨNG DỤNG "NÔNG ƠI!"

I. YÊU CẦU HỆ THỐNG
- Python 3.8 trở lên
- Các thư viện: PyQt6, matplotlib, reportlab, openpyxl
  Có thể cài bằng lệnh: pip install -r requirements.txt

II. CẤU TRÚC THƯ MỤC (sau khi giải nén)
KITHUATLAPTRINH-main/
│
├── database/               # Chứa file khởi tạo CSDL và kết nối
│   ├── database_connector.py
│   └── database_init.py
├── logic/                  # Các module xử lý nghiệp vụ (backend)
├── screens/                # Các lớp giao diện (frontend)
├── ui_files/               # Các file .ui (giao diện)
├── utils/                  # Các tiện ích (window_manager, ...)
├── final_main.py           # File chạy chính
├── demo.py            # File tạo dữ liệu mẫu
└── README.txt              # File hướng dẫn này

III. CÁC BƯỚC CHẠY ỨNG DỤNG

1. Tạo cơ sở dữ liệu
   - Mở terminal (cmd) tại thư mục gốc của dự án (nơi chứa thư mục database/, logic/, ...).
   - Chạy lệnh: python database/database_init.py
   - Sau khi chạy, file "nong_oi.db" sẽ được tạo trong thư mục database/.

2. Di chuyển file cơ sở dữ liệu (QUAN TRỌNG)
   - File "nong_oi.db" hiện đang nằm trong thư mục database/.
   - Hãy copy (hoặc cắt) file này ra thư mục gốc (cùng cấp với final_main.py).
   - Lý do: Các file khác (seed_data.py, final_main.py) đang tìm file .db ở thư mục gốc.

3. Nạp dữ liệu mẫu (tùy chọn, dùng để demo)
   - Chạy lệnh: python seed_data.py
   - Lúc này dữ liệu mẫu sẽ được chèn vào bảng Users, Crops, ... trong file nong_oi.db.
   - Nếu bạn muốn bắt đầu với dữ liệu trống, có thể bỏ qua bước này.

4. Khởi chạy ứng dụng
   - Chạy lệnh: python final_main.py
   - Màn hình Splash sẽ xuất hiện, sau đó chuyển đến màn hình đăng nhập.

5. Đăng nhập
   - Tài khoản mặc định (nếu đã chạy seed_data.py):
     - Nông dân: username: farmer1, password: 123
     - Thương lái: username: merchant1, password: 123
   - Hoặc bạn có thể đăng ký tài khoản mới.

IV. LƯU Ý QUAN TRỌNG
- Nếu không di chuyển file nong_oi.db ra thư mục gốc, ứng dụng sẽ không tìm thấy cơ sở dữ liệu và báo lỗi "no such table".
- Nếu gặp lỗi "no such table" khi chạy final_main.py, hãy kiểm tra lại vị trí file nong_oi.db.
- Nếu muốn reset dữ liệu, bạn có thể xóa file nong_oi.db và làm lại từ bước 1.

V. TÍNH NĂNG CHÍNH
- Nông dân: Quản lý vụ mùa, nhật ký canh tác, gợi ý chăm sóc, gợi ý luân canh, đăng bán nông sản, quản lý đơn hàng đến.
- Thương lái: Xem danh sách nông sản, thêm vào giỏ hàng, thanh toán, theo dõi đơn hàng.
- Báo cáo tài chính: Xuất báo cáo PDF với biểu đồ doanh thu, chi phí.

Chúc bạn sử dụng ứng dụng thành công!
