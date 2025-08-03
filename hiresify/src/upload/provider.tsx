// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import UploadQueue, { UploadQueueContext } from './queue';

export default function UploadQueueProvider(args: {
  children: React.ReactNode;
  concurrency?: number;
}) {
  const { children, concurrency = 1 } = args;
  const queue = new UploadQueue({ concurrency });

  return (
    <UploadQueueContext.Provider value={queue}>
      {children}
    </UploadQueueContext.Provider>
  );
}
