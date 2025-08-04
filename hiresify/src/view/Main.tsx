// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { Box, Paper, Stack, Typography } from '@mui/material';
import { useCallback, useEffect, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { useNavigate } from 'react-router-dom';

import bg from '@/assets/bg.jpg';
import Background from '@/component/Background';
import LogoutButton from '@/component/LogoutButton';
import FileController from '@/composite/FileController';
import { CHUNK_SIZE } from '@/const';
import { routes } from '@/routes';
import { tokenUrls } from '@/urls';

export default function Main() {
  const navigate = useNavigate();
  const [files, setFiles] = useState<Set<File>>(new Set());

  const onDrop = useCallback((curFiles: File[]) => {
    setFiles((preFiles) => new Set([...preFiles, ...curFiles]));
  }, []);
  const { getInputProps, getRootProps, isDragActive } = useDropzone({ onDrop });

  useEffect(() => {
    const refreshToken = async () => {
      const resp = await fetch(tokenUrls.refresh, {
        method: 'POST',
        credentials: 'include',
      });

      if (!resp.ok) {
        navigate(routes.home.root);
      }
    };

    refreshToken();
  }, [navigate]);

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
        <Paper
          elevation={4}
          sx={{
            height: 500,
            overflow: 'auto',
            padding: 4,
            width: 700,
          }}
        >
          {Array.from(files).map((file, index) => (
            <FileController
              key={`controller:${index}`}
              file={file}
              partSize={CHUNK_SIZE}
              removeFile={() =>
                setFiles((preFiles) => {
                  const curFiles = new Set(preFiles);
                  curFiles.delete(file);
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
