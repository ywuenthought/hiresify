// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { useCallback, useContext, useRef, useState } from 'react';

import * as api from '@/api/blob';
import { useAppDispatch } from '@/app/hooks';
import {
  insertPersistedImage,
  insertPersistedVideo,
  removeInTransitMedia,
} from '@/feature/blob/slice';
import { defer, isImage, isVideo } from '@/util';

import { UploadQueueContext } from './queue';
import UploadMemoryStore from './store';
import type { SimpleAsyncThunk, UploadPart, UploadStatus } from './type';

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
  file: File;
  partSize: number;
}): UseUploadReturnType {
  const { file, partSize } = args;

  const queue = useUploadQueue();
  const store = useRef<UploadMemoryStore>(new UploadMemoryStore()).current;

  const uploadIdRef = useRef<string>('');
  const controllers = useRef<AbortController[]>([]).current;

  const [degree, setDegree] = useState<number>(0);
  const [status, setStatus] = useState<UploadStatus>('active');

  const dispatch = useAppDispatch();

  const factory = useCallback(
    (args: { controller: AbortController; part: UploadPart }) => {
      const { controller, part } = args;
      const { chunk, index } = part;

      const fileName = file.name;
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
        setDegree((doneSize / file.size) * 100);

        if (!store.getAllClear()) {
          return;
        }

        // Clear abort controllers.
        controllers.length = 0;

        if (doneSize !== file.size) {
          return setStatus('failed');
        }

        try {
          const { blob } = await api.finish({ fileName, uploadId });

          if (blob) {
            if (isImage(blob)) {
              dispatch(insertPersistedImage({ blob }));
            }
            if (isVideo(blob)) {
              dispatch(insertPersistedVideo({ blob }));
            }

            const { uid } = blob;
            dispatch(removeInTransitMedia({ uid }));
          }

          setStatus(blob ? 'passed' : 'failed');
        } catch {
          setStatus('failed');
        }
      };
    },
    [controllers, file, store, dispatch]
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
        const { text: uploadId } = await api.create({ file });

        if (!uploadId) {
          return setStatus('failed');
        }

        uploadIdRef.current = uploadId;
        await store.init({ file, partSize });

        setStatus('active');
        await enqueueJobs();
      } catch {
        setStatus('failed');
      }
    }
  }, [controllers, file, partSize, queue, store, factory]);

  const pause = useCallback(async () => {
    while (controllers.length > 0) {
      controllers.pop()?.abort();
      await defer();
    }

    await store.pause();
    setStatus('paused');
  }, [controllers, store]);

  const retry = useCallback(async () => {
    if (store.getDoneSize() < file.size) {
      await store.retry();
      await start();
    } else {
      // Clear abort controllers.
      controllers.length = 0;

      try {
        const { blob } = await api.finish({
          fileName: file.name,
          uploadId: uploadIdRef.current,
        });

        if (blob) {
          if (isImage(blob)) {
            dispatch(insertPersistedImage({ blob }));
          }
          if (isVideo(blob)) {
            dispatch(insertPersistedVideo({ blob }));
          }

          const { uid } = blob;
          dispatch(removeInTransitMedia({ uid }));
        }

        setStatus(blob ? 'passed' : 'failed');
      } catch {
        setStatus('failed');
      }
    }
  }, [controllers, file, store, dispatch, start]);

  const abort = useCallback(async () => {
    await pause();
    const uploadId = uploadIdRef.current;

    if (!uploadId) {
      return;
    }

    await api.cancel({ uploadId });
  }, [pause]);

  return {
    degree,
    status,
    abort,
    pause,
    retry,
    start,
  };
}
