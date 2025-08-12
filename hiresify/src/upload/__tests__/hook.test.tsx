// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { act, renderHook } from '@testing-library/react';
import type { ReactNode } from 'react';
import { Provider } from 'react-redux';

import * as api from '@/api/blob';
import { makeStore } from '@/app/store';
import {
  insertInTransitBlob,
  removeInTransitBlob,
  selectOneInTransitBlob,
  selectOnePersistedBlob,
} from '@/feature/blob/slice';
import {
  getTestBackendBlob,
  getTestFrontendBlob,
  getTestJSFile,
} from '@/testing/blob';

import { useUpload } from '../hook';
import UploadQueueProvider from '../provider';

describe('UseUpload hook', () => {
  const partSize = 1024;
  const jsBlob = getTestJSFile({ partNums: 4, partSize });
  const blob = getTestFrontendBlob();
  const { uid: blobUid } = blob;

  const store = makeStore();
  const wrapper = (args: { children: ReactNode }) => {
    const { children } = args;

    return (
      <Provider store={store}>
        <UploadQueueProvider>{children}</UploadQueueProvider>
      </Provider>
    );
  };

  beforeEach(() => {
    store.dispatch(insertInTransitBlob({ blob }));

    vi.spyOn(api, 'create').mockImplementation(async () => {
      return { text: 'upload-id', code: 201 };
    });

    vi.spyOn(api, 'upload').mockImplementation(async () => {
      return { ok: true, code: 200 };
    });

    vi.spyOn(api, 'finish').mockImplementation(async () => {
      return { blob: getTestBackendBlob(), code: 200 };
    });
  });

  afterEach(() => {
    store.dispatch(removeInTransitBlob({ uid: blobUid }));
    vi.restoreAllMocks();
  });

  it('fails to initialize the file upload', async () => {
    // Given
    vi.spyOn(api, 'create').mockRejectedValueOnce(
      new Error('Network error or aborted.')
    );

    const { result } = renderHook(
      () => useUpload({ jsBlob, blobUid, partSize }),
      { wrapper }
    );

    const { start } = result.current;

    // When
    await act(async () => await start());
    await new Promise((resolve) => setTimeout(resolve, 0));

    // Then
    const { progress, status } = selectOneInTransitBlob(
      store.getState(),
      blobUid
    );

    expect(progress).toBe(0);
    expect(status).toBe('failed');
  });

  it('uploads all file chunks successfully', async () => {
    // Given
    const { result } = renderHook(
      () => useUpload({ jsBlob, blobUid, partSize }),
      { wrapper }
    );

    const { start } = result.current;

    // When
    await act(async () => await start());
    await new Promise((resolve) => setTimeout(resolve, 0));

    // Then
    const state = store.getState();
    const inTransitBlob = selectOneInTransitBlob(state, blobUid);
    const persistedBlob = selectOnePersistedBlob(state, 'blob-uid');

    expect(inTransitBlob).toBeUndefined();
    expect(persistedBlob).not.toBeUndefined();
  });

  it('uploads all file chunks with some failed', async () => {
    // Given
    vi.spyOn(api, 'upload')
      .mockRejectedValueOnce(new Error('Network error or aborted.'))
      .mockResolvedValue({ ok: true, code: 200 });

    const { result } = renderHook(
      () => useUpload({ jsBlob, blobUid, partSize }),
      { wrapper }
    );

    const { start } = result.current;

    // When
    await act(async () => await start());
    await new Promise((resolve) => setTimeout(resolve, 0));

    // Then
    const { progress, status } = selectOneInTransitBlob(
      store.getState(),
      blobUid
    );

    expect(progress).toBe(75);
    expect(status).toBe('failed');
  });

  it('fails to finish the file upload', async () => {
    // Given
    vi.spyOn(api, 'finish').mockRejectedValueOnce(
      new Error('Network error or aborted.')
    );

    const { result } = renderHook(
      () => useUpload({ jsBlob, blobUid, partSize }),
      { wrapper }
    );

    const { start } = result.current;

    // When
    await act(async () => await start());
    await new Promise((resolve) => setTimeout(resolve, 0));

    // Then
    const { progress, status } = selectOneInTransitBlob(
      store.getState(),
      blobUid
    );

    expect(progress).toBe(100);
    expect(status).toBe('failed');
  });

  it('retries when initialization failed', async () => {
    // Given
    vi.spyOn(api, 'create')
      .mockRejectedValueOnce(new Error('Network error or aborted.'))
      .mockResolvedValueOnce({ text: 'upload-id', code: 201 });

    const { result } = renderHook(
      () => useUpload({ jsBlob, blobUid, partSize }),
      { wrapper }
    );

    const { retry, start } = result.current;

    await act(async () => await start());

    // When
    await act(async () => await retry());

    // Then
    const state = store.getState();
    const inTransitBlob = selectOneInTransitBlob(state, blobUid);
    const persistedBlob = selectOnePersistedBlob(state, 'blob-uid');

    expect(inTransitBlob).toBeUndefined();
    expect(persistedBlob).not.toBeUndefined();
  });

  it('retries when some chunk uploads failed', async () => {
    // Given
    vi.spyOn(api, 'upload')
      .mockRejectedValueOnce(new Error('Network error or aborted.'))
      .mockRejectedValueOnce(new Error('Network error or aborted.'))
      .mockResolvedValue({ ok: true, code: 200 });

    const { result } = renderHook(
      () => useUpload({ jsBlob, blobUid, partSize }),
      { wrapper }
    );

    const { retry, start } = result.current;

    await act(async () => await start());
    await new Promise((resolve) => setTimeout(resolve, 0));

    // When
    await act(async () => await retry());
    await new Promise((resolve) => setTimeout(resolve, 0));

    // Then
    const state = store.getState();
    const inTransitBlob = selectOneInTransitBlob(state, blobUid);
    const persistedBlob = selectOnePersistedBlob(state, 'blob-uid');

    expect(inTransitBlob).toBeUndefined();
    expect(persistedBlob).not.toBeUndefined();
  });

  it('retries when failed to finish the upload', async () => {
    // Given
    vi.spyOn(api, 'finish').mockRejectedValueOnce(
      new Error('Network error or aborted.')
    );

    const { result } = renderHook(
      () => useUpload({ jsBlob, blobUid, partSize }),
      { wrapper }
    );

    const { retry, start } = result.current;

    await act(async () => await start());
    await new Promise((resolve) => setTimeout(resolve, 0));

    // When
    await act(async () => await retry());

    // Then
    const state = store.getState();
    const inTransitBlob = selectOneInTransitBlob(state, blobUid);
    const persistedBlob = selectOnePersistedBlob(state, 'blob-uid');

    expect(inTransitBlob).toBeUndefined();
    expect(persistedBlob).not.toBeUndefined();
  });
});
