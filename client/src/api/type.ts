// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import type { BlobSchema } from '@/json-schema';

type BaseResponse = {
  code: number;
  err?: string;
};

export type BlobResponse = BaseResponse & { blob?: BlobSchema };

export type BlobsResponse = BaseResponse & { blobs: BlobSchema[] };

export type BoolResponse = BaseResponse & { ok: boolean };

export type TextResponse = BaseResponse & { text?: string };
