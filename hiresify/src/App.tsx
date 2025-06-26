// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import './App.css';

import { Box } from '@mui/material';
import { Route, Routes } from 'react-router-dom';

import { ROUTES } from './const';
import Auth from './view/Auth';
import Home from './view/Home';

function App() {
  return (
    <Box component="main">
      <Routes>
        <Route path={ROUTES.HOME} element={<Home />} />
        <Route path={ROUTES.AUTH} element={<Auth />} />
      </Routes>
    </Box>
  );
}

export default App;
