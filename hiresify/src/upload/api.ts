// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { blobUrls } from '@/urls';

import type { UploadPart } from './type';

export async function cancel(args: { uploadId: string }): Promise<Response> {
  const { uploadId } = args;
  const url = `${blobUrls.upload}?upload_id=${encodeURIComponent(uploadId)}`;

  try {
    return await fetch(url, {
      method: 'DELETE',
      credentials: 'include',
    });
  } catch {
    throw new Error('Network crashed.');
  }
}

export async function create(args: { file: File }): Promise<Response> {
  const { file } = args;
  if (file.size < 4096) {
    throw new Error('File is too small to upload.');
  }

  const form = new FormData();
  form.append('file', file);

  try {
    return await fetch(blobUrls.upload, {
      method: 'POST',
      body: form,
      credentials: 'include',
    });
  } catch {
    throw new Error('Network crashed.');
  }
}

export async function finish(args: {
  fileName: string;
  uploadId: string;
}): Promise<Response> {
  const { fileName, uploadId } = args;

  const form = new FormData();
  form.append('file_name', fileName);
  form.append('upload_id', uploadId);

  try {
    return await fetch(blobUrls.upload, {
      method: 'PUT',
      body: form,
      credentials: 'include',
    });
  } catch {
    throw new Error('Network crashed.');
  }
}

export async function upload(args: {
  part: UploadPart;
  uploadId: string;
  controller: AbortController;
}): Promise<Response> {
  const { part, uploadId, controller } = args;

  const form = new FormData();
  form.append('file', part.chunk);
  form.append('upload_id', uploadId);

  try {
    return await fetch(`${blobUrls.upload}/${part.index}`, {
      method: 'PATCH',
      body: form,
      credentials: 'include',
      signal: controller.signal,
    });
  } catch (error) {
    throw new Error(
      error instanceof DOMException && error.name === 'AbortError'
        ? 'Request aborted.'
        : 'Network crashed.'
    );
  }
}
