// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { CALLBACK_URL, userUrls } from '@/const';

type buildAuthorizeClientUrlProps = {
  clientId: string;
  codeChallenge: string;
  codeVerifier: string;
  state: string;
};

export function buildAuthorizeClientUrl(
  props: buildAuthorizeClientUrlProps
): string {
  const { clientId, codeChallenge, codeVerifier, state } = props;

  // Generate the full authorization URL.
  const authUrl = new URL(userUrls.authorize);
  authUrl.searchParams.set('client_id', clientId);
  authUrl.searchParams.set('code_challenge', codeChallenge);
  authUrl.searchParams.set('code_challenge_method', 's256');
  authUrl.searchParams.set('redirect_uri', CALLBACK_URL);
  authUrl.searchParams.set('response_type', 'code');
  authUrl.searchParams.set('state', state);

  // Save the authorization parameters to be used later.
  sessionStorage.setItem('clientId', clientId);
  sessionStorage.setItem('codeVerifier', codeVerifier);
  sessionStorage.setItem('state', state);

  return authUrl.toString();
}

type buildIssueTokenFormDataProps = {
  clientId: string;
  code: string;
  codeVerifier: string;
  redirectUri: string;
};

export function buildIssueTokenFormData(
  props: buildIssueTokenFormDataProps
): string {
  const { clientId, code, codeVerifier, redirectUri } = props;

  const data = new URLSearchParams();
  data.set('client_id', clientId);
  data.set('code', code);
  data.set('code_verifier', codeVerifier);
  data.set('redirect_uri', redirectUri);

  return data.toString();
}
