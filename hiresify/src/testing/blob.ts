// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import type { BlobSchema } from '@/json-schema';
import type { FrontendBlob } from '@/type';

export function getTestBackendBlob(args?: Partial<BlobSchema>): BlobSchema {
  const {
    uid = 'blob-uid',
    fileName = 'image.png',
    mimeType = 'image/png',
    createdAt = '2025-08-12T05:20:00.000Z',
    validThru = '2025-08-12T05:20:01.000Z',
  } = args ?? {};

  return { uid, fileName, mimeType, createdAt, validThru };
}

export function getTestFrontendBlob(
  args?: Partial<FrontendBlob>
): FrontendBlob {
  const { uid = 'blob-uid', progress = 0, status = 'active' } = args ?? {};

  return { uid, progress, status };
}

export function getTestJSFile(args?: {
  partNums?: number;
  partSize?: number;
}): File {
  const { partNums = 4, partSize = 1024 } = args ?? {};
  const byte = new Uint8Array(partNums * partSize);
  return new File([byte], 'blob.bin', {
    type: 'application/octet-stream',
  });
}
