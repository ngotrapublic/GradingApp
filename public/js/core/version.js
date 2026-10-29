const APP_VERSION = '0.0.16';

function showAppVersion() {
  const el = document.getElementById('app-ver');
  if (el) el.textContent = 'v' + APP_VERSION;
}
showAppVersion();
