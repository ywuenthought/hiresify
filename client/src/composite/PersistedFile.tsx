// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { Delete } from '@mui/icons-material';
import { Box, CircularProgress, IconButton, Stack } from '@mui/material';
import { useCallback, useState } from 'react';

import { useAppDispatch } from '@/app/hooks';
import FileProfile from '@/component/FileProfile';
import { removeThunk } from '@/feature/blob/thunk';
import type { PersistedBlob } from '@/type';

type PersistedFileProps = {
  persistedBlob: PersistedBlob;
};

export default function PersistedFile(props: PersistedFileProps) {
  const { persistedBlob } = props;
  const { uid: blobUid, fileName, mimeType } = persistedBlob;

  const dispatch = useAppDispatch();
  const [pending, setPending] = useState<boolean>(false);

  const handleRemove = useCallback(async () => {
    setPending(true);
    await dispatch(removeThunk({ blobUid }));
    setPending(false);
  }, [blobUid, dispatch, setPending]);

  return (
    <Box sx={{ height: 50, minWidth: 150, my: 4 }}>
      <Stack
        direction="row"
        spacing={1}
        sx={{
          alignItems: 'center',
          display: 'flex',
          justifyContent: 'flex-start',
        }}
      >
        <FileProfile
          fileName={fileName}
          mimeType={mimeType}
          majorButton={
            pending ? (
              <CircularProgress size={30} />
            ) : (
              <IconButton onClick={handleRemove}>
                <Delete />
              </IconButton>
            )
          }
        />
      </Stack>
    </Box>
  );
}
