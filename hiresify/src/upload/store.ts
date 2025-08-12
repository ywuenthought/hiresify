// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { defer } from '@/util';

import type { UploadPart } from './type';

export default class UploadMemoryStore {
  // The parts failed to upload.
  private failedParts: UploadPart[] = [];
  // The parts in an upload process.
  private onDutyParts: Set<UploadPart> = new Set();
  // The parts of the file to send.
  private toSendParts: UploadPart[] = [];

  // Whether ALL the chunk uploads have been cleared.
  // A chunk upload is cleared even if it is failed.
  private allClear: boolean = false;
  // Whether the store has been initialzied.
  private doneInit: boolean = false;
  // The total size of the uploaded parts.
  private doneSize: number = 0;

  public async init(args: { jsBlob: File; partSize: number }): Promise<void> {
    if (this.doneInit) {
      return;
    }

    const { jsBlob, partSize } = args;
    const count = Math.ceil(jsBlob.size / partSize);

    for (let index = 1; index <= count; index += 1) {
      const offset = (index - 1) * partSize;
      const chunk = jsBlob.slice(
        offset,
        Math.min(offset + partSize, jsBlob.size)
      );
      this.toSendParts.push({ index, chunk });
      await defer();
    }

    this.doneInit = true;
  }

  public failPart(args: { part: UploadPart }): void {
    const { part } = args;

    if (!this.onDutyParts.has(part)) {
      return;
    }

    this.failedParts.push(part);
    this.onDutyParts.delete(part);

    this.allClear = this.onDutyParts.size === 0;
  }

  public nextPart(): UploadPart | undefined {
    const part = this.toSendParts.pop();

    if (part) {
      this.onDutyParts.add(part);
    }

    return Object.freeze(part);
  }

  public passPart(args: { part: UploadPart }): void {
    const { part } = args;

    if (!this.onDutyParts.has(part)) {
      return;
    }

    this.onDutyParts.delete(part);

    this.allClear = this.onDutyParts.size === 0;
    this.doneSize += part.chunk.size;
  }

  public async pause(): Promise<void> {
    for (const part of this.onDutyParts) {
      this.toSendParts.push(part);
      await defer();
    }

    this.onDutyParts.clear();
  }

  public async retry(): Promise<void> {
    for (const part of this.failedParts) {
      this.toSendParts.push(part);
      await defer();
    }

    this.failedParts.length = 0;
  }

  public getAllClear(): boolean {
    return this.allClear;
  }

  public getDoneSize(): number {
    return this.doneSize;
  }
}
