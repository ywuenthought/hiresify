// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { Login } from '@mui/icons-material';
import type { ButtonProps } from '@mui/material';
import { Button } from '@mui/material';
import { v4 as uuid4 } from 'uuid';

import { generateCodeChallenge, generateCodeVerifier } from '@/tool/pkce';
import { buildAuthorizeClientUrl } from '@/tool/url';

export default function LoginButton(props: ButtonProps) {
  const handleClick = async () => {
    const clientId = uuid4();
    const state = uuid4();

    const codeVerifier = generateCodeVerifier();
    const codeChallenge = await generateCodeChallenge(codeVerifier);

    // Generate the full authorization URL.
    const authUrl = buildAuthorizeClientUrl({
      clientId,
      codeChallenge,
      codeVerifier,
      state,
    });

    // Save the authorization parameters to be used later.
    sessionStorage.setItem('clientId', clientId);
    sessionStorage.setItem('codeVerifier', codeVerifier);
    sessionStorage.setItem('state', state);

    // Redirect to the authorization URL on the current tab.
    window.location.href = authUrl;
  };

  return (
    <Button
      color="primary"
      fullWidth
      size="large"
      startIcon={<Login />}
      variant="contained"
      onClick={handleClick}
      {...props}
    >
      Get Started
    </Button>
  );
}
