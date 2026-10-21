# Trang chấm điểm Electric Circuit Lab (HCM)

Có 2 cách chạy, **cùng một bộ code**:
- **Online trên Vercel** (dùng chính trong học kỳ): SV vào bằng 4G/wifi bất kỳ. Xem phần *Đưa lên Vercel* ở cuối.
- **Trên laptop** (`start.command`): để thử, hoặc dự phòng. Dữ liệu laptop và dữ liệu online **tách riêng** – khi đã lên online thì chỉ dùng bản online.

## Chạy trên laptop
1. Nhấp đúp **start.command** (lần đầu macOS có thể hỏi: chuột phải → Open).
2. Cửa sổ Terminal hiện 2 địa chỉ:
   - `http://localhost:8000` – mở trên laptop
   - `http://192.168.x.x:8000` – mở trên **điện thoại cùng wifi**
3. **Mở trên điện thoại nhanh**: cửa sổ Terminal in sẵn **mã QR** – mở camera điện thoại quét là vào. Trên web cũng có nút **QR** ở góc trên (và ở trang nhập PIN) để hiện lại mã.
4. Lần đầu: đặt PIN (ít nhất 8 ký tự). Các lần sau: nhập PIN để vào.
5. **Ngôn ngữ**: mặc định tiếng Anh; bấm nút **VI / EN** ở góc trên để đổi. Mỗi máy nhớ lựa chọn riêng.
6. Tắt: đóng cửa sổ Terminal hoặc nhấn Ctrl+C.

Dữ liệu (cả ảnh mạch của SV) lưu trong `data/grading.db`. Muốn sao lưu thì tắt web rồi copy thư mục `data`.
Đã đăng nhập trên điện thoại thì khởi động lại web không cần nhập lại PIN.

## Dùng
- **Lớp & nhóm**:
  - **Nhập file**: bấm **Chọn file danh sách** và chọn cả 3 file `Class_SE09_1/2/3.xlsx` (Canvas → People → xuất danh sách) cùng lúc. Mỗi file tự vào đúng lớp theo cột *Section* (SE009.1 / .2 / .3), chỉ lấy dòng *Role = Student*, tên được bỏ chữ "pending", "(He/Him)". Mã SV lấy theo cột *SIS ID* (khớp với sổ điểm Canvas).
  - **Dán từ Excel**: bôi đen bảng trong Excel (kể cả dòng tiêu đề), Copy, dán vào ô dán rồi bấm **Nhập phần đã dán**.
  - Nhập lại (khi lớp có thay đổi) thì SV đã có giữ nguyên nhóm và thành viên. SV đã rút khỏi lớp thì bấm × để xóa.
  - Chỉ lấy dòng Role = Student (bỏ TA, Teacher).
  - **Nhập xong là web chia nhóm ngẫu nhiên ngay**: 6 nhóm (6 cụm máy) × 3 người; lớp hơn 18 SV thì người dư là thành viên 4 của một nhóm. Nhập lại (có SV mới) thì SV cũ giữ nguyên nhóm, SV mới vào chỗ trống.
  - Muốn đổi: sửa nhóm / thành viên rồi bấm **Lưu nhóm / thành viên**, hoặc bấm **Chia lại ngẫu nhiên** (chỉ nên làm trước Lab 1 – chia lại làm đổi mã đề). Mã đề tự tính.
  - Lớp có hơn 18 SV (ví dụ SE009.2 có 19): nhóm nào có 4 người thì chọn **thành viên 4** cho người thứ 4.
    Thành viên 4 của nhóm t có mã đề = lớp×100 + 18 + t (ví dụ nhóm 2 lớp 2 → 220); SV xem đề của mình trên trang SV.
- **Chấm** (điện thoại): chọn Lab → bấm tên SV → xem đáp án và khoảng ±10% → bấm **Tick** khi đã thấy số trên máy đo.
  Lab 2: chọn điểm đồ thị 0 / 1.5 / 3. Lab 4: chọn điểm demo nhóm 0 / 2 / 4 ở dòng tên nhóm. Bấm lại vào nút đang chọn để bỏ chọn.
- **Gửi Canvas**: kiểm tra lab, tạo file điểm để import vào Canvas, xem bảng điểm, tải Excel lưu trữ.

## Điểm chính thức nằm trên Canvas
Web chỉ là công cụ hỗ trợ chấm. Điểm chính thức và mọi thông báo vẫn ở Canvas. Trên Canvas **chỉ có thông báo và 4 cột điểm** – không quiz, không file đề (SV xem đề, nộp bài, tải file mẫu Lab 2 trên trang SV).

