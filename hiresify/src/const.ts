// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

const {
  VITE_API_SCHEME: API_SCHEME,
  VITE_API_HOST: API_HOST,
  VITE_API_PORT: API_PORT,
} = import.meta.env;

const API_PREFIX = `${API_SCHEME}://${API_HOST}:${API_PORT}`;
const TOKEN_PREFIX = `${API_PREFIX}/token`;
const USER_PREFIX = `${API_PREFIX}/user`;

export const tokenUrls = {
  issue: `${TOKEN_PREFIX}/issue`,
  revoke: `${TOKEN_PREFIX}/revoke`,
};

export const userUrls = {
  authorize: `${USER_PREFIX}/authorize`,
  register: `${USER_PREFIX}/register`,
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
