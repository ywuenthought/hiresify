// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { CssBaseline } from '@mui/material';
import { StrictMode } from 'react';
import { HashRouter } from 'react-router-dom';

import App from './App.tsx';

export default function Root() {
  return (
    <StrictMode>
      <CssBaseline />
      <HashRouter>
        <App />
      </HashRouter>
    </StrictMode>
  );
}
