// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

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
