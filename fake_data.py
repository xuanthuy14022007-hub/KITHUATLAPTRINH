INSERT INTO Users (user_id, username, password, role, full_name, email) VALUES
(1, 'farmer1', '123456', 'Farmer', 'Nguyễn Văn A', 'farmer1@gmail.com'),
(2, 'farmer2', '123456', 'Farmer', 'Trần Văn B', 'farmer2@gmail.com'),
(3, 'farmer3', '123456', 'Farmer', 'Lê Văn C', 'farmer3@gmail.com'),
(4, 'farmer4', '123456', 'Farmer', 'Phạm Văn D', 'farmer4@gmail.com'),
(5, 'farmer5', '123456', 'Farmer', 'Hoàng Văn E', 'farmer5@gmail.com'),
(6, 'merchant1', '123456', 'Merchant', 'Công ty Thu Mua 1', 'merchant1@gmail.com'),
(7, 'merchant2', '123456', 'Merchant', 'Công ty Thu Mua 2', 'merchant2@gmail.com'),
(8, 'merchant3', '123456', 'Merchant', 'Công ty Thu Mua 3', 'merchant3@gmail.com');

INSERT INTO Crops (crop_id, crop_name, category, base_price) VALUES
(1, 'Lúa', 'Hòa thảo', 5200),
(2, 'Ngô', 'Hòa thảo', 4800),
(3, 'Đậu nành', 'Họ đậu', 7500),
(4, 'Khoai lang', 'Củ', 6200),
(5, 'Cà chua', 'Rau quả', 9000),
(6, 'Dưa hấu', 'Rau quả', 8500);

INSERT INTO FarmingActivities
(activity_id, farmer_id, crop_id, cost_seeds, cost_fertilizer, cost_labor, start_date) VALUES
(1, 1, 1, 800000, 500000, 1200000, '2024-01-10'),
(2, 2, 2, 700000, 450000, 1000000, '2024-01-15'),
(3, 3, 3, 600000, 400000, 900000, '2024-02-01'),
(4, 4, 4, 650000, 420000, 950000, '2024-02-10'),
(5, 5, 5, 900000, 600000, 1300000, '2024-02-18');

INSERT INTO Orders
(order_id, merchant_id, farmer_id, status, total_amount, merchant_note) VALUES
(1, 6, 1, 'Hoàn thành', 26000000, 'Giao đủ số lượng'),
(2, 7, 2, 'Đang giao', 18500000, 'Ưu tiên giao sớm'),
(3, 8, 3, 'Chờ xác nhận', 14200000, 'Liên hệ trước khi giao'),
(4, 6, 4, 'Hoàn thành', 19800000, 'Chất lượng đạt yêu cầu');

INSERT INTO OrderItems
(item_id, order_id, crop_id, quantity, unit_price) VALUES
(1, 1, 1, 3000, 5200),
(2, 1, 2, 2000, 4800),
(3, 2, 3, 2500, 7400),
(4, 3, 4, 2200, 6200),
(5, 4, 5, 2000, 9000),
(6, 4, 6, 1500, 8500);

INSERT INTO ActivityLog
(log_id, farm_id, crop_id, end_date, soil_status) VALUES
(1, 1, 1, '2024-03-20', 'Tốt'),
(2, 1, 2, '2024-03-25', 'Cần bón đạm'),
(3, 2, 3, '2024-04-01', 'Tốt'),
(4, 3, 4, '2024-04-05', 'Bạc màu'),
(5, 4, 5, '2024-04-10', 'Khô hạn');

INSERT INTO FinancialReports
(report_id, user_id, total_revenue, total_profit, export_date) VALUES
(1, 1, 26000000, 14500000, '2024-04-15 09:00:00'),
(2, 2, 18500000, 9800000,  '2024-04-15 09:05:00'),
(3, 3, 14200000, 7200000,  '2024-04-15 09:10:00'),
(4, 4, 19800000, 10500000, '2024-04-15 09:15:00');

