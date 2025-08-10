// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';

import type { BlobSchema } from '@/json-schema';
import { blobUrls, tokenUrls } from '@/urls';

const handlers = [
  http.post(tokenUrls.revoke, () => {
    return new HttpResponse(null, { status: 204 });
  }),
  http.post(blobUrls.upload, () => {
    return HttpResponse.json('upload-id', { status: 201 });
  }),
  http.patch(new RegExp(`^${blobUrls.upload}/[1-9]\\d*$`), () => {
    return new HttpResponse(null, { status: 200 });
  }),
  http.delete(blobUrls.upload, () => {
    return new HttpResponse(null, { status: 204 });
  }),
  http.put(blobUrls.upload, async () => {
    const createdAtDate = new Date();
    const validThruDate = new Date(createdAtDate.getTime() + 1000);

    const schema: BlobSchema = {
      uid: 'blob-uid',
      fileName: 'image.png',
      mimeType: 'image/png',
      createdAt: createdAtDate.toISOString(),
      validThru: validThruDate.toISOString(),
    };

    return HttpResponse.json(schema, { status: 200 });
  }),
];

export default setupServer(...handlers);
