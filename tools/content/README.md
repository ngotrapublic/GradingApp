# Nội dung môn SE009 – script tạo đề, đáp án, slide, hình

Các script đã dùng để tạo nội dung HCM của SE009 Electric Circuit Lab. Chạy bằng Python có `python-pptx`, `openpyxl`,
`matplotlib`, `schemdraw`, `segno`, `numpy`, `Pillow`. Đường dẫn trong script là đường dẫn tuyệt đối trên máy này
(`/Users/mac/Tra/SE9_ElecCircuitLab/...`); thư mục làm việc tạm là `tools/content/_build/` (không đưa vào git).

> **Cẩn thận:** hầu hết script **ghi đè** file thật (slide trong `HCM/LabN/`, file Excel trong `HCM/docs/`, đề trong
> `courses/SE009/keys.json`). Nhiều file đã được sửa tay sau đó (ví dụ cột "Cập nhật" trong file mua, ghi chú Task 1/2
> trong `keys.json`). Trước khi chạy lại, sao lưu file đích và so sánh kết quả.

## Đề và đáp án (web)
| Script | Việc |
|---|---|
| `variants.py` | sinh mã đề của 4 lab (giá trị điện trở Lab 1, loại lọc / Q / RC Lab 2, cặp R Lab 3, số đo Lab 4) |
| `gen_keys.py` | xuất `courses/SE009/keys.json` (đáp án, nội dung thẻ đề, hình) + chép hình sang `public/courses/SE009/img` và màn hình osci sang `courses/SE009/assets/lab3` |
| `lab2_team.py` | Lab 2 Bài 2 (RLC) làm theo nhóm: cả nhóm dùng đề RLC của một thành viên, xoay vòng theo số nhóm (nhóm 1, 4 thông thấp; 2, 5 thông cao; 3, 6 thông dải). Phải áp lên mã đề gốc từng thành viên |
| `scope.py` | vẽ màn hình máy hiện sóng mô phỏng (Lab 3), ghi rõ thang mV/div, kênh vào / ra |
| `rlc_check.py` | kiểm tra đáp án Lab 2 với linh kiện thật (sai số L, C, tổn hao cuộn cảm) – xem phần cuối |
| `e2e.py` | test toàn bộ web với 1 lớp 19 SV (chạy với server thử, `GRADING_DATA_DIR` tạm), mong đợi 50/50 |
| `vercel_sim.py` | chạy `api/index.py` giống Vercel trên máy (thử với Postgres) |

## Hình
`fig_d1.py` … `fig_d4.py`, `fig_lab3.py` vẽ sơ đồ mạch vào `fig/`. `fix_divider.py` xóa khối nguồn 12 V / 1 MΩ của HN khỏi
ảnh Proteus Lab 4. `fig/qr_student.png` là mã QR trang SV (tạo lại bằng `add_qr.py`).

## Slide (thứ tự chạy khi tạo lại từ đầu)
1. Giải nén 3 bộ slide HN vào `_build/u1`, `_build/u2`, `_build/u3` (`deck.unzip('HN/Electronic Circuit Lab Slide N.pptx', ...)`).
2. `build_d1.py` … `build_d4.py` – ghép slide HN + slide mới (`deck.py`), lưu vào `HCM/LabN/`.
3. `add_notes.py N <src> <dst>` với `notes1.py` … `notes4.py` – script giảng (chỉ lời nói, `spoken.py` bỏ nhãn SAY/DO/TIP).
4. `add_qr.py` – mã QR trang SV trên các slide nộp bài.
5. `align_web.py` – khớp slide với web (nộp trước rồi gọi tick, 1 ảnh, hộp linh kiện, Lab 2 Task 1/2, micro dây đực–cái,
   slide dọn cụm máy). Chạy lại nhiều lần vẫn an toàn.
