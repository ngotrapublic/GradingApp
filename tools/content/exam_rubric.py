"""Final exam rubric for the grading app (lecturer, 29/10/2026): students still write their results on the exam paper; the
examiner marks on the app (tab "Exam"), by the mark scheme of HN/ElecCircuitLabExam_v1.docx: group work 35 (each item
marked once for the exam group), individual 15 (contribution 1-5, 0 = did nothing = fails the exam; personal skills 0-10),
minus up to 10 for breaking the rules. Exam groups (random, up to 3, within the class) are drawn by the app on the exam day.
Writes keys.json "exam" (run again after gen_keys.py)."""
import json

KEYS = '/Users/mac/Tra/SE9_ElecCircuitLab/HCM/GradingApp/courses/SE009/keys.json'
EXAM = {
    'title': 'Final exam', 'total': 50, 'groupSize': 3,
    'group': [   # [id, English, Vietnamese, max]
        ['A', 'Section A – DC circuit', 'Phần A – Mạch DC', None],
        ['a1', 'DC power supply set at 5 V and running', 'Nguồn DC đặt 5 V và chạy đúng', 1],
        ['a2', 'Resistor values properly chosen', 'Chọn giá trị điện trở hợp lý', 3],
        ['a3', 'Actual resistor values remeasured and noted', 'Đo lại và ghi giá trị điện trở thật', 2],
        ['a4', 'Actual schematic drawn correctly (ideal or measured values)', 'Vẽ đúng sơ đồ với điện trở thật', 3],
        ['a5', 'Breadboard matches their schematic', 'Mạch trên breadboard khớp sơ đồ của SV', 3],
        ['a6', 'I1, I2, I3, V1, V2 measured correctly', 'Đo đúng I1, I2, I3, V1, V2', 4],
        ['a7', 'Theory (KCL, KVL, Ohm) for I1, I2, I3, V2', 'Tính lý thuyết (KCL, KVL, Ohm) I1, I2, I3, V2', 4],
        ['a8', 'Calculations close to the measurement (only if correct)', 'Kết quả tính gần số đo (chỉ khi tính đúng)', 1],
        ['B', 'Section B – AC circuit', 'Phần B – Mạch AC', None],
        ['b1', 'R and C calculated and chosen (100 Hz, 5 kHz)', 'Tính và chọn R, C (100 Hz, 5 kHz)', 3],
        ['b2', 'Filter built correctly on the breadboard', 'Lắp đúng mạch lọc trên breadboard', 3],
        ['b3', 'Generator: correct signal (frequency, offset, Vpp)', 'Máy phát: đúng tín hiệu (tần số, offset, Vpp)', 2],
        ['b4', 'Generator output changed from 50 Ω to High-Z', 'Đổi ngõ ra máy phát từ 50 Ω sang High-Z', 1],
        ['b5', 'Generator with the 1X cable', 'Dùng cáp 1X cho máy phát', 1],
        ['b6', 'Oscilloscope: clear signal with frequency and Vpp', 'Osci: tín hiệu rõ, có tần số và Vpp', 1],
        ['b7', 'Oscilloscope setting matches the cable (1X / 10X)', 'Osci đặt đúng 1X / 10X theo cáp', 1],
        ['b8', 'Output Vpp measured and recorded in Table 1', 'Đo và ghi đúng Vpp ngõ ra vào Bảng 1', 2]],
    'individual': [
        ['contrib', 'Individual contribution (0 = did nothing: fails the exam)', 'Đóng góp cá nhân (0 = không làm gì: rớt môn thi)', 5],
        ['skills', 'Personal skills (measure R, C, V, I; capture a signal; fix a fault; explain)', 'Kỹ năng cá nhân (đo R, C, V, I; bắt tín hiệu; sửa lỗi; giải thích)', 10]],
    'penalty': ['penalty', 'Rules broken (minus, at most 10)', 'Vi phạm quy định (trừ, tối đa 10)', 10],
}


def run():
    K = json.load(open(KEYS, encoding='utf-8'))
    K['exam'] = EXAM
    json.dump(K, open(KEYS, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    g = sum(x[3] for x in EXAM['group'] if x[3]); i = sum(x[3] for x in EXAM['individual'])
    print(f'exam rubric: group {g} + individual {i} = {g + i}')


if __name__ == '__main__':
    run()
