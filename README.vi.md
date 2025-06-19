# Hikari Self-Bot với Python (Đã Lưu Trữ)

> ⚠️ **[ĐÃ LƯU TRỮ]** Kho lưu trữ này không còn được duy trì nữa vì dự án đã được chuyển từ Python sang [NestJS](https://nestjs.com/).  
> 🗃️ Mã nguồn này được giữ công khai chỉ để **tham khảo và phục vụ mục đích giáo dục**.  
> 👉 Vui lòng tham khảo bản triển khai mới nếu bạn cần phiên bản cập nhật.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Type hints: mypy](https://img.shields.io/badge/type%20hints-mypy-blue.svg)](http://mypy-lang.org/)

### Tác giả: NirussVn0

⚠️ **CẢNH BÁO: Dự án này chỉ dành cho mục đích giáo dục!**  
Self-bot vi phạm Điều khoản Dịch vụ của Discord và có thể dẫn đến việc khóa tài khoản. Chỉ sử dụng mã nguồn này để học tập và thử nghiệm trên các máy chủ riêng mà bạn có quyền.

## 🧪 **Tính năng**

- **Yêu cầu Python 3.9 trở lên:** Tận dụng các tính năng mới nhất của ngôn ngữ.
- **100% Type Hints:** Toàn bộ mã nguồn được chú thích kiểu, kiểm tra với `mypy`.
- **Thống kê & Phân tích nâng cao:** Theo dõi hoạt động và hiệu suất bot.
- **Xử lý lỗi mạnh mẽ:** Ổn định hơn và dễ dàng gỡ lỗi.
- **Giới hạn tốc độ:** Ngăn chặn lạm dụng và tuân thủ giới hạn API Discord.
- **Ghi log an toàn:** Không ghi lại dữ liệu nhạy cảm.
- **Xác thực token:** Kiểm tra token với API Discord.
- **Bộ lệnh:** Xem [COMMAND.md](COMMAND.md) để biết các lệnh có sẵn.
- **Cài đặt linh hoạt:** Hỗ trợ Poetry (khuyến nghị) hoặc pip.

## 📦 **Cài đặt**

### **Sao chép kho lưu trữ**

```bash
git clone https://github.com/NirussVn0/Hikari-SelfBot
cd Hikari-SelfBot
```

### **Sử dụng Poetry (Khuyến nghị)**

```bash
# Cài đặt phụ thuộc
poetry install

# Kích hoạt môi trường ảo
poetry env use python3
poetry env activate
```

### **Sử dụng pip**

```bash
# Tạo môi trường ảo
python -m venv venv
source venv/bin/activate  # Trên Windows: venv\Scripts\activate

# Cài đặt phụ thuộc
pip install -e .
```

## ⚙️ **Cấu hình**

### **Thiết lập môi trường**

1. Sao chép mẫu môi trường:

   ```bash
   cp .env.example .env
   ```

2. Chỉnh sửa `.env` và thêm token Discord của bạn:
   ```env
   DISCORD_SELFBOT_DISCORD_TOKEN=your_discord_user_token_here
   DISCORD_SELFBOT_ENVIRONMENT=development
   DISCORD_SELFBOT_DEBUG=true
   ```

### **Xác thực Token**

Kiểm tra token trước khi chạy:

```bash
# Sử dụng trình xác thực tích hợp
python -m src.utils.validators <token> [password]

# Hoặc sử dụng công cụ CLI
discord-selfbot validate-token
```

⚠️ **Cảnh báo bảo mật:** Hãy cực kỳ cẩn thận với token của bạn. Bất kỳ ai có được token đều có thể kiểm soát tài khoản Discord của bạn!

## 🚀 **Sử dụng**

### **Sử dụng cơ bản**

```bash
# Chạy bot
poetry run python -m run_bot
# Hoặc dùng pip
python -m run_bot

# Hoặc dùng CLI
Hikari-SelfBot
```
## 📄 **Giấy phép**

* Dự án này được phát hành theo giấy phép MIT - xem file [LICENSE](LICENSE) để biết chi tiết.
* **Lưu ý: Chỉ sử dụng cho mục đích giáo dục. Self-bot vi phạm ToS của Discord. Hãy sử dụng một cách có trách nhiệm! 🐍⚡**

## 🤝 **Đóng góp & Liên hệ**

* Tác giả: NirussVn0
* Hỗ trợ Discord: [hikariisan.vn](https://discord.gg/5Naa9X9W7f)
* Email: [niruss.dev](mailto:work.niruss.dev@gmail.com)

