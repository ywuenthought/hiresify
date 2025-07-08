// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import {
  AUTHORIZE_CALLBACK_URL,
  REGISTER_CALLBACK_URL,
  userUrls,
} from '@/const';

type buildAuthorizeClientUrlProps = {
  clientId: string;
  codeChallenge: string;
  codeVerifier: string;
  state: string;
};

export function buildAuthorizeClientUrl(
  props: buildAuthorizeClientUrlProps
): URL {
  const { clientId, codeChallenge, codeVerifier, state } = props;

  // Generate the full authorization URL.
  const authUrl = new URL(userUrls.authorize);
  authUrl.searchParams.set('client_id', clientId);
  authUrl.searchParams.set('code_challenge', codeChallenge);
  authUrl.searchParams.set('code_challenge_method', 's256');
  authUrl.searchParams.set('redirect_uri', AUTHORIZE_CALLBACK_URL);
  authUrl.searchParams.set('response_type', 'code');
  authUrl.searchParams.set('state', state);

  // Save the authorization parameters to be used later.
  sessionStorage.setItem('clientId', clientId);
  sessionStorage.setItem('codeVerifier', codeVerifier);
  sessionStorage.setItem('state', state);

  return authUrl;
}

export function buildRegisterUserUrl(): URL {
  // Generate the full registration URL.
  const registerUrl = new URL(userUrls.register);
  registerUrl.searchParams.set('redirect_uri', REGISTER_CALLBACK_URL);

  return registerUrl;
}
