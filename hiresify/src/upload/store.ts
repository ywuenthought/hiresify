// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import Denque from 'denque';

import { CHUNK_SIZE } from '@/const';

import type { PartMeta, Status } from './type';

export default class UploadMemoryStore {
  private failedParts: Denque<PartMeta> = new Denque();
  private onDutyParts: Set<PartMeta> = new Set();
  private passedParts: Denque<PartMeta> = new Denque();
  private pausedParts: PartMeta[] = [];
  private toSendParts: Denque<PartMeta> = new Denque();

  constructor(args: { file: File }) {
    const { file } = args;

    const count = Math.ceil(file.size / CHUNK_SIZE);
    for (let index = 1; index <= count; index += 1) {
      const offset = (index - 1) * CHUNK_SIZE;
      this.toSendParts.push({
        index: index,
        bound: [offset, Math.min(offset + CHUNK_SIZE, file.size)],
      });
    }
  }

  public failPart(args: { part: PartMeta }): void {
    const { part } = args;

    if (!this.onDutyParts.has(part)) {
      return;
    }

    this.onDutyParts.delete(part);
    this.failedParts.push(part);
  }

  public nextPart(): PartMeta | undefined {
    const part = this.toSendParts.shift();

    if (part) {
      this.onDutyParts.add(part);
    }

    return part;
  }

  public passPart(args: { part: PartMeta }): void {
    const { part } = args;

    if (!this.onDutyParts.has(part)) {
      return;
    }

    this.onDutyParts.delete(part);
    this.passedParts.push(part);
  }

  public pause(): void {
    while (this.toSendParts.length > 0) {
      this.pausedParts.push(this.toSendParts.pop() as PartMeta);
    }
  }

  public resume(): void {
    while (this.pausedParts.length > 0) {
      this.toSendParts.push(this.pausedParts.pop() as PartMeta);
    }
  }

  public retry(): void {
    while (this.failedParts.length > 0) {
      this.toSendParts.push(this.failedParts.shift() as PartMeta);
    }
  }

  public status(): Status {
    const failed = this.failedParts.length;
    const onDuty = this.onDutyParts.size;
    const passed = this.passedParts.length;
    const paused = this.pausedParts.length;
    const toSend = this.toSendParts.length;
    const progress = passed / (failed + onDuty + passed + paused + toSend);
    return {
      failed,
      onDuty,
      passed,
      paused,
      toSend,
      progress,
    };
  }
}
