// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import UploadMemoryStore from '../store';
import type { UploadPart } from '../type';

describe('UploadMemoryStore', () => {
  const byte = new Uint8Array(1);
  const jsBlob = new File([byte], 'blob.bin', {
    type: 'application/octet-stream',
  });

  it('gives next parts to upload', async () => {
    // Given
    const store = new UploadMemoryStore();
    await store.init({ jsBlob, partSize: 1 });

    // When
    const part = store.nextPart();

    // Then
    expect(part).not.toBeUndefined();
    expect(part).toEqual({ index: 1, chunk: jsBlob.slice(0, 1) });
    expect(store.getDoneSize()).toBe(0);

    // When/Then
    expect(store.nextPart()).toBeUndefined();

    // When
    await store.pause();
    const partResumed = store.nextPart();

    // Then
    expect(partResumed).toEqual(part);
  });

  it('sets a part upload to be failed', async () => {
    // Given
    const store = new UploadMemoryStore();
    await store.init({ jsBlob, partSize: 1 });

    // When
    const part = store.nextPart() as UploadPart;
    store.failPart({ part });

    expect(store.getAllClear()).toBeTruthy();
    expect(store.getDoneSize()).toBe(0);

    // When
    await store.retry();
    const partRetried = store.nextPart();

    // Then
    expect(partRetried).toEqual(part);
  });

  it('sets a part upload to be passed', async () => {
    // Given
    const store = new UploadMemoryStore();
    await store.init({ jsBlob, partSize: 1 });

    // When
    const part = store.nextPart() as UploadPart;
    store.passPart({ part });

    // Then
    expect(store.getAllClear()).toBeTruthy();
    expect(store.getDoneSize()).toBe(1);
  });
});
