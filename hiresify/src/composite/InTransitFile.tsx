// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { Close, Pause, PlayArrow, Replay } from '@mui/icons-material';
import { Box, CircularProgress, IconButton, Stack } from '@mui/material';
import { useCallback, useEffect, useState } from 'react';

import FileProfile from '@/component/FileProfile';
import ProgressBar from '@/component/ProgressBar';
import type { FrontendBlob } from '@/type';
import { useUpload } from '@/upload/hook';

const SPINNINGWHEEL = <CircularProgress size={30} />;

const iconPerStatus = {
  active: <Pause />,
  failed: <Replay />,
  paused: <PlayArrow />,
};

type InTransitFileProps = {
  jsBlob: File;
  frontendBlob: FrontendBlob;
  partSize: number;
};

export default function InTransitFile(props: InTransitFileProps) {
  const { jsBlob, frontendBlob, partSize } = props;
  const { uid: blobUid, fileName, progress, status } = frontendBlob;

  const { abort, pause, retry, start } = useUpload({
    jsBlob,
    blobUid,
    partSize,
  });

  const [abortOff, setAbortOff] = useState<boolean>(false);
  const [otherOff, setOtherOff] = useState<boolean>(false);

  const handleAbort = useCallback(async () => {
    setOtherOff(true);
    await abort();
    setOtherOff(false);
  }, [abort]);

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

  if (status === 'passed') {
    return <></>;
  }

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
            fileName={fileName}
            majorButton={
              abortOff ? (
                SPINNINGWHEEL
              ) : (
                <IconButton disabled={otherOff} onClick={handleOther}>
                  {iconPerStatus[status]}
                </IconButton>
              )
            }
            minorButton={
              otherOff ? (
                SPINNINGWHEEL
              ) : (
                <IconButton disabled={abortOff} onClick={handleAbort}>
                  <Close />
                </IconButton>
              )
            }
          />
        </Stack>
        <ProgressBar progress={progress} />
      </Stack>
    </Box>
  );
}
