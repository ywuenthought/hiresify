// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { Box, Stack, Typography } from '@mui/material';
import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';

import BackButton from '@/component/BackButton';
import { routes } from '@/routes';
import { callbackUrls, tokenUrls } from '@/urls';
import { getDetail, getManyItems, postWithUrlEncodedFormData } from '@/util';

export default function AuthorizeCallback() {
  const navigate = useNavigate();
  const [params] = useSearchParams();

  const authCode = params.get('code');
  const curState = params.get('state');

  const [clientId, verifier, preState] = getManyItems([
    'clientId',
    'codeVerifier',
    'state',
  ]);

  const [error, setError] = useState<string | null>(null);

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
        setError('Invalid authorization callback.');
        return;
      }

      const resp = await postWithUrlEncodedFormData(tokenUrls.issue, {
        client_id: clientId,
        code: authCode,
        code_verifier: verifier,
        redirect_uri: callbackUrls.authorize,
      });

      if (!resp.ok) {
        setError((await getDetail(resp)) ?? '');
        return;
      }

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

  if (error) {
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
            data-testid="error"
            variant="body1"
            sx={{ textAlign: 'center' }}
          >
            {error}
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
