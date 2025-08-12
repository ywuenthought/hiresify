// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { bindActionCreators } from '@reduxjs/toolkit';
import { useCallback, useContext, useMemo, useRef, useState } from 'react';

import * as api from '@/api/blob';
import { useAppDispatch } from '@/app/hooks';
import type { BackendBlob } from '@/backend-type';
import { insertPersistedBlob, removeInTransitBlob } from '@/feature/blob/slice';
import { cancelThunk, finishThunk } from '@/feature/blob/thunk';
import { defer } from '@/util';

import { UploadQueueContext } from './queue';
import UploadMemoryStore from './store';
import type { SimpleAsyncThunk, UploadPart, UploadStatus } from './type';

const buildActionCreators = (args: { name: string; uid: string }) => {
  const { name, uid } = args;

  return {
    cancel: (args: { uploadId: string }) => {
      const { uploadId } = args;
      return cancelThunk({ blobUid: uid, uploadId });
    },
    finish: (args: { uploadId: string }) => {
      const { uploadId } = args;
      return finishThunk({ blobUid: uid, fileName: name, uploadId });
    },
    insertBlob: (args: { blob: BackendBlob }) => insertPersistedBlob(args),
    removeBlob: () => removeInTransitBlob({ uid }),
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
  degree: number;
  status: UploadStatus;
  abort: SimpleAsyncThunk;
  pause: SimpleAsyncThunk;
  retry: SimpleAsyncThunk;
  start: SimpleAsyncThunk;
};

export function useUpload(args: {
  blob: File;
  uid: string;
  partSize: number;
}): UseUploadReturnType {
  const { blob, uid, partSize } = args;
  const { name } = blob;

  const queue = useUploadQueue();
  const store = useRef<UploadMemoryStore>(new UploadMemoryStore()).current;

  const uploadIdRef = useRef<string>('');
  const controllers = useRef<AbortController[]>([]).current;

  const [degree, setDegree] = useState<number>(0);
  const [status, setStatus] = useState<UploadStatus>('active');

  const dispatch = useAppDispatch();
  const actions = useMemo(
    () => bindActionCreators(buildActionCreators({ name, uid }), dispatch),
    [name, uid, dispatch]
  );

  const factory = useCallback(
    (args: { controller: AbortController; part: UploadPart }) => {
      const { controller, part } = args;
      const { chunk, index } = part;

      const uploadId = uploadIdRef.current;

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
        setDegree((doneSize / blob.size) * 100);

        if (!store.getAllClear()) {
          return;
        }

        // Clear abort controllers.
        controllers.length = 0;

        if (doneSize !== blob.size) {
          return setStatus('failed');
        }

        actions.finish({ uploadId });
      };
    },
    [actions, controllers, blob, store]
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

        const job = factory({ controller, part });
        queue.enqueue({ job });
        await defer();
      }
    };

    if (uploadIdRef.current) {
      setStatus('active');
      await enqueueJobs();
    } else {
      try {
        const { text: uploadId } = await api.create({ blob });

        if (!uploadId) {
          return setStatus('failed');
        }

        uploadIdRef.current = uploadId;
        await store.init({ blob, partSize });

        setStatus('active');
        await enqueueJobs();
      } catch {
        setStatus('failed');
      }
    }
  }, [controllers, blob, partSize, queue, store, factory]);

  const pause = useCallback(async () => {
    while (controllers.length > 0) {
      controllers.pop()?.abort();
      await defer();
    }

    await store.pause();
    setStatus('paused');
  }, [controllers, store]);

  const retry = useCallback(async () => {
    if (store.getDoneSize() < blob.size) {
      await store.retry();
      await start();
    } else {
      // Clear abort controllers.
      controllers.length = 0;
      actions.finish({ uploadId: uploadIdRef.current });
    }
  }, [actions, controllers, blob, store, start]);

  const abort = useCallback(async () => {
    await pause();
    const uploadId = uploadIdRef.current;

    if (!uploadId) {
      return;
    }

    actions.cancel({ uploadId });
  }, [actions, pause]);

  return {
    degree,
    status,
    abort,
    pause,
    retry,
    start,
  };
}
