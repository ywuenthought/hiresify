// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { v4 as uuid4 } from 'uuid';

import type { BlobSchema } from './json-schema';
import type { PersistedBlob } from './type';

export function buildBlobFromSchema(schema: BlobSchema): PersistedBlob {
  const { createdAt, validThru, ...rest } = schema;

  return {
    ...rest,
    createdAt: new Date(createdAt),
    validThru: new Date(validThru),
  };
}

export async function defer() {
  await new Promise<void>((resolve) => queueMicrotask(resolve));
}

export async function getDetail(resp: Response): Promise<string | undefined> {
  const { detail }: { detail?: string } = await resp.json();
  return detail;
}

export function getManyItems(keys: string[]) {
  return keys.map((key) => sessionStorage.getItem(key));
}

export function getManyUuids(length: number) {
  return Array.from({ length }, () => getUuid4());
}

export function getUuid4() {
  return uuid4().replace(/-/g, '');
}

export function mustGet(key: string): string {
  const val = sessionStorage.getItem(key);
  if (val === null) {
    throw new Error(`${key} was not found in sessionStorage.`);
  }
  return val;
}

export async function postWithUrlEncodedFormData(
  url: string,
  formData: Record<string, string>
): Promise<Response> {
  const body = new URLSearchParams(formData).toString();

  return await fetch(url, {
    body,
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    method: 'POST',
    credentials: 'include',
  });
}

export function setManyItems(items: Record<string, string>) {
  Object.entries(items).forEach(([key, value]) =>
    sessionStorage.setItem(key, value)
  );
}
