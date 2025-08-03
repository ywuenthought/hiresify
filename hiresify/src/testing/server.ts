// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';

import { blobUrls, tokenUrls } from '@/urls';

const handlers = [
  http.post(tokenUrls.revoke, () => {
    return new HttpResponse(null, { status: 204 });
  }),
  http.post(blobUrls.upload, () => {
    return new HttpResponse('upload-id', { status: 201 });
  }),
  http.patch(new RegExp(`^${blobUrls.upload}/[1-9]\\d*$`), () => {
    return new HttpResponse(null, { status: 200 });
  }),
  http.delete(blobUrls.upload, () => {
    return new HttpResponse(null, { status: 204 });
  }),
  http.put(blobUrls.upload, async () => {
    return HttpResponse.json(null, { status: 200 });
  }),
];

export default setupServer(...handlers);
