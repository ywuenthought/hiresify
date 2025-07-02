// This file and its contents are confidential information and
// the intellectual property of Daiichi Sankyo.
// Access, use, and distribution is subject to written agreement
// by and between Enthought, Inc. and Daiichi Sankyo.

import { useDispatch, useSelector } from 'react-redux';

import type { AppDispatch, AppStartListening, RootState } from './store';
import { listenerMiddleware } from './store';

export const startAppListening =
  listenerMiddleware.startListening as AppStartListening;

export const useAppDispatch = useDispatch.withTypes<AppDispatch>();
export const useAppSelector = useSelector.withTypes<RootState>();
