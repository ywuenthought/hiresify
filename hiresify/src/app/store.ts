// This file and its contents are confidential information and
// the intellectual property of Daiichi Sankyo.
// Access, use, and distribution is subject to written agreement
// by and between Enthought, Inc. and Daiichi Sankyo.

import { configureStore } from '@reduxjs/toolkit';

import rootReducer from './rootReducer';

export type RootState = ReturnType<typeof rootReducer>;

const store = configureStore({ reducer: rootReducer });

export type AppStore = typeof store;
export type AppDispatch = AppStore['dispatch'];

export default store;
