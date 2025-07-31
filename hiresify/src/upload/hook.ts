// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { useContext, useState } from 'react';

import { defer } from '@/util';

import * as api from './api';
import { UploadQueueContext } from './queue';
import UploadMemoryStore from './store';

export function useUploadQueue() {
  const context = useContext(UploadQueueContext);

  if (!context) {
    throw new Error('useUploadQueue must be used within a context.');
  }

  return context;
}

export function useUpload(file: File) {
  let uploadId: string;

  const store = new UploadMemoryStore({ file });
  const queue = useUploadQueue();

  const controllers: AbortController[] = [];
  const [progress, setProgress] = useState<number>(0);
  const [complete, setComplete] = useState<boolean>(false);

  const create = async () => {
    const response = await api.create({ file });

    if (!response.ok) {
      throw new Error(`Impossible to upload ${file.name}.`);
    }

    uploadId = (await response.json()) as string;
    await store.init();
  };

  const upload = async () => {
    while (true) {
      const part = store.nextPart();

      if (!part) {
        break;
      }

      const controller = new AbortController();
      controllers.push(controller);

      const job = async () => {
        const response = await api.upload({
          file,
          part,
          uploadId,
          controller,
        });

        if (response.ok) {
          store.passPart({ part });
          setComplete(store.complete());
          setProgress(store.progress());
        } else {
          store.failPart({ part });
        }
      };

      queue.enqueue({ job });
      defer();
    }
  };

  const pause = async () => {
    while (controllers.length > 0) {
      controllers.pop()?.abort();
      defer();
    }

    await store.pause();
  };

  const resume = async () => {
    await store.resume();
    await upload();
  };

  const retry = async () => {
    await store.retry();
    await upload();
  };

  const cancel = async () => {
    await api.cancel({ uploadId });
  };

  const finish = async () => {
    await api.finish({ fileName: file.name, uploadId });
  };

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
