// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import type { PartMeta } from './type';

export default class UploadMemoryStore {
  // The parts failed to upload.
  private failedParts: Set<PartMeta> = new Set();
  // The parts in an upload process.
  private onDutyParts: Set<PartMeta> = new Set();
  // A boolean flag for whether the file upload has ended.
  private complete: boolean = false;
  // The total size of the file.
  private fileSize: number = 0;
  // The size of an individual part.
  private partSize: number = 0;
  // The progress of the file upload.
  private progress: number = 0;
  // The index of next part to send.
  private nextPartIndex: number = 1;

  constructor(args: { fileSize: number; partSize: number }) {
    const { fileSize, partSize } = args;

    this.fileSize = fileSize;
    this.partSize = partSize;
  }

  public failPart(args: { part: PartMeta }): void {
    const { part } = args;

    if (!this.onDutyParts.has(part)) {
      return;
    }

    this.onDutyParts.delete(part);
    this.failedParts.add(part);

    this.complete = this.onDutyParts.size === 0;
  }

  public nextPart(): PartMeta | undefined {
    const start = (this.nextPartIndex - 1) * this.partSize;

    if (start >= this.fileSize) {
      return;
    }

    const end = Math.min(start + this.partSize, this.fileSize);
    const part = { index: this.nextPartIndex, start, end };

    this.onDutyParts.add(part);
    this.nextPartIndex += 1;

    return Object.freeze(part);
  }

  public passPart(args: { part: PartMeta }): void {
    const { part } = args;

    if (!this.failedParts.has(part) && !this.onDutyParts.has(part)) {
      return;
    }

    this.failedParts.delete(part);
    this.onDutyParts.delete(part);

    this.complete = this.onDutyParts.size === 0;
    this.progress += (part.end - part.start) / this.fileSize;
  }

  public resume(): Set<PartMeta> {
    return this.onDutyParts;
  }

  public retry(): Set<PartMeta> {
    this.onDutyParts = this.failedParts;
    this.failedParts = new Set();
    return this.onDutyParts;
  }

  public getComplete(): boolean {
    return this.complete;
  }

  public getProgress(): number {
    return this.progress;
  }
}
