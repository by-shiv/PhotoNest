document.addEventListener('DOMContentLoaded', function () {
    const loginTab = document.getElementById('login-tab');
    const regTab = document.getElementById('register-tab');
    const loginForm = document.getElementById('login-form');
    const regForm = document.getElementById('register-form');

    loginTab.addEventListener('click', () => {
        loginTab.classList.add('active');
        regTab.classList.remove('active');
        loginForm.classList.add('active');
        regForm.classList.remove('active');
    });

    regTab.addEventListener('click', () => {
        regTab.classList.add('active');
        loginTab.classList.remove('active');
        regForm.classList.add('active');
        loginForm.classList.remove('active');
    });
});
