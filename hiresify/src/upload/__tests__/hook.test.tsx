// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { act, renderHook } from '@testing-library/react';
import type { ReactNode } from 'react';

import * as api from '../api';
import { useUpload } from '../hook';
import UploadQueueProvider from '../provider';

describe('UseUpload hook', () => {
  const partSize = 1024;
  const byte = new Uint8Array(4 * partSize);
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

  it('fails to initialize the file upload', async () => {
    // Given
    vi.spyOn(api, 'create').mockRejectedValueOnce(
      new Error('Network error or aborted.')
    );

    const { result } = renderHook(() => useUpload({ file, partSize }), {
      wrapper,
    });

    const { start } = result.current;

    // When
    await act(async () => await start());
    await new Promise((resolve) => setTimeout(resolve, 0));

    // Then
    const { degree, status } = result.current;

    expect(degree).toBe(0);
    expect(status).toBe('failed');
  });

  it('uploads all file chunks successfully', async () => {
    // Given
    const { result } = renderHook(() => useUpload({ file, partSize }), {
      wrapper,
    });

    const { start } = result.current;

    // When
    await act(async () => await start());
    await new Promise((resolve) => setTimeout(resolve, 0));

    // Then
    const { degree, status } = result.current;

    expect(degree).toBe(100);
    expect(status).toBe('passed');
  });

  it('uploads all file chunks with some failed', async () => {
    // Given
    vi.spyOn(api, 'upload')
      .mockRejectedValueOnce(new Error('Network error or aborted.'))
      .mockResolvedValue(new Response(null, { status: 200 }));

    const { result } = renderHook(() => useUpload({ file, partSize }), {
      wrapper,
    });

    const { start } = result.current;

    // When
    await act(async () => await start());
    await new Promise((resolve) => setTimeout(resolve, 0));

    // Then
    const { degree, status } = result.current;

    expect(degree).toBe(75);
    expect(status).toBe('failed');
  });

  it('fails to finish the file upload', async () => {
    // Given
    vi.spyOn(api, 'finish').mockRejectedValueOnce(
      new Error('Network error or aborted.')
    );

    const { result } = renderHook(() => useUpload({ file, partSize }), {
      wrapper,
    });

    const { start } = result.current;

    // When
    await act(async () => await start());
    await new Promise((resolve) => setTimeout(resolve, 0));

    // Then
    const { degree, status } = result.current;

    expect(degree).toBe(100);
    expect(status).toBe('failed');
  });

  it('retries when initialization failed', async () => {
    // Given
    vi.spyOn(api, 'create')
      .mockRejectedValueOnce(new Error('Network error or aborted.'))
      .mockResolvedValueOnce(new Response(`upload-id`, { status: 201 }));

    const { result } = renderHook(() => useUpload({ file, partSize }), {
      wrapper,
    });

    const { retry, start } = result.current;

    await act(async () => await start());

    // When
    await act(async () => await retry());

    // Then
    const { degree, status } = result.current;

    expect(degree).toBe(100);
    expect(status).toBe('passed');
  });

  it('retries when some chunk uploads failed', async () => {
    // Given
    vi.spyOn(api, 'upload')
      .mockRejectedValueOnce(new Error('Network error or aborted.'))
      .mockRejectedValueOnce(new Error('Network error or aborted.'))
      .mockResolvedValue(new Response(null, { status: 200 }));

    const { result } = renderHook(() => useUpload({ file, partSize }), {
      wrapper,
    });

    const { retry, start } = result.current;

    await act(async () => await start());
    await new Promise((resolve) => setTimeout(resolve, 0));

    // When
    await act(async () => await retry());
    await new Promise((resolve) => setTimeout(resolve, 0));

    // Then
    const { degree, status } = result.current;

    expect(degree).toBe(100);
    expect(status).toBe('passed');
  });

  it('retries when failed to finish the upload', async () => {
    // Given
    vi.spyOn(api, 'finish').mockRejectedValueOnce(
      new Error('Network error or aborted.')
    );

    const { result } = renderHook(() => useUpload({ file, partSize }), {
      wrapper,
    });

    const { retry, start } = result.current;

    await act(async () => await start());
    await new Promise((resolve) => setTimeout(resolve, 0));

    // When
    await act(async () => await retry());

    // Then
    const { degree, status } = result.current;

    expect(degree).toBe(100);
    expect(status).toBe('passed');
  });
});
