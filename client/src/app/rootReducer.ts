// This file and its contents are confidential information and
// the intellectual property of Daiichi Sankyo.
// Access, use, and distribution is subject to written agreement
// by and between Enthought, Inc. and Daiichi Sankyo.

import { combineSlices } from '@reduxjs/toolkit';

import blobReducer from '@/feature/blob/slice';

const rootReducer = combineSlices({ blob: blobReducer });

export default rootReducer;
