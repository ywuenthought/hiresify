// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { Box, Stack, Typography } from '@mui/material';

import LoginButton from '@/component/LoginButton';
import RegisterLink from '@/component/RegisterLink';
import { userUrls } from '@/const';

function Auth() {
  return (
    <Box
      sx={{
        alignItems: 'center',
        display: 'flex',
        justifyContent: 'center',
      }}
    >
      <Stack
        spacing={7}
        sx={{ alignItems: 'center', justifyContent: 'center' }}
      >
        <Stack spacing={1}>
          <Typography
            variant="h2"
            sx={{ textAlign: 'center', fontSize: '4rem' }}
          >
            HIRESIFY
          </Typography>
          <Typography
            variant="h3"
            sx={{ textAlign: 'center', fontSize: '2.7rem' }}
          >
            YOUR VISION
          </Typography>
        </Stack>
        <Stack spacing={2}>
          <Box width={280}>
            <LoginButton loginUrl={userUrls.login} />
          </Box>
          <Stack
            direction="row"
            spacing={0.5}
            sx={{ alignItems: 'center', justifyContent: 'center' }}
          >
            <Typography variant="subtitle1">New here?</Typography>
            <RegisterLink registerUrl={userUrls.register} />
          </Stack>
        </Stack>
      </Stack>
    </Box>
  );
}

export default Auth;
