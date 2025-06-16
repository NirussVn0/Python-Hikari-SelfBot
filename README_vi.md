# Hikari Self-Bot using Python

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Type hints: mypy](https://img.shields.io/badge/type%20hints-mypy-blue.svg)](http://mypy-lang.org/)

### Tác giả: NirussVn0

⚠️ **CẢNH BÁO: Dự án này chỉ dành cho mục đích học tập!**

Self-bot vi phạm Điều khoản Dịch vụ của Discord và có thể dẫn đến việc khóa tài khoản. Chỉ sử dụng mã này để học tập và thử nghiệm trên các máy chủ riêng tư mà bạn có quyền.

## 🧪 **Tính năng**

- **Yêu cầu Python 3.9 trở lên:** Tận dụng các tính năng mới nhất của ngôn ngữ.
- **100% Type Hints:** Toàn bộ mã nguồn được chú thích kiểu, kiểm tra với `mypy`.
- **Phân tích & Thống kê nâng cao:** Theo dõi hoạt động và hiệu suất của bot.
- **Giới hạn tốc độ:** Ngăn chặn lạm dụng và tuân thủ giới hạn API của Discord.
- **Ghi log an toàn:** Không bao giờ ghi lại dữ liệu nhạy cảm.
- **Xác thực token:** Kiểm tra token với API của Discord.
- **Tạo lệnh:** Xem [COMMAND.md](COMMAND.md) để biết các lệnh có sẵn.
- **Cài đặt linh hoạt:** Hỗ trợ Poetry (khuyến nghị) hoặc pip.

## 📦 **Cài đặt**

### **Sao chép kho mã**

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

1. Sao chép mẫu tệp môi trường:

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

Xác thực token trước khi chạy:

```bash
# Sử dụng trình xác thực tích hợp
python -m src.utils.validators <token> [password]

# Hoặc sử dụng công cụ CLI
discord-selfbot validate-token
```

⚠️ **Cảnh báo bảo mật:** Hãy cực kỳ cẩn thận với token của bạn. Bất kỳ ai có token đều có thể kiểm soát tài khoản Discord của bạn!

## 🚀 **Sử dụng**

### **Cách sử dụng cơ bản**

```bash
# Chạy bot
python -m hikari_selfbot.main

# Hoặc sử dụng CLI
Hikari-SelfBot
```

## 📄 **Giấy phép**

- Dự án này được cấp phép theo giấy phép MIT - xem tệp [LICENSE](LICENSE) để biết chi tiết.
- **Lưu ý: Chỉ sử dụng cho mục đích học tập. Self-bot vi phạm ToS của Discord. Hãy sử dụng một cách có trách nhiệm! 🐍⚡**

## 🤝 **Đóng góp**

- Author: NirussVn0
- Discord: hikarisan.vn
