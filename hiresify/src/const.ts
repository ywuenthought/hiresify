// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

const {
  VITE_BACKEND_SCHEME: SCHEME,
  VITE_BACKEND_HOST: HOST,
  VITE_BACKEND_PORT: PORT,
} = import.meta.env;

const backendPrefix = `${SCHEME}://${HOST}:${PORT}`;

const userPrefix = `${backendPrefix}/user`;

export const userUrls = {
  login: `${userPrefix}/login`,
  register: `${userPrefix}/register`,
};

export const routes = {
  AUTH: '/auth',
  HOME: '/',
};
