// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

export function mustGet(key: string): string {
  const val = sessionStorage.getItem(key);
  if (val === null) {
    throw new Error(`${key} was not found in sessionStorage.`);
  }
  return val;
}

export async function getDetail(resp: Response): Promise<string> {
  const { detail }: { detail?: string } = await resp.json();
  return `HTTP ${resp.status}${detail ? `: ${detail}` : ''}`;
}
