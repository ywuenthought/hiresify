// This file and its contents are confidential information and
// the intellectual property of Daiichi Sankyo.
// Access, use, and distribution is subject to written agreement
// by and between Enthought, Inc. and Daiichi Sankyo.

import { createEntityAdapter, type EntityState } from '@reduxjs/toolkit';

import { createAppSlice } from '@/app/createAppSlice';
import type { BlobSchema } from '@/json-schema';
import type { InTransitBlob, PersistedBlob } from '@/type';

import { cancelThunk, finishThunk, gatherThunk, removeThunk } from './thunk';

const selectId = (entity: { uid: string }) => entity.uid;

const inTransitBlobAdapter = createEntityAdapter<InTransitBlob, string>({
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
  inTransit: EntityState<InTransitBlob, string>;
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
      (args: { blob: InTransitBlob }) => ({ payload: args }),
      (state, action) => {
        const { blob } = action.payload;
        inTransitBlobAdapter.addOne(state.inTransit, blob);
      }
    ),

    removeInTransitBlob: create.preparedReducer(
      (args: { uid: string }) => ({ payload: args }),
      (state, action) => {
        const { uid } = action.payload;
        inTransitBlobAdapter.removeOne(state.inTransit, uid);
      }
    ),

    updateInTransitBlob: create.preparedReducer(
      (args: {
        id: string;
        changes: Partial<Omit<InTransitBlob, 'uid' | 'blob'>>;
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
    selectAllPersistedBlobs: (state) => {
      const schemas = selectPersistedBlobEntities(state.persisted);
      return schemas.map((schema) => buildBlobFromSchema(schema));
    },
    selectOneInTransitBlob: (state, uid: string) =>
      selectInTransitBlobById(state.inTransit, uid),
    selectOnePersistedBlob: (state, uid: string) => {
      const schema = selectPersistedBlobById(state.persisted, uid);
      return buildBlobFromSchema(schema);
    },
  },
});

function buildBlobFromSchema(schema: BlobSchema): PersistedBlob {
  const { createdAt, validThru, ...rest } = schema;

  return {
    ...rest,
    createdAt: new Date(createdAt),
    validThru: new Date(validThru),
  };
}

const { reducer } = blobSlice;

export default reducer;

export const { insertInTransitBlob, removeInTransitBlob, updateInTransitBlob } =
  blobSlice.actions;
export const {
  selectAllInTransitBlobs,
  selectAllPersistedBlobs,
  selectOneInTransitBlob,
  selectOnePersistedBlob,
} = blobSlice.selectors;
