// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { blobUrls } from '@/urls';

import type {
  BlobResponse,
  BlobsResponse,
  BoolResponse,
  TextResponse,
} from './type';
import {
  buildBlobResponse,
  buildBlobsResponse,
  buildBoolResponse,
  buildTextResponse,
} from './util';

export async function cancel(args: {
  uploadId: string;
}): Promise<BoolResponse> {
  const { uploadId } = args;
  const url = `${blobUrls.upload}?upload_id=${encodeURIComponent(uploadId)}`;

  try {
    const response = await fetch(url, {
      method: 'DELETE',
      credentials: 'include',
    });
    return await buildBoolResponse({ response });
  } catch {
    throw new Error('Network crashed.');
  }
}

export async function create(args: { blob: File }): Promise<TextResponse> {
  const { blob } = args;
  if (blob.size < 4096) {
    throw new Error('File is too small to upload.');
  }

  const form = new FormData();
  form.append('file', blob);

  try {
    const response = await fetch(blobUrls.upload, {
      method: 'POST',
      body: form,
      credentials: 'include',
    });
    return await buildTextResponse({ response });
  } catch {
    throw new Error('Network crashed.');
  }
}

export async function finish(args: {
  fileName: string;
  uploadId: string;
}): Promise<BlobResponse> {
  const { fileName, uploadId } = args;

  const form = new FormData();
  form.append('file_name', fileName);
  form.append('upload_id', uploadId);

  try {
    const response = await fetch(blobUrls.upload, {
      method: 'PUT',
      body: form,
      credentials: 'include',
    });
    return await buildBlobResponse({ response });
  } catch {
    throw new Error('Network crashed.');
  }
}

export async function gather(): Promise<BlobsResponse> {
  try {
    const response = await fetch(blobUrls.fetch, {
      method: 'GET',
      credentials: 'include',
    });
    return await buildBlobsResponse({ response });
  } catch {
    throw new Error('Network crashed.');
  }
}

export async function remove(args: { blobUid: string }): Promise<BoolResponse> {
  const { blobUid } = args;

  try {
    const response = await fetch(`${blobUrls.delete}?blob_uid=${blobUid}`, {
      method: 'DELETE',
      credentials: 'include',
    });
    return await buildBoolResponse({ response });
  } catch {
    throw new Error('Network crashed.');
  }
}

export async function upload(args: {
  chunk: Blob;
  index: number;
  uploadId: string;
  controller: AbortController;
}): Promise<BoolResponse> {
  const { chunk, index, uploadId, controller } = args;

  const form = new FormData();
  form.append('file', chunk);
  form.append('upload_id', uploadId);

  try {
    const response = await fetch(`${blobUrls.upload}/${index}`, {
      method: 'PATCH',
      body: form,
      credentials: 'include',
      signal: controller.signal,
    });
    return await buildBoolResponse({ response });
  } catch (error) {
    throw new Error(
      error instanceof DOMException && error.name === 'AbortError'
        ? 'Request aborted.'
        : 'Network crashed.'
    );
  }
}
