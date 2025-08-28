// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { LinearProgress, Stack, Typography } from '@mui/material';

type ProgressBarProps = {
  progress: number;
};

export default function ProgressBar(props: ProgressBarProps) {
  const { progress } = props;

  return (
    <Stack
      direction="row"
      spacing={1}
      sx={{
        alignItems: 'center',
        display: 'flex',
        justifyContent: 'flex-start',
      }}
    >
      <LinearProgress
        value={progress}
        variant="determinate"
        sx={{ flexGrow: 1 }}
      />
      <Typography variant="body1">{`${progress.toFixed(0)}%`}</Typography>
    </Stack>
  );
}
