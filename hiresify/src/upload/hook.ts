// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { useCallback, useContext, useMemo, useRef, useState } from 'react';

import { defer } from '@/util';

import * as api from './api';
import { UploadQueueContext } from './queue';
import UploadMemoryStore from './store';
import type { SimpleAsyncThunk, UploadPart } from './type';

export function useUploadQueue() {
  const context = useContext(UploadQueueContext);

  if (!context) {
    throw new Error('useUploadQueue must be used within a context.');
  }

  return context;
}

export function useUpload(args: { file: File; partSize: number }): {
  allClear: boolean;
  complete: boolean;
  progress: number;
  abort: SimpleAsyncThunk;
  pause: SimpleAsyncThunk;
  retry: SimpleAsyncThunk;
  setup: SimpleAsyncThunk;
  start: SimpleAsyncThunk;
} {
  const { file, partSize } = args;

  const queue = useUploadQueue();
  const store = useMemo(() => new UploadMemoryStore(), []);

  const uploadIdRef = useRef<string>('');
  const controllers: AbortController[] = useMemo(() => [], []);

  const [complete, setComplete] = useState<boolean>(false);
  const [allClear, setAllClear] = useState<boolean>(false);
  const [progress, setProgress] = useState<number>(0);

  const factory = useCallback(
    (args: { controller: AbortController; part: UploadPart }) => {
      const { controller, part } = args;

      const fileName = file.name;
      const uploadId = uploadIdRef.current;

      return async (): Promise<void> => {
        let response: Response;

        try {
          response = await api.upload({ part, uploadId, controller });
        } catch {
          return;
        }

        if (response.ok) {
          store.passPart({ part });

          const allClear = store.getAllClear();
          setAllClear(allClear);

          const doneSize = store.getDoneSize();
          setProgress((doneSize / file.size) * 100);

          if (allClear) {
            const error = new Error(`Failed to upload ${file.name}.`);

            if (doneSize !== file.size) {
              throw error;
            }

            let response: Response;

            try {
              response = await api.finish({ fileName, uploadId });
            } catch {
              throw error;
            }

            if (response.ok) {
              setComplete(true);
            } else {
              throw error;
            }
          }
        } else {
          store.failPart({ part });
        }
      };
    },
    [file, store]
  );

  const setup = useCallback(async () => {
    if (uploadIdRef.current) {
      return;
    }

    const response = await api.create({ file });

    if (!response.ok) {
      throw new Error(`Impossible to upload ${file.name}.`);
    }

    uploadIdRef.current = await response.text();
    store.init({ file, partSize });
  }, [file, partSize, store]);

  const start = useCallback(async () => {
    while (true) {
      const part = store.nextPart();

      if (!part) {
        break;
      }

      const controller = new AbortController();
      controllers.push(controller);

      const job = factory({ controller, part });
      queue.enqueue({ job });
      defer();
    }
  }, [controllers, queue, store, factory]);

  const pause = useCallback(async () => {
    while (controllers.length > 0) {
      controllers.pop()?.abort();
      defer();
    }

    await store.pause();
  }, [controllers, store]);

  const retry = useCallback(async () => {
    if (store.getDoneSize() < file.size) {
      await store.retry();
      await start();
    } else {
      if (complete) {
        return;
      }

      const response = await api.finish({
        fileName: file.name,
        uploadId: uploadIdRef.current,
      });

      if (response.ok) {
        setComplete(true);
      }
    }
  }, [complete, file, store, start]);

  const abort = useCallback(async () => {
    await pause();

    const uploadId = uploadIdRef.current;
    await api.cancel({ uploadId });
  }, [pause]);

  return { allClear, complete, progress, abort, pause, retry, setup, start };
}
