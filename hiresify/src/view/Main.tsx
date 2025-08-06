// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { Box, Paper, Stack } from '@mui/material';
import { useCallback, useState } from 'react';

import bg from '@/assets/bg.jpg';
import Background from '@/component/Background';
import DragDropBox from '@/component/DragDropBox';
import LogoutButton from '@/component/LogoutButton';
import FileController from '@/composite/FileController';
import { CHUNK_SIZE } from '@/const';
import { getUuid4 } from '@/util';

export default function Main() {
  const [files, setFiles] = useState<Map<string, File>>(new Map());

  const onDrop = useCallback((curFiles: File[]) => {
    setFiles(
      (preFiles) =>
        new Map([
          ...preFiles,
          ...curFiles.map((file) => [getUuid4(), file] as [string, File]),
        ])
    );
  }, []);

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
          {Array.from(files.entries()).map(([uid, file]) => (
            <FileController
              key={`controller:${uid}`}
              file={file}
              partSize={CHUNK_SIZE}
              removeFile={() =>
                setFiles((preFiles) => {
                  const curFiles = new Map(preFiles);
                  curFiles.delete(uid);
                  return curFiles;
                })
              }
            />
          ))}
        </Paper>
      </Stack>
    </Background>
  );
}
