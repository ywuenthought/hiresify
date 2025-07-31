// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import Denque from 'denque';
import { createContext } from 'react';

type Job = () => Promise<void>;

export default class UploadQueue {
  private concurrency: number = 1;
  private runningJobs: number = 0;
  private pendingJobs: Denque<Job> = new Denque();

  constructor(args: { concurrency?: number }) {
    const { concurrency = 1 } = args;

    if (concurrency < 1 || !Number.isInteger(concurrency)) {
      throw new Error('Invalid pool concurrency was given.');
    }

    this.concurrency = concurrency;
  }

  public enqueue(args: { job: Job }) {
    const { job } = args;

    this.pendingJobs.push(job);
    this.runNextJobs();
  }

  private runNextJobs() {
    while (this.runningJobs < this.concurrency && this.pendingJobs.length > 0) {
      const job = this.pendingJobs.shift() as Job;
      this.runningJobs += 1;
      job().finally(() => {
        this.runningJobs -= 1;
        queueMicrotask(() => this.runNextJobs());
      });
    }
  }
}

export const UploadQueueContext = createContext<UploadQueue | null>(null);