6. `rlc_slides.py` – 5 slide giải thích lọc RLC trong Lab 2 (thông thấp, thông cao, thông dải: vì sao, băng thông BW,
   cách đo BW). Hình vẽ bằng `fig_rlc_theory.py`. Chạy sau `align_web.py`; chạy lại thì thay slide cũ.
7. `bench_map_slide.py` – slide "Find your table" (sơ đồ phòng chữ U, đánh số theo chiều kim đồng hồ, bàn 1 bên trái
   giảng viên; bàn giảng viên và TV ở đầu trống của chữ U, tường cuối chỉ có cửa sổ) sau slide nhóm của Lab 1. Cùng bố cục với `public/js/core/benchmap.js`. Chạy sau `align_web.py`.
8. `parts_slide.py` – slide "Parts: use up or give back" sau "Find your table" (Lab 1): chỉ điện trở là tiêu hao, mọi
   linh kiện khác (tụ, cuộn 1 mH, LM358, micro, LED, 470 µF) trả về đúng túi. Chạy sau `bench_map_slide.py`.
9. `welcome_notice.py` – hộp nhắc trên slide tên môn (Lab 1): chưa bày đồ ra bàn (laptop, tập vở, cặp), giữ điện thoại
   để đăng nhập trang SV. Chạy lại thì thay hộp cũ.
10. `table_words.py` – phòng HCM chỉ có bàn ghế, không có "bench": đổi bench → table trong chữ và lời giảng của 4 bộ
   slide. Chạy **trước** bước 5 (để các script tìm thấy slide cũ theo tiêu đề mới) và chạy lại ở cuối.
11. `practice_slides.py` – Lab 2–4: bài tập nhỏ theo kiểu Lab 1 ("Exercise N: … (X minutes)", bước đánh số, hình bên phải,
   1 câu hỏi cuối), xen trong bài giảng, ngay sau phần lý thuyết liên quan. Không chấm điểm.
   (Bài chấm điểm trên app mới để cuối buổi.) Giá trị minh họa không trùng mã đề (RC 10 kΩ + 104; RLC 1 mH + 104 + 100 Ω). Hình: `fig_practice.py`.
12. `rc_section.py` – Lab 2 phần RC: một mạch 10 kΩ + 104; Exercise 1 → bảng → nhận xét → màn hình osci → chia áp →
   đổi R, C → Exercise 2 → bảng → nhận xét → đồ thị, điểm −3 dB → công thức f_c → Exercise 3 (không tính trở kháng).
   Task 1 (chấm điểm) dời xuống cuối buổi, ngay trước Task 2. Chạy **sau** `practice_slides.py`.
13. `rlc_table.py` – Lab 2 Exercise 6 (thông dải, 1 mH + 104 + 100 Ω) giống phần RC: bảng 7 tần số + khung vẽ đồ thị, rồi
   "What do you notice?" có đồ thị lý thuyết. Chạy sau `rc_section.py`.
14. `instrument_slides.py` – Lab 2: cách bấm máy có ảnh thật đánh số nút (osci TBS1052C, máy phát AFG1022) trước Exercise 1;
   Exercise 7 (bài tập trên lớp, mạch của Exercise 6): tìm đỉnh, tìm f_L, f_H, BW, bảng, trả lời. Task 2 (chấm điểm) chỉ
   thêm 1 dòng "dùng cách của Exercise 7". Ảnh: `fig_instruments.py` (lấy từ Lab 1).
15. `lab2_task2.py` – Lab 2: Task 1 = thiết kế (nộp R, C; chấm f_c = 1/(2πRC) so với mục tiêu); Task 2 = đo mạch thông dải
   giống Exercise 6–7 với C, R của nhóm (nộp f_0, BW). Sửa chữ các slide Task 1, Task 2, Devices, Real components, What to
   submit. Đáp án: `lab2_team.lab2_task1_design`, `lab2_team.lab2_task2_measure` (đã áp vào `keys.json`). File Excel mẫu:
   `lab2_template.py`.
