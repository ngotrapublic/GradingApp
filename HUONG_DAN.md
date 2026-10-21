# Trang chấm điểm các môn lab

Dùng cho nhiều môn lab (hiện có **SE009 Electric Circuit Lab**), nhiều học kỳ, nhiều giảng viên (HCM, HN…).

Có 2 cách chạy, **cùng một bộ code**:
- **Online trên Vercel** (dùng chính trong học kỳ): SV vào bằng 4G/wifi bất kỳ. Xem phần *Đưa lên Vercel*.
- **Trên laptop** (`start.command`): để thử, hoặc dự phòng. Dữ liệu laptop và dữ liệu online **tách riêng** – khi đã lên online thì chỉ dùng bản online.

## Tài khoản
| Vai trò | Ai tạo | Làm được gì |
|---|---|---|
| **Admin** | có sẵn: username `admin` (mật khẩu mặc định do thầy/cô đặt) | tạo / khóa tài khoản, đặt lại mật khẩu; thấy mọi lớp, giao lớp cho giảng viên |
| **Giảng viên** | admin | tạo lớp của mình (chọn môn + học kỳ), nhập danh sách SV, chấm, gửi Canvas, thêm TA vào lớp. **Chỉ thấy lớp của mình.** |
| **TA** | admin | chỉ thấy lớp được giảng viên thêm vào; được **tick, chấm đồ thị / demo, nhập số tay, bật-tắt Cho SV xem đề / Nhận bài**. Không được: sửa danh sách, chia lại nhóm, sửa điểm tay, công bố điểm, gửi Canvas, đặt lại mật khẩu SV |
| **Sinh viên** | tự tạo | đăng nhập bằng **MSSV + mật khẩu** (một mật khẩu cho mọi môn lab) |

- Mọi người đăng nhập bằng **username + mật khẩu** (ít nhất 8 ký tự). Nút **👤** góc trên: đổi mật khẩu, đăng xuất.
- **Đăng nhập lần đầu bằng mật khẩu được cấp** (admin mặc định, tài khoản mới, mật khẩu vừa được đặt lại) thì web **bắt đổi mật khẩu** trước khi làm việc khác.
- Sai mật khẩu nhiều lần thì bị khóa 15 phút.
- TA muốn vào lớp: báo admin tạo tài khoản TA → giảng viên vào tab **Lớp** → **Sửa lớp này** → **Thêm TA**.

## Chạy trên laptop
1. Nhấp đúp **start.command** (lần đầu macOS có thể hỏi: chuột phải → Open).
2. Cửa sổ Terminal hiện địa chỉ `http://localhost:8000` (laptop) và `http://192.168.x.x:8000` + **mã QR** (điện thoại **cùng wifi**).
3. **Lần đầu**: đăng nhập `admin` + mật khẩu mặc định → đổi mật khẩu admin → tab **Tài khoản** tạo tài khoản giảng viên cho chính mình (và TA nếu có) → đăng xuất, đăng nhập lại bằng tài khoản giảng viên.
4. **Ngôn ngữ**: mặc định tiếng Anh; bấm **EN | VI** để đổi.
5. Tắt: đóng cửa sổ Terminal hoặc nhấn Ctrl+C.

Dữ liệu (cả ảnh mạch của SV) lưu trong `data/grading.db`. Muốn sao lưu thì tắt web rồi copy thư mục `data`.

**Dữ liệu của bản cũ** (3 lớp SE009 trước khi có tài khoản): lần chạy đầu tự chuyển thành 3 lớp **SE009 – Fall 2026** (bộ đề 1, 2, 3) **chưa có giảng viên phụ trách**. Đăng nhập admin → tab **Lớp** → mỗi lớp **Sửa lớp này** → chọn **Giảng viên phụ trách** → Lưu. SV của bản cũ tạo mật khẩu mới ở lần đăng nhập sau (PIN 4 số cũ không dùng nữa).

