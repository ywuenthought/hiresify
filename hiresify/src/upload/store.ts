// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { CHUNK_SIZE } from '@/const';

import type { PartMeta } from './type';

export default class UploadMemoryStore {
  private toSendMap: Map<string, PartMeta[]> = new Map();
  private passedMap: Map<string, PartMeta[]> = new Map();
  private pausedMap: Map<string, PartMeta[]> = new Map();
  private failedMap: Map<string, PartMeta[]> = new Map();

  public failPart(args: { uploadId: string; partMeta: PartMeta }): void {
    const { uploadId, partMeta } = args;
    const parts = this.failedMap.get(uploadId);
    parts?.push(partMeta);
  }

  public nextPart(args: { uploadId: string }): PartMeta | undefined {
    const { uploadId } = args;
    const parts = this.toSendMap.get(uploadId);
    return parts?.pop();
  }

  public passPart(args: { uploadId: string; partMeta: PartMeta }): void {
    const { uploadId, partMeta } = args;
    const parts = this.passedMap.get(uploadId);
    parts?.push(partMeta);
  }

  public pause(args: { uploadId: string }): void {
    const { uploadId } = args;
    const parts = this.toSendMap.get(uploadId);

    if (parts) {
      this.pausedMap.set(uploadId, parts);
    }
  }

  public resume(args: { uploadId: string }): void {
    const { uploadId } = args;
    const parts = this.pausedMap.get(uploadId);

    if (parts) {
      this.toSendMap.set(uploadId, parts);
    }
  }

  public start(args: { uploadId: string; file: File }): void {
    const { uploadId, file } = args;

    const count = Math.ceil(file.size / CHUNK_SIZE);
    const parts: PartMeta[] = Array.from({ length: count }, (_, i) => {
      const offset = i * CHUNK_SIZE;
      return {
        index: i + 1,
        bound: [offset, Math.min(offset + CHUNK_SIZE, file.size)],
      };
    });

    this.toSendMap.set(uploadId, parts.reverse());
  }
}