16. `lab3_fixes.py` – Lab 3: thay ảnh mạch của HN (nguồn ±6 V tự chế) ở slide "Connect the rest of the circuit" bằng sơ
   đồ đấu dây với nguồn ±6 V của PB-503A (`fig/p3_wiring.png`, vẽ bằng `fig_practice.py`); đưa slide cấp nguồn và
   Exercise 1 (mạch đệm) lên trước mạch khuếch đại đảo. Chạy sau `practice_slides.py`.
16. `lab2_instruments.py` – Lab 2: chép phần osci + máy phát (slide "Overview of AC lab instruments" … "Step 5. Rotate the
   Multipurpose knob") từ Lab 1 sang Lab 2, sau slide Devices; Exercise 8, 9, 10, 10 → A, B, C, D. Lab 1 giữ nguyên.
   Chạy lại thì thay bản chép cũ.
16. `lab1_no_ac.py` – (29/10/2026) xóa 28 slide osci + máy phát khỏi Lab 1 (đã chép sang Lab 2), sửa bảng Course Summary
   (Lab 2, Lab 3 mới) và slide Devices của Lab 1. Sau bước này `lab2_instruments.py` không chép lại nữa (giữ bản trong Lab 2).
16. `lab2_demo.py` – Lab 2: Exercise 6–7 thành phần GV làm mẫu (SV chỉ tự đo một lần ở Task 2); đổi tiêu đề và các chỗ
   "Exercise 6/7" trên slide và lời giảng. Chạy sau `lab2_instruments.py`.
16. `lab3_freq.py` – Lab 3, Exercise 4 (đáp tuyến tần số của mạch Exercise 2): bảng 9 tần số 20 Hz – 200 kHz + đồ thị
   trống, rồi "What do you notice?" với đường lý thuyết – cả 3 slide đang ẨN (HIDE = True), chỉ bật cho lớp nhanh (f_L ≈ 72 Hz do R1, C1; f_H ≈ 68 kHz do LM358); sửa slide "Use low
   (audio) frequencies" thành lời giải thích. Chạy sau `lab3_fixes.py`. `practice_slides.py 3` chỉ chạy lại Lab 3.
16. `lab4_review.py` – Lab 4: bỏ phần lý thuyết decoupling (slide "Capacitors", 3 slide "Decoupling capacitor", dòng
   "Decouple both supply rails" ở slide Recap) – đề thi không có; 2 tụ 0.1 µF ở chân nguồn trong "Final circuit version 2" vẫn
   giữ (có trong sơ đồ). Thêm phần ôn thi sau "Skills checklist": Exercise 6 ghép điện trở, Exercise 7 cài máy từ trạng
   thái mặc định (osci Default Setup, máy phát 50 Ω), Exercise 8 thiết kế lọc thông thấp 1 kHz bằng linh kiện trên bàn; mỗi bài
   có slide đáp án. Chỉ còn một mạch final (bỏ version 1: lỗi "tắt sau 1 phút" là do nguồn ±6 V tự chế của HN; điểm chấm
   dùng giá trị version 2), bỏ cả slide tụ 0.1 µF ở chân nguồn và xóa C4, C5 trên các ảnh sơ đồ (`fig/hn_s3_*_noc45.png`,
   thẻ đề `lab4_circuit.png`). Rà lại trước buổi học: sửa câu chữ HN, từ chưa dạy trong bảng từ vựng, ẩn 2 slide HN tính f_c
   với 8 Ω (sai so với đáp án Exercise 2), bài chấm điểm ghi rõ tháo micro và loa, máy phát High-Z (cả thẻ đề trong
   `keys.json`). Chạy sau `practice_slides.py` (chạy `practice_slides.py 4` sẽ xóa phần ôn thi), trước `subscripts.py`.
16. `lab3_rlc.py` – (29/10/2026) chuyển phần cuộn cảm + RLC nối tiếp (bài giảng, demo) và bài chấm RLC từ Lab 2 sang đầu
   Lab 3. Điểm: Lab 1 12, Lab 2 12 (bài RC cá nhân: R, C → f_c 6 + GV xem f_c trên osci 6), Lab 3 16 (Task 1 RLC nhóm: f_0 3,
   BW 3, đồ thị 2; Task 2 khuếch đại từ màn hình osci, cũng làm nhóm: 4 × 2 – cả nhóm chung một màn hình (nhóm 1, 4 cặp R thứ nhất; 2, 5 cặp thứ hai; 3, 6 cặp thứ ba),
   vì trainer chỉ cho 2 người làm cùng lúc), Lab 4 10. `lab3_rlc.py decks` sửa 3 bộ slide (Lab 4: bảng từ của Lab 3 có từ RLC),
   `lab3_rlc.py keys` sửa `keys.json` (Lab 3 có `team_submit`: một bạn nộp cho cả nhóm, các bạn khác bấm Xác nhận). File Excel mẫu: `Lab3_RLC_data_template.xlsx` (`lab2_template.py`). Chạy sau các script
   Lab 2–4 khác, trước `notes_cleanup.py` và `subscripts.py`. **Sau khi chạy lại `gen_keys.py`/`lab2_team.py` hoặc các script
   RLC của Lab 2 (`rlc_slides`, `rlc_table`, `instrument_slides`, `lab2_task2`, `lab2_demo`) phải chạy lại script này.**
16. `review_reveal.py` – Lab 2–4: slide "Review – words from Lab N" hiện đáp án từng dòng khi bấm (khung chữ đặt lên từng ô,
   hiệu ứng Appear); bỏ slide "(answers)". Chạy lại không làm gì nữa.
16. `notes_cleanup.py` – xóa các dòng "New word…" trong lời giảng Lab 1–4 (từ mới đã có trên slide).
17. `subscripts.py` – viết đúng chỉ số dưới cho biến (f_c, f_0, V_in, V_out, X_C, R_L, V_cc…) trên slide Lab 2–4. Chạy **cuối cùng**.

Thứ tự khi chạy lại Lab 2–4: `align_web.py` → `rlc_slides.py` → `table_words.py` → `practice_slides.py` → `rc_section.py` → `rlc_table.py` → `instrument_slides.py` → `lab2_task2.py` → `lab2_instruments.py` → `lab2_demo.py` → (Lab 3: `lab3_fixes.py` → `lab3_freq.py`) → (Lab 4: `lab4_review.py`) → `lab3_rlc.py` → `notes_cleanup.py` → `subscripts.py`.

> **Lab 1 đã sửa tay từ 24/10/2026** (thêm bài tập Exercise 1–10, đổi thứ tự slide). `align_web.py` giờ chỉ sửa Lab 2–4;
> `bench_map_slide.py`, `parts_slide.py`, `welcome_notice.py` không chạy nữa trừ khi thêm `--force` (sẽ ghi đè bản sửa tay).

## Linh kiện
`bom.py`, `bom2.py`, `mkxlsx.py`, `mk2.py`, `mk3.py`, `shop.py` – tạo file mua linh kiện (giá thegioiic).
**Không chạy lại**: file `HCM/docs/HCM_Linh_kien_can_mua.xlsx` đã được cập nhật tay (cột "Cập nhật").
`gen_bags.py` – file chia túi theo cụm (`HCM/docs/HCM_Chia_tui_linh_kien.xlsx`), đọc số đã đặt từ file mua.

## Cũ (không còn dùng)
`labfiles.py`, `make_labfiles.py`, `lab1_files.py`, `sheet.py` – phiếu đề PDF, Excel chấm dự phòng, quiz Canvas (đã bỏ).
`patch_simple.py`, `design.py` – các bước sửa slide một lần trước đây.
