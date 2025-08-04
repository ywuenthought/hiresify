// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

const { VITE_CHUNK_SIZE = '4', VITE_CONCURRENCY = '3' } = import.meta.env;

// Convert the chunk size from mb to bytes.
export const CHUNK_SIZE = 1024 ** 2 * Number(VITE_CHUNK_SIZE);

export const UPLOAD_CONCURRENCY = Number(VITE_CONCURRENCY);