## Lớp và học kỳ (tab **Lớp**)
- **Tạo lớp**: chọn **môn**, **học kỳ** (Spring / Summer / Fall + năm), **tên lớp** (đặt giống tên trên Canvas, vd `SE009.1`) và **bộ đề**.
- **Bộ đề** quyết định mã đề: bộ 1 → mã 101–124, bộ 2 → 201–224, bộ 3 → 301–324. Các lớp cùng môn, cùng học kỳ nên dùng bộ đề khác nhau (web tự gợi ý bộ chưa dùng). Chỉ đổi bộ đề trước Lab 1.
- Ô chọn lớp ở đầu trang chia theo học kỳ (mới nhất ở trên). Lớp mình là TA có chữ "(TA)".
- **Xóa lớp** xóa luôn SV, điểm, ảnh của lớp đó (phải gõ đúng tên lớp để xác nhận).

## Dùng
- **SV & nhóm** (lớp đang chọn):
  - **Nhập file**: Canvas → People → xuất Excel. Chọn một hoặc nhiều file cùng lúc: file có cột *Section* trùng tên một lớp của mình (cùng môn, cùng học kỳ – vd Section "HCM - SE009.2 - …" → lớp `SE009.2`) thì vào lớp đó, không thì vào lớp đang xem. Chỉ lấy dòng *Role = Student*; tên được bỏ chữ "pending", "(He/Him)". Mã SV lấy theo cột *SIS ID*.
  - **Dán từ Excel**: bôi đen bảng (kể cả dòng tiêu đề), Copy, dán vào ô dán rồi bấm **Nhập phần đã dán**.
  - **Nhập xong là web chia nhóm ngẫu nhiên ngay**: 6 nhóm (6 cụm máy) × 3 người; lớp hơn 18 SV thì người dư là thành viên 4 của một nhóm. Nhập lại thì SV cũ giữ nguyên nhóm, SV mới vào chỗ trống. SV đã rút khỏi lớp thì bấm × để xóa.
  - Muốn đổi: sửa nhóm / thành viên rồi bấm **Lưu nhóm / thành viên**, hoặc **Chia lại ngẫu nhiên** (chỉ nên làm trước Lab 1).
  - Cột **Mật khẩu**: **–** = SV chưa đăng nhập lần nào; **✓ ↺** = đã có mật khẩu, bấm để đặt lại khi SV quên.
- **Chấm** (điện thoại): chọn Lab → bấm tên SV → xem đáp án, khoảng ±10% và **Hình đề bài** → bấm **Tick** khi đã thấy số trên máy đo.
  Lab 2: chọn điểm đồ thị 0 / 1.5 / 3. Lab 4: chọn điểm demo nhóm 0 / 2 / 4 ở dòng tên nhóm. Bấm lại vào nút đang chọn để bỏ chọn.
- **Gửi Canvas**: kiểm tra lab, tạo file điểm để import vào Canvas, xem bảng điểm, tải Excel (lớp này hoặc tất cả lớp của mình).

## Điểm chính thức nằm trên Canvas
Web chỉ là công cụ hỗ trợ chấm. Điểm chính thức và mọi thông báo vẫn ở Canvas. Trên Canvas **chỉ có thông báo và các cột điểm** – không quiz, không file đề (SV xem đề, nộp bài, tải file mẫu trên trang SV).

**Làm một lần đầu học kỳ (mỗi lớp trên Canvas):**
- Tạo assignment tên đúng **Lab 1**, **Lab 2**, **Lab 3**, **Lab 4** – điểm tối đa 12, 14, 14, 10 (SE009) – kiểu nộp *No submission*, nhóm assignment "Lab assessment" (trọng số 50%).

**Trong buổi lab:**
1. Tab **Chấm** → hộp **Trang SV**: bật **Cho SV xem đề** và **Nhận bài**, bấm **QR cho SV** và chiếu lên màn hình.
2. SV quét QR, đăng nhập, xem đề (kèm sơ đồ mạch), đo, điền số ngay dưới đề, **chụp đúng 1 ảnh mạch thật** (breadboard, bắt buộc) và bấm **Nộp**. Sửa số / xóa rồi chụp lại ảnh được cho đến khi được tick.
3. Giảng viên / TA đi tick trên điện thoại – số SV nộp và ảnh mạch hiện ngay trong khung chấm. Đã tick thì số và ảnh của SV bị khóa.
4. Hết giờ: tắt **Nhận bài**.
   SV nào không nộp được trên điện thoại: xem số trên máy đo của SV rồi nhập ở mục **Nhập / sửa số tay** trong khung chấm.

