// This file and its contents are confidential information and
// the intellectual property of Daiichi Sankyo.
// Access, use, and distribution is subject to written agreement
// by and between Enthought, Inc. and Daiichi Sankyo.

import { createEntityAdapter, type EntityState } from '@reduxjs/toolkit';

import { createAppSlice } from '@/app/createAppSlice';
import type { BackendBlob } from '@/backend-type';
import { isImage, isVideo } from '@/util';

import { fetchAllBlobs } from './thunk';

const selectId = (entity: { uid: string }) => entity.uid;

const imageAdapter = createEntityAdapter<BackendBlob, string>({ selectId });
const videoAdapter = createEntityAdapter<BackendBlob, string>({ selectId });

const { selectAll: selectImageEntities } = imageAdapter.getSelectors();
const { selectAll: selectVideoEntities } = videoAdapter.getSelectors();

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
  reducers: (create) => ({
    insertImage: create.preparedReducer(
      (blob: BackendBlob) => ({ payload: { blob } }),
      (state, action) => {
        const { blob } = action.payload;

        if (!isImage(blob)) {
          return;
        }

        imageAdapter.addOne(state.entities.images, blob);
      }
    ),

    insertVideo: create.preparedReducer(
      (blob: BackendBlob) => ({ payload: { blob } }),
      (state, action) => {
        const { blob } = action.payload;

        if (!isVideo(blob)) {
          return;
        }

        videoAdapter.addOne(state.entities.videos, blob);
      }
    ),

    removeImage: create.preparedReducer(
      (blobUid: string) => ({ payload: { blobUid } }),
      (state, action) => {
        const { blobUid } = action.payload;
        imageAdapter.removeOne(state.entities.images, blobUid);
      }
    ),

    removeVideo: create.preparedReducer(
      (blobUid: string) => ({ payload: { blobUid } }),
      (state, action) => {
        const { blobUid } = action.payload;
        videoAdapter.removeOne(state.entities.videos, blobUid);
      }
    ),
  }),
  extraReducers: (builder) => {
    builder.addCase(fetchAllBlobs.fulfilled, (state, action) => {
      const { blobs } = action.payload;

      blobs.forEach((blob) => {
        if (isImage(blob)) {
          imageAdapter.addOne(state.entities.images, blob);
        }

        if (isVideo(blob)) {
          videoAdapter.addOne(state.entities.videos, blob);
        }
      });
    });
  },
  selectors: {
    selectAllImages: (state) => selectImageEntities(state.entities.images),
    selectAllVideos: (state) => selectVideoEntities(state.entities.videos),
  },
});

const { reducer } = blobSlice;

export default reducer;

export const { insertImage, insertVideo, removeImage, removeVideo } =
  blobSlice.actions;
export const { selectAllImages, selectAllVideos } = blobSlice.selectors;
