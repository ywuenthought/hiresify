// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import './App.css';

import { Box } from '@mui/material';
import { Navigate, Route, Routes } from 'react-router-dom';

import { routes } from './routes';
import AuthorizeCallback from './view/AuthorizeCallback';
import Home from './view/Home';
import LoginCallback from './view/LoginCallback';
import Main from './view/Main';
import RegisterCallback from './view/RegisterCallback';
import RequireAuthorized from './view/RequireAuthorized';

export default function App() {
  return (
    <Box component="main">
      <Routes>
        <Route path="/" element={<Navigate to={routes.main.root} replace />} />
        <Route path={routes.home.root} element={<Home />} />
        <Route
          path={routes.main.root}
          element={
            <RequireAuthorized homePath={routes.home.root}>
              <Main />
            </RequireAuthorized>
          }
        />
        <Route
          path={
            `${routes.home.root}` +
            `${routes.home.children.callback.root}` +
            `${routes.home.children.callback.children.authorize.root}`
          }
          element={<AuthorizeCallback />}
        />
        <Route
          path={
            `${routes.home.root}` +
            `${routes.home.children.callback.root}` +
            `${routes.home.children.callback.children.login.root}`
          }
          element={<LoginCallback />}
        />
        <Route
          path={
            `${routes.home.root}` +
            `${routes.home.children.callback.root}` +
            `${routes.home.children.callback.children.register.root}`
          }
          element={<RegisterCallback />}
        />
      </Routes>
    </Box>
  );
}
