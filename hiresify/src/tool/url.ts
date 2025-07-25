// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { callbackUrls, userUrls } from '@/urls';

type buildAuthorizeClientUrlProps = {
  clientId: string;
  codeChallenge: string;
  state: string;
};

export function buildAuthorizeClientUrl(
  props: buildAuthorizeClientUrlProps
): URL {
  const { clientId, codeChallenge, state } = props;

  // Generate the full authorization URL.
  const authUrl = new URL(userUrls.authorize);
  authUrl.searchParams.set('client_id', clientId);
  authUrl.searchParams.set('code_challenge', codeChallenge);
  authUrl.searchParams.set('code_challenge_method', 's256');
  authUrl.searchParams.set('redirect_uri', callbackUrls.authorize);
  authUrl.searchParams.set('response_type', 'code');
  authUrl.searchParams.set('state', state);

  return authUrl;
}

export function buildLoginUserUrl(): URL {
  // Generate the full login URL.
  const loginUrl = new URL(userUrls.login);
  loginUrl.searchParams.set('redirect_uri', callbackUrls.login);

  return loginUrl;
}

export function buildRegisterUserUrl(): URL {
  // Generate the full registration URL.
  const registerUrl = new URL(userUrls.register);
  registerUrl.searchParams.set('redirect_uri', callbackUrls.register);

  return registerUrl;
}
