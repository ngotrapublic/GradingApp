const QUIZ_STUDENT_NOTICE_EN = `SE010 – Weekly Review Quiz

Please read before you start.

Purpose
This is a weekly review quiz to help you prepare for the final exam. It is not the final exam itself. Question numbers and wording may differ from the real test.

What to bring / how to work
• Do the quiz on your phone or tablet only (computers cannot open the quiz).
• You may use your laptop to read the weekly review PDFs on Canvas while answering on your phone.
• Bring a non-programmable calculator for numerical questions.

How the quiz works
• You will get 15 questions (shuffled; each student may see a different set).
• Pass mark: 11 / 15.
• For number questions, enter an integer only; the ×10 power is already shown.
• Stay in the quiz app. If you switch to another app, lock the phone, or leave the page, your attempt may end immediately.
• If you get disconnected, open the link again and enter either your full name or student ID (whichever matches what you used before) to continue.

After you pass
• You must read all English explanations on screen.
• Attendance is recorded only after you finish the explanations.
• If you do not pass, you may retry. If you already passed, you cannot retake unless the lecturer resets you.

Hints
• Hints (lightbulb) unlock after 20 minutes, or after several failed attempts.
• Theory hints explain the idea; calculation hints show how to plug in numbers — you still finish the calculator steps yourself.

Please try to understand the material. The goal is review and learning, not only attendance.

Use the class quiz link / QR code provided by your lecturer for this week’s topic.`;

async function showQR(forStudents, clsId) {
  let target = '';
  let title = T('Open on a phone', 'Mở trên điện thoại');
  let hint = T('Open the phone camera and scan:', 'Mở camera điện thoại và quét mã:');
  if (forStudents === true || forStudents === 'student') {
    target = 'student';
    title = T('Students: your team, card and marks', 'Sinh viên: nhóm, đề và điểm');
    hint = T('Scan the code, type your student ID and your password.', 'Quét mã, nhập MSSV và mật khẩu.');
  } else if (forStudents === 'quiz' || forStudents === '/quiz/') {
    target = 'quiz';
    title = T('Students: review quiz', 'Sinh viên: quiz ôn tập');
    hint = T('Scan, enter your name and student ID, then take the quiz.', 'Quét, nhập họ tên + MSSV, rồi làm quiz.');
  }
  let urlPath = '/api/qr.svg';
  const q = [];
  if (target) q.push('target=' + encodeURIComponent(target));
  if (target === 'quiz' && clsId) q.push('cls=' + encodeURIComponent(clsId));
  if (q.length) urlPath += '?' + q.join('&');
  const r = await fetch(urlPath);
  const d = document.createElement('div');
  d.className = 'modal';
  if (!r.ok) {
    const j = await r.json().catch(() => ({}));
    d.innerHTML = `<div class="box"><p>${esc((LANG === 'vi' && j.error_vi) || j.error || T('Could not create the QR code', 'Không tạo được mã QR'))}</p><button class="btn pri" data-close="1">${T('Close', 'Đóng')}</button></div>`;
  } else {
    const url = r.headers.get('X-Url');
    const svg = URL.createObjectURL(await r.blob());
    if (target === 'quiz') {
      d.innerHTML = `<div class="box quiz-qr-box">
        <h2 style="margin-top:0">${title}</h2>
        <div class="quiz-qr-grid">
          <div class="quiz-qr-left">
            <p class="muted">${hint}${/^http:/.test(url) ? ' ' + T('(this laptop address works only on the <b>same Wi-Fi</b>)', '(địa chỉ laptop này chỉ dùng được khi <b>cùng wifi</b>)') : ''}</p>
            <img src="${svg}" alt="QR">
            <p><b>${esc(url)}</b></p>
          </div>
          <div class="quiz-qr-notice">
            <h3>${T('Student notice (English) — share with the class', 'Thông báo cho SV (tiếng Anh) — gửi kèm lớp')}</h3>
            <div class="quiz-notice-body" id="quizNoticeBody">${esc(QUIZ_STUDENT_NOTICE_EN)}</div>
            <div class="quiz-qr-actions">
              <button type="button" class="btn pri" id="quizNoticeCopy">${T('Copy notice', 'Copy thông báo')}</button>
              <button type="button" class="btn pri" data-close="1">${T('Close', 'Đóng')}</button>
            </div>
          </div>
        </div>
      </div>`;
    } else {
      d.innerHTML = `<div class="box"><h2 style="margin-top:0">${title}</h2><p class="muted">${hint}${/^http:/.test(url) ? ' ' + T('(this laptop address works only on the <b>same Wi-Fi</b>)', '(địa chỉ laptop này chỉ dùng được khi <b>cùng wifi</b>)') : ''}</p>
        <img src="${svg}" alt="QR"><p><b>${esc(url)}</b></p><button class="btn pri" data-close="1">${T('Close', 'Đóng')}</button></div>`;
    }
  }
  d.onclick = e => {
    if (e.target === d || e.target.getAttribute('data-close') === '1') d.remove();
  };
  document.body.appendChild(d);
  const copyBtn = d.querySelector('#quizNoticeCopy');
  if (copyBtn) {
    copyBtn.onclick = async e => {
      e.stopPropagation();
      try {
        await navigator.clipboard.writeText(QUIZ_STUDENT_NOTICE_EN);
        toast(T('Notice copied', 'Đã copy thông báo'));
      } catch (err) {
        toast(T('Could not copy', 'Không copy được'));
      }
    };
  }
}
