// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

const { MODE, VITE_API_ORIGIN } = import.meta.env;

const API_ORIGIN = MODE === 'development' ? '/api' : VITE_API_ORIGIN;
const TOK_PREFIX = `${API_ORIGIN}/token`;
const USR_PREFIX = `${VITE_API_ORIGIN}/user`;

export const tokenUrls = {
  issue: `${TOK_PREFIX}/issue`,
  refresh: `${TOK_PREFIX}/refresh`,
  revoke: `${TOK_PREFIX}/revoke`,
};

export const userUrls = {
  authorize: `${USR_PREFIX}/authorize`,
  login: `${USR_PREFIX}/login`,
  register: `${USR_PREFIX}/register`,
};

export const routes = {
  home: {
    children: {
      callback: {
        root: '/callback',
        children: {
          authorize: { root: '/authorize', children: {} },
          login: { root: '/login', children: {} },
          register: { root: '/register', children: {} },
        },
      },
    },
    root: '/home',
  },
  main: {
    children: {},
    root: '/main',
  },
};

export const AUTHORIZE_CALLBACK_URL =
  `${window.location.origin}` +
  `${routes.home.root}` +
  `${routes.home.children.callback.root}` +
  `${routes.home.children.callback.children.authorize.root}`;

export const LOGIN_CALLBACK_URL =
  `${window.location.origin}` +
  `${routes.home.root}` +
  `${routes.home.children.callback.root}` +
  `${routes.home.children.callback.children.login.root}`;

export const REGISTER_CALLBACK_URL =
  `${window.location.origin}` +
  `${routes.home.root}` +
  `${routes.home.children.callback.root}` +
  `${routes.home.children.callback.children.register.root}`;
