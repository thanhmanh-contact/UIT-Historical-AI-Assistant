# Chatbot UIT' 20 Người kể chuyện

Chatbot RAG kỷ niệm 20 năm UIT và lịch sử Khoa Công nghệ Phần mềm

## Cài đặt (Môi trường Local)

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
```

Tạo file `.env`:
```env
GOOGLE_API_KEY=your-gemini-api-key-here
REDIS_URL=rediss://xxxxx (link lấy từ Upstash)
WEB_SEARCH_ENABLED=True
```
*Lưu ý: Để tránh gián đoạn khi test, nên theo dõi quota của Google AI Studio tại aistudio.google.com.*

### 2. Tạo Vector Database

```bash
# Tạo cả hai DB (lần đầu):
python scripts/init_data.py

# Chỉ tạo CNPM (nếu UIT đã có):
python scripts/init_data.py --scope cnpm

# Chỉ tạo UIT:
python scripts/init_data.py --scope uit
```

### 3. Chạy Server

```bash
uvicorn app.main:app --reload --port 8000
```

### 4. Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## Triển khai Hệ thống thực tế (Deployment)

Để biến project thành một sản phẩm thực tế chạy trên Internet, bạn cần triển khai các thành phần lên các dịch vụ đám mây (Cloud). Dưới đây là hướng dẫn sử dụng Upstash (Redis), Render (Backend) và Vercel (Frontend).

### 1. Triển khai Redis với Upstash (Quản lý Cache & Session)
Upstash cung cấp Serverless Redis miễn phí, rất phù hợp cho dự án này.

1. Truy cập [Upstash](https://upstash.com/) và tạo tài khoản.
2. Bấm **Create Database**, đặt tên (vd: `uit-chatbot-redis`), chọn Region gần bạn (vd: Singapore), bật **TLS (SSL)** và chọn tạo.
3. Tìm chuỗi kết nối **REST_URL** như `rediss://...`.
4. Lưu lại thông tin này để cấu hình biến môi trường cho Backend.

### 2. Triển khai Backend FastAPI với Render
Render.com cung cấp dịch vụ hosting để chạy Python Backend.

1. Truy cập [Render](https://render.com/) và tạo tài khoản, sau đó tạo một **Web Service** mới, kết nối với kho lưu trữ GitHub của bạn.
2. Cấu hình Web Service:
   - **Name**: `uit-chatbot-backend`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt && python scripts/init_data.py` *(Lưu ý: Để FAISS index được tạo ra khi deploy, bạn cần đảm bảo các file raw data đã được commit lên GitHub).*
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. Trong phần **Environment Variables**, thêm các biến sau:
   - `GOOGLE_API_KEY`: API Key lấy từ aistudio.google.com.
   - `FRONTEND_URL`: Địa chỉ URL của Vervel(frontend).
   - `REDIS_URL`: Chuỗi kết nối của Upstash Redis ở bước 1.

   *Lưu ý: Để tránh gián đoạn khi test, nên theo dõi quota của Google AI Studio tại aistudio.google.com.*
   
5. Bấm **Create Web Service**. Lấy địa chỉ URL của backend sau khi hoàn tất (vd: `https://uit-chatbot-backend.onrender.com`).

*Lưu ý: Nếu hệ thống sử dụng hosting miễn phí thì lần truy cập đầu tiên có thể phản hồi chậm do server cần thời gian khởi động lại.*

### 3. Triển khai Frontend với Vercel
Vercel là nền tảng tối ưu nhất để deploy các ứng dụng React.

1. Truy cập [Vercel](https://vercel.com/) và kết nối GitHub của bạn.
2. Bấm **Add New... > Project**, chọn repo của dự án.
3. Cấu hình Project:
   - **Framework Preset**: Vite (hoặc Create React App tùy cấu hình hiện tại của dự án).
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
4. Mở phần **Environment Variables**, cấu hình URL của Backend Render vừa tạo:
   - `VITE_API_URL`: `https://xxx.onrender.com/api/v1` (thêm đuôi /api/v1)
5. Bấm **Deploy**. Bạn sẽ nhận được đường link live (vd: `https://uit-chatbot.vercel.app`).

### 4. Chuẩn bị cho Production (Real Project)
Để dự án thực sự hoàn chỉnh và an toàn, bạn nên thiết lập các cấu hình sau:
- **Bảo mật CORS**: Tại Backend (`main.py`), cập nhật `allow_origins` trong `CORSMiddleware` thành danh sách các domain cụ thể (chỉ cho phép tên miền của Vercel frontend được gọi API).
- **Tên miền tùy chỉnh (Custom Domain)**: Trỏ tên miền riêng (như `chatbot.uit.edu.vn`) thay vì dùng subdomain mặc định của Vercel/Render.
