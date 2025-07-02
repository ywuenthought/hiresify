// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { Box, Stack, Typography } from '@mui/material';
import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';

import BackButton from '@/component/BackButton';
import { CALLBACK_URL, routes, tokenUrls } from '@/const';
import { buildIssueTokenFormData } from '@/tool/url';
import type { JWTTokenJson } from '@/type';
import { getDetail } from '@/util';

export default function Callback() {
  const [params] = useSearchParams();
  const navigate = useNavigate();

  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const authCode = params.get('code');
  const curState = params.get('state');

  const clientId = sessionStorage.getItem('clientId');
  const verifier = sessionStorage.getItem('codeVerifier');
  const preState = sessionStorage.getItem('state');

  useEffect(() => {
    const requestToken = async () => {
      if (
        !authCode ||
        !curState ||
        !clientId ||
        !verifier ||
        !preState ||
        curState !== preState
      ) {
        setErrorMsg('Invalid authorization callback.');
        return;
      }

      const formData = buildIssueTokenFormData({
        clientId,
        code: authCode,
        codeVerifier: verifier,
        redirectUri: CALLBACK_URL,
      });

      const resp = await fetch(tokenUrls.issue, {
        body: formData,
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        method: 'POST',
      });

      if (!resp.ok) {
        setErrorMsg(await getDetail(resp));
        return;
      }

      const tokenJson: JWTTokenJson = await resp.json();
      const { accessToken, refreshToken = '' } = tokenJson;

      // Clear all the authorization parameters.
      sessionStorage.clear();

      // Save the access and refresh tokens.
      sessionStorage.setItem('accessToken', accessToken);
      sessionStorage.setItem('refreshToken', refreshToken);

      // Navigate to main after a successful login.
      navigate(routes.main.root);
    };

    requestToken();
    // eslint-disable-next-line prettier/prettier
  }, [
    authCode,
    clientId,
    curState,
    preState,
    verifier,
    navigate,
  ]);

  if (errorMsg) {
    return (
      <Stack
        spacing={7}
        sx={{
          alignItems: 'center',
          height: '100%',
          justifyContent: 'center',
        }}
      >
        <Stack spacing={1}>
          <Typography
            fontWeight="bold"
            variant="h4"
            sx={{ textAlign: 'center' }}
          >
            Authorization Failed
          </Typography>
          <Typography
            color="error"
            variant="body1"
            sx={{ textAlign: 'center' }}
          >
            {errorMsg}
          </Typography>
        </Stack>
        <Box width={280}>
          <BackButton />
        </Box>
      </Stack>
    );
  }

  return <></>;
}
