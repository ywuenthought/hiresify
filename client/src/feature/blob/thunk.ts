// This file and its contents are confidential information and
// the intellectual property of Daiichi Sankyo.
// Access, use, and distribution is subject to written agreement
// by and between Enthought, Inc. and Daiichi Sankyo.

import { createAsyncThunk } from '@reduxjs/toolkit';

import { cancel, finish, gather, remove } from '@/api/blob';

export const gatherThunk = createAsyncThunk(
  'blob/gather',
  async () => await gather()
);

export const cancelThunk = createAsyncThunk(
  'blob/cancel',
  async (args: { blobUid: string; uploadId: string }) => {
    const { uploadId } = args;
    return await cancel({ uploadId });
  }
);

export const finishThunk = createAsyncThunk(
  'blob/finish',
  async (args: { blobUid: string; fileName: string; uploadId: string }) => {
    const { fileName, uploadId } = args;
    return await finish({ fileName, uploadId });
  }
);

export const removeThunk = createAsyncThunk(
  'blob/remove',
  async (args: { blobUid: string }) => await remove(args)
);
