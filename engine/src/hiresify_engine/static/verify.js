// Copyright (c) 2025 Yifeng Wu
// All rights reserved.
// This file is not licensed for use, modification, or distribution without
// explicit written permission from the copyright holder.

USERNAME_REGEX = /^[a-zA-Z][a-zA-Z0-9_]*$/;
PASSWORD_REGEX = /^[A-Za-z\d!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]+$/;

const usernameInput = document.getElementById('username');
const passwordInput = document.getElementById('password');
const usernameError = document.getElementById('usernameError');
const passwordError = document.getElementById('passwordError');

function validateAndUpdateUI() {
  const username = usernameInput.value;
  const password = passwordInput.value;

  const isUsernameValid = USERNAME_REGEX.test(usernameInput.value);
  const isPasswordValid = PASSWORD_REGEX.test(passwordInput.value);

  usernameError.classList.toggle('hidden', isUsernameValid || !username);
  passwordError.classList.toggle('hidden', isPasswordValid || !password);
}

usernameInput.addEventListener('keyup', validateAndUpdateUI);
passwordInput.addEventListener('keyup', validateAndUpdateUI);
