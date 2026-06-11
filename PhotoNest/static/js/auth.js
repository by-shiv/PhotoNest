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

// Registration Validation

const password1 = document.getElementById("password1");
const password2 = document.getElementById("password2");

const strengthBox = document.getElementById("password-strength");
const matchBox = document.getElementById("password-match");

if (password1 && strengthBox) {

    password1.addEventListener("input", function () {

        const value = password1.value;

        let score = 0;

        if (value.length >= 8) score++;
        if (/[A-Z]/.test(value)) score++;
        if (/[a-z]/.test(value)) score++;
        if (/[0-9]/.test(value)) score++;
        if (/[^A-Za-z0-9]/.test(value)) score++;

        let strength = "";
        let color = "";

        if (score <= 2) {
            strength = "Weak Password";
            color = "#ff4d4f";
        }
        else if (score <= 4) {
            strength = "Medium Password";
            color = "#faad14";
        }
        else {
            strength = "Strong Password";
            color = "#52c41a";
        }

        strengthBox.innerHTML = strength;
        strengthBox.style.color = color;
    });
}

if (password1 && password2 && matchBox) {

    function checkPasswordMatch() {

        if (!password2.value) {
            matchBox.innerHTML = "";
            return;
        }

        if (password1.value === password2.value) {

            matchBox.innerHTML = "✓ Passwords Match";
            matchBox.style.color = "#52c41a";

        } else {

            matchBox.innerHTML = "✗ Passwords Do Not Match";
            matchBox.style.color = "#ff4d4f";
        }
    }

    password1.addEventListener("input", checkPasswordMatch);
    password2.addEventListener("input", checkPasswordMatch);
}


// Email Validation

const emailField = document.querySelector(
    '#register-form input[type="email"]'
);

if (emailField) {

    const emailFeedback = document.createElement("div");

    emailFeedback.id = "email-feedback";

    emailField.parentNode.appendChild(emailFeedback);

    emailField.addEventListener("input", function () {

        const email = emailField.value;

        const emailRegex =
            /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (!email) {

            emailFeedback.innerHTML = "";
            return;
        }

        if (emailRegex.test(email)) {

            emailFeedback.innerHTML =
                "✓ Valid Email";

            emailFeedback.style.color =
                "#52c41a";

        } else {

            emailFeedback.innerHTML =
                "✗ Invalid Email Format";

            emailFeedback.style.color =
                "#ff4d4f";
        }
    });
}

// Register Button Validation

const registerBtn =
    document.getElementById("register-btn");

function validateRegisterForm() {

    if (
        !password1 ||
        !password2 ||
        !registerBtn
    ) {
        return;
    }

    const emailField = document.querySelector(
        '#register-form input[type="email"]'
    );

    const emailRegex =
        /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    const emailValid =
        emailField &&
        emailRegex.test(emailField.value);

    const passwordValid =
        password1.value.length >= 8;

    const passwordsMatch =
        password1.value === password2.value &&
        password2.value.length > 0;

    registerBtn.disabled = !(
        emailValid &&
        passwordValid &&
        passwordsMatch
    );
}

if (password1)
    password1.addEventListener(
        "input",
        validateRegisterForm
    );

if (password2)
    password2.addEventListener(
        "input",
        validateRegisterForm
    );

const registerEmailField =
    document.querySelector(
        '#register-form input[type="email"]'
    );

if (registerEmailField)
    registerEmailField.addEventListener(
        "input",
        validateRegisterForm
    );


    // Show / Hide Password

document
    .querySelectorAll(".toggle-password")
    .forEach(toggle => {

        toggle.addEventListener(
            "click",
            function () {

                // Registration Form Password Fields
                const password1 =
                    document.getElementById("password1");

                const password2 =
                    document.getElementById("password2");

                // Login Form Password Field
                const loginPassword =
                    document.getElementById("login-password");

                // Registration Form Logic
                if (
                    password1 &&
                    password2 &&
                    this.closest("#register-form")
                ) {

                    const show =
                        password1.type === "password";

                    password1.type =
                        show ? "text" : "password";

                    password2.type =
                        show ? "text" : "password";

                    document
                        .querySelectorAll(
                            "#register-form .toggle-password"
                        )
                        .forEach(icon => {

                            icon.textContent =
                                show ? "🙈" : "👁";
                        });
                }

                // Login Form Logic
                else if (
                    loginPassword &&
                    this.closest("#login-form")
                ) {

                    const show =
                        loginPassword.type === "password";

                    loginPassword.type =
                        show ? "text" : "password";

                    this.textContent =
                        show ? "🙈" : "👁";
                }
            }
        );
    });