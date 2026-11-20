const QUIZ_STUDENT_NOTICE_EN = `Weekly review quiz (not the final exam)

Before you start
• Phone or tablet only — computers cannot open the quiz
• Scan the QR, then enter your full name and student ID
• Laptop is OK for Canvas review PDFs; keep the quiz open on your phone
• Bring a calculator for number questions

During the quiz
• 15 shuffled questions · pass mark 11/15
• Number answers: any integers for coeff and power of 10 (we check the product; e.g. 259 and −2 for 2.59)
• Stay in this quiz app — switching apps / locking the phone may end your attempt
• Leaving again adds a wait before retry (1 min, then 2, 4, …)
• If disconnected: reopen the link and enter name or student ID to continue
• If you get stuck, a hint bulb may unlock later (not the final answer)

After you finish
• Pass → read every English explanation → attendance is recorded
• Fail → you may retry
• Goal: review and understand, not attendance only`;

const QUIZ_STUDENT_NOTICE_HTML = `
  <div class="quiz-notice-title">Weekly review quiz <span>(not the final exam)</span></div>
  <div class="quiz-notice-cols">
    <div>
      <div class="quiz-notice-h">Before you start</div>
      <ul>
        <li>Phone or tablet only — computers cannot open the quiz</li>
        <li>Scan the QR, then enter your full name and student ID</li>
        <li>Laptop is OK for Canvas review PDFs; keep the quiz open on your phone</li>
        <li>Bring a calculator for number questions</li>
      </ul>
    </div>
    <div>
      <div class="quiz-notice-h">During the quiz</div>
      <ul>
        <li>15 shuffled questions · pass mark <b>11/15</b></li>
        <li>Number answers: any integers for coeff and power of 10 (we check the product; e.g. 259 and −2 for 2.59)</li>
        <li>Stay in this quiz app — switching apps / locking the phone may end your attempt</li>
        <li>Leaving again adds a wait before retry (1 min, then 2, 4, …)</li>
        <li>If disconnected: reopen the link and enter name or student ID to continue</li>
        <li>If you get stuck, a hint bulb may unlock later (not the final answer)</li>
      </ul>
      <div class="quiz-notice-h">After you finish</div>
      <ul>
        <li>Pass → read every English explanation → attendance is recorded</li>
        <li>Fail → you may retry</li>
        <li>Goal: review and understand, not attendance only</li>
      </ul>
    </div>
  </div>`;

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
            <h3>${T('For students (English)', 'Cho SV (tiếng Anh)')}</h3>
            <div class="quiz-notice-body" id="quizNoticeBody">${QUIZ_STUDENT_NOTICE_HTML}</div>
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
