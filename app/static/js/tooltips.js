/* Tooltip-Helfer für Touch-Geräte: Long-Press auf [data-tip] zeigt den Tooltip
 * temporär an. Desktop nutzt rein CSS (siehe tooltips.css).
 */
(function () {
  'use strict';

  let pressTimer = null;
  let activeEl = null;

  function showTip(el) {
    if (activeEl && activeEl !== el) activeEl.classList.remove('tip-show');
    el.classList.add('tip-show');
    activeEl = el;
  }

  function hideTip() {
    if (activeEl) activeEl.classList.remove('tip-show');
    activeEl = null;
  }

  document.addEventListener('touchstart', (evt) => {
    const el = evt.target.closest('[data-tip]');
    if (!el) return;
    pressTimer = setTimeout(() => showTip(el), 450);
  }, { passive: true });

  document.addEventListener('touchend', () => {
    if (pressTimer) { clearTimeout(pressTimer); pressTimer = null; }
    setTimeout(hideTip, 2200);
  });

  document.addEventListener('touchcancel', () => {
    if (pressTimer) { clearTimeout(pressTimer); pressTimer = null; }
    hideTip();
  });

  // Auf Desktop Klick-im-Hintergrund schließt sticky Tooltips
  document.addEventListener('click', (evt) => {
    if (!evt.target.closest('[data-tip]')) hideTip();
  });
})();
