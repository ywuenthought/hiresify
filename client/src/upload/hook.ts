// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { useCallback, useContext, useMemo, useRef } from 'react';

import * as api from '@/api/blob';
import { useAppDispatch } from '@/app/hooks';
import { updateInTransitBlob } from '@/feature/blob/slice';
import { cancelThunk, finishThunk } from '@/feature/blob/thunk';
import type { InTransitBlob } from '@/type';
import { defer } from '@/util';

import { UploadQueueContext } from './queue';
import UploadMemoryStore from './store';
import type { SimpleAsyncThunk, UploadPart } from './type';

const buildActionCreators = (args: { blobUid: string; fileName: string }) => {
  const { blobUid, fileName } = args;

  return {
    cancel: (args: { uploadId: string }) => {
      const { uploadId } = args;
      return cancelThunk({ blobUid, uploadId });
    },
    finish: (args: { uploadId: string }) => {
      const { uploadId } = args;
      return finishThunk({ blobUid, fileName, uploadId });
    },
    update: (changes: Partial<Omit<InTransitBlob, 'uid' | 'blob'>>) => {
      return updateInTransitBlob({ id: blobUid, changes });
    },
  };
};

export function useUploadQueue() {
  const context = useContext(UploadQueueContext);

  if (!context) {
    throw new Error('useUploadQueue must be used within a context.');
  }

  return context;
}

export type UseUploadReturnType = {
  abort: SimpleAsyncThunk;
  pause: SimpleAsyncThunk;
  retry: SimpleAsyncThunk;
  start: SimpleAsyncThunk;
};

export function useUpload(args: {
  jsBlob: File;
  blobUid: string;
  partSize: number;
}): UseUploadReturnType {
  const { jsBlob, blobUid, partSize } = args;
  const { name: fileName, size: blobSize } = jsBlob;

  const queue = useUploadQueue();
  const store = useRef<UploadMemoryStore>(new UploadMemoryStore()).current;

  const uploadIdRef = useRef<string>('');
  const controllers = useRef<AbortController[]>([]).current;

  const dispatch = useAppDispatch();
  const { cancel, finish, update } = useMemo(
    () => buildActionCreators({ fileName, blobUid }),
    [blobUid, fileName]
  );

  const jobFactory = useCallback(
    (args: { controller: AbortController; part: UploadPart }) => {
      const { controller, part } = args;
      const { chunk, index } = part;
      const { current: uploadId } = uploadIdRef;

      return async (): Promise<void> => {
        try {
          const { ok } = await api.upload({
            chunk,
            index,
            uploadId,
            controller,
          });

          if (ok) {
            store.passPart({ part });
          } else {
            store.failPart({ part });
          }
        } catch (error) {
          const { message } = error as Error;

          if (message === 'Request aborted.') {
            return;
          }

          store.failPart({ part });
        }

        const doneSize = store.getDoneSize();
        dispatch(update({ progress: (doneSize / blobSize) * 100 }));

        if (!store.getAllClear()) {
          return;
        }

        // Clear abort controllers.
        controllers.length = 0;

        if (doneSize !== blobSize) {
          dispatch(update({ status: 'failed' }));
          return;
        }

        await dispatch(finish({ uploadId }));
      };
    },
    [blobSize, controllers, store, dispatch, finish, update]
  );

  const start = useCallback(async () => {
    const enqueueJobs = async () => {
      while (true) {
        const part = store.nextPart();

        if (!part) {
          break;
        }

        const controller = new AbortController();
        controllers.push(controller);

        const job = jobFactory({ controller, part });
        queue.enqueue({ job });
        await defer();
      }
    };

    if (uploadIdRef.current) {
      dispatch(update({ status: 'active' }));
      await enqueueJobs();
    } else {
      try {
        const { text: uploadId } = await api.create({ jsBlob });

        if (!uploadId) {
          dispatch(update({ status: 'failed' }));
          return;
        }

        uploadIdRef.current = uploadId;
        await store.init({ jsBlob, partSize });

        dispatch(update({ status: 'active' }));
        await enqueueJobs();
      } catch {
        dispatch(update({ status: 'failed' }));
      }
    }
  }, [
    controllers,
    jsBlob,
    partSize,
    queue,
    store,
    dispatch,
    jobFactory,
    update,
  ]);

  const pause = useCallback(async () => {
    while (controllers.length > 0) {
      controllers.pop()?.abort();
      await defer();
    }

    await store.pause();
    dispatch(update({ status: 'paused' }));
  }, [controllers, store, dispatch, update]);

  const retry = useCallback(async () => {
    if (store.getDoneSize() < blobSize) {
      await store.retry();
      await start();
    } else {
      // Clear abort controllers.
      controllers.length = 0;

      const { current: uploadId } = uploadIdRef;
      await dispatch(finish({ uploadId }));
    }
  }, [blobSize, controllers, store, dispatch, finish, start]);

  const abort = useCallback(async () => {
    await pause();
    const { current: uploadId } = uploadIdRef;

    if (!uploadId) {
      return;
    }

    await dispatch(cancel({ uploadId }));
  }, [cancel, dispatch, pause]);

  return { abort, pause, retry, start };
}
