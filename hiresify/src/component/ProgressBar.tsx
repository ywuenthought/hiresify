// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { Pause } from '@mui/icons-material';
import {
  Box,
  IconButton,
  LinearProgress,
  Stack,
  Typography,
} from '@mui/material';

type ProgressBarProps = {
  progress: number;
  pauseUpload: () => void;
};

export default function ProgressBar(props: ProgressBarProps) {
  const { progress } = props;
  const { pauseUpload } = props;

  const progressPercetage = progress * 100;

  return (
    <Box sx={{ height: 4, width: 60 }}>
      <Stack
        direction="row"
        spacing={2}
        sx={{
          alignItems: 'center',
          display: 'flex',
          justifyContent: 'center',
        }}
      >
        <IconButton onClick={pauseUpload}>
          <Pause />
        </IconButton>
        <LinearProgress value={progressPercetage} variant="determinate" />
        <Typography variant="body1">{progressPercetage}</Typography>
      </Stack>
    </Box>
  );
}
