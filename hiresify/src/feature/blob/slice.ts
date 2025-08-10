// This file and its contents are confidential information and
// the intellectual property of Daiichi Sankyo.
// Access, use, and distribution is subject to written agreement
// by and between Enthought, Inc. and Daiichi Sankyo.

import { createEntityAdapter, type EntityState } from '@reduxjs/toolkit';

import { createAppSlice } from '@/app/createAppSlice';
import type { BackendBlob } from '@/backend-type';

import { fetchAllBlobs } from './thunk';

const selectId = (entity: { uid: string }) => entity.uid;

const imageAdapter = createEntityAdapter<BackendBlob, string>({ selectId });
const videoAdapter = createEntityAdapter<BackendBlob, string>({ selectId });

type BlobState = {
  entities: {
    images: EntityState<BackendBlob, string>;
    videos: EntityState<BackendBlob, string>;
  };
};

const initialState: BlobState = {
  entities: {
    images: imageAdapter.getInitialState(),
    videos: videoAdapter.getInitialState(),
  },
};

const blobSlice = createAppSlice({
  name: 'blob',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder.addCase(fetchAllBlobs.fulfilled, (state, action) => {
      const { blobs } = action.payload;

      blobs.forEach((blob) => {
        if (blob.mimeType.startsWith('image')) {
          imageAdapter.addOne(state.entities.images, blob);
        }

        if (blob.mimeType.startsWith('video')) {
          videoAdapter.addOne(state.entities.videos, blob);
        }
      });
    });
  },
  selectors: {},
});

const { reducer } = blobSlice;

export default reducer;
