// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { routes } from './routes';

const { MODE, VITE_API_ORIGIN } = import.meta.env;

const API_ORIGIN = MODE === 'development' ? '/api' : VITE_API_ORIGIN;

export const tokenUrls = {
  issue: `${API_ORIGIN}/token/issue`,
  refresh: `${API_ORIGIN}/token/refresh`,
  revoke: `${API_ORIGIN}/token/revoke`,
};

export const userUrls = {
  authorize: `${VITE_API_ORIGIN}/user/authorize`,
  login: `${VITE_API_ORIGIN}/user/login`,
  register: `${VITE_API_ORIGIN}/user/register`,
};

export const blobUrls = {
  upload: `${API_ORIGIN}/blob/upload`,
  uploadInit: `${API_ORIGIN}/blob/upload/init`,
};

export const callbackUrls = {
  authorize:
    `${window.location.origin}` +
    `${routes.home.root}` +
    `${routes.home.children.callback.root}` +
    `${routes.home.children.callback.children.authorize.root}`,
  login:
    `${window.location.origin}` +
    `${routes.home.root}` +
    `${routes.home.children.callback.root}` +
    `${routes.home.children.callback.children.login.root}`,
  register:
    `${window.location.origin}` +
    `${routes.home.root}` +
    `${routes.home.children.callback.root}` +
    `${routes.home.children.callback.children.register.root}`,
};
