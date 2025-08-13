// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { Delete } from '@mui/icons-material';
import { Box, CircularProgress, IconButton, Stack } from '@mui/material';
import { useCallback, useState } from 'react';

import { useAppDispatch } from '@/app/hooks';
import type { BackendBlob } from '@/backend-type';
import FileProfile from '@/component/FileProfile';
import { removeThunk } from '@/feature/blob/thunk';
import type { FileType } from '@/type';

type PersistedFileProps = {
  backendBlob: BackendBlob;
};

export default function PersistedFile(props: PersistedFileProps) {
  const { backendBlob } = props;
  const { uid: blobUid, fileName, mimeType } = backendBlob;

  let fileType: FileType = 'unknown';

  if (mimeType.startsWith('image')) {
    fileType = 'image';
  }
  if (mimeType.startsWith('video')) {
    fileType = 'video';
  }

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
          fileType={fileType}
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
