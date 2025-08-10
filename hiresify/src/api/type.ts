// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import type { BackendBlob } from '@/backend-type';

type BaseResponse = {
  code: number;
  err?: string;
};

export type BlobResponse = BaseResponse & { blob?: BackendBlob };

export type BlobsResponse = BaseResponse & { blobs: BackendBlob[] };

export type BoolResponse = BaseResponse & { ok: boolean };

export type TextResponse = BaseResponse & { text?: string };
