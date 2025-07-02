// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';

import { CALLBACK_URL, routes, tokenUrls } from '@/const';
import { buildIssueTokenFormData } from '@/tool/url';
import type { JWTTokenJson } from '@/type';
import { getDetail, mustGet } from '@/util';

export default function Callback() {
  const [params] = useSearchParams();
  const navigate = useNavigate();

  const authCode = params.get('code');
  const curState = params.get('state');

  const clientId = mustGet('clientId');
  const verifier = mustGet('codeVerifier');
  const preState = mustGet('state');

  useEffect(() => {
    const requestToken = async () => {
      if (authCode && curState === preState) {
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
          throw new Error(await getDetail(resp));
        }

        const tokenJson: JWTTokenJson = await resp.json();
        const { accessToken, refreshToken = '' } = tokenJson;

        // Clear all the authorization parameters.
        sessionStorage.clear();

        // Save the access and refresh tokens.
        sessionStorage.setItem('accessToken', accessToken);
        sessionStorage.setItem('refreshToken', refreshToken);

        // Get to the home page.
        navigate(routes.HOME);
      }
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

  return <></>;
}
