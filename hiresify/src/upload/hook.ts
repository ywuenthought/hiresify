// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { useCallback, useContext, useMemo, useRef, useState } from 'react';

import { defer } from '@/util';

import * as api from './api';
import { UploadQueueContext } from './queue';
import UploadMemoryStore from './store';
import type { PartMeta } from './type';

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
  const store = useMemo(
    () => new UploadMemoryStore({ fileSize: file.size, partSize }),
    [file, partSize]
  );

  const uploadIdRef = useRef<string>('');
  const controllers: AbortController[] = useMemo(() => [], []);

  const [progress, setProgress] = useState<number>(0);
  const [complete, setComplete] = useState<boolean>(false);

  const factory = useCallback(
    (args: { controller: AbortController; part: PartMeta }) => {
      const { controller, part } = args;
      return async () => {
        const response = await api.upload({
          file,
          part,
          uploadId: uploadIdRef.current,
          controller,
        });

        if (response.ok) {
          store.passPart({ part });
          setComplete(store.getComplete());
          setProgress(store.getProgress());
        } else {
          store.failPart({ part });
        }
      };
    },
    [file, store]
  );

  const create = useCallback(async () => {
    const response = await api.create({ file });

    if (!response.ok) {
      throw new Error(`Impossible to upload ${file.name}.`);
    }

    const uploadId = (await response.json()) as string;
    uploadIdRef.current = uploadId;
  }, [file]);

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
  }, [controllers]);

  const resume = useCallback(async () => {
    for (const part of store.resume()) {
      const controller = new AbortController();
      controllers.push(controller);

      const job = factory({ controller, part });
      queue.enqueue({ job });
      defer();
    }
  }, [controllers, queue, store, factory]);

  const retry = useCallback(async () => {
    for (const part of store.retry()) {
      const controller = new AbortController();
      controllers.push(controller);

      const job = factory({ controller, part });
      queue.enqueue({ job });
      defer();
    }
  }, [controllers, queue, store, factory]);

  const cancel = useCallback(async () => {
    const uploadId = uploadIdRef.current;
    await api.cancel({ uploadId });
  }, []);

  const finish = useCallback(async () => {
    const fileName = file.name;
    const uploadId = uploadIdRef.current;
    await api.finish({ fileName, uploadId });
  }, [file]);

  return [
    complete,
    progress,
    cancel,
    create,
    finish,
    pause,
    resume,
    retry,
    upload,
  ];
}