**Sau buổi lab (giảng viên, khoảng 3 phút):**
1. Tab **Gửi Canvas** → **Bước 1** xem danh sách cần xử lý (có số nhưng chưa tick, chưa chấm đồ thị / demo…) và sửa ở tab **Chấm**.
2. **Bước 2**: lần đầu chọn file sổ điểm (Canvas → Grades → **Export**); các lần sau web dùng lại file đã lưu. Đánh dấu lab → **Tải file import Canvas**.
3. Canvas → **Grades** → **Import** → chọn file vừa tải → kiểm tra → **Save**. Công bố điểm / thông báo cho SV trên Canvas như bình thường.
4. (Tùy chọn) công bố điểm cho SV: bật **Công bố điểm (cả lớp)**, hoặc mở từng SV → **Công bố điểm cho SV này**.

Nếu sau đó sửa điểm (ví dụ tick bù), tab **Chấm** sẽ báo "x SV có điểm chưa đưa lên Canvas" – làm lại bước 2–3 cho lab đó. Ô vàng trong bảng điểm = điểm đã đổi nhưng chưa gửi.

**Sửa điểm tay** (làm bù, máy hỏng, phúc khảo… – chỉ giảng viên): tab **Chấm** → bấm vào SV → mục **Sửa điểm tay** → nhập điểm + lý do → **Lưu điểm**. Điểm này thay cho điểm tự tính ở mọi nơi (danh sách có dấu ✎, file Canvas, Excel, trang SV). Bấm **Bỏ điều chỉnh** để quay về điểm tự tính.
Lớp có thêm / bớt SV trên Canvas thì Export sổ điểm lại và chọn file mới ở Bước 2.

## Trang cho sinh viên (`<địa chỉ trang>/student/`)
1. SV nhập **MSSV** → web hiện **họ tên** để SV xác nhận "Đúng, là tôi".
2. **Lần đầu**: SV tạo mật khẩu (ít nhất 6 ký tự). **Lần sau**: MSSV + mật khẩu. Một mật khẩu dùng cho mọi môn lab. Sai 5 lần thì khóa 15 phút.
3. SV học nhiều lớp lab (vd SE009 rồi Electronics 1) thì chọn lớp; nút **Lớp khác** để đổi.
4. SV thấy: nhóm / cụm máy, thành viên số mấy, mã đề, các bạn cùng nhóm; **đề**, **nộp bài**, **điểm** của từng lab chỉ khi giảng viên / TA bật công tắc tương ứng.
- Trang SV không bao giờ gửi đáp án. Mỗi SV chỉ xem được đề, ảnh và điểm của chính mình.
- SV quên mật khẩu: giảng viên của một lớp SV đang học → tab **SV & nhóm** → **✓ ↺**.
- Mỗi lần SV nộp đều được ghi lại (thời gian, thiết bị) để đối chiếu khi cần.

## Đưa lên Vercel (làm một lần)
Cần: tài khoản Vercel (đăng nhập bằng GitHub/Google), Node.js trên laptop (để chạy lệnh `npx`).

1. Mở Terminal tại thư mục `GradingApp`, chạy `npx vercel` → đăng nhập → trả lời các câu hỏi (tạo project mới, giữ thư mục hiện tại).
2. Trang Vercel → project → **Storage** → **Create Database** → **Neon (Postgres)** → gói Free → **Connect** vào project. Vercel tự thêm biến `DATABASE_URL`.
3. Chạy `npx vercel --prod`. Địa chỉ dạng `https://<tên-project>.vercel.app`. Nút **QR** tự dùng địa chỉ này.
4. **Ngay sau đó**: đăng nhập `admin` + mật khẩu mặc định → **đổi mật khẩu admin** (web bắt đổi) → tab **Tài khoản** tạo tài khoản giảng viên / TA.
   (Tùy chọn: đặt biến `ADMIN_PASSWORD` trong Settings → Environment Variables thì mật khẩu admin luôn lấy theo biến này.)
