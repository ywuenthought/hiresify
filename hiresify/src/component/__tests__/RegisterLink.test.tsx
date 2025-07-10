// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { render } from '@testing-library/react';

import { buildRegisterUserUrl } from '@/tool/url';

import RegisterLink from '../RegisterLink';

describe('RegisterLink UI component', () => {
  beforeEach(() => sessionStorage.clear());

  it('renders something', () => {
    // When
    const { baseElement: root } = render(<RegisterLink />);

    // Then
    expect(root).toBeTruthy();
  });

  it('links to the user register URL', () => {
    // When
    const { getByRole } = render(<RegisterLink />);

    // Then
    const link = getByRole('link');
    const registerUrl = buildRegisterUserUrl();
    expect(link).toHaveAttribute('href', registerUrl.toString());
    expect(link).toHaveAttribute('rel', 'noopener noreferrer');
  });
});
