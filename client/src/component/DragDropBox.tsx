// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { Box, Stack, Typography } from '@mui/material';
import { useDropzone } from 'react-dropzone';

type DragDropBoxProps = {
  onDrop: (files: File[]) => void;
};

export default function DragDropBox(props: DragDropBoxProps) {
  const { onDrop } = props;
  const { getInputProps, getRootProps, isDragActive } = useDropzone({ onDrop });

  return (
    <Box
      {...getRootProps()}
      sx={{
        bgcolor: isDragActive ? '#808080' : '#ffffff',
        border: '2px dashed #808080',
        cursor: 'pointer',
        height: 150,
        padding: 4,
        width: 700,
        zIndex: 0,
      }}
    >
      <Stack
        sx={{
          alignItems: 'center',
          display: 'flex',
          height: '100%',
          justifyContent: 'center',
        }}
      >
        <input {...getInputProps()} />
        <Typography gutterBottom variant="h5">
          Drag and drop files here, or click to select.
        </Typography>
      </Stack>
    </Box>
  );
}
