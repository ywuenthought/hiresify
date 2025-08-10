// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { buildBlobBySchema } from '@/backend-type';
import type { BlobSchema } from '@/json-schema';
import { getDetail } from '@/util';

import type {
  BlobResponse,
  BlobsResponse,
  BoolResponse,
  TextResponse,
} from './type';

export async function buildBlobResponse(args: {
  response: Response;
}): Promise<BlobResponse> {
  const { response } = args;

  const blobResponse: BlobResponse = {
    code: response.status,
  };

  if (response.ok) {
    const schema: BlobSchema = await response.json();
    blobResponse.blob = buildBlobBySchema({ schema });
  } else {
    blobResponse.err = await getDetail(response);
  }

  return blobResponse;
}

export async function buildBlobsResponse(args: {
  response: Response;
}): Promise<BlobsResponse> {
  const { response } = args;

  const blobsResponse: BlobsResponse = {
    blobs: [],
    code: response.status,
  };

  if (response.ok) {
    const schemas: BlobSchema[] = await response.json();
    schemas.forEach((schema) =>
      blobsResponse.blobs.push(buildBlobBySchema({ schema }))
    );
  } else {
    blobsResponse.err = await getDetail(response);
  }

  return blobsResponse;
}

export async function buildBoolResponse(args: {
  response: Response;
}): Promise<BoolResponse> {
  const { response } = args;

  const boolResponse: BoolResponse = {
    ok: response.ok,
    code: response.status,
  };

  if (!response.ok) {
    boolResponse.err = await getDetail(response);
  }

  return boolResponse;
}

export async function buildTextResponse(args: {
  response: Response;
}): Promise<TextResponse> {
  const { response } = args;

  const textResponse: TextResponse = {
    code: response.status,
  };

  if (response.ok) {
    textResponse.text = await response.json();
  } else {
    textResponse.err = await getDetail(response);
  }

  return textResponse;
}
