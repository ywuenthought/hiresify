// This file and its contents are confidential information and
// the intellectual property of Daiichi Sankyo.
// Access, use, and distribution is subject to written agreement
// by and between Enthought, Inc. and Daiichi Sankyo.

import { createAsyncThunk } from '@reduxjs/toolkit';

import { fetchAll } from '@/api/blob';

export const fetchAllBlobs = createAsyncThunk(
  'blob/fetchAll',
  async () => await fetchAll()
);
