// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import UploadMemoryStore from '../store';
import type { PartMeta } from '../type';

describe('UploadMemoryStore', () => {
  it('gives next parts to upload', () => {
    // Given
    const store = new UploadMemoryStore({ fileSize: 1, partSize: 1 });

    // When
    const part = store.nextPart();

    // Then
    expect(part).not.toBeUndefined();
    expect(part).toEqual({ index: 1, start: 0, end: 1 });

    expect(store.resume()).toEqual(new Set([part]));
    expect(store.getComplete()).toBeFalsy();
    expect(store.getProgress()).toBe(0);

    // When/Then
    expect(store.nextPart()).toBeUndefined();
  });

  it('fails a file part upload', () => {
    // Given
    const store = new UploadMemoryStore({ fileSize: 1, partSize: 1 });

    // When
    const part = store.nextPart() as PartMeta;
    store.failPart({ part });

    expect(store.getComplete()).toBeTruthy();
    expect(store.getProgress()).toBe(0);

    // When/Then
    expect(store.retry()).toEqual(new Set([part]));
  });

  it('passes a file part upload', () => {
    // Given
    const store = new UploadMemoryStore({ fileSize: 1, partSize: 1 });

    // When
    const part = store.nextPart() as PartMeta;
    store.passPart({ part });

    // Then
    expect(store.getComplete()).toBeTruthy();
    expect(store.getProgress()).toBe(1);
  });
});