**Làm một lần đầu học kỳ (mỗi lớp trên Canvas):**
- Tạo 4 assignment tên đúng **Lab 1**, **Lab 2**, **Lab 3**, **Lab 4** – điểm tối đa 12, 14, 14, 10 – kiểu nộp *No submission*, nhóm assignment "Lab assessment" (trọng số 50%).

**Trong buổi lab:**
1. Tab **Chấm** → hộp **Trang SV**: bật **Cho SV xem đề** và **Nhận bài**, bấm **QR cho SV** và chiếu lên màn hình.
2. SV quét QR bằng điện thoại, nhập MSSV, xem đề (kèm sơ đồ mạch), đo, rồi điền số ngay dưới đề, **chụp 1–3 ảnh mạch thật** (bắt buộc) và bấm **Nộp**. Sửa số / thêm, xóa ảnh được cho đến khi được tick.
3. Thầy/cô đi tick trên điện thoại – số SV nộp và ảnh mạch hiện ngay trong khung chấm (bấm ảnh để xem lớn). Đã tick thì số và ảnh của SV bị khóa.
4. Hết giờ: tắt **Nhận bài**.
   SV nào không nộp được trên điện thoại: xem số trên máy đo của SV rồi nhập ở mục **Nhập / sửa số tay** trong khung chấm.

**Sau buổi lab (khoảng 3 phút):**
1. Tab **Gửi Canvas** → **Bước 1** xem danh sách cần xử lý (có số nhưng chưa tick, chưa chấm đồ thị / demo…) và sửa ở tab **Chấm**.
2. **Bước 2**: lần đầu chọn file sổ điểm (Canvas → Grades → **Export**); các lần sau web dùng lại file đã lưu. Đánh dấu lab → **Tải file import Canvas**.
3. Canvas → **Grades** → **Import** → chọn file vừa tải → kiểm tra → **Save**. Công bố điểm / thông báo cho SV trên Canvas như bình thường.
4. (Tùy chọn) bật **Cho SV xem điểm** để SV xem trên trang SV.

Nếu sau đó sửa điểm (ví dụ tick bù), tab **Chấm** sẽ báo "x SV có điểm chưa đưa lên Canvas" – làm lại bước 2–3 cho lab đó. Ô vàng trong bảng điểm = điểm đã đổi nhưng chưa gửi.

**Sửa điểm tay** (làm bù, máy hỏng, phúc khảo…): tab **Chấm** → bấm vào SV → mục **Sửa điểm tay** → nhập điểm + lý do → **Lưu điểm**. Điểm này thay cho điểm tự tính ở mọi nơi (danh sách có dấu ✎, file Canvas, Excel, trang SV). Bấm **Bỏ điều chỉnh** để quay về điểm tự tính. Tab **Gửi Canvas** liệt kê các SV đang có điểm tay để kiểm tra lại.
Lớp có thêm / bớt SV trên Canvas thì Export sổ điểm lại và chọn file mới ở Bước 2.
Nên làm bước 3–4 trên laptop (file tải về nằm trong thư mục Downloads, dễ chọn khi Import).

SV không có trong danh sách web thì ô điểm để trống. Ở màn hình xem trước của Canvas, thầy/cô kiểm tra lại các dòng đó trước khi bấm Save.

## Lưu ý (chạy trên laptop)
- Wifi phòng lab phải cho các máy thấy nhau. Nếu điện thoại không vào được, thử bật hotspot trên điện thoại rồi cho laptop kết nối vào hotspot đó.

## Trang cho sinh viên
- SV vào **`<địa chỉ trang>/student/`**. Tab **Chấm** → hộp **Trang SV** → **QR cho SV**: chiếu mã lên màn hình, SV quét rồi nhập MSSV (SIS ID).
- **PIN của SV**: lần đầu đăng nhập, SV tự đặt PIN 4 số. Các lần sau (hoặc trên điện thoại khác) phải nhập PIN. Sai 5 lần thì bị khóa 15 phút.
  SV quên PIN: tab **Lớp & nhóm** → cột **PIN** → bấm **✓ ↺** ở dòng của SV đó → SV đặt PIN mới ở lần đăng nhập sau. Cột PIN hiện **–** là SV chưa đăng nhập lần nào.
- SV thấy: nhóm / cụm máy, thành viên số mấy, mã đề, các bạn cùng nhóm.
- **Đề**, **nộp bài** và **điểm** của từng lab chỉ mở khi thầy/cô bật công tắc **Cho SV xem đề** / **Nhận bài** / **Cho SV xem điểm** (theo từng lớp, từng lab, ở tab Chấm). Mặc định tắt.
- Mỗi lần SV nộp đều được ghi lại (thời gian, thiết bị) trong cơ sở dữ liệu để đối chiếu khi cần.
  Gợi ý: bật đề khi bắt đầu buổi lab; bật điểm sau khi đã đưa điểm lên Canvas.
