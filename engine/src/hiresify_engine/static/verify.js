// Copyright (c) 2025 Yifeng Wu
// All rights reserved.
// This file is not licensed for use, modification, or distribution without
// explicit written permission from the copyright holder.

USERNAME_REGEX = /^[a-zA-Z][a-zA-Z0-9_]*$/;
PASSWORD_REGEX = /^[A-Za-z\d!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]+$/;
DEBOUNCE_DELAY = 500

const usernameInput = document.getElementById('username');
const passwordInput = document.getElementById('password');
const usernameError = document.getElementById('usernameError');
const passwordError = document.getElementById('passwordError');
const usernameExist = document.getElementById('usernameExist');

let timeout = null;

function validateAndUpdateUI() {
  clearTimeout(timeout);

  const username = usernameInput.value;
  const password = passwordInput.value;

  const isUsernameValid = USERNAME_REGEX.test(username);
  const isPasswordValid = PASSWORD_REGEX.test(password);

  usernameError.classList.toggle('hidden', isUsernameValid || !username);
  passwordError.classList.toggle('hidden', isPasswordValid || !password);
  usernameExist.classList.toggle('hidden', !isUsernameValid);

  if (isUsernameValid) {
    timeout = setTimeout(() => {
      fetch(`/user/check?username=${encodeURIComponent(username)}`)
        .then(res => {
          if (res.status === 200) {
            usernameExist.textContent = '✅ Username usable.';
            usernameExist.classList.remove('text-red-500');
            usernameExist.classList.add('text-green-500');
          } else if (res.status === 409) {
            usernameExist.textContent = '❌ Username exists.';
            usernameExist.classList.remove('text-green-500');
            usernameExist.classList.add('text-red-500');
          } else {
            usernameExist.textContent = '⚠️ Try again later.';
            usernameExist.classList.remove('text-green-500');
            usernameExist.classList.add('text-red-500');
          }
        });
    }, DEBOUNCE_DELAY);
  }
}

usernameInput.addEventListener('keyup', validateAndUpdateUI);
passwordInput.addEventListener('keyup', validateAndUpdateUI);
