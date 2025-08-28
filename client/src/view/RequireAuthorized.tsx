// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { Box, CircularProgress, Stack, Typography } from '@mui/material';
import type { ReactNode } from 'react';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { routes } from '@/routes';
import { tokenUrls } from '@/urls';

type RequireAuthorizedProps = {
  children: ReactNode;
};

export default function RequireAuthorized(props: RequireAuthorizedProps) {
  const { children } = props;

  const navigate = useNavigate();

  const [authorized, setAuthorized] = useState<boolean>(false);

  useEffect(() => {
    const refreshToken = async () => {
      const resp = await fetch(tokenUrls.refresh, {
        method: 'POST',
        credentials: 'include',
      });

      if (!resp.ok) {
        navigate(routes.home.root);
      }

      setAuthorized(resp.ok);
    };

    refreshToken();
  }, [navigate]);

  if (!authorized) {
    return (
      <Box
        sx={{
          left: '50%',
          position: 'absolute',
          top: '50%',
          transform: 'translate(-50%, -50%)',
        }}
      >
        <Stack
          direction="column"
          spacing={4}
          sx={{
            alignItems: 'center',
            display: 'flex',
            justifyContent: 'center',
          }}
        >
          <CircularProgress size={80} />
          <Typography variant="body1">
            Please wait while checking the login status...
          </Typography>
        </Stack>
      </Box>
    );
  }

  return children;
}
