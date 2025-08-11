// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { CssBaseline } from '@mui/material';
import { StrictMode } from 'react';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';

import App from './App.tsx';
import { makeStore } from './app/store.ts';
import { UPLOAD_CONCURRENCY } from './const.ts';
import UploadQueueProvider from './upload/provider.tsx';

export default function Root() {
  const store = makeStore();

  return (
    <StrictMode>
      <Provider store={store}>
        <CssBaseline />
        <BrowserRouter>
          <UploadQueueProvider concurrency={UPLOAD_CONCURRENCY}>
            <App />
          </UploadQueueProvider>
        </BrowserRouter>
      </Provider>
    </StrictMode>
  );
}
