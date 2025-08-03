// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';

import type { BackendBlob } from '@/backend-type';
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
  http.put(blobUrls.upload, async ({ request }) => {
    const data = await request.formData();

    const createdAt = new Date(Date.now());
    const validThru = new Date(createdAt.getTime() + 1000);

    const blob: BackendBlob = {
      uid: 'blob-uid',
      fileName: data.get('file_name') as string,
      mimeType: 'image',
      createdAt: createdAt.toISOString(),
      validThru: validThru.toISOString(),
    };

    return HttpResponse.json(blob, { status: 200 });
  }),
];

export default setupServer(...handlers);
