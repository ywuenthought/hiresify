// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { Login } from '@mui/icons-material';
import type { ButtonProps } from '@mui/material';
import { Button } from '@mui/material';

import { generateCodeChallenge, generateCodeVerifier } from '@/tool/pkce';
import { buildAuthorizeClientUrl } from '@/tool/url';
import { getManyUuids, setManyItems } from '@/util';

export default function LoginButton(props: ButtonProps) {
  const handleClick = async () => {
    // Generate authorization parameters.
    const [clientId, state] = getManyUuids(2);
    const codeVerifier = generateCodeVerifier();
    const codeChallenge = await generateCodeChallenge(codeVerifier);

    // Save the authorization parameters to be used later.
    setManyItems({ clientId, codeVerifier, state });

    // Generate the full authorization URL.
    const authUrl = buildAuthorizeClientUrl({
      clientId,
      codeChallenge,
      codeVerifier,
      state,
    });

    // Redirect to the authorization URL.
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
