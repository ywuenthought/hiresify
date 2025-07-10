// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { Box } from '@mui/material';
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

import LogoutButton from '@/component/LogoutButton';
import { routes, tokenUrls } from '@/const';

function Main() {
  const navigate = useNavigate();

  useEffect(() => {
    async function refreshToken() {
      const resp = await fetch(tokenUrls.refresh, {
        method: 'POST',
        credentials: 'include',
      });

      if (!resp.ok) {
        navigate(routes.home.root);
      }
    }

    refreshToken();
  }, [navigate]);

  return (
    <Box width={150} sx={{ position: 'absolute', right: 0, top: 0 }}>
      <LogoutButton />
    </Box>
  );
}

export default Main;
