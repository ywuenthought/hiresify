// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { useEffect } from 'react';

import { generateCodeChallenge, generateCodeVerifier } from '@/tool/pkce';
import { buildAuthorizeClientUrl } from '@/tool/url';
import { getManyUuids, setManyItems } from '@/util';

export default function LoginCallback() {
  // Generate authorization parameters.
  const [clientId, state] = getManyUuids(2);
  const codeVerifier = generateCodeVerifier();

  // Save the authorization parameters to be used later.
  setManyItems({ clientId, codeVerifier, state });

  useEffect(() => {
    const redirectToAuth = async () => {
      // Generate the code challenge.
      const codeChallenge = await generateCodeChallenge(codeVerifier);

      // Generate the full authorization URL.
      const authUrl = buildAuthorizeClientUrl({
        clientId,
        codeChallenge,
        state,
      });

      // Navigate to the authorization URL.
      window.location.href = authUrl.toString();
    };

    redirectToAuth();
  });

  return <></>;
}
