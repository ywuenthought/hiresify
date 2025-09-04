// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { sha256 } from 'js-sha256';

export async function generateCodeChallenge(
  codeVerifier: string
): Promise<string> {
  const digest = sha256.arrayBuffer(codeVerifier);
  return base64UrlEncode(new Uint8Array(digest));
}

export function generateCodeVerifier(): string {
  const array = new Uint8Array(64);
  window.crypto.getRandomValues(array);
  return base64UrlEncode(array);
}

function base64UrlEncode(buffer: Uint8Array): string {
  return btoa(String.fromCharCode(...buffer))
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/, '');
}
