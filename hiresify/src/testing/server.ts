// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';

import { tokenUrls } from '@/const';

const handlers = [
  http.post(tokenUrls.revoke, () => {
    return new HttpResponse(null, { status: 204 });
  }),
];

export default setupServer(...handlers);
