// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { Box, type BoxProps } from '@mui/material';

interface BackgroundProps extends BoxProps {
  imageAddress: string;
}

export default function Background(props: BackgroundProps) {
  const { imageAddress, children, ...boxProps } = props;
  return (
    <Box
      {...boxProps}
      sx={{
        backgroundImage: `url(${imageAddress})`,
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat',
        backgroundSize: 'cover',
        bottom: 0,
        left: 0,
        position: 'fixed',
        right: 0,
        top: 0,
      }}
    >
      {children}
    </Box>
  );
}
