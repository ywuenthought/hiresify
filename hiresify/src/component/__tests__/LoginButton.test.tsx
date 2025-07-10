// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { render } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import { LOGIN_CALLBACK_URL, userUrls } from '@/const';

import LoginButton from '../LoginButton';

describe('LoginButton UI component', () => {
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
    const { baseElement: root } = render(<LoginButton />);

    // Then
    expect(root).toBeTruthy();
  });

  it('navigates to loginUrl after a click', async () => {
    // Given
    const { getByRole } = render(<LoginButton />);

    // When
    const button = getByRole('button');
    await userEvent.click(button);

    // Then
    const urlObj = new URL(window.location.href);
    const params = new URLSearchParams(urlObj.search);

    expect(urlObj.origin + urlObj.pathname).toBe(userUrls.login);

    const encodedRedirectUri = params.get('redirect_uri') as string;
    expect(encodedRedirectUri).not.toBeNull();
    expect(decodeURIComponent(encodedRedirectUri)).toBe(LOGIN_CALLBACK_URL);
  });
});
