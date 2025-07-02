// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

const {
  VITE_API_SCHEME: API_SCHEME,
  VITE_API_HOST: API_HOST,
  VITE_API_PORT: API_PORT,

  VITE_APP_SCHEME: APP_SCHEME,
  VITE_APP_HOST: APP_HOST,
  VITE_APP_PORT: APP_PORT,
} = import.meta.env;

const API_PREFIX = `${API_SCHEME}://${API_HOST}:${API_PORT}`;
const APP_PREFIX = `${APP_SCHEME}://${APP_HOST}:${APP_PORT}`;

const TOKEN_PREFIX = `${API_PREFIX}/token`;

export const tokenUrls = {
  issue: `${TOKEN_PREFIX}/issue`,
  revoke: `${TOKEN_PREFIX}/revoke`,
};

const USER_PREFIX = `${API_PREFIX}/user`;

export const userUrls = {
  authorize: `${USER_PREFIX}/authorize`,
  register: `${USER_PREFIX}/register`,
};

export const routes = {
  home: {
    children: {
      callback: { root: '/callback', children: {} },
    },
    root: '/',
  },
  main: {
    children: {},
    root: '/main',
  },
};

export const CALLBACK_URL =
  `${APP_PREFIX}/#` +
  `${routes.home.root}` +
  `${routes.home.children.callback.root}`;
