// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

export type PartMeta = {
  // The index of this part.
  readonly index: number;
  // The starting and ending byte positions of this part in the parent file.
  readonly bound: [number, number];
};

export type Status = {
  readonly failed: number;
  readonly onDuty: number;
  readonly passed: number;
  readonly paused: number;
  readonly toSend: number;
  // passed divided by total, a number between 0 and 1.
  readonly progress: number;
};
