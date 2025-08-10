// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import type { BackendBlob } from '@/backend-type';

export function getTestBackendBlob(args?: Partial<BackendBlob>): BackendBlob {
  const {
    uid = 'blob-uid',
    fileName = 'image.png',
    mimeType = 'image/png',
    createdAt = new Date(),
    validThru = new Date(createdAt.getTime() + 1000),
  } = args ?? {};

  return { uid, fileName, mimeType, createdAt, validThru };
}
