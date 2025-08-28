// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { InsertDriveFile, Movie, Photo } from '@mui/icons-material';
import { Box, Stack, Typography } from '@mui/material';
import type { ReactNode } from 'react';

type FileProfileProps = {
  fileName: string;
  mimeType?: string;
  majorButton?: ReactNode;
  minorButton?: ReactNode;
};

export default function FileProfile(props: FileProfileProps) {
  const { fileName, mimeType = 'unknown', majorButton, minorButton } = props;

  return (
    <Box sx={{ width: '100%' }}>
      <Stack
        direction="row"
        spacing={1}
        sx={{
          alignItems: 'center',
          display: 'flex',
          justifyContent: 'flex-start',
        }}
      >
        {mimeType.startsWith('image') ? (
          <Photo fontSize="large" />
        ) : mimeType.startsWith('video') ? (
          <Movie fontSize="large" />
        ) : (
          <InsertDriveFile fontSize="large" />
        )}
        <Typography variant="body1" sx={{ flexGrow: 1, textAlign: 'left' }}>
          {fileName}
        </Typography>
        {majorButton}
        {minorButton}
      </Stack>
    </Box>
  );
}
