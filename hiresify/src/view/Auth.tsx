// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { Box, Stack, Tabs } from '@mui/material';
import { type SyntheticEvent, useState } from 'react';

import AuthTab from '@/component/AuthTab';

function Auth() {
  const [tabIndex, setTabIndex] = useState(0);

  const handleChange = (_event: SyntheticEvent, newTabIndex: number) =>
    setTabIndex(newTabIndex);

  return (
    <Box
      sx={{
        alignItems: 'center',
        display: 'flex',
        justifyContent: 'center',
      }}
    >
      <Box
        sx={{
          borderRadius: 2,
          boxShadow: 3,
          height: 400,
          padding: 2,
          width: 600,
        }}
      >
        <Stack direction="column" spacing={2}>
          <Tabs value={tabIndex} onChange={handleChange}>
            <AuthTab label="Login" onTop={tabIndex === 0} />
            <AuthTab label="Register" onTop={tabIndex === 1} />
          </Tabs>
        </Stack>
      </Box>
    </Box>
  );
}

export default Auth;
