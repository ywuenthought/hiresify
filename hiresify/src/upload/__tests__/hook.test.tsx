// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { act, renderHook } from '@testing-library/react';
import type { ReactNode } from 'react';

import * as api from '../api';
import { useUpload } from '../hook';
import UploadQueueProvider from '../provider';

describe('UseUpload hook', () => {
  const byte = new Uint8Array(4096);
  const file = new File([byte], 'blob.bin', {
    type: 'application/octet-stream',
  });

  const wrapper = (args: { children: ReactNode }) => {
    const { children } = args;
    return <UploadQueueProvider>{children}</UploadQueueProvider>;
  };

  beforeEach(() => {
    vi.spyOn(api, 'create').mockImplementation(async () => {
      return new Response(`upload-id`, { status: 201 });
    });

    vi.spyOn(api, 'upload').mockImplementation(async () => {
      return new Response(null, { status: 200 });
    });

    vi.spyOn(api, 'finish').mockImplementation(async () => {
      return new Response(null, { status: 200 });
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('creates the multipart upload', async () => {
    // Given
    const { result } = renderHook(() => useUpload({ file, partSize: 1024 }), {
      wrapper,
    });

    const { setup } = result.current;

    // When
    await setup();

    // Then
    const { complete, progress } = result.current;

    expect(complete).toBeFalsy();
    expect(progress).toBe(0);
  });

  it('uploads an intermediary file chunk', async () => {
    // Given
    const { result } = renderHook(() => useUpload({ file, partSize: 1024 }), {
      wrapper,
    });

    const { setup, start } = result.current;

    await setup();

    // When
    await act(async () => await start());
    await new Promise((resolve) => setTimeout(resolve, 0));

    // Then
    const { complete, progress } = result.current;

    expect(complete).toBeTruthy();
    expect(progress).toBe(100);
  });
});
