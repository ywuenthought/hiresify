// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { Box, Stack, Typography } from '@mui/material';
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

import BackButton from '@/component/BackButton';
import { routes } from '@/const';
import { getManyItems } from '@/util';

export default function RegisterCallback() {
  const navigate = useNavigate();
  const [registerToken] = getManyItems(['registerToken']);

  useEffect(() => {
    if (!registerToken) {
      navigate(routes.home.root);
    }
  }, [registerToken, navigate]);

  return (
    <Stack
      spacing={7}
      sx={{
        alignItems: 'center',
        height: '100%',
        justifyContent: 'center',
      }}
    >
      <Stack spacing={1}>
        <Typography fontWeight="bold" variant="h4" sx={{ textAlign: 'center' }}>
          Registration Succeeded
        </Typography>
        <Typography
          color="success"
          variant="body1"
          sx={{ textAlign: 'center' }}
        >
          Congratulations!
        </Typography>
      </Stack>
      <Box width={280}>
        <BackButton />
      </Box>
    </Stack>
  );
}
