// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { UPLOAD_CONCURRENCY } from '@/const';

import UploadQueue, { UploadQueueContext } from './queue';

export default function UploadQueueProvider(args: {
  children: React.ReactNode;
}) {
  const { children } = args;
  const queue = new UploadQueue({ concurrency: UPLOAD_CONCURRENCY });

  return (
    <UploadQueueContext.Provider value={queue}>
      {children}
    </UploadQueueContext.Provider>
  );
}
