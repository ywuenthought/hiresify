// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import UploadQueue from '../queue';
import type { Job } from '../type';

function createManualJob(args: { id: string; logs: string[] }): {
  job: Job;
  unblock: () => void;
} {
  const { id, logs } = args;

  let resolver: () => void;
  const promise = new Promise<void>((resolve) => (resolver = resolve));

  return {
    job: async () => {
      logs.push(`run:${id}`);
      await promise;
      logs.push(`end:${id}`);
    },
    unblock: () => resolver(),
  };
}

describe('UploadQueue', () => {
  it('runs jobs respecting concurrency', async () => {
    // Given
    const queue = new UploadQueue({ concurrency: 2 });

    const logs: string[] = [];
    const jobs = [
      createManualJob({ id: 'A', logs }),
      createManualJob({ id: 'B', logs }),
      createManualJob({ id: 'C', logs }),
    ];

    // When
    for (const job of jobs) {
      queue.enqueue({ job: job.job });
    }

    // Then
    expect(logs).toEqual(['run:A', 'run:B']);

    // When
    jobs[0].unblock();
    await Promise.resolve(); // End A.

    // Then
    expect(logs).toEqual(['run:A', 'run:B', 'end:A']);

    // When
    await Promise.resolve(); // Run queueMicrotask.
    await Promise.resolve(); // Enqueue C.

    // Then
    expect(logs).toEqual(['run:A', 'run:B', 'end:A', 'run:C']);

    // When
    jobs[2].unblock();
    await Promise.resolve(); // End C.

    // Then
    expect(logs).toEqual(['run:A', 'run:B', 'end:A', 'run:C', 'end:C']);

    // When
    jobs[1].unblock();
    await Promise.resolve(); // End B.

    // Then
    expect(logs).toEqual([
      'run:A',
      'run:B',
      'end:A',
      'run:C',
      'end:C',
      'end:B',
    ]);
  });
});
