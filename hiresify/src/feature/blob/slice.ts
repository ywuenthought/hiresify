// This file and its contents are confidential information and
// the intellectual property of Daiichi Sankyo.
// Access, use, and distribution is subject to written agreement
// by and between Enthought, Inc. and Daiichi Sankyo.

import { createEntityAdapter, type EntityState } from '@reduxjs/toolkit';

import { createAppSlice } from '@/app/createAppSlice';
import type { BackendBlob } from '@/backend-type';
import type { FrontendBlob } from '@/type';

import { cancelThunk, finishThunk, gatherThunk, removeThunk } from './thunk';

const selectId = (entity: { uid: string }) => entity.uid;

const inTransitBlobAdapter = createEntityAdapter<FrontendBlob, string>({
  selectId,
});
const persistedBlobAdapter = createEntityAdapter<BackendBlob, string>({
  selectId,
});

const { selectAll: selectInTransitBlobEntities } =
  inTransitBlobAdapter.getSelectors();
const { selectAll: selectPersistedBlobEntities } =
  persistedBlobAdapter.getSelectors();

type BlobState = {
  inTransit: EntityState<FrontendBlob, string>;
  persisted: EntityState<BackendBlob, string>;
};

const initialState: BlobState = {
  inTransit: inTransitBlobAdapter.getInitialState(),
  persisted: persistedBlobAdapter.getInitialState(),
};

const blobSlice = createAppSlice({
  name: 'blob',
  initialState,
  reducers: (create) => ({
    insertInTransitBlob: create.preparedReducer(
      (args: { file: FrontendBlob }) => ({ payload: args }),
      (state, action) => {
        const { file } = action.payload;
        inTransitBlobAdapter.addOne(state.inTransit, file);
      }
    ),

    insertPersistedBlob: create.preparedReducer(
      (args: { blob: BackendBlob }) => ({ payload: args }),
      (state, action) => {
        const { blob } = action.payload;
        persistedBlobAdapter.addOne(state.persisted, blob);
      }
    ),

    removeInTransitBlob: create.preparedReducer(
      (args: { uid: string }) => ({ payload: args }),
      (state, action) => {
        const { uid } = action.payload;
        inTransitBlobAdapter.removeOne(state.inTransit, uid);
      }
    ),

    removePersistedBlob: create.preparedReducer(
      (args: { uid: string }) => ({ payload: args }),
      (state, action) => {
        const { uid } = action.payload;
        persistedBlobAdapter.removeOne(state.persisted, uid);
      }
    ),
  }),
  extraReducers: (builder) => {
    builder.addCase(cancelThunk.fulfilled, (state, action) => {
      const { ok } = action.payload;

      if (!ok) {
        return;
      }

      const { blobUid } = action.meta.arg;
      inTransitBlobAdapter.removeOne(state.inTransit, blobUid);
    });

    builder.addCase(finishThunk.fulfilled, (state, action) => {
      const { blob } = action.payload;
      const { blobUid } = action.meta.arg;

      if (blob) {
        persistedBlobAdapter.addOne(state.persisted, blob);
        inTransitBlobAdapter.removeOne(state.inTransit, blobUid);
      } else {
        inTransitBlobAdapter.updateOne(state.inTransit, {
          id: blobUid,
          changes: { status: 'failed' },
        });
      }
    });

    builder.addCase(gatherThunk.fulfilled, (state, action) => {
      const { blobs } = action.payload;

      blobs.forEach((blob) =>
        persistedBlobAdapter.addOne(state.persisted, blob)
      );
    });

    builder.addCase(removeThunk.fulfilled, (state, action) => {
      const { ok } = action.payload;

      if (!ok) {
        return;
      }

      const { blobUid } = action.meta.arg;
      persistedBlobAdapter.removeOne(state.persisted, blobUid);
    });
  },
  selectors: {
    selectAllInTransitBlobs: (state) =>
      selectInTransitBlobEntities(state.inTransit),
    selectAllPersistedBlobs: (state) =>
      selectPersistedBlobEntities(state.persisted),
  },
});

const { reducer } = blobSlice;

export default reducer;

export const {
  insertInTransitBlob,
  insertPersistedBlob,
  removeInTransitBlob,
  removePersistedBlob,
} = blobSlice.actions;
export const { selectAllInTransitBlobs, selectAllPersistedBlobs } =
  blobSlice.selectors;
