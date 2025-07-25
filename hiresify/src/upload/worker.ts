// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import type { BackendBlob } from '@/backend-type';
import { blobUrls } from '@/urls';

import type { PartMeta } from './type';

export class UploadWorker {
  // A controller that can abort an ongoing upload.
  private controller: AbortController | null = null;

  public abort() {
    if (!this.controller) {
      return;
    }

    this.controller.abort();
  }

  public async cancel(args: { uploadId: string }): Promise<void> {
    const { uploadId } = args;
    const url = `${blobUrls.upload}?upload_id=${encodeURIComponent(uploadId)}`;

    try {
      const response = await fetch(url, {
        method: 'DELETE',
        credentials: 'include',
      });

      if (!response.ok) {
        throw new Error('Failed to cancel the upload.');
      }
    } catch {
      throw new Error('Network error or aborted.');
    }
  }

  public async finish(args: {
    fileName: string;
    uploadId: string;
  }): Promise<BackendBlob> {
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

      if (response.ok) {
        const data = await response.json();
        return {
          uid: data.uid,
          fileName: data.file_name,
          mimeType: data.mime_type,
          createdAt: new Date(data.created_at),
          validThru: new Date(data.valid_thru),
        };
      } else {
        throw new Error('Failed to finish the upload.');
      }
    } catch {
      throw new Error('Network error or aborted.');
    }
  }

  public async start(args: { file: File }): Promise<string> {
    const { file } = args;
    if (file.size < 4096) {
      throw new Error('File too small to upload.');
    }

    const form = new FormData();
    form.append('file', file);

    try {
      const response = await fetch(blobUrls.uploadInit, {
        method: 'POST',
        body: form,
        credentials: 'include',
      });

      if (response.ok) {
        return (await response.json()) as string;
      } else {
        throw new Error('Failed to start an upload.');
      }
    } catch {
      throw new Error('Network error or aborted.');
    }
  }

  public async upload(args: {
    file: File;
    partMeta: PartMeta;
    uploadId: string;
  }): Promise<void> {
    const { file, partMeta, uploadId } = args;

    const form = new FormData();
    form.append('file', file.slice(...partMeta.bound));
    form.append('part_index', String(partMeta.index));
    form.append('upload_id', uploadId);

    // Reset the controller in case it was used.
    this.controller = new AbortController();

    try {
      const response = await fetch(blobUrls.upload, {
        method: 'POST',
        body: form,
        credentials: 'include',
        signal: this.controller.signal,
      });

      if (!response.ok) {
        throw new Error(`Failed to upload ${uploadId}:${partMeta.index}.`);
      }
    } catch {
      throw new Error('Network error or aborted.');
    }
  }
}
