// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { Close, Pause, PlayArrow, Replay } from '@mui/icons-material';
import { Box, CircularProgress, IconButton, Stack } from '@mui/material';
import { useCallback, useEffect, useState } from 'react';

import FileProfile from '@/component/FileProfile';
import ProgressBar from '@/component/ProgressBar';
import { useUpload } from '@/upload/hook';

const SPINNINGWHEEL = <CircularProgress size={30} />;

const iconPerStatus = {
  active: <Pause />,
  failed: <Replay />,
  paused: <PlayArrow />,
};

type FileControllerProps = {
  file: File;
  partSize: number;
  removeFile: () => void;
};

export default function FileController(props: FileControllerProps) {
  const { file, partSize } = props;
  const { removeFile } = props;

  const { degree, status, abort, pause, retry, start } = useUpload({
    file,
    partSize,
  });

  const uploading = status !== 'passed';
  const [abortOff, setAbortOff] = useState<boolean>(false);
  const [otherOff, setOtherOff] = useState<boolean>(false);

  const handleAbort = useCallback(async () => {
    setOtherOff(true);
    await abort();
    setOtherOff(false);

    removeFile();
  }, [abort, removeFile]);

  const handleOther = useCallback(async () => {
    setAbortOff(true);

    switch (status) {
      case 'active':
        await pause();
        break;
      case 'failed':
        await retry();
        break;
      case 'paused':
        await start();
        break;
      default:
        break;
    }

    setAbortOff(false);
  }, [status, pause, retry, start]);

  useEffect(() => {
    const startUpload = async () => await start();
    startUpload();
  }, [start]);

  return (
    <Box sx={{ height: 50, minWidth: 150, my: 4 }}>
      <Stack
        direction="column"
        spacing={1}
        sx={{ height: '100%', width: '100%' }}
      >
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
            fileName={file.name}
            majorButton={
              uploading &&
              (abortOff ? (
                SPINNINGWHEEL
              ) : (
                <IconButton disabled={otherOff} onClick={handleOther}>
                  {iconPerStatus[status]}
                </IconButton>
              ))
            }
            minorButton={
              uploading &&
              (otherOff ? (
                SPINNINGWHEEL
              ) : (
                <IconButton disabled={abortOff} onClick={handleAbort}>
                  <Close />
                </IconButton>
              ))
            }
          />
        </Stack>
        {uploading && <ProgressBar progress={degree} />}
      </Stack>
    </Box>
  );
}
