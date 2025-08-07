// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import server from '@/testing/server';
import { blobUrls } from '@/urls';

import { cancel, create, finish, upload } from '../blob';

describe('Multipart Upload APIs', () => {
  const calledEndpoints: string[] = [];

  const byte = new Uint8Array(4096);
  const file = new File([byte], 'blob.bin', {
    type: 'application/octet-stream',
  });

  beforeAll(() => {
    server.listen();

    server.events.on('request:start', ({ request }) =>
      calledEndpoints.push(request.url)
    );
  });

  beforeEach(() => {
    server.resetHandlers();

    calledEndpoints.length = 0;
  });

  afterAll(() => {
    server.close();
  });

  it('creates the multipart upload', async () => {
    // Given
    const emptyFile = new File([], 'blob.bin', {
      type: 'application/octet-stream',
    });

    // When/Then
    await expect(create({ file: emptyFile })).rejects.toThrow(
      'File is too small to upload.'
    );

    expect(calledEndpoints).toEqual([]);

    // When
    const response = await create({ file });

    // Then
    expect(calledEndpoints).toEqual([blobUrls.upload]);
    expect(response.status).toBe(201);
  });

  it('uploads file chunks that is abortable', async () => {
    // Given
    const chunk = file;
    const index = 1;
    const uploadId = 'upload-id';

    const controller = new AbortController();
    controller.abort();

    const expectedEndpoint = `${blobUrls.upload}/${index}`;

    // When/Then
    await expect(
      upload({ chunk, index, uploadId, controller })
    ).rejects.toThrow('Request aborted.');

    expect(calledEndpoints).toEqual([expectedEndpoint]);

    // When
    const response = await upload({
      chunk,
      index,
      uploadId,
      controller: new AbortController(),
    });

    // Then
    expect(calledEndpoints).toEqual([expectedEndpoint, expectedEndpoint]);
    expect(response.status).toBe(200);
  });

  it('cancels the file upload this time', async () => {
    // Given
    const uploadId = 'upload-id';

    // When
    const response = await cancel({ uploadId });

    // Then
    expect(calledEndpoints).toEqual([
      `${blobUrls.upload}?upload_id=${uploadId}`,
    ]);
    expect(response.status).toBe(204);
  });

  it('finishes the file upload', async () => {
    // Given
    const fileName = 'image.png';
    const uploadId = 'upload-id';

    // When
    const response = await finish({ fileName, uploadId });

    // Then
    expect(calledEndpoints).toEqual([blobUrls.upload]);
    expect(response.status).toBe(200);
  });
});
