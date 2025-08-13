// This file and its contents are confidential information and
// the intellectual property of Daiichi Sankyo.
// Access, use, and distribution is subject to written agreement
// by and between Enthought, Inc. and Daiichi Sankyo.

export type InTransitBlob = {
  // The UID of this blob.
  uid: string;

  // The name of this blob.
  fileName: string;

  // The progress of the upload.
  progress: number;

  // The status of the upload.
  status: 'active' | 'failed' | 'passed' | 'paused';
};

export type PersistedBlob = {
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
