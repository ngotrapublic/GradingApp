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

## Linh kiện
`bom.py`, `bom2.py`, `mkxlsx.py`, `mk2.py`, `mk3.py`, `shop.py` – tạo file mua linh kiện (giá thegioiic).
**Không chạy lại**: file `HCM/docs/HCM_Linh_kien_can_mua.xlsx` đã được cập nhật tay (cột "Cập nhật").
`gen_bags.py` – file chia túi theo cụm (`HCM/docs/HCM_Chia_tui_linh_kien.xlsx`), đọc số đã đặt từ file mua.

## Cũ (không còn dùng)
`labfiles.py`, `make_labfiles.py`, `lab1_files.py`, `sheet.py` – phiếu đề PDF, Excel chấm dự phòng, quiz Canvas (đã bỏ).
`patch_simple.py`, `design.py` – các bước sửa slide một lần trước đây.
