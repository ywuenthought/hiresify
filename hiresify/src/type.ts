// This file and its contents are confidential information and
// the intellectual property of Daiichi Sankyo.
// Access, use, and distribution is subject to written agreement
// by and between Enthought, Inc. and Daiichi Sankyo.

export type FileType = 'image' | 'video' | 'unknown';

export type FrontendBlob = {
  // The UID of this blob.
  uid: string;

  // The name of this blob.
  fileName: string;

  // The progress of the upload.
  progress: number;

  // The status of the upload.
  status: 'active' | 'failed' | 'passed' | 'paused';
};
