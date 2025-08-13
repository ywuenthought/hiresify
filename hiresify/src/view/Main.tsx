// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { Box, Paper, Stack } from '@mui/material';
import { bindActionCreators } from '@reduxjs/toolkit';
import { useCallback, useMemo, useRef } from 'react';

import { useAppDispatch, useAppSelector } from '@/app/hooks';
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
import type { FrontendBlob } from '@/type';
import { getUuid4 } from '@/util';

const buildActionCreators = () => {
  return {
    insert: (args: { blob: FrontendBlob }) => insertInTransitBlob(args),
  };
};

export default function Main() {
  const indexedJSBlobs = useRef<Map<string, File>>(new Map()).current;
  const inTransitBlobs = useAppSelector(selectAllInTransitBlobs);
  const blobUids = new Set(inTransitBlobs.map(({ uid }) => uid));

  indexedJSBlobs.forEach((_, uid) => {
    if (!blobUids.has(uid)) {
      indexedJSBlobs.delete(uid);
    }
  });

  const dispatch = useAppDispatch();
  const actions = useMemo(
    () => bindActionCreators(buildActionCreators(), dispatch),
    [dispatch]
  );

  const onDrop = useCallback(
    (curFiles: File[]) =>
      curFiles.forEach((file) => {
        const uid = getUuid4();
        const blob: FrontendBlob = {
          uid,
          fileName: file.name,
          progress: 0,
          status: 'active',
        };

        indexedJSBlobs.set(uid, file);
        actions.insert({ blob });
      }),
    [actions, indexedJSBlobs]
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
          {inTransitBlobs.map((frontendBlob) => {
            const { uid } = frontendBlob;
            return (
              <InTransitFile
                key={`controller:${uid}`}
                jsBlob={indexedJSBlobs.get(uid) as File}
                frontendBlob={frontendBlob}
                partSize={CHUNK_SIZE}
              />
            );
          })}
        </Paper>
      </Stack>
    </Background>
  );
}
