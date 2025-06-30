// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import './App.css';

import { Box } from '@mui/material';
import { Route, Routes } from 'react-router-dom';

import { routes } from './const';
import Auth from './view/Auth';
import Home from './view/Home';

export default function App() {
  return (
    <Box component="main">
      <Routes>
        <Route path={routes.HOME} element={<Home />} />
        <Route path={routes.AUTH} element={<Auth />} />
      </Routes>
    </Box>
  );
}
