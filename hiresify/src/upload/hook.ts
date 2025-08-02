// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { useCallback, useContext, useMemo, useRef, useState } from 'react';

import { defer } from '@/util';

import * as api from './api';
import { UploadQueueContext } from './queue';
import UploadMemoryStore from './store';
import type { UploadPart } from './type';

export function useUploadQueue() {
  const context = useContext(UploadQueueContext);

  if (!context) {
    throw new Error('useUploadQueue must be used within a context.');
  }

  return context;
}

export function useUpload(args: { file: File; partSize: number }) {
  const { file, partSize } = args;

  const queue = useUploadQueue();
  const store = useMemo(() => new UploadMemoryStore(), []);

  const uploadIdRef = useRef<string>('');
  const controllers: AbortController[] = useMemo(() => [], []);

  const [complete, setComplete] = useState<boolean>(false);
  const [progress, setProgress] = useState<number>(0);

  const factory = useCallback(
    (args: { controller: AbortController; part: UploadPart }) => {
      const { controller, part } = args;

      const fileName = file.name;
      const uploadId = uploadIdRef.current;

      return async () => {
        const response = await api.upload({ part, uploadId, controller });

        if (response.ok) {
          store.passPart({ part });

          const doneSize = store.getDoneSize();
          setProgress((doneSize / file.size) * 100);

          if (doneSize === file.size) {
            const response = await api.finish({ fileName, uploadId });

            if (response.ok) {
              setComplete(true);
            } else {
              throw new Error(`Failed to finish the upload for ${file.name}.`);
            }
          }
        } else {
          store.failPart({ part });
        }
      };
    },
    [file, store]
  );

  const create = useCallback(async () => {
    if (uploadIdRef.current) {
      return;
    }

    const response = await api.create({ file });

    if (!response.ok) {
      throw new Error(`Impossible to upload ${file.name}.`);
    }

    const uploadId = (await response.json()) as string;
    uploadIdRef.current = uploadId;

    store.init({ file, partSize });
  }, [file, partSize, store]);

  const upload = useCallback(async () => {
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
      await upload();
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
  }, [complete, file, store, upload]);

  const remove = useCallback(async () => {
    await pause();

    const uploadId = uploadIdRef.current;
    await api.cancel({ uploadId });
  }, [pause]);

  return [complete, progress, create, pause, remove, retry, upload];
}
