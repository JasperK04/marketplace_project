const menuButton = document.getElementById('menu-button');
const menu = document.getElementById('vertical-menu');

if (menuButton && menu) {
    menuButton.addEventListener('click', () => {
        menu.style.display = menu.style.display === 'flex' ? 'none' : 'flex';
    });
}
