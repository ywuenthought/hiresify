// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { Box } from '@mui/material';
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

import LogoutButton from '@/component/LogoutButton';
import { routes } from '@/const';
import { getManyItems } from '@/util';

function Main() {
  const navigate = useNavigate();
  const [token] = getManyItems(['refreshToken']);

  useEffect(() => {
    if (!token) {
      navigate(routes.home.root);
    }
  }, [token, navigate]);

  return (
    <Box width={150} sx={{ position: 'absolute', right: 0, top: 0 }}>
      <LogoutButton />
    </Box>
  );
}

export default Main;