5. (Nếu đã có dữ liệu trên laptop) chép lên **một lần**, khi database online còn trống:
   - Bật `start.command` một lần rồi tắt (để nâng cấp file dữ liệu cũ).
   - Vercel → Storage → database → **.env.local** → copy giá trị `DATABASE_URL`.
   - Terminal ở thư mục `GradingApp`:
     `.venv/bin/pip install "psycopg[binary]"` rồi
     `DATABASE_URL='<dán vào đây>' .venv/bin/python tools/upload_to_cloud.py`
   - Tài khoản, lớp, SV (cả mật khẩu SV), điểm, ảnh được chép nguyên. Tài khoản `admin` online giữ mật khẩu đang dùng online.
6. Sửa code sau này: chạy lại `npx vercel --prod`.

Lưu ý:
- Gói Free của Neon có 0,5 GB – đủ cho vài học kỳ (ảnh SV được thu nhỏ còn khoảng 100–200 KB mỗi ảnh).
- Tên và MSSV sinh viên nằm trên server của Vercel/Neon: nên hỏi lại quy định của trường về dữ liệu SV.

## Thêm một môn lab mới
Mỗi môn là một **gói đề**: thư mục `courses/<MÃ MÔN>/` gồm `course.json` (tên môn, số bộ đề), `keys.json` (các lab, câu hỏi, điểm, mã đề, đáp án, nội dung thẻ đề) và `assets/` (ảnh riêng tư, vd màn hình osci theo mã đề); ảnh công khai (sơ đồ mạch) ở `public/courses/<MÃ MÔN>/`. Có gói đề mới thì giảng viên chọn được môn đó khi tạo lớp.

## Cấu trúc code
```
GradingApp/
├── start.command          nhấp đúp để chạy
├── server.py              file khởi động (laptop)
├── api/index.py           file khởi động trên Vercel
├── vercel.json            cấu hình Vercel (trang web = public/, API = api/index.py)
├── requirements.txt       thư viện Python cho Vercel
├── tools/upload_to_cloud.py  chép dữ liệu laptop lên database online (một lần)
├── courses/SE009/         gói đề môn SE009: course.json, keys.json, assets/ (ảnh osci Lab 3)
├── backend/               Python
│   ├── config.py          đường dẫn, cổng
│   ├── courses.py         đọc các gói đề trong courses/
│   ├── store.py           kết nối database: SQLite (laptop) hoặc Postgres (Vercel)
│   ├── db.py              bảng dữ liệu, tài khoản, mật khẩu, quyền xem lớp, giới hạn số lần thử, chia nhóm
│   ├── scoring.py         luật chấm 10% / 20%, xuất Excel
│   ├── network.py         địa chỉ wifi, mã QR
│   └── handler.py         các API /api/...
├── public/                trang web
│   ├── index.html         khung trang (nạp các file bên dưới)
│   ├── css/base.css       giao diện chung
│   ├── js/core/           ngôn ngữ, tiện ích, gọi API, trạng thái + tính điểm, QR
│   ├── js/login/          đăng nhập, tạo admin lần đầu, đổi mật khẩu
│   ├── js/app.js          thanh trên cùng, chọn lớp, chuyển tab
│   ├── courses/SE009/     ảnh sơ đồ mạch, file mẫu của môn SE009
│   ├── student/           trang cho sinh viên (/student/)
│   └── tabs/              mỗi tab một thư mục
│       ├── grade/         Chấm
│       ├── canvas/        Gửi Canvas
│       ├── class/         SV & nhóm
│       ├── classes/       Lớp (tạo lớp, TA)
│       └── users/         Tài khoản (admin)
└── data/                  dữ liệu khi chạy trên laptop (grading.db) – sao lưu thư mục này
```
