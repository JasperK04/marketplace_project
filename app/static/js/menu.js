const menuButton = document.getElementById('menu-button');
const menu = document.getElementById('vertical-menu');

if (menuButton && menu) {
    menuButton.addEventListener('click', () => {
        menu.style.display = menu.style.display === 'flex' ? 'none' : 'flex';
    });

    // ensure the vertical menu is closed when crossing the responsive breakpoint
    let lastWidth = window.innerWidth;
    window.addEventListener('resize', () => {
        const w = window.innerWidth;
        if (lastWidth <= 800 && w > 800) {
            menu.style.display = 'none';
        }
        lastWidth = w;
    });
}
