// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

export type BackendBlob = {
  // The UID of this blob.
  uid: string;

  // The name of this blob file.
  fileName: string;

  // The MIME type of this blob file.
  mimeType: string;

  // The date and time when the blob was created.
  createdAt: Date;

  // The date and time when the blob is valid through.
  validThru: Date;
};
