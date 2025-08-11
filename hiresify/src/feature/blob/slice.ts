// This file and its contents are confidential information and
// the intellectual property of Daiichi Sankyo.
// Access, use, and distribution is subject to written agreement
// by and between Enthought, Inc. and Daiichi Sankyo.

import { createEntityAdapter, type EntityState } from '@reduxjs/toolkit';

import { createAppSlice } from '@/app/createAppSlice';
import type { BackendBlob } from '@/backend-type';
import { isImage, isVideo } from '@/util';

import type { IndexedFile } from '../../type';
import { fetchAllBlobs } from './thunk';

const selectId = (entity: { uid: string }) => entity.uid;

const inTransitMediaAdapter = createEntityAdapter<IndexedFile, string>({
  selectId,
});
const persistedImageAdapter = createEntityAdapter<BackendBlob, string>({
  selectId,
});
const persistedVideoAdapter = createEntityAdapter<BackendBlob, string>({
  selectId,
});

const { selectAll: selectInTransitMediaEntities } =
  inTransitMediaAdapter.getSelectors();
const { selectAll: selectPersistedImageEntities } =
  persistedImageAdapter.getSelectors();
const { selectAll: selectPersistedVideoEntities } =
  persistedVideoAdapter.getSelectors();

type BlobState = {
  inTransit: EntityState<IndexedFile, string>;
  persisted: {
    images: EntityState<BackendBlob, string>;
    videos: EntityState<BackendBlob, string>;
  };
};

const initialState: BlobState = {
  inTransit: inTransitMediaAdapter.getInitialState(),
  persisted: {
    images: persistedImageAdapter.getInitialState(),
    videos: persistedVideoAdapter.getInitialState(),
  },
};

const blobSlice = createAppSlice({
  name: 'blob',
  initialState,
  reducers: (create) => ({
    insertInTransitMedia: create.preparedReducer(
      (args: { file: IndexedFile }) => ({ payload: args }),
      (state, action) => {
        const { file } = action.payload;
        inTransitMediaAdapter.addOne(state.inTransit, file);
      }
    ),

    insertPersistedImage: create.preparedReducer(
      (args: { blob: BackendBlob }) => ({ payload: args }),
      (state, action) => {
        const { blob } = action.payload;

        if (!isImage(blob)) {
          return;
        }

        persistedImageAdapter.addOne(state.persisted.images, blob);
      }
    ),

    insertPersistedVideo: create.preparedReducer(
      (args: { blob: BackendBlob }) => ({ payload: args }),
      (state, action) => {
        const { blob } = action.payload;

        if (!isVideo(blob)) {
          return;
        }

        persistedVideoAdapter.addOne(state.persisted.videos, blob);
      }
    ),

    removeInTransitMedia: create.preparedReducer(
      (args: { uid: string }) => ({ payload: args }),
      (state, action) => {
        const { uid } = action.payload;
        inTransitMediaAdapter.removeOne(state.inTransit, uid);
      }
    ),

    removePersistedImage: create.preparedReducer(
      (args: { uid: string }) => ({ payload: args }),
      (state, action) => {
        const { uid } = action.payload;
        persistedImageAdapter.removeOne(state.persisted.images, uid);
      }
    ),

    removePersistedVideo: create.preparedReducer(
      (args: { uid: string }) => ({ payload: args }),
      (state, action) => {
        const { uid } = action.payload;
        persistedVideoAdapter.removeOne(state.persisted.videos, uid);
      }
    ),
  }),
  extraReducers: (builder) => {
    builder.addCase(fetchAllBlobs.fulfilled, (state, action) => {
      const { blobs } = action.payload;

      blobs.forEach((blob) => {
        if (isImage(blob)) {
          persistedImageAdapter.addOne(state.persisted.images, blob);
        }

        if (isVideo(blob)) {
          persistedVideoAdapter.addOne(state.persisted.videos, blob);
        }
      });
    });
  },
  selectors: {
    selectAllInTransitMedia: (state) =>
      selectInTransitMediaEntities(state.inTransit),
    selectAllPersistedImages: (state) =>
      selectPersistedImageEntities(state.persisted.images),
    selectAllPersistedVideos: (state) =>
      selectPersistedVideoEntities(state.persisted.videos),
  },
});

const { reducer } = blobSlice;

export default reducer;

export const {
  insertInTransitMedia,
  insertPersistedImage,
  insertPersistedVideo,
  removeInTransitMedia,
  removePersistedImage,
  removePersistedVideo,
} = blobSlice.actions;
export const {
  selectAllInTransitMedia,
  selectAllPersistedImages,
  selectAllPersistedVideos,
} = blobSlice.selectors;
