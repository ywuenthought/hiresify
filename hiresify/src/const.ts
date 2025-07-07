// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

const { MODE, VITE_API_ORIGIN } = import.meta.env;

const API_ORIGIN = MODE === 'development' ? '/api' : VITE_API_ORIGIN;
const TOK_PREFIX = `${API_ORIGIN}/token`;
const USR_PREFIX = `${VITE_API_ORIGIN}/user`;

export const tokenUrls = {
  issue: `${TOK_PREFIX}/issue`,
  revoke: `${TOK_PREFIX}/revoke`,
};

export const userUrls = {
  authorize: `${USR_PREFIX}/authorize`,
  register: `${USR_PREFIX}/register`,
};

export const routes = {
  home: {
    children: {
      callback: { root: '/callback', children: {} },
    },
    root: '',
  },
  main: {
    children: {},
    root: '/main',
  },
};

export const CALLBACK_URL =
  `${window.location.origin}` +
  `${routes.home.root}` +
  `${routes.home.children.callback.root}`;