- Trang SV không bao giờ gửi đáp án. Mỗi SV chỉ xem được đề, ảnh và điểm của chính mình; ảnh osci Lab 3 chỉ tải được khi đề Lab 3 của lớp đó đang bật.
- Lab 2: SV tải file Excel mẫu ghi số liệu RLC ngay dưới đề Lab 2.
- Điểm trên trang SV chỉ để tham khảo – điểm chính thức trên Canvas.

## Đưa lên Vercel (làm một lần)
Cần: tài khoản Vercel (đăng nhập bằng GitHub/Google), Node.js trên laptop (để chạy lệnh `npx`).

1. Mở Terminal tại thư mục `GradingApp`, chạy `npx vercel` → đăng nhập → trả lời các câu hỏi (tạo project mới, giữ thư mục hiện tại). Lệnh này đưa bản thử lên.
2. Trên trang Vercel → project vừa tạo → **Storage** → **Create Database** → chọn **Neon (Postgres)** → gói Free → **Connect** vào project. Vercel tự thêm biến `DATABASE_URL`.
3. **Settings → Environment Variables** → thêm `LECTURER_PIN` = PIN giảng viên (ít nhất 8 ký tự, đừng dùng PIN dễ đoán). PIN này chỉ đổi được ở đây.
4. Chạy `npx vercel --prod` để đưa bản chính thức lên. Địa chỉ dạng `https://<tên-project>.vercel.app` – mở trên điện thoại, nhập `LECTURER_PIN`. Nút **QR** tự dùng địa chỉ này.
5. (Nếu đã có dữ liệu trên laptop – danh sách lớp, nhóm, điểm) chép lên **một lần**:
   - Bật `start.command` một lần rồi tắt (để nâng cấp file dữ liệu cũ).
   - Vercel → Storage → database → **.env.local** → copy giá trị `DATABASE_URL`.
   - Trong Terminal ở thư mục `GradingApp`:
     `.venv/bin/pip install "psycopg[binary]"` rồi
     `DATABASE_URL='<dán vào đây>' .venv/bin/python tools/upload_to_cloud.py`
   - Công cụ chỉ chép khi database online còn trống. SV sẽ tự đặt PIN ở lần đăng nhập đầu trên trang online.
6. Sửa code sau này: chạy lại `npx vercel --prod` trong thư mục `GradingApp`.

Lưu ý:
- Gói Free của Neon có 0,5 GB – đủ cho cả học kỳ (ảnh SV được thu nhỏ còn khoảng 100–200 KB mỗi ảnh).
- Tên và MSSV sinh viên nằm trên server của Vercel/Neon: nên hỏi lại quy định của trường về dữ liệu SV.

## Cấu trúc code
```
GradingApp/
├── start.command          nhấp đúp để chạy
├── server.py              file khởi động (laptop)
├── api/index.py           file khởi động trên Vercel
├── vercel.json            cấu hình Vercel (trang web = public/, API = api/index.py)
├── requirements.txt       thư viện Python cho Vercel
├── tools/upload_to_cloud.py  chép dữ liệu laptop lên database online (một lần)
├── keys.json              đáp án + nội dung phiếu đề (sinh tự động)
├── assets/lab3/           ảnh osci Lab 3 (chỉ trả cho SV khi đề Lab 3 đang bật)
├── backend/               Python
│   ├── config.py          đường dẫn, cổng, đáp án
│   ├── store.py           kết nối database: SQLite (laptop) hoặc Postgres (Vercel)
│   ├── db.py              bảng dữ liệu, PIN, giới hạn số lần thử, chia nhóm ngẫu nhiên
│   ├── scoring.py         luật chấm 10% / 20%, xuất Excel
│   ├── network.py         địa chỉ wifi, mã QR
│   └── handler.py         các API /api/...
├── public/                trang web
│   ├── index.html         khung trang (nạp các file bên dưới)
│   ├── css/base.css       giao diện chung, nút gạt EN | VI
│   ├── js/core/           ngôn ngữ, tiện ích, gọi API, trạng thái + tính điểm, QR
│   ├── js/login/          màn hình PIN
│   ├── js/app.js          thanh trên cùng, chuyển tab
│   ├── student/           trang cho sinh viên (/student/)
│   └── tabs/              mỗi tab một thư mục
│       ├── grade/         Chấm
│       ├── canvas/        Gửi Canvas
│       └── class/         Lớp & nhóm
└── data/                  dữ liệu khi chạy trên laptop (grading.db) – sao lưu thư mục này
```
