// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { render, waitFor } from '@testing-library/react';

import { AUTHORIZE_CALLBACK_URL, userUrls } from '@/const';
import { getManyItems } from '@/util';

import LoginCallback from '../LoginCallback';

describe('LoginCallback UI component', () => {
  const originalLocation = window.location;
  let mockHref: string;

  beforeAll(() => {
    Object.defineProperty(window, 'location', {
      configurable: true,
      enumerable: true,
      get: () => ({
        ...originalLocation,
        get href() {
          return mockHref;
        },
        set href(value: string) {
          mockHref = value;
        },
      }),
    });
  });

  afterAll(() => {
    Object.defineProperty(window, 'location', {
      configurable: true,
      enumerable: true,
      value: originalLocation,
    });
  });

  it('renders something', () => {
    // When
    const { baseElement: root } = render(<LoginCallback />);

    // Then
    expect(root).toBeTruthy();
  });

  it('navigates to authUrl after being rendered', async () => {
    // When
    render(<LoginCallback />);
    await waitFor(() => window.location.href !== undefined);

    // Then
    const urlObj = new URL(window.location.href);
    const params = new URLSearchParams(urlObj.search);
    const [clientId, codeVerifier, state] = getManyItems([
      'clientId',
      'codeVerifier',
      'state',
    ]);

    expect(urlObj.origin + urlObj.pathname).toBe(userUrls.authorize);
    expect(clientId).toHaveLength(32);
    expect(codeVerifier).toHaveLength(86);
    expect(state).toHaveLength(32);

    expect(params.get('client_id')).toBe(clientId);
    expect(params.get('code_challenge')).toHaveLength(43);
    expect(params.get('code_challenge_method')).toBe('s256');
    expect(params.get('response_type')).toBe('code');
    expect(params.get('state')).toBe(state);

    const encodedRedirectUri = params.get('redirect_uri') as string;
    expect(encodedRedirectUri).not.toBeNull();
    expect(decodeURIComponent(encodedRedirectUri)).toBe(AUTHORIZE_CALLBACK_URL);
  });
});
