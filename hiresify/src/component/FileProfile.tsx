// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { InsertDriveFile, Movie, Photo } from '@mui/icons-material';
import { Box, Stack, Typography } from '@mui/material';
import type { ReactNode } from 'react';

import type { FileType } from '@/type';

const iconPerMedia = {
  image: <Photo fontSize="large" />,
  video: <Movie fontSize="large" />,
  unknown: <InsertDriveFile fontSize="large" />,
};

type FileProfileProps = {
  fileName: string;
  fileType?: FileType;
  majorButton?: ReactNode;
  minorButton?: ReactNode;
};

export default function FileProfile(props: FileProfileProps) {
  const { fileName, fileType = 'unknown', majorButton, minorButton } = props;
  const mediaIcon = iconPerMedia[fileType];

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
        {mediaIcon}
        <Typography variant="body1" sx={{ flexGrow: 1, textAlign: 'left' }}>
          {fileName}
        </Typography>
        {majorButton}
        {minorButton}
      </Stack>
    </Box>
  );
}
