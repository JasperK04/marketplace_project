document.addEventListener('DOMContentLoaded', () => {
  const adminMenu = document.querySelector('.admin-menu');
  if (!adminMenu) return;
  const adminBtn = adminMenu.querySelector('.admin-btn');
  const dropdown = adminMenu.querySelector('.admin-dropdown');
  if (!adminBtn || !dropdown) return;

  let hideTimeout = null;

  const showMenu = () => {
    if (hideTimeout) {
      clearTimeout(hideTimeout);
      hideTimeout = null;
    }
    adminMenu.classList.add('open');
    adminBtn.setAttribute('aria-expanded', 'true');
  };

  const hideMenu = (delay = 250) => {
    if (hideTimeout) clearTimeout(hideTimeout);
    hideTimeout = setTimeout(() => {
      adminMenu.classList.remove('open');
      adminBtn.setAttribute('aria-expanded', 'false');
      hideTimeout = null;
    }, delay);
  };

  adminBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    if (adminMenu.classList.contains('open')) {
      // clicking when open should close immediately
      if (hideTimeout) clearTimeout(hideTimeout);
      adminMenu.classList.remove('open');
      adminBtn.setAttribute('aria-expanded', 'false');
    } else {
      showMenu();
    }
  });

  // close when clicking outside
  document.addEventListener('click', (e) => {
    if (!adminMenu.contains(e.target)) {
      if (hideTimeout) clearTimeout(hideTimeout);
      adminMenu.classList.remove('open');
      adminBtn.setAttribute('aria-expanded', 'false');
    }
  });

  // close on escape
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      if (hideTimeout) clearTimeout(hideTimeout);
      adminMenu.classList.remove('open');
      adminBtn.setAttribute('aria-expanded', 'false');
    }
  });

  // close dropdown when crossing responsive breakpoint
  let lastWidth = window.innerWidth;
  window.addEventListener('resize', () => {
    const w = window.innerWidth;
    if ((lastWidth <= 800 && w > 800) || (lastWidth > 800 && w <= 800)) {
      if (hideTimeout) clearTimeout(hideTimeout);
      adminMenu.classList.remove('open');
      adminBtn.setAttribute('aria-expanded', 'false');
    }
    lastWidth = w;
  });

  // hover behaviour: show immediately on enter, hide 500ms after leave
  adminMenu.addEventListener('mouseenter', () => {
    showMenu();
  });

  adminMenu.addEventListener('mouseleave', () => {
    hideMenu(250);
  });
});
