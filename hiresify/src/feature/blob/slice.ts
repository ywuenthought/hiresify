// This file and its contents are confidential information and
// the intellectual property of Daiichi Sankyo.
// Access, use, and distribution is subject to written agreement
// by and between Enthought, Inc. and Daiichi Sankyo.

import { createEntityAdapter, type EntityState } from '@reduxjs/toolkit';

import { createAppSlice } from '@/app/createAppSlice';
import type { BlobSchema } from '@/json-schema';
import type { FrontendBlob } from '@/type';

import { cancelThunk, finishThunk, gatherThunk, removeThunk } from './thunk';

const selectId = (entity: { uid: string }) => entity.uid;

const inTransitBlobAdapter = createEntityAdapter<FrontendBlob, string>({
  selectId,
});
const persistedBlobAdapter = createEntityAdapter<BlobSchema, string>({
  selectId,
});

const {
  selectAll: selectInTransitBlobEntities,
  selectById: selectInTransitBlobById,
} = inTransitBlobAdapter.getSelectors();
const {
  selectAll: selectPersistedBlobEntities,
  selectById: selectPersistedBlobById,
} = persistedBlobAdapter.getSelectors();

type BlobState = {
  inTransit: EntityState<FrontendBlob, string>;
  persisted: EntityState<BlobSchema, string>;
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
      (args: { blob: FrontendBlob }) => ({ payload: args }),
      (state, action) => {
        const { blob } = action.payload;
        inTransitBlobAdapter.addOne(state.inTransit, blob);
      }
    ),

    insertPersistedBlob: create.preparedReducer(
      (args: { blob: BlobSchema }) => ({ payload: args }),
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

    updateInTransitBlob: create.preparedReducer(
      (args: {
        id: string;
        changes: Partial<Omit<FrontendBlob, 'uid' | 'blob'>>;
      }) => ({ payload: args }),
      (state, action) => {
        const { id, changes } = action.payload;
        inTransitBlobAdapter.updateOne(state.inTransit, { id, changes });
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
    selectOneInTransitBlob: (state, blobUid: string) =>
      selectInTransitBlobById(state.inTransit, blobUid),
    selectOnePersistedBlob: (state, blobUid: string) =>
      selectPersistedBlobById(state.persisted, blobUid),
  },
});

const { reducer } = blobSlice;

export default reducer;

export const {
  insertInTransitBlob,
  insertPersistedBlob,
  removeInTransitBlob,
  removePersistedBlob,
  updateInTransitBlob,
} = blobSlice.actions;
export const {
  selectAllInTransitBlobs,
  selectAllPersistedBlobs,
  selectOneInTransitBlob,
  selectOnePersistedBlob,
} = blobSlice.selectors;
