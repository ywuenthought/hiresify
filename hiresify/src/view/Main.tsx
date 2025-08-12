// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { Box, Paper, Stack } from '@mui/material';
import { useCallback } from 'react';

import { useAppSelector } from '@/app/hooks';
import bg from '@/assets/bg.jpg';
import Background from '@/component/Background';
import DragDropBox from '@/component/DragDropBox';
import LogoutButton from '@/component/LogoutButton';
import InTransitFile from '@/composite/InTransitFile';
import { CHUNK_SIZE } from '@/const';
import {
  insertInTransitBlob,
  selectAllInTransitBlobs,
} from '@/feature/blob/slice';
import { getUuid4 } from '@/util';

export default function Main() {
  const inTransitBlobs = useAppSelector(selectAllInTransitBlobs);

  const onDrop = useCallback(
    (curFiles: File[]) =>
      curFiles.forEach((curFile) => {
        const file = { uid: getUuid4(), file: curFile };
        insertInTransitBlob({ file });
      }),
    []
  );

  return (
    <Background imageAddress={bg}>
      <Box width={150} sx={{ position: 'absolute', right: 0, top: 10 }}>
        <LogoutButton />
      </Box>
      <Stack
        direction="column"
        spacing={2}
        sx={{
          alignItems: 'center',
          height: '100%',
          justifyContent: 'center',
        }}
      >
        <DragDropBox onDrop={onDrop} />
        <Paper
          elevation={4}
          sx={{
            height: 500,
            overflow: 'auto',
            padding: 4,
            width: 700,
          }}
        >
          {inTransitBlobs.map((file) => (
            <InTransitFile
              key={`controller:${file.uid}`}
              file={file}
              partSize={CHUNK_SIZE}
            />
          ))}
        </Paper>
      </Stack>
    </Background>
  );
}
