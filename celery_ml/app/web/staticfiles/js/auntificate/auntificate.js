const signUpButton = document.getElementById('signUp');
const signInButton = document.getElementById('signIn');
const authContainer = document.getElementById('authContainer');

signUpButton.addEventListener('click', () => {
    authContainer.classList.add("auth__container--right-panel-active");
});

signInButton.addEventListener('click', () => {
    authContainer.classList.remove("auth__container--right-panel-active");
});