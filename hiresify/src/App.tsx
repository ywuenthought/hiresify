// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import './App.css';

import { Box } from '@mui/material';
import { Route, Routes } from 'react-router-dom';

import { routes } from './const';
import Callback from './view/Callback';
import Home from './view/Home';
import Main from './view/Main';

export default function App() {
  return (
    <Box component="main">
      <Routes>
        <Route path={routes.home.root} element={<Home />} />
        <Route path={routes.main.root} element={<Main />} />
        <Route
          path={
            `${routes.home.root}` +
            `${routes.home.children.callback.root}` +
            `${routes.home.children.callback.children.authorize.root}`
          }
          element={<Callback />}
        />
        <Route
          path={
            `${routes.home.root}` +
            `${routes.home.children.callback.root}` +
            `${routes.home.children.callback.children.register.root}`
          }
          element={<Callback />}
        />
      </Routes>
    </Box>
  );
}
