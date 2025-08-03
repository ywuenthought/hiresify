// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

export type SimpleAsyncThunk = () => Promise<void>;

export type UploadPart = {
  // The index of this part.
  readonly index: number;
  // The chunk of the parent file.
  readonly chunk: Blob;
};

export type UploadStatus = 'active' | 'failed' | 'passed' | 'paused' | null;
